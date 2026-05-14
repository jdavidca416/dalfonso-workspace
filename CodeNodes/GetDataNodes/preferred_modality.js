const text = `$$${identify_state.output}`;

// preferred_modality puede ser: null o un string (ej: "virtual", "presencial", etc)
const regexPreferredModality = /"preferred_modality"\s*:\s*(null|"[^"]*")/;

const match = text.match(regexPreferredModality);

const preferredModality = match
  ? (match[1] === "null" ? null : match[1].replace(/"/g, ""))
  : null;

console.log(preferredModality); // "virtual" o null
