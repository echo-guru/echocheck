# EchoCheck Suite – PRD v1.0

Author: Tony Forshaw  
Date: 2025-10-26  
Frontend: React (port 8000)  
Backend: Node.js (port 8080)  
Helper Modules: Python (`win32com.client`, `python-docx`, `docx2pdf`)  
Target Platform: Windows (Word automation required)

---

## 🎯 Goal

A browser-based QA tool for echocardiography reports that:

1. Accepts `.rtf` report uploads  
2. Runs consistency checks on Ejection Fraction (EF) across:
   - Conclusion section
   - First mention in body
   - Calculations table
3. Displays pass/fail status with parsed EF values
4. If valid, allows PDF generation with:
   - Letterhead
   - Physician signature

---

## ⚙️ Tech Stack

| Layer         | Technology                         |
|---------------|-------------------------------------|
| Frontend      | React + Tailwind CSS (port 8000)    |
| Backend       | Node.js + Express (port 8080)       |
| File Upload   | `multer` (via backend)              |
| Word Parsing  | Python `win32com.client` (Windows only) |
| PDF Export    | Python `docx2pdf` or Word SaveAs    |

---

## 🧩 Features

### 1. File Upload
- Drag-and-drop or browse to upload
- Accepts `.rtf` only
- No processing triggered on upload

### 2. Run EF Consistency Check
- Button: `Run EF Consistency Check`
- Triggers backend `/check-file` API
- Python parses RTF (via Word automation) and extracts:
  - EF from Conclusion
  - First EF in text body
  - EF (%) in Calculations table
- Returns status + extracted values:

```json
{
  "status": "good",
  "values": {
    "conclusion": "55%",
    "text": "55%",
       "calcs": "55%"
  }
}
```

### 3. Show Results
- Color-coded status:
  - ✅ Good (Green)
  - ❌ Discordant (Red)
- Always show all 3 extracted values

### 4. Post-Check Actions
- Visible only after consistency check completes:
  - Close Report
  - Save Changes (placeholder)
  - Generate PDF (only if EF is consistent)

### 5. Generate PDF
- Button triggers /generate-pdf
- Backend pipeline:
  - Upload RTF → Convert RTF→DOCX via win32com.client
  - Insert letterhead + signature (python-docx/docxtpl)
  - Export final PDF (docx2pdf or Word)
  - Return PDF download to frontend
- Output PDF includes:
  - Header/footer from DOCX template
  - Signature image inserted
  - Optional page number, date/time

---

## 📁 Project Structure

```
echocheck/
├── client/                      # React frontend (port 8000)
│   └── src/components/
│       ├── FileUploader.jsx
│       ├── VerifyButton.jsx
│       ├── ResultDisplay.jsx
│       └── ActionButtons.jsx
├── server/                      # Node.js backend (port 8080)
│   ├── routes/
│   ├── controllers/
│   └── utils/
├── python/                      # Word automation + PDF
│   ├── convert_rtf_to_docx.py
│   └── generate_pdf.py
├── assets/                      # Signature image, letterhead DOCX
├── .env                         # PORT=8080
└── README.md
```

---

## 🔌 Ports Used

| Component | Port |
|-----------|------|
| React frontend | 8000 |
| Node backend | 8080 |

No conflict with ports 5163 or 3100 ✅

---

## 🐍 Python Modules

### convert_rtf_to_docx.py
```python
import win32com.client
import os

def convert_rtf_to_docx(rtf_path, output_path=None):
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    doc = word.Documents.Open(rtf_path)
    if not output_path:
        output_path = os.path.splitext(rtf_path)[0] + ".docx"
    doc.SaveAs2(output_path, FileFormat=16)  # 16 = .docx
    doc.Close()
    word.Quit()
    return output_path
```

### generate_pdf.py
- Uses python-docx, docxtpl, or docx2pdf
- Applies template and signature
- Returns path to generated PDF

---

## 🧪 Testing Matrix

| Scenario | Result |
|----------|--------|
| EF matches in all 3 | ✅ Good → Allow PDF generation |
| EF mismatch (e.g. 55/55/60) | ❌ Discordant → Block PDF |
| Missing EF field | ❌ Incomplete → Show error |
| Invalid file type | ❌ Reject upload |
| RTF parsing error | ❌ Log + return error message |

---

## 🔒 Environment Notes

- Must be run on Windows machine with:
  - MS Word installed
  - Python 3.11+
  - Node.js LTS
- Required Python packages:
  - pywin32
  - docx2pdf
  - python-docx or docxtpl

---

## 🚧 Future Features

- Batch folder scanning
- Additional report validations (MR, LA size, aorta)
- Save/Resume functionality
- Digital signing (DocuSign/X.509)
- PACS or EMR integration

---

## 👨‍⚕️ Author

Tony Forshaw  
Echo Guru Pty Ltd
