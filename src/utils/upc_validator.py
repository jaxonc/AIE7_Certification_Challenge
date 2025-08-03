from langchain.tools import BaseTool
from typing import Optional
import re

class UPCValidatorTool(BaseTool):
    name: str = "upc_validator"
    description: str = "Validates if a UPC (Universal Product Code) is valid. Input should be a UPC code as a string."
    
    def _run(self, upc: str) -> str:
        """
        Validate a UPC code using the standard UPC validation algorithm.
        
        Args:
            upc (str): The UPC code to validate
            
        Returns:
            str: Validation result with explanation
        """
        # Remove any non-digit characters
        upc_clean = re.sub(r'[^\d]', '', upc)
        
        # Check if it's a valid length (UPC-A is 12 digits, UPC-E is 8 digits)
        if len(upc_clean) not in [8, 12]:
            return f"Invalid UPC: {upc}. UPC codes must be either 8 digits (UPC-E) or 12 digits (UPC-A). Got {len(upc_clean)} digits."
        
        # For UPC-A (12 digits), validate using the check digit algorithm
        if len(upc_clean) == 12:
            return self._validate_upc_a(upc_clean)
        else:
            return self._validate_upc_e(upc_clean)
    
    def _validate_upc_a(self, upc: str) -> str:
        """
        Validate a 12-digit UPC-A code.
        
        UPC-A validation algorithm:
        1. Sum the digits in odd positions (1st, 3rd, 5th, etc.)
        2. Multiply by 3
        3. Add the sum of digits in even positions (2nd, 4th, 6th, etc.)
        4. The result should be divisible by 10
        """
        if len(upc) != 12:
            return f"Invalid UPC-A: {upc}. Must be exactly 12 digits."
        
        # Convert to list of integers
        digits = [int(d) for d in upc]
        
        # Sum of odd positions (0-indexed, so positions 0, 2, 4, 6, 8, 10)
        odd_sum = sum(digits[i] for i in range(0, 11, 2))
        
        # Sum of even positions (positions 1, 3, 5, 7, 9)
        even_sum = sum(digits[i] for i in range(1, 10, 2))
        
        # Calculate check digit
        total = (odd_sum * 3) + even_sum
        check_digit = (10 - (total % 10)) % 10
        
        # Check if the calculated check digit matches the last digit
        if check_digit == digits[-1]:
            return f"Valid UPC-A: {upc}. Check digit validation passed."
        else:
            return f"Invalid UPC-A: {upc}. Expected check digit: {check_digit}, got: {digits[-1]}."
    
    def _validate_upc_e(self, upc: str) -> str:
        """
        Validate an 8-digit UPC-E code.
        
        UPC-E is a compressed version of UPC-A. The validation is more complex
        and involves expanding to UPC-A format first.
        """
        if len(upc) != 8:
            return f"Invalid UPC-E: {upc}. Must be exactly 8 digits."
        
        # For simplicity, we'll do basic format validation
        # UPC-E codes typically start with 0 and have specific patterns
        if upc[0] != '0':
            return f"Invalid UPC-E: {upc}. UPC-E codes typically start with 0."
        
        # Basic pattern validation (this is a simplified check)
        return f"UPC-E code {upc} appears to be in valid format. Note: Full UPC-E validation requires expansion to UPC-A format."


class UPCCheckDigitCalculatorTool(BaseTool):
    name: str = "upc_check_digit_calculator"
    description: str = "Calculates and adds the check digit to a UPC code. Input should be a UPC code with 11 digits (missing check digit) or any length that needs to be converted to a valid 12-digit UPC-A format."
    
    def _run(self, upc: str) -> str:
        """
        Calculate the check digit for a UPC code and return the complete valid UPC.
        
        Args:
            upc (str): The UPC code (typically 11 digits without check digit)
            
        Returns:
            str: The complete UPC with calculated check digit and explanation
        """
        # Remove any non-digit characters
        upc_clean = re.sub(r'[^\d]', '', upc)
        
        # Handle different input lengths
        if len(upc_clean) == 12:
            # Already 12 digits, recalculate check digit
            upc_without_check = upc_clean[:11]
            calculated_check_digit = self._calculate_check_digit(upc_without_check)
            complete_upc = upc_without_check + str(calculated_check_digit)
            return f"Input UPC: {upc_clean}\nRecalculated UPC with correct check digit: {complete_upc}\nCalculated check digit: {calculated_check_digit}"
        
        elif len(upc_clean) == 11:
            # Missing check digit, calculate it
            calculated_check_digit = self._calculate_check_digit(upc_clean)
            complete_upc = upc_clean + str(calculated_check_digit)
            return f"Input UPC: {upc_clean}\nComplete UPC with check digit: {complete_upc}\nCalculated check digit: {calculated_check_digit}"
        
        elif len(upc_clean) < 11:
            # Pad with leading zeros to make it 11 digits, then calculate check digit
            padded_upc = upc_clean.zfill(11)
            calculated_check_digit = self._calculate_check_digit(padded_upc)
            complete_upc = padded_upc + str(calculated_check_digit)
            return f"Input UPC: {upc_clean}\nPadded to 11 digits: {padded_upc}\nComplete UPC with check digit: {complete_upc}\nCalculated check digit: {calculated_check_digit}"
        
        else:
            return f"Invalid UPC length: {len(upc_clean)} digits. Cannot process UPC codes longer than 12 digits."
    
    def _calculate_check_digit(self, upc_11_digits: str) -> int:
        """
        Calculate the check digit for an 11-digit UPC code using the UPC-A algorithm.
        
        Args:
            upc_11_digits (str): 11-digit UPC code without check digit
            
        Returns:
            int: The calculated check digit
        """
        if len(upc_11_digits) != 11:
            raise ValueError(f"UPC must be exactly 11 digits, got {len(upc_11_digits)}")
        
        # Convert to list of integers
        digits = [int(d) for d in upc_11_digits]
        
        # Sum of odd positions (0-indexed, so positions 0, 2, 4, 6, 8, 10)
        odd_sum = sum(digits[i] for i in range(0, 11, 2))
        
        # Sum of even positions (positions 1, 3, 5, 7, 9)
        even_sum = sum(digits[i] for i in range(1, 10, 2))
        
        # Calculate check digit
        total = (odd_sum * 3) + even_sum
        check_digit = (10 - (total % 10)) % 10
        
        return check_digit

def parse_upc_description(input_text: str) -> Optional[dict]:
    """
    Parse input text in the format {upc:###,description:words} (legacy format)
    
    Args:
        input_text (str): Input text in the specified format
        
    Returns:
        dict: Parsed UPC and description, or None if parsing fails
    """
    import re
    
    # Pattern to match {upc:([^,]+),description:([^}]+)}
    pattern = r'\{upc:([^,]+),description:([^}]+)\}'
    match = re.search(pattern, input_text.strip())
    
    if match:
        upc = match.group(1).strip()
        description = match.group(2).strip()
        return {"upc": upc, "description": description}
    
    return None 


# Legacy LLM extraction function removed - now handled by UPCExtractionTool