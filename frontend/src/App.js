import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import Dashboard from './components/Dashboard';
import UploadImage from './components/UploadImage';
import MapView from './components/MapView';
import Insights from './components/Insights';
import Navbar from './components/Navbar';
import LoadingScreen from './components/LoadingScreen';
import Footer from './components/Footer';
import { useState, useEffect } from 'react';
import axios from 'axios';

// Define API base URL
const API_URL = 'http://localhost:5000';

function App() {
  const [sewageData, setSewageData] = useState({
    demands: [],
    complaints: [],
    illegalConnections: []
  });
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch data from backend when component mounts
  useEffect(() => {
    const fetchData = async () => {
      try {
        console.log('Starting API calls to:', API_URL);
        setLoading(true);
        
        // Fetch sewage demand data
        console.log('Fetching sewage demand...');
        const demandRes = await axios.get(`${API_URL}/sewage-demand`);
        console.log('Sewage demand response:', demandRes.data);
        
        // Fetch complaint data
        console.log('Fetching complaints...');
        const complaintsRes = await axios.get(`${API_URL}/complaints`);
        console.log('Complaints response:', complaintsRes.data);
        
        // Fetch illegal connections
        console.log('Fetching illegal connections...');
        const illegalRes = await axios.get(`${API_URL}/illegal-connections`);
        console.log('Illegal connections response:', illegalRes.data);
        
        setSewageData({
          demands: demandRes.data.data || [],
          complaints: complaintsRes.data.data || [],
          illegalConnections: illegalRes.data.data || []
        });
        
        console.log('All data loaded successfully');
        setLoading(false);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to load data from server');
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative overflow-hidden">
        {/* Animated Background */}
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-0 -left-4 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl animate-blob"></div>
          <div className="absolute top-0 -right-4 w-72 h-72 bg-yellow-300 rounded-full mix-blend-multiply filter blur-xl animate-blob animation-delay-2000"></div>
          <div className="absolute -bottom-8 left-20 w-72 h-72 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl animate-blob animation-delay-4000"></div>
        </div>
        
        {loading && <LoadingScreen />}
        
        <div className="relative z-10">
          <Navbar />
          
          <main className="container mx-auto px-4 py-8">
            {error && (
              <div className="bg-red-500/10 backdrop-blur-sm border border-red-500/20 text-red-200 p-4 mb-6 rounded-xl animate-pulse" role="alert">
                <p className="font-medium">⚠️ {error}</p>
              </div>
            )}
            
            <Routes>
              <Route 
                path="/" 
                element={<Dashboard data={sewageData} loading={loading} />} 
              />
              <Route 
                path="/upload" 
                element={<UploadImage apiUrl={API_URL} />} 
              />
              <Route 
                path="/map" 
                element={
                  <MapView 
                    demands={sewageData.demands}
                    complaints={sewageData.complaints}
                    illegalConnections={sewageData.illegalConnections}
                    loading={loading}
                  />
                } 
              />
              <Route 
                path="/insights" 
                element={<Insights data={sewageData} loading={loading} />} 
              />
            </Routes>
          </main>
          
          <Footer />
        </div>
      </div>
    </Router>
  );
}

export default App;
