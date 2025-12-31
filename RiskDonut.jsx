import { PieChart, Pie, Cell, ResponsiveContainer } from "recharts";

const COLORS = {
  GREEN: "#16A34A",
  AMBER: "#F59E0B",
  RED: "#DC2626"
};

export default function RiskDonut({ data }) {
  const hasData = data.some(d => d.value > 0);

  if (!hasData) {
    return (
      <div style={{ padding: 40, textAlign: "center", color: "#94a3b8" }}>
        No risk data available
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={260}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={90}
          dataKey="value"
        >
          {data.map(entry => (
            <Cell key={entry.name} fill={COLORS[entry.name]} />
          ))}
        </Pie>
      </PieChart>
    </ResponsiveContainer>
  );
}
