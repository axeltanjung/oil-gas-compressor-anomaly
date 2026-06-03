import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Wrench, AlertTriangle, CheckCircle } from 'lucide-react';
import LoadingState from '../components/LoadingState';
import { getMaintenanceRecommendations } from '../lib/api';

export default function Maintenance() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const res = await getMaintenanceRecommendations();
        setData(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <LoadingState />;

  const recommendations = data?.recommendations || [];

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <h1 className="text-2xl font-bold">Maintenance Recommendations</h1>
        <p className="text-sm text-gray-400">AI-powered maintenance prioritization</p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass-card p-5 border border-neon-red/20">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle size={16} className="text-neon-red" />
            <p className="text-sm text-gray-300">High Priority</p>
          </div>
          <p className="text-3xl font-bold text-neon-red">{recommendations.filter(r => r.priority === 'HIGH').length}</p>
        </div>
        <div className="glass-card p-5 border border-neon-orange/20">
          <div className="flex items-center gap-2 mb-2">
            <Wrench size={16} className="text-neon-orange" />
            <p className="text-sm text-gray-300">Medium Priority</p>
          </div>
          <p className="text-3xl font-bold text-neon-orange">{recommendations.filter(r => r.priority === 'MEDIUM').length}</p>
        </div>
        <div className="glass-card p-5 border border-neon-green/20">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle size={16} className="text-neon-green" />
            <p className="text-sm text-gray-300">No Action Needed</p>
          </div>
          <p className="text-3xl font-bold text-neon-green">
            {8 - recommendations.length}
          </p>
        </div>
      </div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="space-y-4">
        {recommendations.map((item, i) => (
          <motion.div
            key={item.compressor_id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 * i }}
            className="glass-card p-5 border border-industrial-500/30 hover:border-neon-blue/30 transition-all"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className={`w-3 h-3 rounded-full ${item.priority === 'HIGH' ? 'bg-neon-red animate-pulse' : 'bg-neon-orange'}`} />
                <h3 className="font-semibold text-white">{item.compressor_id}</h3>
                <span className={`px-2 py-0.5 rounded text-xs ${
                  item.priority === 'HIGH' ? 'bg-neon-red/10 text-neon-red' : 'bg-neon-orange/10 text-neon-orange'
                }`}>
                  {item.priority}
                </span>
              </div>
              <p className="text-sm text-gray-400">Health: <span className="text-white font-mono">{item.health_score}</span></p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {(item.recommendations || []).map((rec, j) => (
                <div key={j} className="p-3 rounded-lg bg-industrial-800/50 border border-industrial-600/20">
                  <p className="text-sm text-white">{rec.action}</p>
                  <p className="text-xs text-gray-400 mt-1">{rec.component}</p>
                </div>
              ))}
            </div>
          </motion.div>
        ))}
      </motion.div>

      {recommendations.length === 0 && (
        <div className="glass-card p-12 text-center">
          <CheckCircle size={48} className="text-neon-green mx-auto mb-4" />
          <p className="text-lg text-white">All compressors operating normally</p>
          <p className="text-sm text-gray-400">No immediate maintenance actions required</p>
        </div>
      )}
    </div>
  );
}
