const text = `$$${identify_state.output}`;

// parent_tutor_name puede ser: null o un string (ej: "María López")
const regexParentTutorName = /"parent_tutor_name"\s*:\s*(null|"[^"]*")/;

const match = text.match(regexParentTutorName);

const parentTutorName = match
  ? (match[1] === "null" ? null : match[1].replace(/"/g, ""))
  : null;

console.log(parentTutorName); // "María López" o null
