import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis } from 'recharts';
import LoadingState from '../components/LoadingState';
import { getExplanation } from '../lib/api';

const COMPRESSORS = ['COMP-001', 'COMP-002', 'COMP-003', 'COMP-004', 'COMP-005', 'COMP-006', 'COMP-007', 'COMP-008'];

export default function AIInsights() {
  const [selected, setSelected] = useState('COMP-001');
  const [explanation, setExplanation] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const res = await getExplanation(selected);
        setExplanation(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [selected]);

  if (loading) return <LoadingState />;

  const driverData = (explanation?.top_drivers || []).map((d) => ({
    name: d.feature.replace(/_/g, ' ').slice(0, 15),
    contribution: Math.abs(d.contribution * 100),
  }));

  const radarData = Object.entries(explanation?.component_contributions || {}).map(([key, val]) => ({
    subject: key.replace(/_/g, ' ').slice(0, 12),
    value: val * 100,
  }));

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <h1 className="text-2xl font-bold">AI Insights</h1>
        <p className="text-sm text-gray-400">SHAP-based anomaly explainability</p>
      </motion.div>

      <div className="flex gap-2 flex-wrap">
        {COMPRESSORS.map((comp) => (
          <button
            key={comp}
            onClick={() => setSelected(comp)}
            className={`px-3 py-1.5 rounded-lg text-xs transition-all ${
              selected === comp ? 'bg-neon-blue/20 text-neon-blue border border-neon-blue/30' : 'bg-industrial-700 text-gray-400 hover:text-white'
            }`}
          >
            {comp}
          </button>
        ))}
      </div>

      {explanation && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="glass-card p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-gray-300">Anomaly Score</h3>
              <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                explanation.severity === 'HIGH' ? 'bg-neon-red/20 text-neon-red' :
                explanation.severity === 'MEDIUM' ? 'bg-neon-orange/20 text-neon-orange' :
                'bg-neon-green/20 text-neon-green'
              }`}>
                {explanation.severity}
              </span>
            </div>
            <div className="text-center py-8">
              <p className="text-5xl font-bold text-neon-blue">{(explanation.anomaly_score * 100).toFixed(1)}%</p>
              <p className="text-sm text-gray-400 mt-2">Weighted Degradation Index</p>
            </div>
          </motion.div>

          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="glass-card p-6">
            <h3 className="text-sm font-semibold text-gray-300 mb-4">Top Anomaly Drivers</h3>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={driverData} layout="vertical">
                <XAxis type="number" tick={{ fontSize: 10, fill: '#9ca3af' }} />
                <YAxis type="category" dataKey="name" tick={{ fontSize: 10, fill: '#9ca3af' }} width={100} />
                <Tooltip contentStyle={{ background: '#1a2332', border: '1px solid #2d3d56', borderRadius: 8 }} />
                <Bar dataKey="contribution" fill="#00d4ff" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="glass-card p-6 lg:col-span-2">
            <h3 className="text-sm font-semibold text-gray-300 mb-4">Component Health Radar</h3>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="#2d3d56" />
                <PolarAngleAxis dataKey="subject" tick={{ fontSize: 10, fill: '#9ca3af' }} />
                <PolarRadiusAxis tick={{ fontSize: 9, fill: '#9ca3af' }} />
                <Radar dataKey="value" stroke="#00d4ff" fill="#00d4ff" fillOpacity={0.2} strokeWidth={2} />
              </RadarChart>
            </ResponsiveContainer>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="glass-card p-6 lg:col-span-2">
            <h3 className="text-sm font-semibold text-gray-300 mb-4">Maintenance Recommendations</h3>
            <div className="space-y-3">
              {(explanation.recommendations || []).map((rec, i) => (
                <div key={i} className="flex items-center gap-4 p-3 rounded-lg bg-industrial-800/50 border border-industrial-600/30">
                  <div className={`w-2 h-8 rounded-full ${
                    rec.severity === 'HIGH' ? 'bg-neon-red' : rec.severity === 'MEDIUM' ? 'bg-neon-orange' : 'bg-neon-green'
                  }`} />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-white">{rec.action}</p>
                    <p className="text-xs text-gray-400">{rec.component} • {rec.feature}</p>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs ${
                    rec.severity === 'HIGH' ? 'bg-neon-red/10 text-neon-red' : rec.severity === 'MEDIUM' ? 'bg-neon-orange/10 text-neon-orange' : 'bg-neon-green/10 text-neon-green'
                  }`}>
                    {rec.severity}
                  </span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}
