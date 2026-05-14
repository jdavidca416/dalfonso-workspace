const text = `$$${triggers_detection.output}`;

const regex = /"category"\s*:\s*(null|"[^"]*")/;

const match = text.match(regex);

const category = match
  ? (match[1] === "null" ? null : match[1].replace(/"/g, ""))
  : null;

console.log(category); // "category" o null
