import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Cpu, BrainCircuit, Wrench, Database } from 'lucide-react';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Overview' },
  { to: '/compressor/COMP-001', icon: Cpu, label: 'Compressor Detail' },
  { to: '/insights', icon: BrainCircuit, label: 'AI Insights' },
  { to: '/maintenance', icon: Wrench, label: 'Maintenance' },
  { to: '/data', icon: Database, label: 'Data Explorer' },
];

export default function Sidebar() {
  return (
    <aside className="w-64 h-screen bg-industrial-800 border-r border-industrial-600/50 flex flex-col">
      <div className="p-6 border-b border-industrial-600/50">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-neon-blue to-neon-purple flex items-center justify-center">
            <Cpu size={20} className="text-white" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-white">Compressor AI</h1>
            <p className="text-xs text-gray-400">Anomaly Platform</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            <Icon size={18} />
            <span className="text-sm">{label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t border-industrial-600/50">
        <div className="glass-card p-3">
          <p className="text-xs text-gray-400">System Status</p>
          <div className="flex items-center gap-2 mt-1">
            <div className="w-2 h-2 rounded-full bg-neon-green animate-pulse" />
            <span className="text-xs text-neon-green">All Models Active</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
