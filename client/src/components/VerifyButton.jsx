import React from 'react';
import axios from 'axios';

const VerifyButton = ({ filename, onEfCheck, onError, isLoading, setIsLoading }) => {
  const handleVerify = async () => {
    if (!filename) {
      onError('No file to verify');
      return;
    }

    setIsLoading(true);
    
    try {
      const response = await axios.post('/check-file', {
        filename: filename
      });

      if (response.data) {
        onEfCheck(response.data);
      } else {
        onError('No results received from server');
      }
    } catch (error) {
      console.error('Verification error:', error);
      if (error.response?.data?.error) {
        onError('Verification failed: ' + error.response.data.error);
      } else {
        onError('Verification failed: ' + error.message);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <p className="text-sm text-gray-600">
        Click the button below to run the EF consistency check on your uploaded report.
        The system will extract and compare Ejection Fraction values from:
      </p>
      
      <ul className="text-sm text-gray-600 list-disc list-inside ml-4 space-y-1">
        <li>Conclusion section</li>
        <li>First mention in text body</li>
        <li>Calculations table</li>
      </ul>

      <div className="pt-4">
        <button
          onClick={handleVerify}
          disabled={isLoading}
          className={`medical-button medical-button-primary ${
            isLoading ? 'opacity-50 cursor-not-allowed' : ''
          }`}
        >
          {isLoading ? (
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>Running EF Check...</span>
            </div>
          ) : (
            'Run EF Consistency Check'
          )}
        </button>
      </div>

      {isLoading && (
        <div className="text-sm text-gray-500">
          <p>Processing your report...</p>
          <p className="text-xs mt-1">
            This may take a few moments as we extract and analyze the EF values.
          </p>
        </div>
      )}
    </div>
  );
};

export default VerifyButton;
