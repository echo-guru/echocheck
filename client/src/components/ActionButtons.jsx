import React, { useState } from 'react';
import axios from 'axios';

const ActionButtons = ({ results, filename, onSaveChanges, onGeneratePdf }) => {
  const [isGeneratingPdf, setIsGeneratingPdf] = useState(false);
  const [pdfError, setPdfError] = useState(null);

  const handleGeneratePdf = async () => {
    if (results.status !== 'good') {
      alert('PDF generation is only available when EF values are consistent.');
      return;
    }

    setIsGeneratingPdf(true);
    setPdfError(null);

    try {
      const response = await axios.post('/generate-pdf', {
        filename: filename
      }, {
        responseType: 'blob'
      });

      // Create blob link to download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      // Extract filename from response headers or use default
      const contentDisposition = response.headers['content-disposition'];
      let pdfFilename = 'echocardiography_report.pdf';
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/);
        if (filenameMatch) {
          pdfFilename = filenameMatch[1];
        }
      }
      
      link.setAttribute('download', pdfFilename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

    } catch (error) {
      console.error('PDF generation error:', error);
      if (error.response?.data?.error) {
        setPdfError('PDF generation failed: ' + error.response.data.error);
      } else {
        setPdfError('PDF generation failed: ' + error.message);
      }
    } finally {
      setIsGeneratingPdf(false);
    }
  };

  const handleCleanup = async () => {
    try {
      await axios.post('/cleanup', {
        filename: filename
      });
      // Optionally refresh the page or reset state
      window.location.reload();
    } catch (error) {
      console.error('Cleanup error:', error);
      alert('Failed to clean up files. Please try again.');
    }
  };

  return (
    <div className="medical-card">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">
        Actions
      </h2>
      
      <div className="space-y-4">
        {/* Save Changes Button */}
        <div>
          <button
            onClick={onSaveChanges}
            className="medical-button medical-button-secondary w-full"
          >
            💾 Save Changes
          </button>
          <p className="text-xs text-gray-500 mt-1">
            Save current report state (placeholder functionality)
          </p>
        </div>

        {/* Generate PDF Button */}
        <div>
          <button
            onClick={handleGeneratePdf}
            disabled={results.status !== 'good' || isGeneratingPdf}
            className={`medical-button w-full ${
              results.status === 'good' 
                ? 'medical-button-success' 
                : 'medical-button-secondary opacity-50 cursor-not-allowed'
            }`}
          >
            {isGeneratingPdf ? (
              <div className="flex items-center justify-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Generating PDF...</span>
              </div>
            ) : (
              '📄 Generate PDF'
            )}
          </button>
          
          {results.status === 'good' ? (
            <p className="text-xs text-gray-500 mt-1">
              Generate PDF with letterhead and signature
            </p>
          ) : (
            <p className="text-xs text-red-500 mt-1">
              PDF generation only available when EF values are consistent
            </p>
          )}
        </div>

        {/* PDF Error Display */}
        {pdfError && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800">{pdfError}</p>
            <button
              onClick={() => setPdfError(null)}
              className="text-xs text-red-600 underline mt-1"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Cleanup Button */}
        <div className="pt-4 border-t border-gray-200">
          <button
            onClick={handleCleanup}
            className="medical-button medical-button-danger w-full"
          >
            🗑️ Clean Up Files
          </button>
          <p className="text-xs text-gray-500 mt-1">
            Remove uploaded files from server
          </p>
        </div>
      </div>

      {/* Status Information */}
      <div className="mt-6 p-3 bg-gray-50 rounded-lg">
        <h4 className="font-medium text-sm text-gray-700 mb-2">
          Current Status:
        </h4>
        <div className="text-sm text-gray-600 space-y-1">
          <div>• File: {filename}</div>
          <div>• EF Status: {results.status}</div>
          <div>• PDF Available: {results.status === 'good' ? 'Yes' : 'No'}</div>
        </div>
      </div>
    </div>
  );
};

export default ActionButtons;
