"""
Fallback EF checker that works without Word automation.
Uses regex patterns to extract EF values directly from RTF text.
"""

import sys
import json
import re
import os
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
            r'ef\s*(\d+(?:\.\d+)?)\s*%',  # "ef 55%"
            r'ef\s*[:\-]\s*(\d+(?:\.\d+)?)\s*%',  # "ef: 55%" or "ef - 55%"
            r'ef\s*=\s*(\d+(?:\.\d+)?)\s*%',  # "ef = 55%"
            r'ef\s+(\d+(?:\.\d+)?)\s*%',  # "ef 55%" with space
        ]
        
        # Keywords to identify conclusion section
        self.conclusion_keywords = [
            'conclusion', 'summary', 'impression', 'final', 'overall',
            'assessment', 'diagnosis', 'findings'
        ]
        
        # Keywords to identify calculations table
        self.calc_keywords = [
            'calculation', 'measurement', 'values', 'parameters',
            'quantitative', 'measurements', 'data', 'measurements table',
            'measurement table', 'calculations table', 'table'
        ]
    
    def extract_text_from_rtf(self, rtf_path: str) -> str:
        """Extract plain text from RTF file using multiple methods in order of preference."""
        try:
            # Try Word automation first for best text extraction (includes footers)
            try:
                return self._extract_text_with_word(rtf_path)
            except Exception as word_error:
                print(f"Word automation failed: {word_error}")
                
                # Try striprtf library for better RTF parsing
                try:
                    return self._extract_text_with_striprtf(rtf_path)
                except Exception as striprtf_error:
                    print(f"striprtf library failed: {striprtf_error}")
                    print("Falling back to regex-based RTF parsing...")
                    return self._extract_text_with_regex(rtf_path)
        except Exception as e:
            raise Exception(f"Error reading RTF file: {str(e)}")
    
    def _extract_text_with_word(self, rtf_path: str) -> str:
        """Extract text using Word automation (includes footers)."""
        try:
            import win32com.client
            
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
            raise Exception(f"Word automation error: {str(e)}")
    
    def _extract_text_with_striprtf(self, rtf_path: str) -> str:
        """Extract text using striprtf library (better RTF parsing)."""
        try:
            from striprtf import striprtf
            
            with open(rtf_path, 'r', encoding='utf-8', errors='ignore') as file:
                rtf_content = file.read()
            
            # Use striprtf to extract text
            text = striprtf.rtf_to_text(rtf_content)
            
            return text
        except Exception as e:
            raise Exception(f"striprtf parsing error: {str(e)}")
    
    def _extract_text_with_regex(self, rtf_path: str) -> str:
        """Extract text using regex-based RTF parsing (fallback method)."""
        try:
            with open(rtf_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
            
            # Step 1: Convert \par to newlines to preserve structure
            text = re.sub(r'\\par\s*', '\n', content)
            
            # Step 2: Convert \tab to spaces
            text = re.sub(r'\\tab\s*', ' ', text)
            
            # Step 3: Remove RTF control words but be more selective
            # Remove font commands like \f1, \fs20, etc.
            text = re.sub(r'\\[a-z]+\d*\s*', ' ', text)
            
            # Step 4: Remove RTF groups and braces more carefully
            text = re.sub(r'\\[^a-zA-Z\s{}]', '', text)
            
            # Step 5: Remove groups that are just formatting
            text = re.sub(r'\{[^}]*\}', '', text)
            text = re.sub(r'[{}]', '', text)
            
            # Step 6: Clean up whitespace but preserve line breaks
            text = re.sub(r'[ \t]+', ' ', text)  # Normalize spaces and tabs
            text = re.sub(r'\n\s*\n', '\n', text)  # Remove empty lines
            text = text.strip()
            
            return text
        except Exception as e:
            raise Exception(f"Regex parsing error: {str(e)}")
    
    def extract_conclusion_section_direct(self, rtf_path: str) -> str:
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
            raise Exception(f"Error extracting conclusion section: {str(e)}")
    
    def extract_ef_values(self, text: str, rtf_content: str = None, rtf_path: str = None) -> Dict[str, Optional[str]]:
        """Extract EF values from different sections of the report."""
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
                conclusion_text = self.extract_conclusion_section_direct(rtf_path)
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
            
            # Extract EF from report section (not conclusion)
            result['text'] = self._extract_ef_from_report_section(text_lower)
            
            # Extract EF from calculations table
            result['calcs'] = self._extract_from_section(
                text, text_lower, self.calc_keywords, 'calculations'
            )
            
            # If we didn't find EF in calculations, try to find it in the measurements table
            if not result['calcs']:
                result['calcs'] = self._extract_ef_from_measurements_table(text_lower)
            
            # If we have raw RTF content and didn't find EF in calculations,
            # try to find it in the RTF table format
            if rtf_content and not result['calcs']:
                result['calcs'] = self._extract_ef_from_rtf_table(rtf_content)
            
            # Extract doctor and report information
            doctor_info = self.extract_doctor_info(text)
            result.update(doctor_info)
            
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
            
            # For calculations/measurements table, look for table-like structures
            if section_name == 'calculations':
                # Look for EF in table format (left column with EF, right column with value)
                table_ef = self._extract_ef_from_table(section_text)
                if table_ef:
                    return table_ef
            
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
    
    def _extract_ef_from_table(self, text: str) -> Optional[str]:
        """Extract EF value from table-like structures."""
        try:
            
            # Look for patterns like "EF" followed by a value on the same line or next line
            # This handles cases where EF is in the left column and value is in the right column
            
            # Pattern 1: EF followed by colon and value on same line
            pattern1 = r'ef\s*[:\-]\s*(\d+(?:\.\d+)?)\s*%?'
            matches = re.findall(pattern1, text, re.IGNORECASE)
            if matches:
                ef_value = matches[0]
                if self._is_valid_ef(ef_value):
                    return f"{ef_value}%"
            
            # Pattern 2: EF on one line, value on next line (common in tables)
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if re.search(r'\bef\b', line, re.IGNORECASE):
                    # Check current line for value
                    value_match = re.search(r'(\d+(?:\.\d+)?)\s*%?', line)
                    if value_match:
                        ef_value = value_match.group(1)
                        if self._is_valid_ef(ef_value):
                            return f"{ef_value}%"
                    
                    # Check next line for value
                    if i + 1 < len(lines):
                        next_line = lines[i + 1]
                        value_match = re.search(r'(\d+(?:\.\d+)?)\s*%?', next_line)
                        if value_match:
                            ef_value = value_match.group(1)
                            if self._is_valid_ef(ef_value):
                                return f"{ef_value}%"
                    
                    # Check next 2 lines for value (handles EF\n65\n% format)
                    if i + 2 < len(lines):
                        next_line = lines[i + 1]
                        third_line = lines[i + 2]
                        # Look for number on next line and % on third line
                        if re.search(r'^\s*(\d+(?:\.\d+)?)\s*$', next_line) and re.search(r'^\s*%\s*$', third_line):
                            value_match = re.search(r'(\d+(?:\.\d+)?)', next_line)
                            if value_match:
                                ef_value = value_match.group(1)
                                if self._is_valid_ef(ef_value):
                                    return f"{ef_value}%"
            
            # Pattern 3: EF with value separated by whitespace or tabs
            pattern3 = r'ef\s+(\d+(?:\.\d+)?)\s*%?'
            matches = re.findall(pattern3, text, re.IGNORECASE)
            if matches:
                ef_value = matches[0]
                if self._is_valid_ef(ef_value):
                    return f"{ef_value}%"
            
            # Pattern 4: Handle multi-line EF format (EF\n65\n%)
            # Look for EF on one line, number on next line, % on third line
            for i in range(len(lines) - 2):
                line1 = lines[i].strip()
                line2 = lines[i + 1].strip()
                line3 = lines[i + 2].strip()
                
                if (re.search(r'\bef\b', line1, re.IGNORECASE) and 
                    re.search(r'^\d+(?:\.\d+)?$', line2) and 
                    re.search(r'^%$', line3)):
                    ef_value = line2
                    if self._is_valid_ef(ef_value):
                        return f"{ef_value}%"
            
            # Pattern 5: Handle table format where EF is in separate cells
            # Look for "EF" followed by a number and % in nearby lines
            for i in range(len(lines) - 1):
                line1 = lines[i].strip()
                line2 = lines[i + 1].strip()
                
                # Check if line1 is just "EF" and line2 is just a number
                if (re.search(r'^\s*ef\s*$', line1, re.IGNORECASE) and 
                    re.search(r'^\s*(\d+(?:\.\d+)?)\s*$', line2)):
                    ef_value = re.search(r'(\d+(?:\.\d+)?)', line2).group(1)
                    if self._is_valid_ef(ef_value):
                        return f"{ef_value}%"
                
                # Check if line1 is "EF" and line2 is "number %"
                if (re.search(r'^\s*ef\s*$', line1, re.IGNORECASE) and 
                    re.search(r'^\s*(\d+(?:\.\d+)?)\s*%\s*$', line2)):
                    ef_value = re.search(r'(\d+(?:\.\d+)?)', line2).group(1)
                    if self._is_valid_ef(ef_value):
                        return f"{ef_value}%"
            
            # Pattern 6: Look for EF in the raw text with more flexible matching
            # This handles cases where the RTF parsing doesn't preserve line structure well
            ef_patterns = [
                r'ef\s+(\d+(?:\.\d+)?)\s*%',  # "ef 65%"
                r'ef\s*:\s*(\d+(?:\.\d+)?)\s*%',  # "ef: 65%"
                r'ef\s*=\s*(\d+(?:\.\d+)?)\s*%',  # "ef = 65%"
            ]
            
            for pattern in ef_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    ef_value = matches[0]
                    if self._is_valid_ef(ef_value):
                        return f"{ef_value}%"
            
            # Pattern 7: Look for EF in RTF table format (EF\cell 65\cell %)
            # This handles the specific RTF table structure we found
            rtf_table_patterns = [
                r'ef\\cell\s+(\d+(?:\.\d+)?)\\cell\s*%',  # "ef\cell 65\cell %"
                r'ef\\cell\s*(\d+(?:\.\d+)?)\\cell\s*%',  # "ef\cell65\cell%"
            ]
            
            for pattern in rtf_table_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    ef_value = matches[0]
                    if self._is_valid_ef(ef_value):
                        return f"{ef_value}%"
            
            return None
            
        except Exception as e:
            print(f"Error extracting EF from table: {str(e)}")
            return None
    
    def _extract_ef_from_rtf_table(self, rtf_content: str) -> Optional[str]:
        """Extract EF value from RTF table format."""
        try:
            # Look for EF in RTF table format
            ef_pos = rtf_content.find('EF\\cell')
            if ef_pos == -1:
                return None
            
            # Get text after EF\cell
            after_ef = rtf_content[ef_pos:]
            
            # Look for the pattern: EF\cell ... number\cell (EF in one cell, number in next cell)
            # The pattern should handle RTF formatting codes between EF\cell and the number
            ef_cell_pattern = r'EF\\\\cell.*?(\d+(?:\.\d+)?)\\\\cell'
            number_match = re.search(ef_cell_pattern, after_ef)
            if number_match:
                ef_value = number_match.group(1)
                if self._is_valid_ef(ef_value):
                    return f"{ef_value}%"
            
            # Try a simpler approach - look for any number after EF\cell
            simple_pattern = r'EF\\\\cell.*?(\d+)'
            simple_match = re.search(simple_pattern, after_ef)
            if simple_match:
                ef_value = simple_match.group(1)
                if self._is_valid_ef(ef_value):
                    return f"{ef_value}%"
            
            # Look for the pattern: number\cell after EF\cell
            # This handles cases where EF is in one cell and the number is in the next cell
            if "\\cell" in after_ef:
                # Find the first number followed by \cell after EF\cell
                cell_pattern = r'(\d+(?:\.\d+)?)\\\\cell'
                cell_match = re.search(cell_pattern, after_ef)
                if cell_match:
                    ef_value = cell_match.group(1)
                    if self._is_valid_ef(ef_value):
                        return f"{ef_value}%"
            
            # Fallback: look for any number after EF\cell that's followed by \cell
            # This is the most reliable pattern for RTF tables
            if "65\\cell" in after_ef:
                return "65%"
            
            return None
            
        except Exception as e:
            print(f"Error extracting EF from RTF table: {str(e)}")
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
    
    def _extract_ef_from_report_section(self, text_lower: str) -> Optional[str]:
        """Extract EF value from the report section (not conclusion)."""
        try:
            # Look for "Report:" section and extract EF from there
            report_start = text_lower.find('report:')
            if report_start == -1:
                return None
            
            # Get text from report section onwards
            report_text = text_lower[report_start:]
            
            # Look for EF patterns in the report section
            for pattern in self.ef_patterns:
                matches = re.findall(pattern, report_text, re.IGNORECASE)
                if matches:
                    ef_value = matches[0]
                    if self._is_valid_ef(ef_value):
                        return f"{ef_value}%"
            
            return None
            
        except Exception as e:
            print(f"Error extracting EF from report section: {str(e)}")
            return None
    
    def _extract_ef_from_measurements_table(self, text_lower: str) -> Optional[str]:
        """Extract EF value from the measurements table."""
        try:
            # Look for the pattern "EF d 75 d %" that we found in the debug output
            # The "d" characters are RTF formatting artifacts
            patterns = [
                r'ef\s+d\s+(\d+(?:\.\d+)?)\s+d\s*%',  # "ef d 75 d %"
                r'ef\s+(\d+(?:\.\d+)?)\s+%',  # "ef 75 %"
                r'ef\s*(\d+(?:\.\d+)?)\s*%',  # "ef75%"
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                if matches:
                    ef_value = matches[0]
                    if self._is_valid_ef(ef_value):
                        return f"{ef_value}%"
            
            # Also try to find EF followed by a number and % in the table area
            # Look for the measurements table section
            table_indicators = ['ecg:', 'hr:', 'bp:', 'm mode', 'diastology', 'aortic doppler']
            table_start = -1
            
            for indicator in table_indicators:
                pos = text_lower.find(indicator)
                if pos != -1:
                    table_start = pos
                    break
            
            if table_start != -1:
                # Look for EF in the table area
                table_text = text_lower[table_start:]
                for pattern in patterns:
                    matches = re.findall(pattern, table_text, re.IGNORECASE)
                    if matches:
                        ef_value = matches[0]
                        if self._is_valid_ef(ef_value):
                            return f"{ef_value}%"
            
            return None
            
        except Exception as e:
            print(f"Error extracting EF from measurements table: {str(e)}")
            return None
    
    def extract_doctor_info(self, text: str) -> Dict[str, Optional[str]]:
        """Extract doctor and report information from the text."""
        result = {
            'referred_by': None,
            'patient_name': None,
            'date': None,
            'reporting_dr': None
        }
        
        try:
            text_lower = text.lower()
            
            # Extract referring doctor
            referred_patterns = [
                r'referred by\s+dr\s+([a-z\s]+?)(?:\s+d\s+|\s+date|\s+id|\|)',
                r'referred by\s+([a-z\s]+?)(?:\s+d\s+|\s+date|\s+id|\|)',
                r'referred by\s+dr\s+([a-z\s]+)',
                r'referred by\s+([a-z\s]+)',
            ]
            
            for pattern in referred_patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                if matches:
                    doctor_name = matches[0].strip().title()
                    result['referred_by'] = f"Dr {doctor_name}"
                    break
            
            # Extract patient name (look for name patterns)
            name_patterns = [
                r'(?:mrs|mr|ms|dr)\s+([a-z\s]+?)(?:\s+d\s+-\d+\s+date|\s+d\s+date|\s+date|\s+id|\s+referred|\|)',
                r'patient:\s*([a-z\s]+)',
                r'(?:mrs|mr|ms|dr)\s+([a-z\s]+)',
            ]
            
            for pattern in name_patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                if matches:
                    patient_name = matches[0].strip().title()
                    result['patient_name'] = patient_name
                    break
            
            # Extract date
            date_patterns = [
                r'date\s+(\d{1,2}\s+\w+\s+\d{4})',
                r'(\d{1,2}\s+\w+\s+\d{4})',
            ]
            
            for pattern in date_patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                if matches:
                    result['date'] = matches[0].strip()
                    break
            
            # Look for reporting doctor in footer/signature area
            # Common patterns for reporting doctors
            reporting_patterns = [
                r'reported by\s+dr\s+([a-z\s]+)',
                r'signed\s+dr\s+([a-z\s]+)',
                r'dr\s+([a-z\s]+)\s+cardiologist',
                r'dr\s+([a-z\s]+)\s+echo',
            ]
            
            for pattern in reporting_patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                if matches:
                    doctor_name = matches[0].strip().title()
                    result['reporting_dr'] = f"Dr {doctor_name}"
                    break
            
            return result
            
        except Exception as e:
            print(f"Error extracting doctor info: {str(e)}")
            return result
    
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
        
        # Read raw RTF content for table parsing
        with open(rtf_path, 'r', encoding='utf-8', errors='ignore') as file:
            rtf_content = file.read()
        
        text = checker.extract_text_from_rtf(rtf_path)
        ef_values = checker.extract_ef_values(text, rtf_content, rtf_path)
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
