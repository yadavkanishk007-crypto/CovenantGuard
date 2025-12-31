import { useState } from "react";
import api from "../api/client";

export default function NewEvaluation({ back }) {
  const [f, setF] = useState({
    period: "FY2024",
    revenue: "",
    ebitda: "",
    debt: "",
    interest_expense: ""
  });

  const submit = async () => {
    try {
      await api.post("/evaluate", {
        covenants: [
          { covenant_name: "Leverage", metric: "leverage", threshold: 3 }
        ],
        financials: {
          ...f,
          revenue: +f.revenue,
          ebitda: +f.ebitda,
          debt: +f.debt,
          interest_expense: +f.interest_expense
        }
      });
      back();
    } catch (err) {
      console.error("Evaluation failed", err);
    }
  };

  const handleChange = (key, value) => {
    setF(prev => ({ ...prev, [key]: value }));
  };

  return (
    <div style={{ padding: "0 0 48px 0" }}>
      <h1 style={{ marginBottom: 24 }}>New Evaluation</h1>
      
      <div className="card" style={{ maxWidth: 520 }}>
        {/* REPORTING PERIOD */}
        <div style={{ marginBottom: 16 }}>
          <label className="muted" style={{ display: "block", marginBottom: 8 }}>
            Reporting Period
          </label>
          <input
            value={f.period}
            onChange={e => handleChange("period", e.target.value)}
            style={{ width: "100%" }}
            placeholder="e.g. FY2024-Q3"
          />
        </div>

        {/* REVENUE */}
        <div style={{ marginBottom: 16 }}>
          <label className="muted" style={{ display: "block", marginBottom: 8 }}>
            Revenue (₹ Mn)
          </label>
          <input
            type="number"
            value={f.revenue}
            onChange={e => handleChange("revenue", e.target.value)}
            style={{ width: "100%" }}
          />
        </div>

        {/* EBITDA */}
        <div style={{ marginBottom: 16 }}>
          <label className="muted" style={{ display: "block", marginBottom: 8 }}>
            EBITDA (₹ Mn)
          </label>
          <input
            type="number"
            value={f.ebitda}
            onChange={e => handleChange("ebitda", e.target.value)}
            style={{ width: "100%" }}
          />
        </div>

        {/* DEBT */}
        <div style={{ marginBottom: 16 }}>
          <label className="muted" style={{ display: "block", marginBottom: 8 }}>
            Total Debt (₹ Mn)
          </label>
          <input
            type="number"
            value={f.debt}
            onChange={e => handleChange("debt", e.target.value)}
            style={{ width: "100%" }}
          />
        </div>

        {/* INTEREST */}
        <div style={{ marginBottom: 32 }}>
          <label className="muted" style={{ display: "block", marginBottom: 8 }}>
            Interest Expense (₹ Mn)
          </label>
          <input
            type="number"
            value={f.interest_expense}
            onChange={e => handleChange("interest_expense", e.target.value)}
            style={{ width: "100%" }}
          />
        </div>

        {/* ACTIONS */}
        <div style={{ display: "flex", gap: 12 }}>
          <button className="primary" onClick={submit}>
            Run Evaluation
          </button>
          <button className="secondary" onClick={back}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}