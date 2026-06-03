import { motion } from 'framer-motion';
import clsx from 'clsx';

export default function KpiCard({ title, value, subtitle, icon: Icon, color = 'blue', delay = 0 }) {
  const colorMap = {
    blue: 'text-neon-blue border-neon-blue/20',
    green: 'text-neon-green border-neon-green/20',
    orange: 'text-neon-orange border-neon-orange/20',
    red: 'text-neon-red border-neon-red/20',
    purple: 'text-neon-purple border-neon-purple/20',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
      className={clsx('kpi-card border', colorMap[color])}
    >
      <div className="flex items-center justify-between mb-3">
        <p className="text-sm text-gray-400">{title}</p>
        {Icon && <Icon size={20} className={colorMap[color]?.split(' ')[0]} />}
      </div>
      <p className={clsx('text-3xl font-bold', colorMap[color]?.split(' ')[0])}>{value}</p>
      {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
    </motion.div>
  );
}
