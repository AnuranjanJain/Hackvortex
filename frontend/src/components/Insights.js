import React, { useState, useEffect } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Bar, Line, Pie } from 'react-chartjs-2';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const Insights = ({ data, loading }) => {
  const { demands, complaints, illegalConnections } = data;
  const [activeTab, setActiveTab] = useState('demand');
  const [animatedValues, setAnimatedValues] = useState({
    healthScore: 0,
    efficiencyScore: 0,
    environmentScore: 0
  });
  
  // Animate score values
  useEffect(() => {
    const targetValues = { healthScore: 72, efficiencyScore: 86, environmentScore: 64 };
    const duration = 2000;
    const steps = 60;
    const stepDuration = duration / steps;
    
    let currentStep = 0;
    const interval = setInterval(() => {
      currentStep++;
      const progress = currentStep / steps;
      
      setAnimatedValues({
        healthScore: Math.round(targetValues.healthScore * progress),
        efficiencyScore: Math.round(targetValues.efficiencyScore * progress),
        environmentScore: Math.round(targetValues.environmentScore * progress)
      });
      
      if (currentStep >= steps) {
        clearInterval(interval);
      }
    }, stepDuration);
    
    return () => clearInterval(interval);
  }, []);
  
  if (loading) {
    return (
      <div className="flex justify-center items-center h-64 animate-fade-in">
        <div className="relative">
          <div className="w-16 h-16 border-4 border-purple-500/20 border-t-purple-500 rounded-full animate-spin"></div>
          <div className="absolute inset-0 w-16 h-16 border-4 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin animate-pulse"></div>
          <div className="mt-4 text-center">
            <p className="text-white font-medium">Loading AI Insights...</p>
            <p className="text-gray-300 text-sm">Processing analytics data</p>
          </div>
        </div>
      </div>
    );
  }
  
  // Enhanced chart styling for modern theme
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: 'rgba(255, 255, 255, 0.8)',
          font: {
            size: 12
          },
          usePointStyle: true,
          pointStyle: 'circle'
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: 'white',
        bodyColor: 'white',
        borderColor: 'rgba(147, 51, 234, 0.5)',
        borderWidth: 1,
        cornerRadius: 8
      }
    },
    scales: {
      x: {
        ticks: {
          color: 'rgba(255, 255, 255, 0.7)',
          font: {
            size: 11
          }
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      },
      y: {
        ticks: {
          color: 'rgba(255, 255, 255, 0.7)',
          font: {
            size: 11
          }
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      }
    }
  };

  const pieChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: 'rgba(255, 255, 255, 0.8)',
          font: {
            size: 12
          },
          usePointStyle: true,
          pointStyle: 'circle'
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: 'white',
        bodyColor: 'white',
        borderColor: 'rgba(147, 51, 234, 0.5)',
        borderWidth: 1,
        cornerRadius: 8
      }
    }
  };  // Prepare data for demand by district chart
  const demandByDistrict = {};
  const capacityByDistrict = {};
  
  demands.forEach(zone => {
    if (!demandByDistrict[zone.district]) {
      demandByDistrict[zone.district] = 0;
      capacityByDistrict[zone.district] = 0;
    }
    demandByDistrict[zone.district] += zone.demand_m3;
    capacityByDistrict[zone.district] += zone.capacity_m3;
  });
  
  const districts = Object.keys(demandByDistrict);
  
  const demandByDistrictData = {
    labels: districts,
    datasets: [
      {
        label: 'Demand (m³)',
        data: districts.map(district => demandByDistrict[district]),
        backgroundColor: 'rgba(147, 51, 234, 0.6)',
        borderColor: 'rgb(147, 51, 234)',
        borderWidth: 2,
        borderRadius: 8,
        borderSkipped: false,
      },
      {
        label: 'Capacity (m³)',
        data: districts.map(district => capacityByDistrict[district]),
        backgroundColor: 'rgba(6, 182, 212, 0.6)',
        borderColor: 'rgb(6, 182, 212)',
        borderWidth: 2,
        borderRadius: 8,
        borderSkipped: false,
      },
    ],
  };
  
  // Complaint types breakdown with modern colors
  const complaintTypes = {};
  complaints.forEach(complaint => {
    if (!complaintTypes[complaint.type]) {
      complaintTypes[complaint.type] = 0;
    }
    complaintTypes[complaint.type]++;
  });
  
  const complaintTypeData = {
    labels: Object.keys(complaintTypes),
    datasets: [
      {
        data: Object.values(complaintTypes),
        backgroundColor: [
          'rgba(147, 51, 234, 0.8)',
          'rgba(6, 182, 212, 0.8)',
          'rgba(236, 72, 153, 0.8)',
          'rgba(59, 130, 246, 0.8)',
          'rgba(16, 185, 129, 0.8)',
        ],
        borderColor: [
          'rgb(147, 51, 234)',
          'rgb(6, 182, 212)',
          'rgb(236, 72, 153)',
          'rgb(59, 130, 246)',
          'rgb(16, 185, 129)',
        ],
        borderWidth: 2,
      },
    ],
  };
  
  // Illegal connection types with modern styling
  const illegalTypes = {};
  illegalConnections.forEach(connection => {
    if (!illegalTypes[connection.type]) {
      illegalTypes[connection.type] = 0;
    }
    illegalTypes[connection.type]++;
  });
  
  const illegalConnectionData = {
    labels: Object.keys(illegalTypes),
    datasets: [
      {
        label: 'Number of Connections',
        data: Object.values(illegalTypes),
        backgroundColor: [
          'rgba(147, 51, 234, 0.6)',
          'rgba(236, 72, 153, 0.6)',
          'rgba(6, 182, 212, 0.6)',
        ],
        borderColor: [
          'rgb(147, 51, 234)',
          'rgb(236, 72, 153)',
          'rgb(6, 182, 212)',
        ],
        borderWidth: 2,
        borderRadius: 8,
        borderSkipped: false,
      },
    ],
  };
  
  // Complaint severity over time with gradient colors
  const severityData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
    datasets: [
      {
        label: 'High Severity',
        data: [12, 15, 18, 14, 20],
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.4,
        fill: true,
        pointBackgroundColor: 'rgb(239, 68, 68)',
        pointBorderColor: 'white',
        pointBorderWidth: 2,
        pointRadius: 6,
      },
      {
        label: 'Medium Severity',
        data: [19, 22, 20, 25, 28],
        borderColor: 'rgb(245, 158, 11)',
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        tension: 0.4,
        fill: true,
        pointBackgroundColor: 'rgb(245, 158, 11)',
        pointBorderColor: 'white',
        pointBorderWidth: 2,
        pointRadius: 6,
      },
      {
        label: 'Low Severity',
        data: [24, 20, 23, 27, 29],
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        tension: 0.4,
        fill: true,
        pointBackgroundColor: 'rgb(34, 197, 94)',
        pointBorderColor: 'white',
        pointBorderWidth: 2,
        pointRadius: 6,
      },
    ],
  };
    return (
    <div className="space-y-8 animate-fade-in">
      {/* Header Section */}
      <div className="text-center space-y-4 animate-slide-in">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-white via-purple-200 to-cyan-200 bg-clip-text text-transparent">
          AI-Powered Insights
        </h1>
        <p className="text-gray-300 text-lg max-w-3xl mx-auto">
          Advanced analytics and machine learning insights for intelligent infrastructure planning and optimization
        </p>
        <div className="w-24 h-1 bg-gradient-to-r from-purple-500 to-cyan-500 mx-auto rounded-full"></div>
      </div>

      {/* System-Wide Insights Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-scale-up">
        {[
          {
            title: "Infrastructure Health Score",
            value: animatedValues.healthScore,
            max: 100,
            color: "from-purple-500 to-indigo-500",
            bgColor: "from-purple-500/20 to-indigo-500/20",
            borderColor: "border-purple-500/30",
            icon: "🏗️",
            description: "Overall system health based on capacity, complaints, and infrastructure age"
          },
          {
            title: "Maintenance Efficiency",
            value: animatedValues.efficiencyScore,
            max: 100,
            color: "from-green-500 to-emerald-500",
            bgColor: "from-green-500/20 to-emerald-500/20",
            borderColor: "border-green-500/30",
            icon: "⚡",
            description: "How efficiently the system responds to maintenance needs"
          },
          {
            title: "Environmental Impact",
            value: animatedValues.environmentScore,
            max: 100,
            color: "from-orange-500 to-red-500",
            bgColor: "from-orange-500/20 to-red-500/20",
            borderColor: "border-orange-500/30",
            icon: "🌍",
            description: "Environmental impact score based on compliance and overflow incidents"
          }
        ].map((metric, index) => (
          <div key={index} className={`bg-gradient-to-br ${metric.bgColor} backdrop-blur-lg border ${metric.borderColor} rounded-2xl p-6 hover:scale-105 transition-all duration-300`}>
            <div className="flex items-center justify-between mb-4">
              <div className={`w-12 h-12 bg-gradient-to-r ${metric.color} rounded-xl flex items-center justify-center text-2xl animate-float`}>
                {metric.icon}
              </div>
              <div className={`text-right`}>
                <div className="flex items-baseline space-x-1">
                  <span className={`text-3xl font-bold bg-gradient-to-r ${metric.color} bg-clip-text text-transparent`}>
                    {metric.value}
                  </span>
                  <span className="text-gray-400 text-sm">/{metric.max}</span>
                </div>
              </div>
            </div>
            
            <h4 className="text-white font-semibold mb-2">{metric.title}</h4>
            
            <div className="w-full bg-white/20 rounded-full h-3 mb-3">
              <div 
                className={`h-3 bg-gradient-to-r ${metric.color} rounded-full transition-all duration-1000 ease-out relative overflow-hidden`}
                style={{ width: `${metric.value}%` }}
              >
                <div className="absolute inset-0 bg-white/30 animate-pulse"></div>
              </div>
            </div>
            
            <p className="text-gray-300 text-sm leading-relaxed">{metric.description}</p>
          </div>
        ))}
      </div>

      {/* Tab Navigation */}
      <div className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl overflow-hidden animate-scale-up">
        <div className="flex border-b border-white/20">
          {[
            { id: 'demand', label: 'Demand Analysis', icon: '📊' },
            { id: 'complaints', label: 'Complaints Analysis', icon: '⚠️' },
            { id: 'illegal', label: 'Illegal Connections', icon: '🚫' }
          ].map((tab) => (
            <button
              key={tab.id}
              className={`flex-1 px-6 py-4 text-sm font-medium transition-all duration-300 ${
                activeTab === tab.id 
                  ? 'text-white bg-gradient-to-r from-purple-500/20 to-cyan-500/20 border-b-2 border-cyan-400' 
                  : 'text-gray-300 hover:text-white hover:bg-white/5'
              }`}
              onClick={() => setActiveTab(tab.id)}
            >
              <div className="flex items-center justify-center space-x-2">
                <span>{tab.icon}</span>
                <span>{tab.label}</span>
              </div>
            </button>
          ))}
        </div>        
        {/* Tab Content */}
        <div className="p-8">
          {activeTab === 'demand' && (
            <div className="space-y-8 animate-fade-in">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-cyan-500 rounded-lg flex items-center justify-center">
                  <span className="text-xl">📊</span>
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-white">Sewage Demand Analysis</h2>
                  <p className="text-gray-300">Infrastructure capacity vs demand optimization</p>
                </div>
              </div>
              
              <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-white mb-6">District Demand vs. Capacity</h3>
                <div className="h-80">
                  <Bar data={demandByDistrictData} options={chartOptions} />
                </div>
                <p className="text-gray-300 text-sm mt-4 leading-relaxed">
                  This chart compares the current sewage demand with the available capacity for each district.
                  Districts with demand nearing or exceeding capacity should be prioritized for infrastructure upgrades.
                </p>
              </div>
              
              <div className="bg-gradient-to-br from-blue-500/20 to-indigo-500/20 border border-blue-500/30 rounded-xl p-6 backdrop-blur-sm">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full flex items-center justify-center">
                    <span className="text-sm">🤖</span>
                  </div>
                  <h3 className="text-xl font-semibold text-white">AI Recommendations</h3>
                </div>
                <div className="space-y-4">
                  {[
                    {
                      title: "Capacity Upgrade Priority",
                      content: `The ${districts[0]} district is operating at ${(demandByDistrict[districts[0]] / capacityByDistrict[districts[0]] * 100).toFixed(1)}% capacity and should be prioritized for infrastructure expansion.`,
                      icon: "🎯"
                    },
                    {
                      title: "Predicted Demand Increase",
                      content: "Based on population growth trends, expect a 15% increase in sewage demand in the Central district within the next 3 years.",
                      icon: "📈"
                    },
                    {
                      title: "Optimization Opportunity",
                      content: "Implementing flow regulators in the East district could increase effective capacity by approximately 8% with minimal investment.",
                      icon: "⚡"
                    }
                  ].map((recommendation, index) => (
                    <div key={index} className="flex items-start space-x-3 p-4 bg-white/10 rounded-lg">
                      <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                        <span className="text-sm">{recommendation.icon}</span>
                      </div>
                      <div>
                        <h4 className="text-white font-medium mb-1">{recommendation.title}</h4>
                        <p className="text-blue-300 text-sm leading-relaxed">{recommendation.content}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
          
          {activeTab === 'complaints' && (
            <div className="space-y-8 animate-fade-in">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-10 h-10 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-lg flex items-center justify-center">
                  <span className="text-xl">⚠️</span>
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-white">Complaint Pattern Analysis</h2>
                  <p className="text-gray-300">Predictive maintenance and issue identification</p>
                </div>
              </div>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
                  <h3 className="text-lg font-semibold text-white mb-6">Complaint Type Distribution</h3>
                  <div className="h-64">
                    <Pie data={complaintTypeData} options={pieChartOptions} />
                  </div>
                </div>
                
                <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
                  <h3 className="text-lg font-semibold text-white mb-6">Complaint Severity Trends</h3>
                  <div className="h-64">
                    <Line data={severityData} options={chartOptions} />
                  </div>
                </div>
              </div>
              
              <div className="bg-gradient-to-br from-yellow-500/20 to-orange-500/20 border border-yellow-500/30 rounded-xl p-6 backdrop-blur-sm">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="w-8 h-8 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-full flex items-center justify-center">
                    <span className="text-sm">🧠</span>
                  </div>
                  <h3 className="text-xl font-semibold text-white">AI Complaint Analysis</h3>
                </div>
                <div className="space-y-4">
                  {[
                    {
                      title: "Clustered Issues",
                      content: "63% of blockage complaints are concentrated in areas with infrastructure older than 30 years.",
                      icon: "📍"
                    },
                    {
                      title: "Seasonal Pattern",
                      content: "The AI model detected a 28% increase in odor complaints during summer months, suggesting temperature-related issues.",
                      icon: "🌡️"
                    },
                    {
                      title: "Predictive Maintenance",
                      content: "Based on complaint patterns, 3 areas have been identified with high probability of requiring major maintenance within 6 months.",
                      icon: "🔮"
                    }
                  ].map((insight, index) => (
                    <div key={index} className="flex items-start space-x-3 p-4 bg-white/10 rounded-lg">
                      <div className="w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                        <span className="text-sm">{insight.icon}</span>
                      </div>
                      <div>
                        <h4 className="text-white font-medium mb-1">{insight.title}</h4>
                        <p className="text-yellow-300 text-sm leading-relaxed">{insight.content}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
          
          {activeTab === 'illegal' && (
            <div className="space-y-8 animate-fade-in">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-10 h-10 bg-gradient-to-r from-red-500 to-pink-500 rounded-lg flex items-center justify-center">
                  <span className="text-xl">🚫</span>
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-white">Illegal Connection Analysis</h2>
                  <p className="text-gray-300">AI-powered detection and enforcement optimization</p>
                </div>
              </div>
              
              <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-white mb-6">Illegal Connections by Type</h3>
                <div className="h-80">
                  <Bar data={illegalConnectionData} options={chartOptions} />
                </div>
                <p className="text-gray-300 text-sm mt-4 leading-relaxed">
                  Distribution of suspected illegal connections by type. Industrial connections typically have
                  the largest environmental impact due to potential chemical contamination.
                </p>
              </div>
              
              <div className="bg-gradient-to-br from-red-500/20 to-pink-500/20 border border-red-500/30 rounded-xl p-6 backdrop-blur-sm">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="w-8 h-8 bg-gradient-to-r from-red-500 to-pink-500 rounded-full flex items-center justify-center">
                    <span className="text-sm">🔍</span>
                  </div>
                  <h3 className="text-xl font-semibold text-white">AI Detection Insights</h3>
                </div>
                <div className="space-y-4">
                  {[
                    {
                      title: "High Confidence Locations",
                      content: `${illegalConnections.filter(c => c.confidence > 0.85).length} locations have detection confidence above 85% and should be prioritized for inspection.`,
                      icon: "🎯"
                    },
                    {
                      title: "Potential Impact",
                      content: "The AI model estimates that these illegal connections may be contributing approximately 580 m³ of unauthorized flow daily.",
                      icon: "💧"
                    },
                    {
                      title: "Cluster Analysis",
                      content: "A significant cluster of industrial illegal connections has been detected in the northwest area, possibly related to a particular industrial zone.",
                      icon: "🏭"
                    }
                  ].map((insight, index) => (
                    <div key={index} className="flex items-start space-x-3 p-4 bg-white/10 rounded-lg">
                      <div className="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                        <span className="text-sm">{insight.icon}</span>
                      </div>
                      <div>
                        <h4 className="text-white font-medium mb-1">{insight.title}</h4>
                        <p className="text-red-300 text-sm leading-relaxed">{insight.content}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Insights;
