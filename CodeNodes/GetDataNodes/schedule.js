// Regex para schedule.selected_date (puede ser null o string)
const regexSelectedDate = /"selected_date"\s*:\s*(null|"[^"]*")/;

// Regex para schedule.schedule_confirmed (true/false)
const regexScheduleConfirmed = /"schedule_confirmed"\s*:\s*(true|false)/;
const text = `$$${identify_state.output}`;

const matchSelectedDate = text.match(regexSelectedDate);
const matchScheduleConfirmed = text.match(regexScheduleConfirmed);

// Parseos

const selected_date = matchSelectedDate
  ? (matchSelectedDate[1] === "null" ? null : matchSelectedDate[1].replace(/"/g, ""))
  : null;

const schedule_confirmed = matchScheduleConfirmed
  ? matchScheduleConfirmed[1] === "true"
  : null;

// Logs
console.log("selected_date:", selected_date);
console.log("schedule_confirmed:", schedule_confirmed);
