import { useEffect, useState } from "react";
import api from "../api/client";
import RiskBadge from "../components/RiskBadge";

export default function EvaluationDetail({ evaluationId, back }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    if (!evaluationId) return;

    api.get(`/evaluations/${evaluationId}`)
      .then(res => setData(res.data))
      .catch(err => console.error("Detail load failed", err));
  }, [evaluationId]);

  const downloadPDF = async () => {
    try {
      const response = await api.get(
        `/evaluations/${data.id}/report/pdf`,
        { responseType: "blob" }
      );

      const blob = new Blob([response.data], { type: "application/pdf" });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `Covenant_Report_${data.id}.pdf`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("PDF download failed", err);
    }
  };

  const downloadExcel = async () => {
    try {
      const response = await api.get(
        `/evaluations/${data.id}/report/excel`,
        { responseType: "blob" }
      );

      const blob = new Blob([response.data], {
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
      });

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `Covenant_Report_${data.id}.xlsx`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Excel download failed", err);
    }
  };

  if (!data) {
    return <p>Loading evaluation…</p>;
  }

  return (
    <>
      {/* HEADER */}
      <div style={{ marginBottom: 24 }}>
        <button className="secondary" onClick={back}>
          ← Back
        </button>
      </div>

      {/* SUMMARY */}
      <div className="grid grid-3" style={{ marginBottom: 28 }}>
        <div className="card">
          <p className="muted">Evaluation ID</p>
          <h1>{data.id}</h1>
        </div>

        <div className="card">
          <p className="muted">Reporting Period</p>
          <h1>{data.period}</h1>
        </div>

        <div className="card">
          <p className="muted">Overall Risk</p>
          <RiskBadge value={data.overall_risk} />
        </div>
      </div>

      {/* COVENANT TABLE */}
      <div className="card" style={{ marginBottom: 24 }}>
        <h2 style={{ marginBottom: 12 }}>Covenant Results</h2>

        <table className="table">
          <thead>
            <tr>
              <th>Covenant</th>
              <th>Metric</th>
              <th>Value</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {data.results.map((r, idx) => (
              <tr key={idx}>
                <td>{r.covenant_name}</td>
                <td>{r.metric}</td>
                <td>{r.value}</td>
                <td>
                  <RiskBadge value={r.status} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* EXPORT ACTIONS */}
      <div style={{ display: "flex", gap: 12 }}>
        <button className="primary" onClick={downloadPDF}>
           PDF
        </button>

        <button className="secondary" onClick={downloadExcel}>
           Excel
        </button>
      </div>
    </>
  );
}