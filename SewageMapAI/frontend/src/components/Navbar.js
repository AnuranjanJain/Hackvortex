import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';

const Navbar = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const isActive = (path) => location.pathname === path;

  return (
    <>
      {/* Backdrop blur support div */}
      <div className="fixed top-0 left-0 right-0 z-40 h-20 bg-white/10 backdrop-blur-md border-b border-white/20"></div>
      
      <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled 
          ? 'bg-white/10 backdrop-blur-lg border-b border-white/20 shadow-lg shadow-purple-500/10' 
          : 'bg-white/5 backdrop-blur-sm'
      }`}>
        <div className="container mx-auto px-6">
          <div className="flex justify-between items-center py-4">
            {/* Logo Section */}
            <div className="flex items-center group">
              <div className="relative">
                <div className="absolute -inset-1 bg-gradient-to-r from-purple-600 to-cyan-600 rounded-full blur opacity-30 group-hover:opacity-100 transition duration-300 animate-pulse-slow"></div>
                <div className="relative flex items-center justify-center w-10 h-10 bg-gradient-to-r from-purple-500 to-cyan-500 rounded-full shadow-lg">
                  <svg 
                    className="h-6 w-6 text-white" 
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24" 
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path 
                      strokeLinecap="round" 
                      strokeLinejoin="round" 
                      strokeWidth={2} 
                      d="M13 10V3L4 14h7v7l9-11h-7z" 
                    />
                  </svg>
                </div>
              </div>
              
              <div className="ml-3">
                <span className="font-bold text-xl bg-gradient-to-r from-white to-gray-200 bg-clip-text text-transparent">
                  SewageMapAI
                </span>
                <div className="text-xs text-gray-300 font-light -mt-1">
                  Urban Planning System
                </div>
              </div>
            </div>
            
            {/* Navigation Links */}
            <div className="flex space-x-1">
              {[
                { to: '/', label: 'Dashboard', icon: '📊' },
                { to: '/upload', label: 'Upload', icon: '📤' },
                { to: '/map', label: 'Map View', icon: '🗺️' },
                { to: '/insights', label: 'Insights', icon: '📈' }
              ].map((item) => (
                <Link
                  key={item.to}
                  to={item.to}
                  className={`group relative px-4 py-2 rounded-xl transition-all duration-300 ${
                    isActive(item.to)
                      ? 'bg-white/20 text-white shadow-lg shadow-purple-500/20 border border-white/30'
                      : 'text-gray-200 hover:text-white hover:bg-white/10'
                  }`}
                >
                  <div className="flex items-center space-x-2">
                    <span className="text-sm">{item.icon}</span>
                    <span className="font-medium">{item.label}</span>
                  </div>
                  
                  {/* Active indicator */}
                  {isActive(item.to) && (
                    <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-purple-500/20 to-cyan-500/20 animate-pulse"></div>
                  )}
                  
                  {/* Hover effect */}
                  <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-purple-500/0 to-cyan-500/0 group-hover:from-purple-500/10 group-hover:to-cyan-500/10 transition-all duration-300"></div>
                </Link>
              ))}
            </div>

            {/* Status Indicator */}
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2 px-3 py-1 rounded-full bg-green-500/20 border border-green-500/30">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-xs text-green-300 font-medium">System Online</span>
              </div>
            </div>
          </div>
        </div>
      </nav>
      
      {/* Spacer for fixed navbar */}
      <div className="h-20"></div>
    </>
  );
};

export default Navbar;
