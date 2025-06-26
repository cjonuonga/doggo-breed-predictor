import React, { useState, useRef } from "react";

const DogBreedPredictor = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [apiStatus, setApiStatus] = useState("checking");
  const fileInputRef = useRef(null);

  // Check API status on component mount
  React.useEffect(() => {
    checkApiStatus();
  }, []);

  const checkApiStatus = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/health");
      if (response.ok) {
        setApiStatus("connected");
      } else {
        setApiStatus("disconnected");
      }
    } catch (err) {
      setApiStatus("disconnected");
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setError(null);

      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => setPreview(e.target.result);
      reader.readAsDataURL(file);

      // Clear previous prediction
      setPrediction(null);
    }
  };

  const handleDrop = (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file && file.type.startsWith("image/")) {
      setSelectedFile(file);
      setError(null);

      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => setPreview(e.target.result);
      reader.readAsDataURL(file);

      setPrediction(null);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const predictBreed = async () => {
    if (!selectedFile) {
      setError("Please select an image first");
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setPrediction(data);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || "Failed to predict breed");
      }
    } catch (err) {
      setError("Failed to predict breed. Make sure the API is running.");
    } finally {
      setLoading(false);
    }
  };

  const clearSelection = () => {
    setSelectedFile(null);
    setPreview(null);
    setPrediction(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                🐕 Dog Breed Predictor
              </h1>
              <p className="text-gray-600 mt-1">
                Upload a photo to identify your dog's breed using AI
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <div
                className={`w-3 h-3 rounded-full ${
                  apiStatus === "connected" ? "bg-green-500" : "bg-red-500"
                }`}
              ></div>
              <span className="text-sm text-gray-600">
                API {apiStatus === "connected" ? "Connected" : "Disconnected"}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Upload Section */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">
              Upload Dog Image
            </h2>

            {/* Drag & Drop Area */}
            <div
              className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors cursor-pointer"
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onClick={() => fileInputRef.current?.click()}
            >
              {preview ? (
                <div className="space-y-4">
                  <img
                    src={preview}
                    alt="Preview"
                    className="max-w-full max-h-64 mx-auto rounded-lg shadow-md"
                  />
                  <div className="text-sm text-gray-600">
                    <p className="font-medium">{selectedFile?.name}</p>
                    <p>{(selectedFile?.size / 1024).toFixed(1)} KB</p>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="text-6xl">📷</div>
                  <div>
                    <p className="text-lg font-medium text-gray-700">
                      Drop your dog image here
                    </p>
                    <p className="text-gray-500">or click to browse files</p>
                  </div>
                  <p className="text-sm text-gray-400">
                    Supports JPG, PNG, GIF
                  </p>
                </div>
              )}
            </div>

            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
            />

            {/* Action Buttons */}
            <div className="flex space-x-3 mt-6">
              <button
                onClick={predictBreed}
                disabled={!selectedFile || loading || apiStatus !== "connected"}
                className="flex-1 bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <svg
                      className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      ></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                    Analyzing...
                  </span>
                ) : (
                  "Predict Breed"
                )}
              </button>

              {selectedFile && (
                <button
                  onClick={clearSelection}
                  className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Clear
                </button>
              )}
            </div>

            {/* Error Message */}
            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            )}
          </div>

          {/* Results Section */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">
              Prediction Results
            </h2>

            {prediction ? (
              <div className="space-y-6">
                {/* Main Prediction */}
                <div className="text-center p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border">
                  <div className="text-4xl mb-2">🏆</div>
                  <h3 className="text-2xl font-bold text-gray-800 mb-2">
                    {prediction.prediction.breed}
                  </h3>
                  <div className="text-3xl font-bold text-blue-600">
                    {prediction.prediction.confidence_percentage}%
                  </div>
                  <p className="text-gray-600 text-sm mt-1">Confidence</p>
                </div>

                {/* Top 3 Predictions */}
                <div>
                  <h4 className="font-semibold text-gray-800 mb-3">
                    Top 3 Predictions:
                  </h4>
                  <div className="space-y-2">
                    {prediction.top_3_predictions.map((pred, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                      >
                        <div className="flex items-center space-x-3">
                          <span className="text-lg font-semibold text-gray-500">
                            #{index + 1}
                          </span>
                          <span className="font-medium text-gray-800">
                            {pred.breed}
                          </span>
                        </div>
                        <div className="text-right">
                          <div className="font-semibold text-gray-800">
                            {(pred.confidence * 100).toFixed(1)}%
                          </div>
                          <div className="w-20 bg-gray-200 rounded-full h-2 mt-1">
                            <div
                              className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                              style={{ width: `${pred.confidence * 100}%` }}
                            ></div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Image Info */}
                <div className="border-t pt-4">
                  <h4 className="font-semibold text-gray-800 mb-2">
                    Image Details:
                  </h4>
                  <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                    <div>
                      <span className="font-medium">Dimensions:</span>
                      <br />
                      {prediction.image_info.width} ×{" "}
                      {prediction.image_info.height}px
                    </div>
                    <div>
                      <span className="font-medium">File Size:</span>
                      <br />
                      {prediction.image_info.size_kb} KB
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-12 text-gray-500">
                <div className="text-6xl mb-4">🔍</div>
                <p className="text-lg">
                  Upload an image to see prediction results
                </p>
                <p className="text-sm mt-2">
                  Our AI will identify the dog breed with confidence scores
                </p>
              </div>
            )}
          </div>
        </div>

        {/* API Status Footer */}
        {apiStatus === "disconnected" && (
          <div className="mt-8 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex items-center space-x-2">
              <span className="text-yellow-600">⚠️</span>
              <div>
                <p className="font-medium text-yellow-800">
                  API Connection Issue
                </p>
                <p className="text-yellow-700 text-sm">
                  Make sure your FastAPI server is running:{" "}
                  <code className="bg-yellow-100 px-2 py-1 rounded">
                    uvicorn main:app --reload
                  </code>
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DogBreedPredictor;
