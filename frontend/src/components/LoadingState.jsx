import { motion } from 'framer-motion';

export default function LoadingState() {
  return (
    <div className="flex items-center justify-center h-64">
      <motion.div
        className="w-12 h-12 border-4 border-neon-blue/20 border-t-neon-blue rounded-full"
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
      />
    </div>
  );
}
