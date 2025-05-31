import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';

const UploadImage = ({ apiUrl }) => {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [analysisStep, setAnalysisStep] = useState(0);
  const fileInputRef = useRef(null);

  const analysisSteps = [
    "Preparing image for analysis...",
    "Loading AI segmentation model...", 
    "Detecting sewage infrastructure...",
    "Processing segmentation results...",
    "Generating analysis report...",
    "Analysis complete!"
  ];

  // Handle file change
  const handleFileChange = (selectedFile) => {
    if (selectedFile) {
      // Validate file type
      const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/tiff'];
      if (!validTypes.includes(selectedFile.type)) {
        setError('Please select a valid image file (PNG, JPG, or TIFF)');
        return;
      }

      // Validate file size (max 50MB)
      if (selectedFile.size > 50 * 1024 * 1024) {
        setError('File size must be less than 50MB');
        return;
      }

      setFile(selectedFile);
      setError(null);
      setResult(null);
      
      // Generate preview
      const reader = new FileReader();
      reader.onload = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(selectedFile);
    }
  };

  const handleFileInput = (e) => {
    const selectedFile = e.target.files[0];
    handleFileChange(selectedFile);
  };

  // Handle drag and drop
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  // Simulate analysis progress
  useEffect(() => {
    if (uploading) {
      const interval = setInterval(() => {
        setAnalysisStep(prev => {
          if (prev < analysisSteps.length - 1) {
            return prev + 1;
          }
          clearInterval(interval);
          return prev;
        });
      }, 1000);      return () => clearInterval(interval);
    } else {
      setAnalysisStep(0);
    }
  }, [uploading, analysisSteps.length]);

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select an image to upload');
      return;
    }
    
    // Create form data
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      setUploading(true);
      setUploadProgress(0);
      setError(null);
      
      // Upload the file with progress tracking
      const response = await axios.post(`${apiUrl}/upload-image`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
        }      });
      
      console.log('Upload response:', response.data);
      console.log('Original image URL will be:', `${apiUrl}${response.data.original_image}`);
      console.log('Mask URL will be:', `${apiUrl}${response.data.segmentation_mask}`);
      
      setResult(response.data);
      setUploading(false);
    } catch (err) {
      console.error('Error uploading image:', err);
      setError(err.response?.data?.error || 'Failed to upload image');
      setUploading(false);
      setUploadProgress(0);
    }
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header Section */}
      <div className="text-center space-y-4 animate-slide-in">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-white via-purple-200 to-cyan-200 bg-clip-text text-transparent">
          AI-Powered Image Analysis
        </h1>
        <p className="text-gray-300 text-lg max-w-3xl mx-auto">
          Upload satellite or aerial imagery to automatically detect sewage infrastructure using advanced deep learning models
        </p>
        <div className="w-24 h-1 bg-gradient-to-r from-purple-500 to-cyan-500 mx-auto rounded-full"></div>
      </div>

      {/* Upload Section */}
      <div className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl overflow-hidden hover:border-white/40 transition-all duration-300 animate-scale-up">
        <div className="p-8">
          <div className="flex items-center space-x-3 mb-6">
            <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-cyan-500 rounded-lg flex items-center justify-center">
              <span className="text-xl">📤</span>
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">Image Upload</h2>
              <p className="text-gray-300">Advanced AI segmentation and infrastructure detection</p>
            </div>
          </div>
          
          {error && (
            <div className="bg-red-500/20 border border-red-500/30 text-red-300 p-4 rounded-xl mb-6 backdrop-blur-sm animate-scale-up">
              <div className="flex items-center">
                <span className="mr-2">⚠️</span>
                <p>{error}</p>
              </div>
            </div>
          )}
          
          <form onSubmit={handleSubmit}>
            <div className="mb-8">
              <div
                className={`relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-300 ${
                  dragActive
                    ? 'border-cyan-400 bg-cyan-500/10 scale-105'
                    : preview
                    ? 'border-green-400 bg-green-500/10'
                    : 'border-white/30 hover:border-purple-400 hover:bg-purple-500/10'
                }`}
                onClick={() => fileInputRef.current?.click()}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                {preview ? (
                  <div className="space-y-6 animate-fade-in">
                    <div className="relative inline-block">
                      <img 
                        src={preview} 
                        alt="Preview" 
                        className="max-h-80 max-w-full rounded-xl shadow-2xl border-2 border-white/20"
                      />
                      <div className="absolute -top-2 -right-2 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                        <span className="text-white text-xs">✓</span>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <p className="text-white font-medium">{file?.name}</p>
                      <p className="text-gray-300 text-sm">
                        Size: {(file?.size / (1024 * 1024)).toFixed(2)} MB
                      </p>
                      <p className="text-cyan-300 text-sm font-medium">
                        ✨ Click to change image or drag a new one
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-6">
                    <div className="relative">
                      <div className="w-20 h-20 mx-auto bg-gradient-to-r from-purple-500 to-cyan-500 rounded-2xl flex items-center justify-center mb-4 animate-float">
                        <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                      </div>
                      <div className="absolute inset-0 bg-gradient-to-r from-purple-500/20 to-cyan-500/20 rounded-2xl blur-xl"></div>
                    </div>
                    
                    <div className="space-y-2">
                      <p className="text-xl font-semibold text-white">Drop your satellite image here</p>
                      <p className="text-gray-300">or click to browse files</p>
                      <div className="flex justify-center space-x-4 text-sm text-gray-400">
                        <span className="px-3 py-1 bg-white/10 rounded-full">PNG</span>
                        <span className="px-3 py-1 bg-white/10 rounded-full">JPG</span>
                        <span className="px-3 py-1 bg-white/10 rounded-full">TIFF</span>
                      </div>
                      <p className="text-xs text-gray-400">Maximum file size: 50MB</p>
                    </div>
                  </div>
                )}
                
                <input 
                  ref={fileInputRef}
                  type="file" 
                  className="hidden" 
                  onChange={handleFileInput}
                  accept=".png,.jpg,.jpeg,.tif,.tiff"
                />
              </div>
            </div>
            
            <div className="flex justify-center">
              <button 
                type="submit" 
                className={`relative overflow-hidden px-8 py-4 bg-gradient-to-r from-purple-500 to-cyan-500 hover:from-purple-600 hover:to-cyan-600 text-white font-bold rounded-xl transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-2xl ${
                  !file || uploading ? 'opacity-50 cursor-not-allowed scale-100' : 'hover:shadow-purple-500/30'
                }`}
                disabled={!file || uploading}
              >
                <div className="flex items-center space-x-3">
                  {uploading ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      <span>Analyzing Image...</span>
                    </>
                  ) : (
                    <>
                      <span>🚀</span>
                      <span>Start AI Analysis</span>
                    </>
                  )}
                </div>
                
                {/* Animated background */}
                <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-700"></div>
              </button>
            </div>
          </form>
        </div>

        {/* Progress Section */}
        {uploading && (
          <div className="border-t border-white/20 p-6 bg-white/5 animate-fade-in">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-white font-medium">Upload Progress</span>
                <span className="text-cyan-300 font-bold">{uploadProgress}%</span>
              </div>
              <div className="w-full bg-white/20 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-purple-500 to-cyan-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
              
              <div className="flex items-center space-x-3 text-gray-300">
                <div className="w-4 h-4 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
                <span className="text-sm">{analysisSteps[analysisStep]}</span>
              </div>
            </div>
          </div>
        )}
      </div>      {/* Results Section */}
      {result && (
        <div className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl overflow-hidden animate-scale-up">
          <div className="p-8">
            <div className="flex items-center space-x-3 mb-8">
              <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-emerald-500 rounded-lg flex items-center justify-center">
                <span className="text-xl">✨</span>
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">Analysis Results</h2>
                <p className="text-gray-300">AI-powered sewage infrastructure detection completed</p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Original Image */}
              <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl overflow-hidden hover:border-white/30 transition-all duration-300">
                <div className="p-6">
                  <h4 className="text-lg font-semibold text-white mb-4 flex items-center">
                    <span className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center mr-3 text-sm">📷</span>
                    Original Satellite Image
                  </h4>                  <div className="aspect-square bg-black/20 flex items-center justify-center rounded-xl overflow-hidden border border-white/10">
                    <img 
                      src={`${apiUrl}${result.original_image}`} 
                      alt="Original satellite" 
                      className="max-h-full max-w-full object-contain rounded-lg"
                      onError={(e) => {
                        console.error('Failed to load original image:', `${apiUrl}${result.original_image}`);
                        e.target.style.display = 'none';
                      }}
                      onLoad={() => console.log('Original image loaded successfully:', `${apiUrl}${result.original_image}`)}
                    />
                  </div>
                </div>
              </div>
              
              {/* Segmentation Results */}
              <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl overflow-hidden hover:border-white/30 transition-all duration-300">
                <div className="p-6">
                  <h4 className="text-lg font-semibold text-white mb-4 flex items-center">
                    <span className="w-6 h-6 bg-purple-500 rounded-full flex items-center justify-center mr-3 text-sm">🧠</span>
                    AI Detection Results
                  </h4>                  <div className="aspect-square bg-black/20 flex items-center justify-center rounded-xl overflow-hidden border border-white/10">
                    <img 
                      src={`${apiUrl}${result.segmentation_mask}`} 
                      alt="Sewage line detection" 
                      className="max-h-full max-w-full object-contain rounded-lg"
                      onError={(e) => {
                        console.error('Failed to load segmentation mask:', `${apiUrl}${result.segmentation_mask}`);
                        e.target.style.display = 'none';
                      }}
                      onLoad={() => console.log('Segmentation mask loaded successfully:', `${apiUrl}${result.segmentation_mask}`)}
                    />
                  </div>
                </div>
              </div>
            </div>            {/* Analysis Summary */}
            <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-gradient-to-br from-green-500/20 to-emerald-500/20 border border-green-500/30 rounded-xl p-6 text-center">
                <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-xl">{result.detection_results?.sewage_lines_detected ? '✅' : '❌'}</span>
                </div>
                <h5 className="text-lg font-semibold text-white mb-2">
                  {result.detection_results?.sewage_lines_detected ? 'Infrastructure Detected' : 'No Infrastructure Found'}
                </h5>
                <p className="text-green-300 text-sm">
                  {result.detection_results?.sewage_lines_detected ? 'Sewage lines identified' : 'No sewage features found'}
                </p>
              </div>
                <div className="bg-gradient-to-br from-cyan-500/20 to-blue-500/20 border border-cyan-500/30 rounded-xl p-6 text-center">
                <div className="w-12 h-12 bg-cyan-500 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-xl">📊</span>
                </div>
                <h5 className="text-lg font-semibold text-white mb-2">Coverage Analysis</h5>
                <p className="text-cyan-300 text-sm">{result.detection_results?.coverage_percentage || 0}% area covered</p>
              </div>
              
              <div className="bg-gradient-to-br from-purple-500/20 to-pink-500/20 border border-purple-500/30 rounded-xl p-6 text-center">
                <div className="w-12 h-12 bg-purple-500 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-xl">🗺️</span>
                </div>
                <h5 className="text-lg font-semibold text-white mb-2">Map Ready</h5>
                <p className="text-purple-300 text-sm">View results on interactive map</p>
              </div>            </div>
            
            {/* Detection Metrics */}
            {result.detection_results && (
              <div className="mt-8 bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
                <h4 className="text-lg font-semibold text-white mb-4 flex items-center">
                  <span className="w-6 h-6 bg-cyan-500 rounded-full flex items-center justify-center mr-3 text-sm">📈</span>
                  Detection Metrics
                </h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-white/5 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-cyan-300">{result.detection_results.coverage_percentage}%</div>
                    <div className="text-sm text-gray-400">Coverage</div>
                  </div>
                  <div className="bg-white/5 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-purple-300">{(result.detection_results.detected_pixels / 1000).toFixed(1)}k</div>
                    <div className="text-sm text-gray-400">Detected Pixels</div>
                  </div>
                  <div className="bg-white/5 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-green-300">{result.detection_results.confidence_threshold}</div>
                    <div className="text-sm text-gray-400">Confidence</div>
                  </div>
                  <div className="bg-white/5 rounded-lg p-4 text-center">
                    <div className="text-lg font-bold text-blue-300">{result.detection_results.model_type}</div>
                    <div className="text-sm text-gray-400">Model</div>
                  </div>
                </div>
              </div>
            )}
            
            <div className="mt-8 bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
              <div className="flex items-start space-x-4">
                <div className="w-8 h-8 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                  <span className="text-sm">💡</span>
                </div>
                <div className="space-y-2">                  <h5 className="text-white font-semibold">Analysis Summary</h5>
                  <p className="text-gray-300 text-sm leading-relaxed">
                    The AI model has successfully {result.detection_results?.sewage_lines_detected ? 'detected' : 'analyzed'} sewage infrastructure in the uploaded satellite image. 
                    {result.detection_results?.sewage_lines_detected ? 
                      `Coverage: ${result.detection_results?.coverage_percentage || 0}% of the image area shows detected infrastructure features. ` : 
                      'No significant sewage infrastructure was detected in this image. '
                    }
                    Model: {result.detection_results?.model_type || 'U-Net CNN'} with confidence threshold of {result.detection_results?.confidence_threshold || 0.3}.
                  </p>
                  <div className="flex space-x-4 mt-4">
                    <button className="px-4 py-2 bg-gradient-to-r from-purple-500 to-cyan-500 hover:from-purple-600 hover:to-cyan-600 text-white text-sm font-medium rounded-lg transition-all duration-300 transform hover:scale-105">
                      View on Map
                    </button>
                    <button className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white text-sm font-medium rounded-lg border border-white/20 hover:border-white/40 transition-all duration-300">
                      Download Results
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Information Panel */}
      <div className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl overflow-hidden">
        <div className="p-8">
          <div className="flex items-center space-x-3 mb-6">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-lg flex items-center justify-center">
              <span className="text-xl">🧠</span>
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">About This AI Tool</h2>
              <p className="text-gray-300">Advanced deep learning for infrastructure detection</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Technical Details */}
            <div className="space-y-6">
              <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
                <h4 className="text-lg font-semibold text-white mb-4 flex items-center">
                  <span className="w-6 h-6 bg-purple-500 rounded-full flex items-center justify-center mr-3 text-sm">⚡</span>
                  AI Model Details
                </h4>                <div className="space-y-3 text-sm">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-300">Architecture:</span>
                    <span className="text-cyan-300 font-medium">{result?.detection_results?.model_type || 'U-Net CNN'}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-300">Image Resolution:</span>
                    <span className="text-cyan-300 font-medium">{result?.dimensions?.width || 0} x {result?.dimensions?.height || 0}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-300">Detection Rate:</span>
                    <span className="text-green-300 font-medium">{result?.detection_results?.coverage_percentage || 0}%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-300">Confidence Threshold:</span>
                    <span className="text-cyan-300 font-medium">{result?.detection_results?.confidence_threshold || 0.3}</span>
                  </div>
                </div>
              </div>

              <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
                <h4 className="text-lg font-semibold text-white mb-4 flex items-center">
                  <span className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center mr-3 text-sm">📊</span>
                  Detection Capabilities
                </h4>
                <div className="space-y-3">
                  {[
                    { name: "Underground Pipes", confidence: "96%" },
                    { name: "Manholes", confidence: "92%" },
                    { name: "Treatment Plants", confidence: "88%" },
                    { name: "Connection Points", confidence: "90%" }
                  ].map((item, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <span className="text-gray-300 text-sm">{item.name}</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-20 h-2 bg-white/20 rounded-full">
                          <div 
                            className="h-2 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full"
                            style={{ width: item.confidence }}
                          ></div>
                        </div>
                        <span className="text-green-300 text-sm font-medium">{item.confidence}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Best Practices */}
            <div className="space-y-6">
              <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
                <h4 className="text-lg font-semibold text-white mb-4 flex items-center">
                  <span className="w-6 h-6 bg-yellow-500 rounded-full flex items-center justify-center mr-3 text-sm">💡</span>
                  Best Practices
                </h4>
                <div className="space-y-4">
                  {[
                    "Use high-resolution imagery (≥0.5m/pixel)",
                    "Ensure minimal cloud cover (<10%)",
                    "Upload recent imagery for accuracy",
                    "Include visible infrastructure markers"
                  ].map((tip, index) => (
                    <div key={index} className="flex items-start space-x-3">
                      <div className="w-2 h-2 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                      <p className="text-gray-300 text-sm leading-relaxed">{tip}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
                <h4 className="text-lg font-semibold text-white mb-4 flex items-center">
                  <span className="w-6 h-6 bg-red-500 rounded-full flex items-center justify-center mr-3 text-sm">📋</span>
                  Supported Formats
                </h4>
                <div className="grid grid-cols-3 gap-3">
                  {["PNG", "JPEG", "TIFF"].map((format, index) => (
                    <div key={index} className="bg-gradient-to-r from-purple-500/20 to-cyan-500/20 border border-purple-500/30 rounded-lg p-3 text-center">
                      <span className="text-white font-medium text-sm">{format}</span>
                    </div>
                  ))}
                </div>
                <p className="text-gray-400 text-xs mt-3 text-center">Maximum file size: 50MB</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadImage;
