import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Overview from './pages/Overview';
import CompressorDetail from './pages/CompressorDetail';
import AIInsights from './pages/AIInsights';
import Maintenance from './pages/Maintenance';
import DataExplorer from './pages/DataExplorer';

function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto p-6">
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/compressor/:id" element={<CompressorDetail />} />
            <Route path="/insights" element={<AIInsights />} />
            <Route path="/maintenance" element={<Maintenance />} />
            <Route path="/data" element={<DataExplorer />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
