const text = `$$${identify_state.output}`;

const regexName = /"consulting_type"\s*:\s*(?:null|"([^"]*)")/;

const match = text.match(regexName);

// Si match[1] es undefined, significa que cayó en la opción 'null'
const name = (match && match[1] !== undefined) ? match[1] : null;

console.log(name);
