import React, { useRef, useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix Leaflet marker icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
});

// Enhanced custom icons with modern styling
const createCustomIcon = (color, glow = false) => {
  return new L.Icon({
    iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-${color}.png`,
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [28, 45],
    iconAnchor: [14, 45],
    popupAnchor: [1, -38],
    shadowSize: [45, 45],
    className: glow ? 'animate-pulse' : ''
  });
};

const complaintIcon = createCustomIcon('red', true);
const illegalIcon = createCustomIcon('violet', true);
const highPriorityIcon = createCustomIcon('orange', true);

const MapView = ({ demands, complaints, illegalConnections, loading }) => {
  const mapRef = useRef(null);
  const [mapLayers, setMapLayers] = useState({
    complaints: true,
    illegalConnections: true,
    demandZones: true,
    heatmap: false
  });
  
  const [selectedMapStyle, setSelectedMapStyle] = useState('standard');
  const [filterSeverity, setFilterSeverity] = useState('all');
  const [showStats, setShowStats] = useState(true);
  const [animatedStats, setAnimatedStats] = useState({
    totalComplaints: 0,
    highSeverity: 0,
    illegalConnections: 0,
    overCapacityZones: 0
  });

  // Map style options
  const mapStyles = {
    standard: {
      url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      name: 'Standard'
    },
    dark: {
      url: "https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png",
      attribution: '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>, &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors',
      name: 'Dark Mode'
    },
    satellite: {
      url: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
      attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP',
      name: 'Satellite'
    }
  };

  // Calculate statistics
  const stats = {
    totalComplaints: complaints.length,
    highSeverity: complaints.filter(c => c.severity === 'high').length,
    illegalConnections: illegalConnections.length,
    overCapacityZones: demands.filter(zone => zone.demand_m3 > zone.capacity_m3).length
  };

  // Animate statistics on mount
  useEffect(() => {
    if (!loading) {
      const animateValue = (start, end, duration, callback) => {
        const startTime = Date.now();
        const changeValue = end - start;
        
        const updateValue = () => {
          const now = Date.now();
          const progress = Math.min((now - startTime) / duration, 1);
          const currentValue = start + changeValue * progress;
          callback(Math.floor(currentValue));
          
          if (progress < 1) {
            requestAnimationFrame(updateValue);
          }
        };
        updateValue();
      };

      animateValue(0, stats.totalComplaints, 1500, (val) => 
        setAnimatedStats(prev => ({ ...prev, totalComplaints: val }))
      );
      animateValue(0, stats.highSeverity, 1800, (val) => 
        setAnimatedStats(prev => ({ ...prev, highSeverity: val }))
      );
      animateValue(0, stats.illegalConnections, 2000, (val) => 
        setAnimatedStats(prev => ({ ...prev, illegalConnections: val }))
      );
      animateValue(0, stats.overCapacityZones, 2200, (val) => 
        setAnimatedStats(prev => ({ ...prev, overCapacityZones: val }))
      );
    }
  }, [loading, stats.totalComplaints, stats.highSeverity, stats.illegalConnections, stats.overCapacityZones]);
    // Calculate map center based on all coordinates
  const getMapBounds = () => {
    const allPoints = [
      ...complaints.map(c => [c.lat, c.lng]),
      ...illegalConnections.map(c => [c.lat, c.lng])
    ];
    
    if (allPoints.length === 0) {
      // Default to New York City coordinates if no points
      return {
        center: [40.7128, -74.0060],
        zoom: 12
      };
    }

    // Calculate center
    const center = allPoints.reduce(
      (acc, point) => {
        return [acc[0] + point[0] / allPoints.length, acc[1] + point[1] / allPoints.length];
      }, 
      [0, 0]
    );
    
    return {
      center,
      zoom: 13
    };
  };
  
  const { center, zoom } = getMapBounds();
  
  // Toggle map layers
  const toggleLayer = (layer) => {
    setMapLayers(prev => ({
      ...prev,
      [layer]: !prev[layer]
    }));
  };
  
  // Enhanced color schemes for zones
  const getZoneColor = (demand, capacity) => {
    const ratio = demand / capacity;
    if (ratio >= 1.2) return '#dc2626'; // red-600 (critical over capacity)
    if (ratio >= 1) return '#ef4444'; // red-500 (over capacity)
    if (ratio >= 0.8) return '#f97316'; // orange-500 (near capacity)    if (ratio >= 0.6) return '#eab308'; // yellow-500 (moderate usage)
    return '#22c55e'; // green-500 (low usage)
  };

  // Filter complaints by severity
  const filteredComplaints = filterSeverity === 'all' 
    ? complaints 
    : complaints.filter(c => c.severity === filterSeverity);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-96 bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl">
        <div className="text-center">
          <div className="relative">
            <div className="w-16 h-16 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin mb-4"></div>
            <div className="absolute inset-0 w-16 h-16 border-4 border-cyan-200 border-b-cyan-600 rounded-full animate-spin animate-reverse"></div>
          </div>
          <div className="text-white/80 font-medium">Loading interactive map...</div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header Section */}
      <div className="text-center space-y-4 animate-slide-in">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-white via-purple-200 to-cyan-200 bg-clip-text text-transparent">
          Interactive Infrastructure Map
        </h1>
        <p className="text-gray-300 text-lg max-w-3xl mx-auto">
          Comprehensive real-time mapping of sewage infrastructure, demand zones, complaints, and system performance analytics
        </p>
        <div className="w-24 h-1 bg-gradient-to-r from-purple-500 to-cyan-500 mx-auto rounded-full"></div>
      </div>

      {/* Statistics Cards */}
      {showStats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 animate-scale-up">
          {[
            {
              title: 'Total Complaints',
              value: animatedStats.totalComplaints,
              icon: '🚨',
              gradient: 'from-red-500 to-red-700',
              bgGradient: 'from-red-500/20 to-red-700/10'
            },
            {
              title: 'High Priority',
              value: animatedStats.highSeverity,
              icon: '⚠️',
              gradient: 'from-orange-500 to-orange-700',
              bgGradient: 'from-orange-500/20 to-orange-700/10'
            },
            {
              title: 'Illegal Connections',
              value: animatedStats.illegalConnections,
              icon: '🔍',
              gradient: 'from-purple-500 to-purple-700',
              bgGradient: 'from-purple-500/20 to-purple-700/10'
            },
            {
              title: 'Over Capacity Zones',
              value: animatedStats.overCapacityZones,
              icon: '📊',
              gradient: 'from-cyan-500 to-cyan-700',
              bgGradient: 'from-cyan-500/20 to-cyan-700/10'
            }
          ].map((stat, index) => (
            <div
              key={stat.title}
              className={`relative overflow-hidden bg-gradient-to-br ${stat.bgGradient} backdrop-blur-lg border border-white/20 rounded-xl p-4 hover:border-white/40 transition-all duration-300 hover:scale-105`}
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-2xl font-bold text-white">{stat.value}</div>
                  <div className="text-sm text-gray-300">{stat.title}</div>
                </div>
                <div className={`w-12 h-12 rounded-lg bg-gradient-to-r ${stat.gradient} flex items-center justify-center text-2xl`}>
                  {stat.icon}
                </div>
              </div>
              <div className="absolute top-0 right-0 w-16 h-16 bg-white/10 rounded-full -translate-y-8 translate-x-8"></div>
            </div>
          ))}
        </div>
      )}

      {/* Enhanced Control Panel */}
      <div className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl p-6 hover:border-white/40 transition-all duration-300">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Layer Controls */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
              <span className="mr-2">🗂️</span>
              Map Layers
            </h3>
            <div className="space-y-3">
              {[
                { key: 'complaints', label: 'Complaints', icon: '🚨', color: 'red' },
                { key: 'illegalConnections', label: 'Illegal Connections', icon: '🔍', color: 'purple' },
                { key: 'demandZones', label: 'Demand Zones', icon: '🌐', color: 'blue' },
                { key: 'heatmap', label: 'Heat Map', icon: '🔥', color: 'orange' }
              ].map((layer) => (
                <button
                  key={layer.key}
                  className={`w-full flex items-center justify-between px-4 py-3 rounded-xl transition-all duration-300 ${
                    mapLayers[layer.key]
                      ? `bg-${layer.color}-500/20 border border-${layer.color}-500/30 text-white`
                      : 'bg-white/5 border border-white/10 text-gray-300 hover:bg-white/10'
                  }`}
                  onClick={() => toggleLayer(layer.key)}
                >
                  <div className="flex items-center">
                    <span className="mr-3 text-lg">{layer.icon}</span>
                    <span className="font-medium">{layer.label}</span>
                  </div>
                  <div className={`w-5 h-5 rounded border-2 transition-all duration-200 ${
                    mapLayers[layer.key] 
                      ? `bg-${layer.color}-500 border-${layer.color}-500` 
                      : 'border-gray-400'
                  }`}>
                    {mapLayers[layer.key] && (
                      <svg className="w-3 h-3 text-white m-0.5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    )}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Map Style Selector */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
              <span className="mr-2">🎨</span>
              Map Style
            </h3>
            <div className="space-y-3">
              {Object.entries(mapStyles).map(([key, style]) => (
                <button
                  key={key}
                  className={`w-full px-4 py-3 rounded-xl transition-all duration-300 text-left ${
                    selectedMapStyle === key
                      ? 'bg-gradient-to-r from-purple-500/20 to-cyan-500/20 border border-purple-500/30 text-white'
                      : 'bg-white/5 border border-white/10 text-gray-300 hover:bg-white/10'
                  }`}
                  onClick={() => setSelectedMapStyle(key)}
                >
                  <div className="font-medium">{style.name}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Filters */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
              <span className="mr-2">🎯</span>
              Filters & Options
            </h3>
            <div className="space-y-3">
              <div>
                <label className="block text-sm text-gray-300 mb-2">Complaint Severity</label>
                <select
                  value={filterSeverity}
                  onChange={(e) => setFilterSeverity(e.target.value)}
                  className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-purple-500 transition-colors"
                >
                  <option value="all" className="bg-gray-800">All Severities</option>
                  <option value="high" className="bg-gray-800">High Priority</option>
                  <option value="medium" className="bg-gray-800">Medium Priority</option>
                  <option value="low" className="bg-gray-800">Low Priority</option>
                </select>
              </div>
              
              <button
                className={`w-full px-4 py-3 rounded-xl transition-all duration-300 ${
                  showStats
                    ? 'bg-green-500/20 border border-green-500/30 text-green-300'
                    : 'bg-white/5 border border-white/10 text-gray-300 hover:bg-white/10'
                }`}
                onClick={() => setShowStats(!showStats)}
              >
                <div className="flex items-center justify-between">
                  <span>Show Statistics</span>
                  <span>{showStats ? '👁️' : '👁️‍🗨️'}</span>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>      {/* Enhanced Interactive Map */}
      <div className="relative bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl overflow-hidden hover:border-white/40 transition-all duration-300 shadow-2xl shadow-purple-500/10">
        <div className="h-[700px] relative">
          {/* Map Controls Overlay */}
          <div className="absolute top-4 right-4 z-[1000] space-y-2">
            <button className="w-10 h-10 bg-white/20 backdrop-blur-md border border-white/30 rounded-lg flex items-center justify-center text-white hover:bg-white/30 transition-all duration-200">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
            </button>
            <button className="w-10 h-10 bg-white/20 backdrop-blur-md border border-white/30 rounded-lg flex items-center justify-center text-white hover:bg-white/30 transition-all duration-200">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
              </svg>
            </button>
            <button className="w-10 h-10 bg-white/20 backdrop-blur-md border border-white/30 rounded-lg flex items-center justify-center text-white hover:bg-white/30 transition-all duration-200">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              </svg>
            </button>
          </div>

          {/* Live Status Indicator */}
          <div className="absolute top-4 left-4 z-[1000]">
            <div className="flex items-center space-x-2 px-4 py-2 bg-black/50 backdrop-blur-md border border-green-500/30 rounded-full">
              <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-green-300 text-sm font-medium">Live Data</span>
            </div>
          </div>

          <MapContainer 
            center={center} 
            zoom={zoom} 
            style={{ height: '100%', width: '100%' }}
            ref={mapRef}
            className="rounded-2xl"
          >
            <TileLayer
              attribution={mapStyles[selectedMapStyle].attribution}
              url={mapStyles[selectedMapStyle].url}
            />

            {/* Enhanced Demand Zones with better styling */}
            {mapLayers.demandZones && demands.map((zone) => (
              <Circle
                key={zone.zone_id}
                center={[zone.lat || 40.7128 + ((zone.zone_id * 0.01) % 0.05), zone.lng || -74.0060 + ((zone.zone_id * 0.01) % 0.05)]}
                radius={600}
                pathOptions={{
                  color: getZoneColor(zone.demand_m3, zone.capacity_m3),
                  fillColor: getZoneColor(zone.demand_m3, zone.capacity_m3),
                  fillOpacity: 0.3,
                  weight: 3,
                  opacity: 0.8
                }}
              >
                <Popup>
                  <div className="p-2 min-w-[250px]">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-bold text-lg text-gray-800">{zone.district} District</h3>
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
                        Zone {zone.zone_id}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-3 mb-3">
                      <div className="bg-gray-50 p-2 rounded">
                        <div className="text-xs text-gray-500 uppercase">Population</div>
                        <div className="font-semibold text-gray-800">{zone.population?.toLocaleString()}</div>
                      </div>
                      <div className="bg-gray-50 p-2 rounded">
                        <div className="text-xs text-gray-500 uppercase">Utilization</div>
                        <div className="font-semibold text-gray-800">
                          {zone.capacity_m3 > 0 ? ((zone.demand_m3 / zone.capacity_m3) * 100).toFixed(1) : 0}%
                        </div>
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Demand:</span>
                        <span className="font-medium text-gray-800">{zone.demand_m3?.toLocaleString()} m³</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Capacity:</span>
                        <span className="font-medium text-gray-800">{zone.capacity_m3?.toLocaleString()} m³</span>
                      </div>
                    </div>
                    
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        zone.demand_m3 > zone.capacity_m3 
                          ? 'bg-red-100 text-red-800' 
                          : 'bg-green-100 text-green-800'
                      }`}>
                        {zone.demand_m3 > zone.capacity_m3 ? '⚠️ Over Capacity' : '✅ Within Capacity'}
                      </span>
                    </div>
                  </div>
                </Popup>
              </Circle>
            ))}

            {/* Enhanced Complaint Markers */}
            {mapLayers.complaints && filteredComplaints.map((complaint) => (
              <Marker
                key={complaint.id}
                position={[complaint.lat, complaint.lng]}
                icon={complaint.severity === 'high' ? highPriorityIcon : complaintIcon}
              >
                <Popup>
                  <div className="p-2 min-w-[200px]">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-bold text-gray-800 capitalize">{complaint.type}</h3>
                      <span 
                        className={`px-2 py-1 rounded-full text-xs font-medium ${
                          complaint.severity === 'high' ? 'bg-red-100 text-red-800' :
                          complaint.severity === 'medium' ? 'bg-orange-100 text-orange-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}
                      >
                        {complaint.severity.toUpperCase()}
                      </span>
                    </div>
                    
                    <p className="text-sm text-gray-600 mb-3">{complaint.description}</p>
                    
                    <div className="text-xs text-gray-500">
                      📍 {complaint.lat.toFixed(6)}, {complaint.lng.toFixed(6)}
                    </div>
                    
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <button className="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 px-3 rounded text-sm font-medium transition-colors">
                        View Details
                      </button>
                    </div>
                  </div>
                </Popup>
              </Marker>
            ))}

            {/* Enhanced Illegal Connection Markers */}
            {mapLayers.illegalConnections && illegalConnections.map((connection) => (
              <Marker
                key={connection.id}
                position={[connection.lat, connection.lng]}
                icon={illegalIcon}
              >
                <Popup>
                  <div className="p-2 min-w-[200px]">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-bold text-gray-800">Suspected Illegal Connection</h3>
                      <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-medium">
                        {(connection.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                    
                    <div className="space-y-2 mb-3">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Type:</span>
                        <span className="font-medium text-gray-800">{connection.type}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Detected:</span>
                        <span className="font-medium text-gray-800">{connection.detected_date}</span>
                      </div>
                    </div>
                    
                    <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
                      <div 
                        className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${connection.confidence * 100}%` }}
                      ></div>
                    </div>
                    
                    <div className="flex space-x-2">
                      <button className="flex-1 bg-orange-500 hover:bg-orange-600 text-white py-2 px-3 rounded text-sm font-medium transition-colors">
                        Investigate
                      </button>
                      <button className="flex-1 bg-gray-500 hover:bg-gray-600 text-white py-2 px-3 rounded text-sm font-medium transition-colors">
                        Dismiss
                      </button>
                    </div>
                  </div>
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>
      </div>

      {/* Enhanced Legend */}
      <div className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl p-6 hover:border-white/40 transition-all duration-300">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-bold text-white">Map Legend & Guide</h3>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-sm text-gray-300">Real-time Data</span>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Complaints Legend */}
          <div className="space-y-4">
            <h4 className="text-lg font-semibold text-white flex items-center">
              <span className="mr-2">🚨</span>
              Complaint Severity
            </h4>
            <div className="space-y-3">
              {[
                { severity: 'high', color: 'red-500', label: 'Critical Issues' },
                { severity: 'medium', color: 'orange-500', label: 'Moderate Issues' },
                { severity: 'low', color: 'yellow-500', label: 'Minor Issues' }
              ].map((item) => (
                <div key={item.severity} className="flex items-center space-x-3">
                  <div className={`w-4 h-4 bg-${item.color} rounded-full shadow-lg`}></div>
                  <span className="text-gray-300 font-medium">{item.label}</span>
                  <span className="text-xs text-gray-400 bg-white/10 px-2 py-1 rounded-full">
                    {complaints.filter(c => c.severity === item.severity).length}
                  </span>
                </div>
              ))}
            </div>
          </div>
          
          {/* Demand Zones Legend */}
          <div className="space-y-4">
            <h4 className="text-lg font-semibold text-white flex items-center">
              <span className="mr-2">🌐</span>
              Capacity Status
            </h4>
            <div className="space-y-3">
              {[
                { range: '120%+', color: 'red-600', label: 'Critical Overload' },
                { range: '100-119%', color: 'red-500', label: 'Over Capacity' },
                { range: '80-99%', color: 'orange-500', label: 'Near Capacity' },
                { range: '60-79%', color: 'yellow-500', label: 'Moderate Load' },
                { range: '<60%', color: 'green-500', label: 'Low Usage' }
              ].map((item) => (
                <div key={item.range} className="flex items-center space-x-3">
                  <div className={`w-4 h-4 bg-${item.color} rounded-full opacity-70 shadow-lg`}></div>
                  <span className="text-gray-300 font-medium">{item.label}</span>
                  <span className="text-xs text-gray-400">{item.range}</span>
                </div>
              ))}
            </div>
          </div>
          
          {/* System Information */}
          <div className="space-y-4">
            <h4 className="text-lg font-semibold text-white flex items-center">
              <span className="mr-2">🔍</span>
              Detection Systems
            </h4>
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <div className="w-4 h-4 bg-purple-500 rounded-full shadow-lg"></div>
                <span className="text-gray-300 font-medium">AI-Detected Connections</span>
              </div>
              
              <div className="bg-white/5 p-3 rounded-lg border border-white/10">                <div className="text-sm text-gray-300 mb-2">Confidence Levels:</div>
                <div className="space-y-1 text-xs text-gray-400">
                  <div>• 80-100%: High confidence</div>
                  <div>• 60-79%: Medium confidence</div>
                  <div>• &lt;60%: Low confidence</div>
                </div>
              </div>
              
              <div className="text-xs text-gray-400 bg-white/5 p-2 rounded border border-white/10">
                💡 Click on any marker for detailed information and available actions.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MapView;
