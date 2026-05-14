const text = `$$${identify_state.output}`;

// valid es siempre un string entrecomillado (ej: "TRUE", "FALSE", "null")
const regexValid = /"valid"\s*:\s*"([^"]*)"/;

const match = text.match(regexValid);

const valid = match ? match[1] : null;

console.log(valid); // "TRUE", "FALSE", "null", etc.
