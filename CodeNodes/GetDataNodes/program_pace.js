const text = `$$${identify_state.output}`;

// program_pace puede ser: null o un string (ej: "intensivo", "regular")
const regexPreferredModality = /"program_pace"\s*:\s*(null|"[^"]*")/;

const match = text.match(regexPreferredModality);

const program_pace = match
  ? (match[1] === "null" ? null : match[1].replace(/"/g, ""))
  : null;

console.log(program_pace); // "virtual" o null
