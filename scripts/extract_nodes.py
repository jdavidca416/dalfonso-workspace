#!/usr/bin/env python3
"""
extract_nodes.py
================

Extrae los nodos editables de un agente conversacional exportado como JSON
y los vuelca como archivos de texto listos para editar y hacer copy-paste.

Estructura generada (idempotente):

    <workspace>/
      PromptNodes/
        <label>.md            # un archivo por cada promptNode
      CodeNodes/
        <label>.js            # nodos de código genéricos
        GetDataNodes/
          <label>.js          # nodos que extraen datos via regex desde
                              # una o más fuentes de estado configurables

Clasificación de codeExecutionNode:
  GetDataNode  → el código usa regex (/.../, .match(), new RegExp) Y
                 referencia al menos una de las fuentes de estado
                 definidas con --state-sources.
  CodeNode     → cualquier otro nodo de código.

Convenciones:
  - Cada archivo contiene ÚNICAMENTE el cuerpo del prompt o el código JS,
    sin metadata, listo para copy-paste al sistema.
  - Line endings normalizados a LF.
  - Separadores Unicode invisibles (U+2028, U+2029, U+0085) eliminados.
  - Archivos huérfanos (que ya no existen en el JSON) se eliminan por
    defecto; desactivar con --no-clean.

Uso:
    python3 scripts/extract_nodes.py
    python3 scripts/extract_nodes.py --json path/al/export.json
    python3 scripts/extract_nodes.py --out /otro/proyecto
    python3 scripts/extract_nodes.py --state-sources identify_state.output categorizador.output
    python3 scripts/extract_nodes.py --dry-run
    python3 scripts/extract_nodes.py --no-clean
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Iterable, Sequence


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9_\- ]+")
REGEX_HINT_RE = re.compile(r"\bregex\w*\b|\.match\(|new\s+RegExp", re.IGNORECASE)

DEFAULT_STATE_SOURCES = ["identify_state.output"]


def safe_name(value: str, fallback: str) -> str:
    """Sanitiza un label para usarlo como nombre de archivo."""
    cleaned = SAFE_NAME_RE.sub("", value or "").strip().replace(" ", "_")
    return cleaned or fallback


def normalize_lf(text: str) -> str:
    """
    Normaliza saltos de línea a LF y asegura un único newline final.

    Convierte también separadores Unicode invisibles que aparecen en
    algunos exports y rompen el copy-paste desde VS Code:
      U+2028  LINE SEPARATOR
      U+2029  PARAGRAPH SEPARATOR
      U+0085  NEXT LINE
    """
    text = (
        text.replace("\r\n", "\n")
            .replace("\r", "\n")
            .replace(chr(0x2028), "\n")
            .replace(chr(0x2029), "\n")
            .replace(chr(0x0085), "\n")
    )
    return text.rstrip() + "\n"


def is_regex_state_extractor(code: str, state_sources: Sequence[str]) -> bool:
    """
    Heurística: nodo que extrae información por regex desde el estado
    conversacional. Devuelve True si el código:
      1. Contiene al menos un patrón de regex, Y
      2. Referencia al menos una de las fuentes de estado indicadas.
    """
    if not code or not state_sources:
        return False
    if not REGEX_HINT_RE.search(code):
        return False
    return any(src in code for src in state_sources)


def autodetect_json(workspace: Path) -> Path | None:
    """Devuelve el .json más reciente en la raíz del workspace."""
    candidates = sorted(
        (p for p in workspace.glob("*.json") if p.is_file()),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def parse_nodes(raw_nodes: Iterable) -> list[dict]:
    """Normaliza nodos que pueden venir como dicts o como strings JSON."""
    parsed: list[dict] = []
    for n in raw_nodes:
        if isinstance(n, str):
            try:
                parsed.append(json.loads(n))
            except json.JSONDecodeError as exc:
                print(f"  ! nodo descartado (JSON inválido): {exc}", file=sys.stderr)
        elif isinstance(n, dict):
            parsed.append(n)
    return parsed


def write_file(path: Path, content: str, dry_run: bool) -> str:
    """
    Escribe content en path.
    Devuelve: 'created', 'updated' o 'unchanged'.
    """
    existed = path.exists()
    if existed:
        try:
            current = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            current = None
        if current == content:
            return "unchanged"
    if dry_run:
        return "updated" if existed else "created"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return "updated" if existed else "created"


def clean_orphans(
    folder: Path, keep: set[str], suffix: str, dry_run: bool
) -> list[str]:
    """Elimina archivos con el sufijo dado que no están en `keep`."""
    if not folder.exists():
        return []
    removed: list[str] = []
    for entry in folder.iterdir():
        if entry.is_file() and entry.name.endswith(suffix) and entry.name not in keep:
            removed.append(entry.name)
            if not dry_run:
                entry.unlink()
    return removed


# -----------------------------------------------------------------------------
# Core extraction
# -----------------------------------------------------------------------------

def extract(
    json_path: Path,
    out_dir: Path,
    dry_run: bool,
    clean: bool,
    state_sources: Sequence[str],
) -> int:
    if not json_path.is_file():
        print(f"ERROR: no encuentro el JSON en {json_path}", file=sys.stderr)
        return 1

    with json_path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    try:
        raw_nodes = data["agentFlow"]["nodes"]
    except (KeyError, TypeError):
        print("ERROR: el JSON no contiene agentFlow.nodes", file=sys.stderr)
        return 1

    nodes = parse_nodes(raw_nodes)

    prompt_dir  = out_dir / "PromptNodes"
    code_root   = out_dir / "CodeNodes"
    get_data_dir = code_root / "GetDataNodes"

    if not dry_run:
        prompt_dir.mkdir(parents=True, exist_ok=True)
        code_root.mkdir(parents=True, exist_ok=True)
        get_data_dir.mkdir(parents=True, exist_ok=True)

    prompt_files:   set[str] = set()
    code_root_files: set[str] = set()
    get_data_files: set[str] = set()

    stats = {"created": 0, "updated": 0, "unchanged": 0}
    rows: list[tuple[str, str, str]] = []  # (status, kind, rel_path)

    for node in nodes:
        ntype  = node.get("type", "")
        cfg    = (node.get("data") or {}).get("config") or {}
        label  = (node.get("data") or {}).get("label") or ""
        node_id = node.get("id", "unknown")

        if ntype == "promptNode":
            text = cfg.get("prompt", "")
            filename = safe_name(label, f"prompt_{node_id[:8]}") + ".md"
            path = prompt_dir / filename
            status = write_file(path, normalize_lf(text), dry_run)
            stats[status] += 1
            prompt_files.add(filename)
            rows.append((status, "prompt", f"PromptNodes/{filename}"))

        elif ntype == "codeExecutionNode":
            code = cfg.get("code", "")
            filename = safe_name(label, f"code_{node_id[:8]}") + ".js"
            if is_regex_state_extractor(code, state_sources):
                path = get_data_dir / filename
                rel  = f"CodeNodes/GetDataNodes/{filename}"
                get_data_files.add(filename)
            else:
                path = code_root / filename
                rel  = f"CodeNodes/{filename}"
                code_root_files.add(filename)
            status = write_file(path, normalize_lf(code), dry_run)
            stats[status] += 1
            rows.append((status, "code", rel))

    # Limpiar huérfanos
    removed: list[str] = []
    if clean:
        removed += [
            f"PromptNodes/{n}"
            for n in clean_orphans(prompt_dir, prompt_files, ".md", dry_run)
        ]
        removed += [
            f"CodeNodes/{n}"
            for n in clean_orphans(code_root, code_root_files, ".js", dry_run)
        ]
        removed += [
            f"CodeNodes/GetDataNodes/{n}"
            for n in clean_orphans(get_data_dir, get_data_files, ".js", dry_run)
        ]

    # Reporte
    prefix = "[DRY-RUN] " if dry_run else ""
    print(f"{prefix}Source       : {json_path}")
    print(f"{prefix}Output       : {out_dir}")
    print(f"{prefix}State sources: {', '.join(state_sources)}")
    print(
        f"{prefix}Result       : {stats['created']} creados, "
        f"{stats['updated']} actualizados, {stats['unchanged']} sin cambios, "
        f"{len(removed)} eliminados"
    )
    print()

    if rows:
        rows.sort(key=lambda r: (r[1], r[2]))
        width = max(len(r[2]) for r in rows)
        for status, _kind, rel in rows:
            print(f"  {status:9s}  {rel:<{width}s}")

    if removed:
        print()
        print("Huérfanos eliminados:")
        for r in removed:
            print(f"  removed    {r}")

    return 0


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extrae prompts y nodos de código de un export JSON de agente conversacional.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--json",
        type=Path,
        default=None,
        help=(
            "Ruta al export JSON. "
            "Si se omite, se usa el .json más reciente en --out."
        ),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help=(
            "Workspace donde se generan PromptNodes/ y CodeNodes/. "
            "Por defecto, la carpeta padre de scripts/."
        ),
    )
    parser.add_argument(
        "--state-sources",
        nargs="+",
        default=DEFAULT_STATE_SOURCES,
        metavar="SOURCE",
        help=(
            "Nombres de output de nodos que actúan como fuente de estado "
            "conversacional. Los codeExecutionNode que los referencien y "
            "usen regex se clasifican en GetDataNodes/. "
            f"Por defecto: {DEFAULT_STATE_SOURCES}. "
            "Ejemplo: --state-sources identify_state.output categorizador.output"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="No escribe nada; solo reporta lo que haría.",
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="No elimina archivos huérfanos.",
    )

    args = parser.parse_args(argv)
    out_dir   = args.out.resolve()
    json_path = args.json.resolve() if args.json else autodetect_json(out_dir)

    if json_path is None:
        print(f"ERROR: no se encontró ningún .json en {out_dir}", file=sys.stderr)
        return 1

    return extract(
        json_path=json_path,
        out_dir=out_dir,
        dry_run=args.dry_run,
        clean=not args.no_clean,
        state_sources=args.state_sources,
    )


if __name__ == "__main__":
    sys.exit(main())
