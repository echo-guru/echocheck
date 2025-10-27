const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const multer = require('multer');
const path = require('path');
const fs = require('fs-extra');
const { spawn } = require('child_process');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 8080;

// Middleware
app.use(helmet());
app.use(cors());
app.use(morgan('combined'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Create uploads directory
const uploadsDir = path.join(__dirname, 'uploads');
fs.ensureDirSync(uploadsDir);

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadsDir);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({
  storage: storage,
  fileFilter: (req, file, cb) => {
    // Only allow RTF files
    if (file.mimetype === 'application/rtf' || path.extname(file.originalname).toLowerCase() === '.rtf') {
      cb(null, true);
    } else {
      cb(new Error('Only RTF files are allowed'), false);
    }
  },
  limits: {
    fileSize: 10 * 1024 * 1024 // 10MB limit
  }
});

// Routes
app.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// File upload endpoint
app.post('/upload', upload.single('rtfFile'), (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    res.json({
      success: true,
      message: 'File uploaded successfully',
      filename: req.file.filename,
      originalName: req.file.originalname,
      size: req.file.size
    });
  } catch (error) {
    console.error('Upload error:', error);
    res.status(500).json({ error: 'File upload failed' });
  }
});

// EF consistency check endpoint
app.post('/check-file', async (req, res) => {
  try {
    const { filename } = req.body;
    
    if (!filename) {
      return res.status(400).json({ error: 'Filename is required' });
    }

    const filePath = path.join(uploadsDir, filename);
    
    if (!await fs.pathExists(filePath)) {
      return res.status(404).json({ error: 'File not found' });
    }

    // Run Python script to extract text and check EF
    const pythonScript = path.join(__dirname, '..', 'python', 'ef_checker.py');
    const pythonProcess = spawn('python', [pythonScript, filePath]);

    let output = '';
    let errorOutput = '';

    pythonProcess.stdout.on('data', (data) => {
      output += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });

    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        console.error('Python script error:', errorOutput);
        return res.status(500).json({ 
          error: 'EF check failed', 
          details: errorOutput 
        });
      }

      try {
        // Parse the JSON output from Python script
        const result = JSON.parse(output.trim());
        res.json(result);
      } catch (parseError) {
        console.error('JSON parse error:', parseError);
        res.status(500).json({ 
          error: 'Failed to parse EF check results',
          details: output
        });
      }
    });

  } catch (error) {
    console.error('EF check error:', error);
    res.status(500).json({ error: 'EF check failed' });
  }
});

// Generate PDF endpoint
app.post('/generate-pdf', async (req, res) => {
  try {
    const { filename } = req.body;
    
    if (!filename) {
      return res.status(400).json({ error: 'Filename is required' });
    }

    const rtfPath = path.join(uploadsDir, filename);
    
    if (!await fs.pathExists(rtfPath)) {
      return res.status(404).json({ error: 'File not found' });
    }

    // Convert RTF to DOCX first
    const convertScript = path.join(__dirname, '..', 'python', 'convert_rtf_to_docx.py');
    const docxPath = rtfPath.replace('.rtf', '.docx');
    
    const convertProcess = spawn('python', [convertScript, rtfPath, docxPath]);
    
    convertProcess.on('close', async (code) => {
      if (code !== 0) {
        return res.status(500).json({ error: 'RTF to DOCX conversion failed' });
      }

      // Generate PDF from DOCX
      const pdfScript = path.join(__dirname, '..', 'python', 'generate_pdf.py');
      const pdfPath = docxPath.replace('.docx', '.pdf');
      
      const pdfProcess = spawn('python', [pdfScript, docxPath, pdfPath]);
      
      pdfProcess.on('close', async (pdfCode) => {
        if (pdfCode !== 0) {
          return res.status(500).json({ error: 'PDF generation failed' });
        }

        // Check if PDF was created
        if (await fs.pathExists(pdfPath)) {
          // Send PDF file
          res.download(pdfPath, path.basename(pdfPath), (err) => {
            if (err) {
              console.error('PDF download error:', err);
            }
            // Clean up temporary files
            fs.remove(docxPath).catch(console.error);
            fs.remove(pdfPath).catch(console.error);
          });
        } else {
          res.status(500).json({ error: 'PDF file was not created' });
        }
      });
    });

  } catch (error) {
    console.error('PDF generation error:', error);
    res.status(500).json({ error: 'PDF generation failed' });
  }
});

// Clean up old files endpoint
app.post('/cleanup', async (req, res) => {
  try {
    const { filename } = req.body;
    
    if (!filename) {
      return res.status(400).json({ error: 'Filename is required' });
    }

    const filePath = path.join(uploadsDir, filename);
    
    if (await fs.pathExists(filePath)) {
      await fs.remove(filePath);
      res.json({ success: true, message: 'File cleaned up successfully' });
    } else {
      res.status(404).json({ error: 'File not found' });
    }
  } catch (error) {
    console.error('Cleanup error:', error);
    res.status(500).json({ error: 'Cleanup failed' });
  }
});

// Error handling middleware
app.use((error, req, res, next) => {
  if (error instanceof multer.MulterError) {
    if (error.code === 'LIMIT_FILE_SIZE') {
      return res.status(400).json({ error: 'File too large' });
    }
  }
  
  console.error('Server error:', error);
  res.status(500).json({ error: 'Internal server error' });
});

// Start server
app.listen(PORT, () => {
  console.log(`EchoCheck Server running on port ${PORT}`);
  console.log(`Health check: http://localhost:${PORT}/health`);
});
