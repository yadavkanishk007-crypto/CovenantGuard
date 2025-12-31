export default function RiskBadge({ value }) {
  const map = {
    GREEN: "#16a34a",
    AMBER: "#f59e0b",
    RED: "#dc2626"
  };

  return (
    <span style={{
      padding: "6px 12px",
      borderRadius: 999,
      fontSize: 12,
      background: map[value] + "22",
      color: map[value]
    }}>
      {value}
    </span>
  );
}