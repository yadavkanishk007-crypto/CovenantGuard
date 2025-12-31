import { useEffect, useState } from "react";
import api from "../api/client";

import KPI from "../components/KPI";
import RiskDonut from "../components/RiskDonut";
import RiskTrend from "../components/RiskTrend";
import RiskBadge from "../components/RiskBadge";
import AdminKPIs from "../components/AdminKPIs";

import { getRole, isAuthenticated } from "../auth/auth";
import { normalizeRisk } from "../utils/riskMap";

export default function Dashboard({ openDetail }) {
  const [evaluations, setEvaluations] = useState([]);
  const role = getRole();

  /* =========================
     FETCH DATA
  ========================== */
  useEffect(() => {
    if (!isAuthenticated()) return;

    api
      .get("/evaluations")
      .then(res => setEvaluations(res.data || []))
      .catch(() => setEvaluations([]));
  }, []);

  /* =========================
     DERIVED METRICS
  ========================== */
  const green = evaluations.filter(
    e => normalizeRisk(e.overall_risk) === "GREEN"
  ).length;

  const amber = evaluations.filter(
    e => normalizeRisk(e.overall_risk) === "AMBER"
  ).length;

  const red = evaluations.filter(
    e => normalizeRisk(e.overall_risk) === "RED"
  ).length;

  const total = evaluations.length;
  const breachRate = total === 0 ? 0 : Math.round((red / total) * 100);

  const recentEvaluations = [...evaluations]
    .sort((a, b) => b.id - a.id)
    .slice(0, 5);

  /* =========================
     RENDER
  ========================== */
  return (
    <>
      {/* HEADER */}
      <div style={{ marginBottom: 40 }}>
        <h1>Risk Dashboard</h1>
        <p style={{ color: "#64748b" }}>
          Covenant portfolio monitoring & compliance overview
        </p>
      </div>

      {/* =========================
         ADMIN KPIs
      ========================== */}
      {role === "admin" && (
        <section style={{ marginBottom: 40 }}>
          <AdminKPIs evaluations={evaluations} />
        </section>
      )}

      {/* =========================
         CORE KPIs
      ========================== */}
      <section style={{ marginBottom: 48 }}>
        <div className="grid grid-4">
          <KPI title="Total Evaluations" value={total} />
          <KPI title="GREEN" value={green} tone="green" />
          <KPI title="AMBER" value={amber} tone="amber" />
          <KPI title="RED" value={red} tone="red" />
        </div>
      </section>

      {/* =========================
         CHARTS
      ========================== */}
      <section
        style={{
          marginBottom: 48,
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 24
        }}
      >
        {/* Donut */}
        <div className="card">
          <h3>Risk Distribution</h3>
          <RiskDonut
            data={[
              { name: "GREEN", value: green },
              { name: "AMBER", value: amber },
              { name: "RED", value: red }
            ]}
          />
        </div>

        {/* Trend */}
        <div className="card">
          <h3>Risk Trend</h3>
          <p className="muted">Portfolio risk evolution over time</p>
          <RiskTrend evaluations={evaluations} />
        </div>
      </section>

      {/* =========================
         RECENT EVALUATIONS
      ========================== */}
      <section>
        <div className="card">
          <h3 style={{ marginBottom: 12 }}>Recent Evaluations</h3>

          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Period</th>
                <th>Risk</th>
                <th>Action</th>
              </tr>
            </thead>

            <tbody>
              {recentEvaluations.map(e => (
                <tr key={e.id}>
                  <td>{e.id}</td>
                  <td>{e.period}</td>
                  <td>
                    <RiskBadge value={e.overall_risk} />
                  </td>
                  <td>
                    <button
                      className="secondary"
                      onClick={() => openDetail && openDetail(e.id)}
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))}

              {recentEvaluations.length === 0 && (
                <tr>
                  <td
                    colSpan="4"
                    style={{
                      padding: 32,
                      textAlign: "center",
                      color: "#64748b"
                    }}
                  >
                    No evaluations yet. Run your first covenant evaluation to
                    populate the dashboard.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}
