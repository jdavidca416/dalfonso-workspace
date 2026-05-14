const text = `$$${identify_state.output}`;

// company es siempre un string entrecomillado (ej: "Acme S.A.", "null")
const regexCompany = /"company"\s*:\s*"([^"]*)"/;

const match = text.match(regexCompany);

const company = match ? match[1] : null;

console.log(company); // string o null si no hay match
