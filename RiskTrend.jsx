import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer
} from "recharts";
import { normalizeRisk } from "../utils/riskMap";

const riskScore = {
  GREEN: 1,
  AMBER: 2,
  RED: 3
};

export default function RiskTrend({ evaluations }) {
  if (!evaluations.length) {
    return (
      <div style={{ padding: 40, textAlign: "center", color: "#94a3b8" }}>
        No trend data available
      </div>
    );
  }

  // Sort oldest → newest
  const data = [...evaluations]
    .sort((a, b) => a.id - b.id)
    .map(e => ({
      period: e.period,
      risk: riskScore[normalizeRisk(e.overall_risk)]
    }));

  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={data}>
        <XAxis dataKey="period" />
        <YAxis ticks={[1, 2, 3]} domain={[1, 3]} />
        <Tooltip />
        <Line
          type="monotone"
          dataKey="risk"
          stroke="#2563EB"
          strokeWidth={3}
          dot={{ r: 4 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
