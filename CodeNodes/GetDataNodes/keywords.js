const text = `$$${triggers_detection.output}`;

// detected_keywords puede ser: null, un string, o un array
const regex = /"keywords"\s*:\s*(null|"[^"]*"|\[[^\]]*\])/;

const match = text.match(regex);

const detected_keywords = match
  ? (match[1] === "null"
    ? null
    : match[1]
      .replace(/^"|"$|^\[|\]$/g, "") // elimina comillas o corchetes
      .replace(/,/g, ", ") // opcional: añade espacio después de comas para mejor formato
  )
  : null;

console.log(detected_keywords);
