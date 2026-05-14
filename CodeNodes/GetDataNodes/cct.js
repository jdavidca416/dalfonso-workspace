const text = `$$${identify_state.output}`;

// cct es siempre un string entrecomillado (ej: "clave", "null")
const regexCct = /"cct"\s*:\s*"([^"]*)"/;

const match = text.match(regexCct);

const cct = match ? match[1] : null;

console.log(cct); // string o null si no hay match
