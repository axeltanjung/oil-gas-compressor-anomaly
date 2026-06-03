import { motion } from 'framer-motion';

export default function HealthGauge({ score, size = 120 }) {
  const getColor = (s) => {
    if (s >= 76) return '#00ff88';
    if (s >= 51) return '#fbbf24';
    if (s >= 26) return '#ff6b35';
    return '#ff3366';
  };

  const color = getColor(score);
  const radius = (size - 20) / 2;
  const circumference = Math.PI * radius;
  const progress = (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size / 2 + 20} viewBox={`0 0 ${size} ${size / 2 + 20}`}>
        <path
          d={`M 10 ${size / 2 + 10} A ${radius} ${radius} 0 0 1 ${size - 10} ${size / 2 + 10}`}
          fill="none"
          stroke="#1a2332"
          strokeWidth="8"
          strokeLinecap="round"
        />
        <motion.path
          d={`M 10 ${size / 2 + 10} A ${radius} ${radius} 0 0 1 ${size - 10} ${size / 2 + 10}`}
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: circumference - progress }}
          transition={{ duration: 1.2, ease: 'easeOut' }}
        />
        <text
          x={size / 2}
          y={size / 2}
          textAnchor="middle"
          fill={color}
          fontSize="20"
          fontWeight="bold"
        >
          {score}
        </text>
        <text
          x={size / 2}
          y={size / 2 + 16}
          textAnchor="middle"
          fill="#9ca3af"
          fontSize="10"
        >
          Health Score
        </text>
      </svg>
    </div>
  );
}
