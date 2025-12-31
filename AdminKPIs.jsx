import RiskBadge from "./RiskBadge";
import { normalizeRisk } from "../utils/riskMap";

export default function AdminKPIs({ evaluations }) {
  const total = evaluations.length;

  const green = evaluations.filter(
    e => normalizeRisk(e.overall_risk) === "GREEN"
  ).length;

  const amber = evaluations.filter(
    e => normalizeRisk(e.overall_risk) === "AMBER"
  ).length;

  const red = evaluations.filter(
    e => normalizeRisk(e.overall_risk) === "RED"
  ).length;

  const breachRate = total ? Math.round((red / total) * 100) : 0;

  return (
    <>
      <h2 style={{ marginBottom: 16 }}>Portfolio Risk Snapshot</h2>

      <div className="grid grid-4" style={{ marginBottom: 28 }}>
        <div className="card">
          <p>Total Evaluations</p>
          <h1>{total}</h1>
        </div>

        <div className="card">
          <p>RED Breaches</p>
          <h1 style={{ color: "#DC2626" }}>{red}</h1>
        </div>

        <div className="card">
          <p>AMBER Warnings</p>
          <h1 style={{ color: "#F59E0B" }}>{amber}</h1>
        </div>

        <div className="card">
          <p>Breach Rate</p>
          <h1>{breachRate}%</h1>
        </div>
      </div>

      {/* Recent RED Evaluations */}
      <div className="card">
        <h3 style={{ marginBottom: 12 }}>Recent High-Risk Evaluations</h3>

        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Period</th>
              <th>Risk</th>
            </tr>
          </thead>
          <tbody>
            {evaluations
              .filter(e => normalizeRisk(e.overall_risk) === "RED")
              .slice(0, 5)
              .map(e => (
                <tr key={e.id}>
                  <td>{e.id}</td>
                  <td>{e.period}</td>
                  <td>
                    <RiskBadge value="RED" />
                  </td>
                </tr>
              ))}

            {red === 0 && (
              <tr>
                <td colSpan="3" style={{ padding: 20, color: "#64748b" }}>
                  No RED breaches detected
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </>
  );
}
