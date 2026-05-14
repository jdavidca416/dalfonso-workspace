const text = `$$${identify_state.output}`;

// name puede ser: null o un string (ej: "Juan Pérez")
const regexName = /"recipient"\s*:\s*(null|"[^"]*")/;

const match = text.match(regexName);

const recipient = match
  ? (match[1] === "null" ? null : match[1].replace(/"/g, ""))
  : null;

const parent_tone = "formal, empático, informativo, vendedor profesional.";
const young_tone = "cercano, ágil, motivador, entusiasta.";
const professional_tone = "ejecutivo, enfocado en resultados y transformación.";

let tone = parent_tone;

switch (recipient) {
  case "Padre":
    tone = parent_tone;
    break;
  case "Joven":
    tone = young_tone;
    break;
  case "Profesional":
    tone = professional_tone;
    break;
  default:
    tone = parent_tone;
    break;
}

console.log(tone)
