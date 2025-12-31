import { useEffect, useState } from "react";
import api from "../api/client";
import RiskBadge from "../components/RiskBadge";

export default function History({ openDetail }) {
  const [evaluations, setEvaluations] = useState([]);

  useEffect(() => {
    api.get("/evaluations")
      .then(res => setEvaluations(res.data || []))
      .catch(err => console.error("History load failed", err));
  }, []);

  return (
    <>
      <h1 style={{ marginBottom: 6 }}>Evaluation History</h1>
      <p style={{ marginBottom: 24 }}>
        Complete audit trail of covenant evaluations
      </p>

      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Period</th>
              <th>Overall Risk</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {evaluations.map(e => (
              <tr key={e.id}>
                <td>{e.id}</td>
                <td>{e.period}</td>
                <td>
                  <RiskBadge value={e.overall_risk} />
                </td>
                <td>
                  <button
                    className="secondary"
                    onClick={() => openDetail(e.id)}
                  >
                    View
                  </button>
                </td>
              </tr>
            ))}

            {evaluations.length === 0 && (
              <tr>
                <td colSpan="4" style={{ padding: 20, color: "#64748b" }}>
                  No evaluations found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </>
  );
}
