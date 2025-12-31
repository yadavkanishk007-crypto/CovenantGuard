import Sidebar from "./Sidebar";
import Header from "./Header";
import "../styles/layout.css";

export default function AppLayout({ page, setPage, title, children }) {
  return (
    <div className="app-shell">
      <Sidebar current={page} setCurrent={setPage} />

      <div className="app-main">
        <Header title={title} />
        <div className="app-content">
          {children}
        </div>
      </div>
    </div>
  );
}
