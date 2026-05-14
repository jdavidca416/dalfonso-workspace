const text = `$$${identify_state.output}`;

// name puede ser: null o un string (ej: "Juan Pérez")
const regexName = /"name"\s*:\s*(null|"[^"]*")/;

const match = text.match(regexName);

const name = match
  ? (match[1] === "null" ? null : match[1].replace(/"/g, ""))
  : null;

console.log(name); // "Juan Pérez" o null
