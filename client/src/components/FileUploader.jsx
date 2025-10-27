import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';

const FileUploader = ({ onFileUpload, onError }) => {
  const [isUploading, setIsUploading] = useState(false);

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    
    if (!file) {
      onError('No file selected');
      return;
    }

    // Validate file type
    if (!file.name.toLowerCase().endsWith('.rtf')) {
      onError('Please select an RTF file');
      return;
    }

    // Validate file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      onError('File size must be less than 10MB');
      return;
    }

    setIsUploading(true);
    
    try {
      const formData = new FormData();
      formData.append('rtfFile', file);

      const response = await axios.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        onFileUpload({
          filename: response.data.filename,
          originalName: response.data.originalName,
          size: response.data.size
        });
      } else {
        onError('Upload failed: ' + response.data.message);
      }
    } catch (error) {
      console.error('Upload error:', error);
      if (error.response?.data?.error) {
        onError('Upload failed: ' + error.response.data.error);
      } else {
        onError('Upload failed: ' + error.message);
      }
    } finally {
      setIsUploading(false);
    }
  }, [onFileUpload, onError]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/rtf': ['.rtf']
    },
    multiple: false,
    disabled: isUploading
  });

  return (
    <div className="medical-card">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">
        Upload Echocardiography Report
      </h2>
      
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'drag-active' : ''} ${
          isUploading ? 'opacity-50 cursor-not-allowed' : ''
        }`}
      >
        <input {...getInputProps()} />
        
        {isUploading ? (
          <div className="space-y-4">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-medical-blue mx-auto"></div>
            <p className="text-lg font-medium text-gray-700">Uploading file...</p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="text-6xl text-gray-400">
              📄
            </div>
            <div>
              <p className="text-lg font-medium text-gray-700">
                {isDragActive ? 'Drop the RTF file here' : 'Drag & drop your RTF file here'}
              </p>
              <p className="text-sm text-gray-500 mt-2">
                or click to browse files
              </p>
            </div>
            <div className="text-xs text-gray-400">
              Only RTF files are accepted • Max size: 10MB
            </div>
          </div>
        )}
      </div>

      <div className="mt-4 text-sm text-gray-600">
        <h3 className="font-medium mb-2">Supported file types:</h3>
        <ul className="list-disc list-inside space-y-1">
          <li>RTF (Rich Text Format) files only</li>
          <li>Files exported from echocardiography systems</li>
          <li>Maximum file size: 10MB</li>
        </ul>
      </div>
    </div>
  );
};

export default FileUploader;
