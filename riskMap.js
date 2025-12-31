export function normalizeRisk(risk) {
  if (!risk) return "GREEN";

  switch (risk.toUpperCase()) {
    case "HIGH":
    case "RED":
      return "RED";

    case "MEDIUM":
    case "AMBER":
      return "AMBER";

    case "LOW":
    case "GREEN":
    default:
      return "GREEN";
  }
}
