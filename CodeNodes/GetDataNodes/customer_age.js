const text = `$$${identify_state.output}`;

// age puede ser: null o un número (ej: 16, 25, etc)
const regexAge = /"age"\s*:\s*(null|\d+)/;

const match = text.match(regexAge);

const age = match
  ? (match[1] === "null" ? null : Number(match[1]))
  : null;

console.log(age); // 16, 25 o null
