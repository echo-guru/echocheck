import React from 'react';

const ResultDisplay = ({ results }) => {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'good':
        return '✅';
      case 'discordant':
        return '❌';
      case 'error':
        return '⚠️';
      default:
        return '❓';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'good':
        return 'status-good';
      case 'discordant':
        return 'status-discordant';
      case 'error':
        return 'status-error';
      default:
        return 'status-error';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'good':
        return 'All EF values are consistent';
      case 'discordant':
        return 'EF values are inconsistent';
      case 'error':
        return 'Error during analysis';
      default:
        return 'Unknown status';
    }
  };

  return (
    <div className="medical-card">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">
        EF Consistency Results
      </h2>
      
      <div className={`border-2 rounded-lg p-4 ${getStatusColor(results.status)}`}>
        <div className="flex items-center space-x-3 mb-4">
          <span className="text-2xl">{getStatusIcon(results.status)}</span>
          <div>
            <h3 className="text-lg font-semibold">
              {getStatusText(results.status)}
            </h3>
            {results.message && (
              <p className="text-sm opacity-75 mt-1">
                {results.message}
              </p>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white bg-opacity-50 rounded-lg p-3">
            <h4 className="font-medium text-sm text-gray-700 mb-2">
              Conclusion Section
            </h4>
            <div className="text-lg font-semibold">
              {results.values?.conclusion || 'Not found'}
            </div>
          </div>
          
          <div className="bg-white bg-opacity-50 rounded-lg p-3">
            <h4 className="font-medium text-sm text-gray-700 mb-2">
              Text Body
            </h4>
            <div className="text-lg font-semibold">
              {results.values?.text || 'Not found'}
            </div>
          </div>
          
          <div className="bg-white bg-opacity-50 rounded-lg p-3">
            <h4 className="font-medium text-sm text-gray-700 mb-2">
              Calculations Table
            </h4>
            <div className="text-lg font-semibold">
              {results.values?.calcs || 'Not found'}
            </div>
          </div>
        </div>

        {(results.referred_by || results.patient_name || results.date || results.reporting_dr) && (
          <div className="mt-4 pt-4 border-t border-gray-300">
            <h4 className="font-medium text-sm text-gray-700 mb-2">
              Report Information:
            </h4>
            <div className="text-sm text-gray-600 space-y-1">
              {results.patient_name && (
                <div><span className="font-medium">Patient:</span> {results.patient_name}</div>
              )}
              {results.referred_by && (
                <div><span className="font-medium">Referred By:</span> {results.referred_by}</div>
              )}
              {results.reporting_dr && (
                <div><span className="font-medium">Reported By:</span> {results.reporting_dr}</div>
              )}
              {results.date && (
                <div><span className="font-medium">Date:</span> {results.date}</div>
              )}
            </div>
          </div>
        )}
      </div>

      {results.status === 'good' && (
        <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-sm text-green-800">
            <strong>✓ Ready for PDF Generation:</strong> All EF values are consistent. 
            You can now generate a PDF with letterhead and signature.
          </p>
        </div>
      )}

      {results.status === 'discordant' && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-800">
            <strong>⚠️ PDF Generation Blocked:</strong> EF values are inconsistent. 
            Please review the report and ensure all EF values match before generating a PDF.
          </p>
        </div>
      )}

      {results.status === 'error' && (
        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-sm text-yellow-800">
            <strong>⚠️ Analysis Error:</strong> There was an error processing the report. 
            Please check the file format and try again.
          </p>
        </div>
      )}
    </div>
  );
};

export default ResultDisplay;
