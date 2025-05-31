import React from 'react';

const LoadingScreen = () => {
  return (
    <div className="fixed inset-0 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center z-50">
      <div className="text-center">
        {/* Animated Logo/Icon */}
        <div className="relative mb-8">
          <div className="w-24 h-24 mx-auto">
            <div className="absolute inset-0 rounded-full border-4 border-purple-500/30 animate-pulse"></div>
            <div className="absolute inset-2 rounded-full border-4 border-cyan-500/30 animate-spin"></div>
            <div className="absolute inset-4 rounded-full border-4 border-pink-500/30 animate-bounce"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <svg className="w-8 h-8 text-white animate-pulse" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
              </svg>
            </div>
          </div>
        </div>
        
        {/* Loading Text */}
        <div className="space-y-4">
          <h2 className="text-3xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400 bg-clip-text text-transparent">
            SewageMapAI
          </h2>
          <p className="text-white/70 text-lg">Loading sewage infrastructure data...</p>
          
          {/* Progress Bar */}
          <div className="w-64 mx-auto">
            <div className="bg-white/10 rounded-full h-2 overflow-hidden">
              <div className="bg-gradient-to-r from-purple-400 to-cyan-400 h-full rounded-full animate-pulse"></div>
            </div>
          </div>
          
          {/* Loading Steps */}
          <div className="mt-8 space-y-2 text-sm text-white/50">
            <div className="flex items-center justify-center space-x-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span>Connecting to servers...</span>
            </div>
            <div className="flex items-center justify-center space-x-2">
              <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse animation-delay-1000"></div>
              <span>Loading AI models...</span>
            </div>
            <div className="flex items-center justify-center space-x-2">
              <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse animation-delay-2000"></div>
              <span>Preparing dashboard...</span>
            </div>
          </div>
        </div>
      </div>
      
      {/* Background Animation */}
      <div className="absolute inset-0 opacity-30">
        <div className="absolute top-1/4 left-1/4 w-32 h-32 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl animate-float"></div>
        <div className="absolute top-3/4 right-1/4 w-32 h-32 bg-cyan-500 rounded-full mix-blend-multiply filter blur-xl animate-float animation-delay-2000"></div>
        <div className="absolute bottom-1/4 left-3/4 w-32 h-32 bg-pink-500 rounded-full mix-blend-multiply filter blur-xl animate-float animation-delay-4000"></div>
      </div>
    </div>
  );
};

export default LoadingScreen;
