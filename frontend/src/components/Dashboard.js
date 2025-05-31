import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, LineElement, PointElement } from 'chart.js';
import { Doughnut, Bar, Line } from 'react-chartjs-2';

// Register ChartJS components
ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, LineElement, PointElement);

const Dashboard = ({ data, loading }) => {
  const { demands, complaints, illegalConnections } = data;
  const [animatedStats, setAnimatedStats] = useState({
    totalDemand: 0,
    capacityUtilization: 0,
    complaints: 0,
    illegalConnections: 0
  });

  // Calculate statistics
  const totalDemand = demands.reduce((sum, item) => sum + item.demand_m3, 0);
  const totalCapacity = demands.reduce((sum, item) => sum + item.capacity_m3, 0);
  const capacityUtilization = totalDemand > 0 ? (totalDemand / totalCapacity * 100) : 0;
  const overCapacityZones = demands.filter(zone => zone.demand_m3 > zone.capacity_m3).length;
  const highSeverityComplaints = complaints.filter(complaint => complaint.severity === 'high').length;
  const highConfidenceIllegal = illegalConnections.filter(conn => conn.confidence > 0.8).length;

  // Animate numbers on mount
  useEffect(() => {
    if (!loading) {
      const animateValue = (start, end, duration, callback) => {
        const startTime = Date.now();
        const changeValue = end - start;
        
        const updateValue = () => {
          const now = Date.now();
          const progress = Math.min((now - startTime) / duration, 1);
          const currentValue = start + changeValue * progress;
          callback(currentValue);
          
          if (progress < 1) {
            requestAnimationFrame(updateValue);
          }
        };
        updateValue();
      };

      animateValue(0, totalDemand, 2000, (val) => 
        setAnimatedStats(prev => ({ ...prev, totalDemand: Math.floor(val) }))
      );
      animateValue(0, capacityUtilization, 2500, (val) => 
        setAnimatedStats(prev => ({ ...prev, capacityUtilization: val }))
      );
      animateValue(0, complaints.length, 1500, (val) => 
        setAnimatedStats(prev => ({ ...prev, complaints: Math.floor(val) }))
      );
      animateValue(0, illegalConnections.length, 1800, (val) => 
        setAnimatedStats(prev => ({ ...prev, illegalConnections: Math.floor(val) }))
      );
    }
  }, [loading, totalDemand, capacityUtilization, complaints.length, illegalConnections.length]);

  // Enhanced chart configurations
  const capacityChartData = {
    labels: ['Used Capacity', 'Available Capacity'],
    datasets: [
      {
        data: [totalDemand, Math.max(0, totalCapacity - totalDemand)],
        backgroundColor: [
          'rgba(139, 92, 246, 0.8)',
          'rgba(6, 182, 212, 0.8)'
        ],
        borderColor: [
          'rgba(139, 92, 246, 1)',
          'rgba(6, 182, 212, 1)'
        ],
        borderWidth: 2,
        hoverBackgroundColor: [
          'rgba(139, 92, 246, 0.9)',
          'rgba(6, 182, 212, 0.9)'
        ],
      },
    ],
  };

  const complaintsByTypeData = {
    labels: Array.from(new Set(complaints.map(c => c.type))),
    datasets: [
      {
        label: 'Complaints by Type',
        data: Array.from(new Set(complaints.map(c => c.type))).map(
          type => complaints.filter(c => c.type === type).length
        ),
        backgroundColor: [
          'rgba(239, 68, 68, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(34, 197, 94, 0.8)',
          'rgba(59, 130, 246, 0.8)',
          'rgba(236, 72, 153, 0.8)'
        ],
        borderColor: [
          'rgba(239, 68, 68, 1)',
          'rgba(245, 158, 11, 1)',
          'rgba(34, 197, 94, 1)',
          'rgba(59, 130, 246, 1)',
          'rgba(236, 72, 153, 1)'
        ],
        borderWidth: 2,
        borderRadius: 8,
        borderSkipped: false,
      },
    ],
  };

  // Mock trend data for the line chart
  const trendData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Infrastructure Load',
        data: [65, 72, 68, 75, 82, 78],
        borderColor: 'rgba(139, 92, 246, 1)',
        backgroundColor: 'rgba(139, 92, 246, 0.1)',
        fill: true,
        tension: 0.4,
        pointBackgroundColor: 'rgba(139, 92, 246, 1)',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 6,
      },
      {
        label: 'Complaints Trend',
        data: [28, 35, 32, 28, 42, 38],
        borderColor: 'rgba(236, 72, 153, 1)',
        backgroundColor: 'rgba(236, 72, 153, 0.1)',
        fill: true,
        tension: 0.4,
        pointBackgroundColor: 'rgba(236, 72, 153, 1)',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 6,
      }
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          padding: 20,
          font: {
            family: 'Inter',
            size: 12
          },
          color: 'rgba(255, 255, 255, 0.8)'
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: 'rgba(255, 255, 255, 1)',
        bodyColor: 'rgba(255, 255, 255, 0.9)',
        borderColor: 'rgba(139, 92, 246, 0.5)',
        borderWidth: 1,
        cornerRadius: 8,
      }
    },
    scales: {
      y: {
        ticks: {
          color: 'rgba(255, 255, 255, 0.6)',
          font: {
            family: 'Inter'
          }
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        }
      },
      x: {
        ticks: {
          color: 'rgba(255, 255, 255, 0.6)',
          font: {
            family: 'Inter'
          }
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        }
      }
    }
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '70%',
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          padding: 20,
          font: {
            family: 'Inter',
            size: 12
          },
          color: 'rgba(255, 255, 255, 0.8)'
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: 'rgba(255, 255, 255, 1)',
        bodyColor: 'rgba(255, 255, 255, 0.9)',
        borderColor: 'rgba(139, 92, 246, 0.5)',
        borderWidth: 1,
        cornerRadius: 8,
      }
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="relative">
          <div className="w-16 h-16 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin"></div>
          <div className="mt-4 text-white/80 font-medium">Loading dashboard data...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header Section */}
      <div className="text-center space-y-2 animate-slide-in">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-white via-purple-200 to-cyan-200 bg-clip-text text-transparent">
          City Infrastructure Dashboard
        </h1>
        <p className="text-gray-300 text-lg">
          Real-time overview of sewage infrastructure and system performance
        </p>
        <div className="w-24 h-1 bg-gradient-to-r from-purple-500 to-cyan-500 mx-auto rounded-full"></div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          {
            title: 'Total Sewage Demand',
            value: animatedStats.totalDemand.toLocaleString(),
            unit: 'm³',
            icon: '🏗️',
            gradient: 'from-purple-500 to-purple-700',
            bgGradient: 'from-purple-500/20 to-purple-700/10'
          },
          {
            title: 'Capacity Utilization',
            value: animatedStats.capacityUtilization.toFixed(1),
            unit: '%',
            icon: '📊',
            gradient: 'from-cyan-500 to-cyan-700',
            bgGradient: 'from-cyan-500/20 to-cyan-700/10',
            subtitle: `${overCapacityZones} zones over capacity`
          },
          {
            title: 'Active Complaints',
            value: animatedStats.complaints,
            unit: '',
            icon: '🚨',
            gradient: 'from-pink-500 to-pink-700',
            bgGradient: 'from-pink-500/20 to-pink-700/10',
            subtitle: `${highSeverityComplaints} high severity`
          },
          {
            title: 'Illegal Connections',
            value: animatedStats.illegalConnections,
            unit: '',
            icon: '⚠️',
            gradient: 'from-orange-500 to-orange-700',
            bgGradient: 'from-orange-500/20 to-orange-700/10',
            subtitle: `${highConfidenceIllegal} high confidence`
          }
        ].map((metric, index) => (
          <div
            key={metric.title}
            className={`group relative overflow-hidden bg-gradient-to-br ${metric.bgGradient} backdrop-blur-lg border border-white/20 rounded-2xl p-6 hover:border-white/40 transition-all duration-300 hover:scale-105 animate-scale-up`}
            style={{ animationDelay: `${index * 0.1}s` }}
          >
            {/* Background decoration */}
            <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-white/10 to-transparent rounded-full -translate-y-10 translate-x-10"></div>
            
            <div className="relative z-10">
              <div className="flex items-center justify-between mb-4">
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-r ${metric.gradient} flex items-center justify-center text-2xl shadow-lg group-hover:animate-bounce-slow`}>
                  {metric.icon}
                </div>
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              </div>
              
              <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-2">
                {metric.title}
              </h3>
              
              <div className="flex items-baseline space-x-2">
                <span className="text-3xl font-bold text-white">
                  {metric.value}
                </span>
                <span className="text-lg text-gray-300 font-medium">
                  {metric.unit}
                </span>
              </div>
              
              {metric.subtitle && (
                <p className="text-sm text-gray-400 mt-2">{metric.subtitle}</p>
              )}
            </div>
            
            {/* Hover glow effect */}
            <div className="absolute inset-0 bg-gradient-to-r from-purple-500/0 via-cyan-500/0 to-purple-500/0 group-hover:from-purple-500/5 group-hover:via-cyan-500/5 group-hover:to-purple-500/5 transition-all duration-500"></div>
          </div>
        ))}
      </div>
      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Capacity Utilization Chart */}
        <div className="lg:col-span-1 bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl p-6 hover:border-white/40 transition-all duration-300">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-white">Capacity Utilization</h3>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-purple-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-gray-300">Live</span>
            </div>
          </div>
          <div className="h-64 relative">
            <Doughnut data={capacityChartData} options={doughnutOptions} />
            {/* Center text */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <div className="text-2xl font-bold text-white">{capacityUtilization.toFixed(1)}%</div>
                <div className="text-sm text-gray-300">Utilized</div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Complaints by Type */}
        <div className="lg:col-span-1 bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl p-6 hover:border-white/40 transition-all duration-300">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-white">Complaints by Type</h3>
            <div className="px-3 py-1 bg-orange-500/20 border border-orange-500/30 rounded-full">
              <span className="text-xs text-orange-300 font-medium">Active Issues</span>
            </div>
          </div>
          <div className="h-64">
            <Bar data={complaintsByTypeData} options={chartOptions} />
          </div>
        </div>
        
        {/* Trends Chart */}
        <div className="lg:col-span-1 bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl p-6 hover:border-white/40 transition-all duration-300">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-white">System Trends</h3>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-gray-300">6 Months</span>
            </div>
          </div>
          <div className="h-64">
            <Line data={trendData} options={chartOptions} />
          </div>
        </div>
      </div>

      {/* Quick Actions Section */}
      <div className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl p-8 hover:border-white/40 transition-all duration-300">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h3 className="text-2xl font-bold text-white mb-2">Quick Actions</h3>
            <p className="text-gray-300">Access key features and tools</p>
          </div>
          <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-cyan-500 rounded-2xl flex items-center justify-center animate-float">
            <span className="text-2xl">⚡</span>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            {
              to: '/upload',
              title: 'Upload Satellite Image',
              description: 'Analyze new satellite imagery for infrastructure insights',
              icon: '📤',
              gradient: 'from-purple-500 to-purple-700',
              hoverGradient: 'from-purple-600 to-purple-800'
            },
            {
              to: '/map',
              title: 'View Infrastructure Map',
              description: 'Interactive map with real-time infrastructure data',
              icon: '🗺️',
              gradient: 'from-cyan-500 to-cyan-700',
              hoverGradient: 'from-cyan-600 to-cyan-800'
            },
            {
              to: '/insights',
              title: 'Analyze Insights',
              description: 'Deep analytics and predictive insights',
              icon: '📈',
              gradient: 'from-pink-500 to-pink-700',
              hoverGradient: 'from-pink-600 to-pink-800'
            }
          ].map((action, index) => (
            <Link
              key={action.to}
              to={action.to}
              className={`group relative overflow-hidden bg-gradient-to-r ${action.gradient} hover:${action.hoverGradient} rounded-xl p-6 transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:shadow-purple-500/20 animate-scale-up`}
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="relative z-10">
                <div className="flex items-center justify-between mb-4">
                  <div className="text-3xl">{action.icon}</div>
                  <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center group-hover:bg-white/30 transition-all duration-300">
                    <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
                
                <h4 className="text-lg font-bold text-white mb-2">{action.title}</h4>
                <p className="text-sm text-white/80">{action.description}</p>
              </div>
              
              {/* Background decoration */}
              <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -translate-y-16 translate-x-16 group-hover:scale-110 transition-transform duration-500"></div>
            </Link>
          ))}
        </div>
      </div>

      {/* Recent Issues Table */}
      <div className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl overflow-hidden hover:border-white/40 transition-all duration-300">
        <div className="p-6 border-b border-white/10">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-2xl font-bold text-white mb-2">Recent Issues</h3>
              <p className="text-gray-300">Latest system alerts and complaints</p>
            </div>
            <div className="flex items-center space-x-2">
              <div className="px-4 py-2 bg-red-500/20 border border-red-500/30 rounded-lg">
                <span className="text-sm text-red-300 font-medium">
                  {highSeverityComplaints} Critical
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-white/5">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Type</th>
                <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Location</th>
                <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Severity</th>
                <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Description</th>
                <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Status</th>
              </tr>            </thead>
            <tbody className="divide-y divide-white/10">
              {complaints.slice(0, 15).map((complaint, index) => (
                <tr key={complaint.id} className="hover:bg-white/5 transition-all duration-200">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-cyan-500 rounded-lg flex items-center justify-center mr-3">
                        <span className="text-xs text-white font-bold">
                          {complaint.type.substring(0, 2).toUpperCase()}
                        </span>
                      </div>
                      <div className="text-sm font-medium text-white">{complaint.type}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                    <div className="flex items-center">
                      <svg className="w-4 h-4 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      {complaint.lat.toFixed(4)}, {complaint.lng.toFixed(4)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${
                      complaint.severity === 'high' 
                        ? 'bg-red-500/20 text-red-300 border border-red-500/30' :
                      complaint.severity === 'medium' 
                        ? 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30' :
                        'bg-green-500/20 text-green-300 border border-green-500/30'
                    }`}>
                      <div className={`w-2 h-2 rounded-full mr-2 ${
                        complaint.severity === 'high' ? 'bg-red-400' :
                        complaint.severity === 'medium' ? 'bg-yellow-400' : 'bg-green-400'
                      } animate-pulse`}></div>
                      {complaint.severity}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-300 max-w-xs truncate">
                    {complaint.description}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-orange-400 rounded-full animate-pulse"></div>
                      <span className="text-xs text-orange-300 font-medium">Pending</span>
                    </div>
                  </td>
                </tr>
              ))}
              {complaints.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center">
                    <div className="flex flex-col items-center">
                      <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mb-4">
                        <span className="text-2xl">✅</span>
                      </div>
                      <div className="text-lg font-medium text-white mb-2">No Issues Found</div>
                      <div className="text-sm text-gray-400">All systems are running smoothly</div>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
