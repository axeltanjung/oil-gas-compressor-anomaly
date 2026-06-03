import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ScatterChart, Scatter } from 'recharts';
import LoadingState from '../components/LoadingState';
import { getCompressorDetail } from '../lib/api';

const COMPRESSORS = ['COMP-001', 'COMP-002', 'COMP-003', 'COMP-004', 'COMP-005', 'COMP-006', 'COMP-007', 'COMP-008'];
const SENSORS = ['vibration_x', 'vibration_y', 'bearing_temperature', 'oil_temperature', 'suction_pressure', 'discharge_pressure', 'rpm', 'flow_rate', 'power_consumption', 'efficiency_score'];

export default function DataExplorer() {
  const [selected, setSelected] = useState('COMP-001');
  const [sensor, setSensor] = useState('vibration_x');
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const res = await getCompressorDetail(selected);
        setData(res.data.sensor_history || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [selected]);

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <h1 className="text-2xl font-bold">Data Explorer</h1>
        <p className="text-sm text-gray-400">Raw sensor data visualization and filtering</p>
      </motion.div>

      <div className="flex flex-wrap gap-4">
        <div className="glass-card p-4 flex-1 min-w-[200px]">
          <p className="text-xs text-gray-400 mb-2">Compressor</p>
          <select
            value={selected}
            onChange={(e) => setSelected(e.target.value)}
            className="w-full bg-industrial-800 border border-industrial-500/30 rounded-lg px-3 py-2 text-sm text-white"
          >
            {COMPRESSORS.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>

        <div className="glass-card p-4 flex-1 min-w-[200px]">
          <p className="text-xs text-gray-400 mb-2">Sensor</p>
          <select
            value={sensor}
            onChange={(e) => setSensor(e.target.value)}
            className="w-full bg-industrial-800 border border-industrial-500/30 rounded-lg px-3 py-2 text-sm text-white"
          >
            {SENSORS.map((s) => <option key={s} value={s}>{s.replace(/_/g, ' ')}</option>)}
          </select>
        </div>
      </div>

      {loading ? (
        <LoadingState />
      ) : (
        <div className="space-y-6">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-6">
            <h3 className="text-sm font-semibold text-gray-300 mb-4">
              {sensor.replace(/_/g, ' ')} — {selected}
            </h3>
            <ResponsiveContainer width="100%" height={350}>
              <LineChart data={data.slice(-200)}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2d3d56" />
                <XAxis dataKey="timestamp" tick={{ fontSize: 9, fill: '#9ca3af' }} />
                <YAxis tick={{ fontSize: 10, fill: '#9ca3af' }} />
                <Tooltip contentStyle={{ background: '#1a2332', border: '1px solid #2d3d56', borderRadius: 8 }} />
                <Line type="monotone" dataKey={sensor} stroke="#00d4ff" strokeWidth={1.5} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="glass-card p-6">
            <h3 className="text-sm font-semibold text-gray-300 mb-4">Data Statistics</h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {data.length > 0 && (() => {
                const values = data.map(d => d[sensor]).filter(v => v != null);
                const stats = {
                  Count: values.length,
                  Mean: (values.reduce((a, b) => a + b, 0) / values.length).toFixed(2),
                  Min: Math.min(...values).toFixed(2),
                  Max: Math.max(...values).toFixed(2),
                  Std: Math.sqrt(values.map(v => Math.pow(v - values.reduce((a, b) => a + b, 0) / values.length, 2)).reduce((a, b) => a + b, 0) / values.length).toFixed(2),
                };
                return Object.entries(stats).map(([key, val]) => (
                  <div key={key} className="text-center p-3 rounded-lg bg-industrial-800/50">
                    <p className="text-xs text-gray-400">{key}</p>
                    <p className="text-lg font-bold text-neon-blue">{val}</p>
                  </div>
                ));
              })()}
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}
