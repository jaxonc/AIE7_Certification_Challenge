from langchain.tools import BaseTool
from typing import Optional, Any
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
import json
from .prompts import get_upc_extraction_prompt


class UPCExtractionTool(BaseTool):
    name: str = "upc_extraction"
    description: str = "Extracts UPC codes and product descriptions from natural language text about products. Use this tool when the user mentions numbers that could be UPC codes or asks about specific products. Input should be the user's complete message."
    model: Optional[Any] = None
    debug: bool = False
    
    class Config:
        arbitrary_types_allowed = True
    
    def _run(self, input_text: str) -> str:
        """
        Extract UPC and description from natural language text.
        
        Args:
            input_text (str): Natural language text that may contain UPC and product description
            
        Returns:
            str: JSON-formatted extraction result with UPC, description, confidence, and success flag
        """
        if not self.model:
            return json.dumps({
                "success": False,
                "error": "No model provided for extraction",
                "upc": "",
                "description": "",
                "confidence": "Low"
            })
            
        try:
            class UPCExtraction(BaseModel):
                upc: str = Field(description="The UPC code found in the text (digits only, no spaces or dashes)")
                description: str = Field(description="The product description or name found in the text")
                confidence: str = Field(description="High, Medium, or Low confidence in the extraction")
                found_upc: bool = Field(description="True if a valid UPC code was found, False otherwise")
            
            parser = JsonOutputParser(pydantic_object=UPCExtraction)
            
            system_message = get_upc_extraction_prompt(parser.get_format_instructions())

            messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=f"Extract UPC and description from: {input_text}")
            ]
            
            response = self.model.invoke(messages)
            
            # Debug: Print the actual response content
            if self.debug:
                print(f"DEBUG - Model response content: {response.content}")
            
            # Try multiple JSON parsing approaches
            result = None
            parse_error = None
            
            # Method 1: Use LangChain's JsonOutputParser
            try:
                result = parser.parse(response.content)
            except Exception as e1:
                parse_error = e1
                if self.debug:
                    print(f"DEBUG - LangChain parser failed: {e1}")
                
                # Method 2: Try direct JSON parsing
                try:
                    import json as json_lib
                    result = json_lib.loads(response.content)
                except Exception as e2:
                    if self.debug:
                        print(f"DEBUG - Direct JSON parsing failed: {e2}")
                    
                    # Method 3: Try to clean and parse JSON aggressively
                    try:
                        # Aggressive cleaning of the response content
                        cleaned_content = response.content.strip()
                        
                        # Remove common markdown wrappers
                        if cleaned_content.startswith('```json'):
                            cleaned_content = cleaned_content[7:]
                        if cleaned_content.startswith('```'):
                            cleaned_content = cleaned_content[3:]
                        if cleaned_content.endswith('```'):
                            cleaned_content = cleaned_content[:-3]
                        
                        # Remove extra text before/after JSON
                        import re
                        json_match = re.search(r'(\{.*\})', cleaned_content, re.DOTALL)
                        if json_match:
                            cleaned_content = json_match.group(1)
                        
                        # Fix common escaping issues
                        cleaned_content = cleaned_content.replace('\\"', '"')  # Fix over-escaped quotes
                        cleaned_content = cleaned_content.replace('"upc"', '"upc"')  # Ensure proper quotes
                        cleaned_content = cleaned_content.replace('"description"', '"description"')
                        cleaned_content = cleaned_content.replace('"confidence"', '"confidence"')  
                        cleaned_content = cleaned_content.replace('"found_upc"', '"found_upc"')
                        
                        cleaned_content = cleaned_content.strip()
                        if self.debug:
                            print(f"DEBUG - Cleaned content: {cleaned_content}")
                        
                        result = json_lib.loads(cleaned_content)
                        if self.debug:
                            print(f"DEBUG - Aggressive cleaning JSON parsing succeeded")
                    except Exception as e3:
                        if self.debug:
                            print(f"DEBUG - Cleaned JSON parsing failed: {e3}")
                            print(f"DEBUG - Raw content: {repr(response.content)}")
                        
                        # Method 4: Regex extraction from malformed JSON
                        try:
                            import re
                            # Try to extract JSON components using regex
                            upc_match = re.search(r'"upc":\s*"([^"]*)"', response.content)
                            desc_match = re.search(r'"description":\s*"([^"]*)"', response.content)
                            conf_match = re.search(r'"confidence":\s*"([^"]*)"', response.content)
                            found_match = re.search(r'"found_upc":\s*(true|false)', response.content)
                            
                            if upc_match:
                                result = {
                                    "upc": upc_match.group(1),
                                    "description": desc_match.group(1) if desc_match else "",
                                    "confidence": conf_match.group(1) if conf_match else "Medium",
                                    "found_upc": found_match.group(1) == "true" if found_match else False
                                }
                                if self.debug:
                                    print(f"DEBUG - Regex extraction from JSON succeeded: {result}")
                            else:
                                if self.debug:
                                    print(f"DEBUG - Regex extraction failed, falling back to input parsing")
                                # Final fallback: parse the original input
                                upc_input_match = re.search(r'\b(\d{8,12})\b', input_text)
                                desc_patterns = [
                                    r'description\s+([^.!?]+)',
                                    r'and\s+the\s+description\s+([^.!?]+)',
                                ]
                                
                                description = ""
                                for pattern in desc_patterns:
                                    match = re.search(pattern, input_text.lower())
                                    if match:
                                        description = match.group(1).strip()
                                        break
                                
                                if not description:
                                    desc_words = re.findall(r'\b(?:chips?|fries?|cereal|cookies?|snacks?|food|product|crackers?|candy|chocolate|soda|drink)\b', input_text.lower())
                                    description = " ".join(desc_words) if desc_words else ""
                                
                                if upc_input_match:
                                    return json.dumps({
                                        "success": True,
                                        "upc": upc_input_match.group(1),
                                        "description": description,
                                        "confidence": "Medium",
                                        "message": f"Extracted via input fallback: UPC={upc_input_match.group(1)}, Description={description}"
                                    })
                                else:
                                    return json.dumps({
                                        "success": False,
                                        "error": f"All parsing methods failed: {e1}, {e2}, {e3}",
                                        "upc": "",
                                        "description": "",
                                        "confidence": "Low"
                                    })
                        except Exception as e4:
                            return json.dumps({
                                "success": False,
                                "error": f"All extraction methods failed: {e1}, {e2}, {e3}, {e4}",
                                "upc": "",
                                "description": "",
                                "confidence": "Low"
                            })
            
            # Validate and format response
            upc = result.get('upc', '').strip()
            description = result.get('description', '').strip()
            confidence = result.get('confidence', 'Medium')
            found_upc = result.get('found_upc', False) and len(upc) >= 8
            
            extraction_result = {
                "success": found_upc,
                "upc": upc,
                "description": description,
                "confidence": confidence,
                "message": f"Extracted UPC: {upc}, Description: {description}" if found_upc else "No valid UPC found in input"
            }
            
            return json.dumps(extraction_result)
                
        except Exception as e:
            error_result = {
                "success": False,
                "error": f"Extraction failed: {str(e)}",
                "upc": "",
                "description": "",
                "confidence": "Low"
            }
            return json.dumps(error_result)