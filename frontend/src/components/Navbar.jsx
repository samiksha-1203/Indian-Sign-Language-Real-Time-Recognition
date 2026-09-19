import { NavLink } from "react-router-dom";
import { Hand } from "lucide-react";

const links = [
  { to: "/", label: "Home", end: true },
  { to: "/recognize", label: "Live Recognition" },
  { to: "/analytics", label: "Analytics" },
  { to: "/dataset", label: "Dataset" },
  { to: "/model", label: "Model" },
];

export default function Navbar() {
  return (
    <header className="sticky top-0 z-40 border-b border-navy/5 bg-canvas/80 backdrop-blur-md">
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <NavLink to="/" className="flex items-center gap-2.5">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-sky to-lav text-white shadow-soft">
            <Hand size={18} strokeWidth={2.2} />
          </span>
          <span className="font-display text-lg font-semibold text-navy">
            SignSpeak AI
          </span>
        </NavLink>

        <div className="hidden items-center gap-1 rounded-full border border-navy/5 bg-surface p-1 shadow-soft md:flex">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              className={({ isActive }) =>
                `focus-ring rounded-full px-4 py-2 text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-sky text-white"
                    : "text-navy-soft hover:bg-sky-soft hover:text-navy"
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
        </div>

        <NavLink
          to="/recognize"
          className="focus-ring rounded-full bg-navy px-4 py-2 text-sm font-medium text-white shadow-soft transition-transform hover:scale-[1.02] md:hidden"
        >
          Start
        </NavLink>
      </nav>

      {/* mobile links row */}
      <div className="flex gap-1 overflow-x-auto px-6 pb-3 md:hidden">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.end}
            className={({ isActive }) =>
              `focus-ring shrink-0 rounded-full px-3 py-1.5 text-xs font-medium ${
                isActive ? "bg-sky text-white" : "bg-surface text-navy-soft"
              }`
            }
          >
            {link.label}
          </NavLink>
        ))}
      </div>
    </header>
  );
}
