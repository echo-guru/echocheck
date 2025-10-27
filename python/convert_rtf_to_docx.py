"""
Convert RTF files to DOCX format using Microsoft Word automation.
Requires Windows with MS Word installed.
"""

import win32com.client
import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_rtf_to_docx(rtf_path, output_path=None):
    """
    Convert RTF file to DOCX format using Word automation.
    
    Args:
        rtf_path (str): Path to the input RTF file
        output_path (str, optional): Path for the output DOCX file
        
    Returns:
        str: Path to the converted DOCX file
        
    Raises:
        Exception: If conversion fails
    """
    try:
        # Validate input file
        if not os.path.exists(rtf_path):
            raise FileNotFoundError(f"RTF file not found: {rtf_path}")
        
        if not rtf_path.lower().endswith('.rtf'):
            raise ValueError("Input file must be an RTF file")
        
        # Set output path if not provided
        if not output_path:
            output_path = os.path.splitext(rtf_path)[0] + ".docx"
        
        logger.info(f"Converting {rtf_path} to {output_path}")
        
        # Initialize Word application
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        
        try:
            # Open the RTF document
            doc = word.Documents.Open(os.path.abspath(rtf_path))
            
            # Save as DOCX (FileFormat=16)
            doc.SaveAs2(os.path.abspath(output_path), FileFormat=16)
            
            # Close the document
            doc.Close()
            
            logger.info(f"Successfully converted to {output_path}")
            return output_path
            
        finally:
            # Quit Word application
            word.Quit()
            
    except Exception as e:
        logger.error(f"Error converting RTF to DOCX: {str(e)}")
        raise

def extract_text_from_rtf(rtf_path):
    """
    Extract plain text from RTF file for EF analysis.
    
    Args:
        rtf_path (str): Path to the RTF file
        
    Returns:
        str: Extracted plain text
    """
    try:
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        
        try:
            doc = word.Documents.Open(os.path.abspath(rtf_path))
            text = doc.Content.Text
            doc.Close()
            return text
        finally:
            word.Quit()
            
    except Exception as e:
        logger.error(f"Error extracting text from RTF: {str(e)}")
        raise

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_rtf_to_docx.py <rtf_file_path> [output_path]")
        sys.exit(1)
    
    rtf_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        result = convert_rtf_to_docx(rtf_file, output_file)
        print(f"Conversion successful: {result}")
    except Exception as e:
        print(f"Conversion failed: {e}")
        sys.exit(1)
