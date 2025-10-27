"""
Main script to check EF consistency from RTF files.
This script is called by the Node.js backend.
"""

import sys
import json
import os
from ef_checker import EFChecker
from convert_rtf_to_docx import extract_text_from_rtf

def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            'status': 'error',
            'message': 'RTF file path is required',
            'values': {}
        }))
        sys.exit(1)
    
    rtf_path = sys.argv[1]
    
    try:
        # Extract text from RTF file
        text = extract_text_from_rtf(rtf_path)
        
        # Check EF consistency
        checker = EFChecker()
        ef_values = checker.extract_ef_values(text, rtf_path)
        result = checker.check_consistency(ef_values)
        
        # Output JSON result
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({
            'status': 'error',
            'message': f'Error processing file: {str(e)}',
            'values': {}
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()
