import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, CartesianGrid } from 'recharts';
import { Activity, AlertTriangle, CheckCircle, Cpu, TrendingDown } from 'lucide-react';
import KpiCard from '../components/KpiCard';
import LoadingState from '../components/LoadingState';
import { getDashboardSummary, getAnomalyTrend } from '../lib/api';

const HEALTH_COLORS = {
  Healthy: '#00ff88',
  'Minor Degradation': '#fbbf24',
  Warning: '#ff6b35',
  Critical: '#ff3366',
};

export default function Overview() {
  const [summary, setSummary] = useState(null);
  const [trend, setTrend] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [summaryRes, trendRes] = await Promise.all([
          getDashboardSummary(),
          getAnomalyTrend(),
        ]);
        setSummary(summaryRes.data);
        setTrend(trendRes.data.trend || []);
      } catch (err) {
        console.error('Failed to load dashboard:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <LoadingState />;
  if (!summary) return <p className="text-gray-400">No data available. Run training pipeline first.</p>;

  const pieData = Object.entries(summary.health_distribution).map(([name, value]) => ({ name, value }));

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Executive Overview</h1>
          <p className="text-sm text-gray-400">Real-time compressor health monitoring</p>
        </div>
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <div className="w-2 h-2 rounded-full bg-neon-green animate-pulse" />
          Live Monitoring
        </div>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard title="Total Compressors" value={summary.total_compressors} icon={Cpu} color="blue" delay={0} />
        <KpiCard title="Active Anomalies" value={summary.active_anomalies} icon={AlertTriangle} color="red" delay={0.1} />
        <KpiCard title="Avg Health Score" value={summary.average_health_score} icon={Activity} color="green" delay={0.2} />
        <KpiCard title="Critical Equipment" value={summary.critical_count} icon={TrendingDown} color="orange" delay={0.3} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="glass-card p-6">
          <h3 className="text-sm font-semibold text-gray-300 mb-4">Health Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={pieData} cx="50%" cy="50%" outerRadius={90} dataKey="value" label={({ name, value }) => `${name}: ${value}`}>
                {pieData.map((entry) => (
                  <Cell key={entry.name} fill={HEALTH_COLORS[entry.name]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: '#1a2332', border: '1px solid #2d3d56', borderRadius: 8 }} />
            </PieChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }} className="glass-card p-6">
          <h3 className="text-sm font-semibold text-gray-300 mb-4">Vibration Trend (30 Days)</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={trend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2d3d56" />
              <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#9ca3af' }} />
              <YAxis tick={{ fontSize: 10, fill: '#9ca3af' }} />
              <Tooltip contentStyle={{ background: '#1a2332', border: '1px solid #2d3d56', borderRadius: 8 }} />
              <Line type="monotone" dataKey="avg_vibration" stroke="#00d4ff" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="avg_bearing_temp" stroke="#ff6b35" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }} className="glass-card p-6">
        <h3 className="text-sm font-semibold text-gray-300 mb-4">Compressor Health Map</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {(summary.compressor_health || []).map((comp) => (
            <div key={comp.compressor_id} className={`p-4 rounded-lg border ${
              comp.category === 'Critical' ? 'border-neon-red/40 bg-neon-red/5' :
              comp.category === 'Warning' ? 'border-neon-orange/40 bg-neon-orange/5' :
              comp.category === 'Minor Degradation' ? 'border-neon-yellow/40 bg-neon-yellow/5' :
              'border-neon-green/40 bg-neon-green/5'
            }`}>
              <p className="text-xs text-gray-400">{comp.compressor_id}</p>
              <p className="text-lg font-bold" style={{ color: HEALTH_COLORS[comp.category] }}>{comp.health_score}</p>
              <p className="text-xs" style={{ color: HEALTH_COLORS[comp.category] }}>{comp.category}</p>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
