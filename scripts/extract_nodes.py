#!/usr/bin/env python3
"""
extract_nodes.py
================

Regenera los archivos editables de prompts y nodos de código a partir de un
export JSON del agente Lucrecia (D'Alfonso).

Estructura generada (idempotente):

    <workspace>/
      PromptNodes/
        <label>.md            # un archivo por cada promptNode (texto crudo del prompt)
      CodeNodes/
        <label>.js            # nodos de código que NO son extractores regex de estado
        GetDataNodes/
          <label>.js          # nodos que extraen info via regex desde
                              # identify_state.output o triggers_detection.output

Reglas de clasificación de codeExecutionNode:
- GetDataNode  → el código usa regex (/.../, .match(), new RegExp) Y
                 lee de `identify_state.output` o `triggers_detection.output`.
- CodeNode     → cualquier otro nodo de código (transformaciones, HTTP, etc.).

Convenciones:
- El contenido de cada archivo es ÚNICAMENTE el cuerpo del prompt/código
  (sin headers de metadata), listo para copy-paste al sistema.
- Line endings normalizados a LF.
- Archivos "huérfanos" en PromptNodes/ y CodeNodes/ (que ya no existen en el
  JSON actual) se eliminan, salvo que se use --no-clean.

Uso:
    python3 scripts/extract_nodes.py                       # autodetecta JSON
    python3 scripts/extract_nodes.py --json path/al.json
    python3 scripts/extract_nodes.py --out /otro/destino
    python3 scripts/extract_nodes.py --dry-run             # no escribe nada
    python3 scripts/extract_nodes.py --no-clean            # no borra huérfanos
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Iterable


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9_\- ]+")
REGEX_HINT_RE = re.compile(r"\bregex\w*\b|\.match\(|new\s+RegExp", re.IGNORECASE)
STATE_SOURCES = ("identify_state.output", "triggers_detection.output")


def safe_name(value: str, fallback: str) -> str:
    """Sanitiza un label para usarlo como nombre de archivo."""
    cleaned = SAFE_NAME_RE.sub("", value or "").strip().replace(" ", "_")
    return cleaned or fallback


def normalize_lf(text: str) -> str:
    """
    Normaliza saltos de linea a LF y asegura un unico newline final.

    Convierte tambien separadores Unicode invisibles que aparecen a veces en
    exports y rompen el copy-paste desde VS Code:
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


def is_regex_state_extractor(code: str) -> bool:
    """Heurística: nodo que extrae info por regex desde el estado conversacional."""
    if not code:
        return False
    if not REGEX_HINT_RE.search(code):
        return False
    return any(src in code for src in STATE_SOURCES)


def autodetect_json(workspace: Path) -> Path | None:
    """Devuelve el .json más reciente en la raíz del workspace, si existe uno."""
    candidates = sorted(
        (p for p in workspace.glob("*.json") if p.is_file()),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def parse_nodes(raw_nodes: Iterable) -> list[dict]:
    """Los nodes pueden venir como dicts o como strings JSON; los normaliza."""
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
    Escribe content a path. Devuelve uno de: 'created', 'updated', 'unchanged'.
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


def clean_orphans(folder: Path, keep: set[str], suffix: str, dry_run: bool) -> list[str]:
    """Elimina archivos del folder con el suffix dado que no están en `keep`."""
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

def extract(json_path: Path, out_dir: Path, dry_run: bool, clean: bool) -> int:
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

    prompt_dir = out_dir / "PromptNodes"
    code_root = out_dir / "CodeNodes"
    get_data_dir = code_root / "GetDataNodes"

    if not dry_run:
        prompt_dir.mkdir(parents=True, exist_ok=True)
        code_root.mkdir(parents=True, exist_ok=True)
        get_data_dir.mkdir(parents=True, exist_ok=True)

    prompt_files: set[str] = set()
    code_root_files: set[str] = set()
    get_data_files: set[str] = set()

    stats = {"created": 0, "updated": 0, "unchanged": 0}
    rows: list[tuple[str, str, str]] = []  # (status, kind, filename)

    for node in nodes:
        ntype = node.get("type", "")
        cfg = (node.get("data") or {}).get("config") or {}
        label = (node.get("data") or {}).get("label") or ""
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
            if is_regex_state_extractor(code):
                path = get_data_dir / filename
                rel = f"CodeNodes/GetDataNodes/{filename}"
                get_data_files.add(filename)
            else:
                path = code_root / filename
                rel = f"CodeNodes/{filename}"
                code_root_files.add(filename)
            status = write_file(path, normalize_lf(code), dry_run)
            stats[status] += 1
            rows.append((status, "code", rel))

    # Limpiar huérfanos
    removed: list[str] = []
    if clean:
        removed += [f"PromptNodes/{n}" for n in clean_orphans(prompt_dir, prompt_files, ".md", dry_run)]
        removed += [f"CodeNodes/{n}" for n in clean_orphans(code_root, code_root_files, ".js", dry_run)]
        removed += [
            f"CodeNodes/GetDataNodes/{n}"
            for n in clean_orphans(get_data_dir, get_data_files, ".js", dry_run)
        ]

    # Reporte
    prefix = "[DRY-RUN] " if dry_run else ""
    print(f"{prefix}Source : {json_path}")
    print(f"{prefix}Output : {out_dir}")
    print(
        f"{prefix}Result : {stats['created']} creados, "
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
        description="Extrae prompts y nodos de código del JSON del agente Lucrecia.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--json",
        type=Path,
        default=None,
        help="Ruta al export JSON. Si se omite, se usa el .json más reciente en --out.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Workspace donde se generan PromptNodes/ y CodeNodes/. "
             "Por defecto, la carpeta padre de scripts/.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="No escribe nada; solo reporta lo que haría.",
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="No elimina archivos huérfanos (los que ya no están en el JSON).",
    )

    args = parser.parse_args(argv)
    out_dir = args.out.resolve()
    json_path = args.json.resolve() if args.json else autodetect_json(out_dir)

    if json_path is None:
        print(f"ERROR: no se encontró ningún .json en {out_dir}", file=sys.stderr)
        return 1

    return extract(
        json_path=json_path,
        out_dir=out_dir,
        dry_run=args.dry_run,
        clean=not args.no_clean,
    )


if __name__ == "__main__":
    sys.exit(main())
