"""
Extract and validate Ejection Fraction (EF) values from echocardiography reports.
Checks consistency across conclusion, text body, and calculations table.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EFChecker:
    """Class to extract and validate EF values from echocardiography reports."""
    
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
    
    def extract_ef_values(self, text: str, rtf_path: str = None) -> Dict[str, Optional[str]]:
        """
        Extract EF values from different sections of the report.
        
        Args:
            text (str): Full text of the echocardiography report
            rtf_path (str): Optional path to RTF file for direct conclusion extraction
            
        Returns:
            Dict containing EF values from conclusion, text, and calculations
        """
        result = {
            'conclusion': None,
            'text': None,
            'calcs': None
        }
        
        try:
            # Convert to lowercase for pattern matching
            text_lower = text.lower()
            
            # Extract EF from conclusion section using direct extraction if RTF path is available
            if rtf_path:
                conclusion_text = self._extract_conclusion_section_direct(rtf_path)
                if conclusion_text:
                    conclusion_lower = conclusion_text.lower()
                    result['conclusion'] = self._extract_first_ef(conclusion_lower)
                else:
                    # Fallback to regular section extraction
                    result['conclusion'] = self._extract_from_section(
                        text, text_lower, self.conclusion_keywords, 'conclusion'
                    )
            else:
                # Use regular section extraction
                result['conclusion'] = self._extract_from_section(
                    text, text_lower, self.conclusion_keywords, 'conclusion'
                )
            
            # Extract first EF mention in text body
            result['text'] = self._extract_first_ef(text_lower)
            
            # Extract EF from calculations table
            result['calcs'] = self._extract_from_section(
                text, text_lower, self.calc_keywords, 'calculations'
            )
            
            logger.info(f"Extracted EF values: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting EF values: {str(e)}")
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
                logger.warning(f"No {section_name} section found")
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
            
            logger.warning(f"No EF value found in {section_name} section")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting from {section_name}: {str(e)}")
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
            
            logger.warning("No EF value found in text body")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting first EF: {str(e)}")
            return None
    
    def _extract_conclusion_section_direct(self, rtf_path: str) -> str:
        """Extract conclusion section directly from RTF using pattern matching."""
        try:
            with open(rtf_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
            
            # Look for the conclusion section using the pattern we found
            # Pattern: CONCLUSIONS: followed by content until the next major section
            conclusion_pattern = r'CONCLUSIONS?:\s*.*?(?=\\pard|\Z)'
            
            match = re.search(conclusion_pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                conclusion_text = match.group(0)
                
                # Clean up the conclusion text
                # Convert \par to newlines
                conclusion_text = re.sub(r'\\par\s*', '\n', conclusion_text)
                
                # Convert \tab to spaces
                conclusion_text = re.sub(r'\\tab\s*', ' ', conclusion_text)
                
                # Remove RTF control words
                conclusion_text = re.sub(r'\\[a-z]+\d*\s*', ' ', conclusion_text)
                conclusion_text = re.sub(r'\\[^a-zA-Z\s{}]', '', conclusion_text)
                
                # Remove groups and braces
                conclusion_text = re.sub(r'\{[^}]*\}', '', conclusion_text)
                conclusion_text = re.sub(r'[{}]', '', conclusion_text)
                
                # Clean up whitespace
                conclusion_text = re.sub(r'[ \t]+', ' ', conclusion_text)
                conclusion_text = re.sub(r'\n\s*\n', '\n', conclusion_text)
                conclusion_text = conclusion_text.strip()
                
                return conclusion_text
            
            return ""
        except Exception as e:
            logger.error(f"Error extracting conclusion section: {str(e)}")
            return ""
    
    def _is_valid_ef(self, value: str) -> bool:
        """Validate if the extracted value is a reasonable EF percentage."""
        try:
            ef_num = float(value)
            # EF should be between 10% and 90% (reasonable range)
            return 10 <= ef_num <= 90
        except (ValueError, TypeError):
            return False
    
    def check_consistency(self, ef_values: Dict[str, Optional[str]]) -> Dict[str, any]:
        """
        Check consistency of EF values across different sections.
        
        Args:
            ef_values (Dict): EF values from different sections
            
        Returns:
            Dict containing status and validation results
        """
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
            logger.error(f"Error checking consistency: {str(e)}")
            return {
                'status': 'error',
                'message': f'Error during consistency check: {str(e)}',
                'values': ef_values
            }

def main():
    """Test function for EF checker."""
    checker = EFChecker()
    
    # Sample text for testing
    sample_text = """
    ECHOCARDIOGRAPHY REPORT
    
    Patient: John Doe
    Date: 2025-10-26
    
    FINDINGS:
    The left ventricular ejection fraction is 55%.
    The patient shows normal systolic function.
    
    CALCULATIONS:
    LVEF: 55%
    LVEDV: 120 ml
    LVESV: 54 ml
    
    CONCLUSION:
    Normal left ventricular function with ejection fraction of 55%.
    No significant valvular abnormalities.
    """
    
    ef_values = checker.extract_ef_values(sample_text)
    result = checker.check_consistency(ef_values)
    
    print("EF Values:", ef_values)
    print("Consistency Check:", result)

if __name__ == "__main__":
    main()
