import React, { useState } from 'react';
import FileUploader from './components/FileUploader';
import VerifyButton from './components/VerifyButton';
import ResultDisplay from './components/ResultDisplay';
import ActionButtons from './components/ActionButtons';
import './index.css';

function App() {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [efResults, setEfResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileUpload = (file) => {
    setUploadedFile(file);
    setEfResults(null);
    setError(null);
  };

  const handleEfCheck = (results) => {
    setEfResults(results);
    setError(null);
  };

  const handleError = (errorMessage) => {
    setError(errorMessage);
    setEfResults(null);
  };

  const handleCloseReport = () => {
    setUploadedFile(null);
    setEfResults(null);
    setError(null);
  };

  const handleSaveChanges = () => {
    // Placeholder for save functionality
    alert('Save functionality will be implemented in future version');
  };

  const handleGeneratePdf = () => {
    // This will be handled by ActionButtons component
    console.log('Generate PDF requested');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            EchoCheck Suite
          </h1>
          <p className="text-lg text-gray-600">
            Echocardiography Report QA Tool
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Upload RTF reports • Check EF consistency • Generate PDFs
          </p>
        </div>

        {/* Main Content */}
        <div className="max-w-4xl mx-auto">
          {!uploadedFile ? (
            <FileUploader onFileUpload={handleFileUpload} onError={handleError} />
          ) : (
            <div className="space-y-6">
              {/* File Info */}
              <div className="medical-card">
                <h2 className="text-xl font-semibold text-gray-800 mb-4">
                  Uploaded File
                </h2>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">
                      <span className="font-medium">File:</span> {uploadedFile.originalName}
                    </p>
                    <p className="text-sm text-gray-600">
                      <span className="font-medium">Size:</span> {(uploadedFile.size / 1024).toFixed(1)} KB
                    </p>
                  </div>
                  <button
                    onClick={handleCloseReport}
                    className="medical-button medical-button-secondary text-sm"
                  >
                    Close Report
                  </button>
                </div>
              </div>

              {/* Verification Section */}
              <div className="medical-card">
                <h2 className="text-xl font-semibold text-gray-800 mb-4">
                  EF Consistency Check
                </h2>
                <VerifyButton
                  filename={uploadedFile.filename}
                  onEfCheck={handleEfCheck}
                  onError={handleError}
                  isLoading={isLoading}
                  setIsLoading={setIsLoading}
                />
              </div>

              {/* Results Display */}
              {efResults && (
                <ResultDisplay results={efResults} />
              )}

              {/* Error Display */}
              {error && (
                <div className="medical-card status-error border-2">
                  <h3 className="text-lg font-semibold mb-2">Error</h3>
                  <p className="text-sm">{error}</p>
                </div>
              )}

              {/* Action Buttons */}
              {efResults && (
                <ActionButtons
                  results={efResults}
                  filename={uploadedFile.filename}
                  onSaveChanges={handleSaveChanges}
                  onGeneratePdf={handleGeneratePdf}
                />
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="text-center mt-12 text-sm text-gray-500">
          <p>EchoCheck Suite v1.0 • Tony Forshaw • Echo Guru Pty Ltd</p>
        </div>
      </div>
    </div>
  );
}

export default App;
