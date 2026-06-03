import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, AreaChart, Area } from 'recharts';
import HealthGauge from '../components/HealthGauge';
import LoadingState from '../components/LoadingState';
import { getCompressorDetail, getCompressorHealthHistory } from '../lib/api';

export default function CompressorDetail() {
  const { id } = useParams();
  const [detail, setDetail] = useState(null);
  const [healthHistory, setHealthHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('vibration');

  useEffect(() => {
    async function load() {
      try {
        const [detailRes, historyRes] = await Promise.all([
          getCompressorDetail(id),
          getCompressorHealthHistory(id),
        ]);
        setDetail(detailRes.data);
        setHealthHistory(historyRes.data.health_history || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  if (loading) return <LoadingState />;
  if (!detail) return <p className="text-gray-400">Compressor not found.</p>;

  const tabs = ['vibration', 'temperature', 'pressure', 'efficiency'];
  const sensorHistory = detail.sensor_history || [];

  const chartConfig = {
    vibration: { keys: ['vibration_x', 'vibration_y'], colors: ['#00d4ff', '#a855f7'] },
    temperature: { keys: ['bearing_temperature', 'oil_temperature'], colors: ['#ff6b35', '#fbbf24'] },
    pressure: { keys: ['suction_pressure', 'discharge_pressure'], colors: ['#00ff88', '#00d4ff'] },
    efficiency: { keys: ['efficiency_score', 'power_consumption'], colors: ['#00ff88', '#ff3366'] },
  };

  const currentConfig = chartConfig[activeTab];

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <h1 className="text-2xl font-bold">{id}</h1>
        <p className="text-sm text-gray-400">Compressor Detail Analysis</p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="glass-card p-6 flex flex-col items-center">
          <HealthGauge score={detail.latest_health_score} size={160} />
          <p className={`text-sm font-semibold mt-2 ${
            detail.health_category === 'Healthy' ? 'text-neon-green' :
            detail.health_category === 'Warning' ? 'text-neon-orange' :
            detail.health_category === 'Critical' ? 'text-neon-red' : 'text-neon-yellow'
          }`}>
            {detail.health_category}
          </p>
          <p className="text-xs text-gray-400 mt-1">{detail.total_records} readings</p>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="glass-card p-6 lg:col-span-2">
          <h3 className="text-sm font-semibold text-gray-300 mb-4">Health Score Evolution</h3>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={healthHistory.slice(-50)}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2d3d56" />
              <XAxis dataKey="timestamp" tick={{ fontSize: 9, fill: '#9ca3af' }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: '#9ca3af' }} />
              <Tooltip contentStyle={{ background: '#1a2332', border: '1px solid #2d3d56', borderRadius: 8 }} />
              <Area type="monotone" dataKey="health_score" stroke="#00ff88" fill="#00ff88" fillOpacity={0.1} strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="glass-card p-6">
        <div className="flex items-center gap-2 mb-4">
          {tabs.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded-lg text-xs font-medium transition-all ${
                activeTab === tab ? 'bg-neon-blue/20 text-neon-blue border border-neon-blue/30' : 'text-gray-400 hover:text-white'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={sensorHistory.slice(-100)}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2d3d56" />
            <XAxis dataKey="timestamp" tick={{ fontSize: 9, fill: '#9ca3af' }} />
            <YAxis tick={{ fontSize: 10, fill: '#9ca3af' }} />
            <Tooltip contentStyle={{ background: '#1a2332', border: '1px solid #2d3d56', borderRadius: 8 }} />
            {currentConfig.keys.map((key, i) => (
              <Line key={key} type="monotone" dataKey={key} stroke={currentConfig.colors[i]} strokeWidth={2} dot={false} />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </motion.div>
    </div>
  );
}
