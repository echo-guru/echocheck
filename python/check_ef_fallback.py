"""
Fallback EF checker that works without Word automation.
Uses regex patterns to extract EF values directly from RTF text.
"""

import sys
import json
import re
from typing import Dict, Optional, List

class EFFallbackChecker:
    """Fallback EF checker that doesn't require Word automation."""
    
    def __init__(self):
        # Regex patterns for EF extraction
        self.ef_patterns = [
            r'ejection\s+fraction[:\s]*(\d+(?:\.\d+)?)\s*%?',  # "ejection fraction: 55%"
            r'ef[:\s]*(\d+(?:\.\d+)?)\s*%?',  # "ef: 55%"
            r'(\d+(?:\.\d+)?)\s*%\s*ef',  # "55% ef"
            r'(\d+(?:\.\d+)?)\s*%\s*ejection',  # "55% ejection"
            r'lvef[:\s]*(\d+(?:\.\d+)?)\s*%?',  # "lvef: 55%"
        ]
        
        # Keywords to identify conclusion section
        self.conclusion_keywords = [
            'conclusion', 'summary', 'impression', 'final', 'overall',
            'assessment', 'diagnosis', 'findings'
        ]
        
        # Keywords to identify calculations table
        self.calc_keywords = [
            'calculation', 'measurement', 'values', 'parameters',
            'quantitative', 'measurements', 'data'
        ]
    
    def extract_text_from_rtf(self, rtf_path: str) -> str:
        """Extract plain text from RTF file using regex."""
        try:
            with open(rtf_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
            
            # Remove RTF formatting codes
            text = re.sub(r'\\[a-z]+\d*\s?', '', content)  # Remove RTF commands
            text = re.sub(r'[{}]', '', text)  # Remove braces
            text = re.sub(r'\\par\s*', '\n', text)  # Convert \par to newlines
            text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
            text = re.sub(r'\n\s*\n', '\n', text)  # Remove empty lines
            
            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading RTF file: {str(e)}")
    
    def extract_ef_values(self, text: str) -> Dict[str, Optional[str]]:
        """Extract EF values from different sections of the report."""
        result = {
            'conclusion': None,
            'text': None,
            'calcs': None
        }
        
        try:
            # Convert to lowercase for pattern matching
            text_lower = text.lower()
            
            # Extract EF from conclusion section
            result['conclusion'] = self._extract_from_section(
                text, text_lower, self.conclusion_keywords, 'conclusion'
            )
            
            # Extract first EF mention in text body
            result['text'] = self._extract_first_ef(text_lower)
            
            # Extract EF from calculations table
            result['calcs'] = self._extract_from_section(
                text, text_lower, self.calc_keywords, 'calculations'
            )
            
            return result
            
        except Exception as e:
            print(f"Error extracting EF values: {str(e)}")
            return result
    
    def _extract_from_section(self, text: str, text_lower: str, 
                            keywords: List[str], section_name: str) -> Optional[str]:
        """Extract EF value from a specific section."""
        try:
            # Find section containing keywords
            section_start = -1
            for keyword in keywords:
                pos = text_lower.find(keyword)
                if pos != -1:
                    section_start = pos
                    break
            
            if section_start == -1:
                return None
            
            # Extract text around the keyword (500 chars before and after)
            start = max(0, section_start - 500)
            end = min(len(text), section_start + 500)
            section_text = text_lower[start:end]
            
            # Search for EF patterns in this section
            for pattern in self.ef_patterns:
                matches = re.findall(pattern, section_text, re.IGNORECASE)
                if matches:
                    # Return the first valid EF value found
                    ef_value = matches[0]
                    if self._is_valid_ef(ef_value):
                        return f"{ef_value}%"
            
            return None
            
        except Exception as e:
            print(f"Error extracting from {section_name}: {str(e)}")
            return None
    
    def _extract_first_ef(self, text_lower: str) -> Optional[str]:
        """Extract the first EF value mentioned in the text."""
        try:
            for pattern in self.ef_patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                if matches:
                    ef_value = matches[0]
                    if self._is_valid_ef(ef_value):
                        return f"{ef_value}%"
            
            return None
            
        except Exception as e:
            print(f"Error extracting first EF: {str(e)}")
            return None
    
    def _is_valid_ef(self, value: str) -> bool:
        """Validate if the extracted value is a reasonable EF percentage."""
        try:
            ef_num = float(value)
            # EF should be between 10% and 90% (reasonable range)
            return 10 <= ef_num <= 90
        except (ValueError, TypeError):
            return False
    
    def check_consistency(self, ef_values: Dict[str, Optional[str]]) -> Dict[str, any]:
        """Check consistency of EF values across different sections."""
        try:
            # Filter out None values and extract numeric values
            valid_values = {}
            for section, value in ef_values.items():
                if value and value != 'None':
                    try:
                        # Extract numeric value from "55%" format
                        numeric_value = float(value.replace('%', ''))
                        valid_values[section] = numeric_value
                    except (ValueError, AttributeError):
                        continue
            
            if not valid_values:
                return {
                    'status': 'error',
                    'message': 'No valid EF values found',
                    'values': ef_values
                }
            
            # Check if all values are the same
            unique_values = set(valid_values.values())
            
            if len(unique_values) == 1:
                return {
                    'status': 'good',
                    'message': 'All EF values are consistent',
                    'values': ef_values,
                    'numeric_values': valid_values
                }
            else:
                return {
                    'status': 'discordant',
                    'message': f'EF values are inconsistent: {dict(valid_values)}',
                    'values': ef_values,
                    'numeric_values': valid_values
                }
                
        except Exception as e:
            print(f"Error checking consistency: {str(e)}")
            return {
                'status': 'error',
                'message': f'Error during consistency check: {str(e)}',
                'values': ef_values
            }

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
        # Use fallback checker
        checker = EFFallbackChecker()
        text = checker.extract_text_from_rtf(rtf_path)
        ef_values = checker.extract_ef_values(text)
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
