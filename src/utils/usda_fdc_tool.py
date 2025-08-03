from langchain.tools import BaseTool
from typing import Optional
import requests
import json
import os


class USDAFoodDataCentralTool(BaseTool):
    name: str = "usda_fdc_search"
    description: str = "Searches the USDA Food Data Central database using a valid 12-digit UPC code. Input should be a valid 12-digit UPC code as a string."
    
    def _run(self, upc: str) -> str:
        """
        Search for product information in USDA Food Data Central database.
        
        Args:
            upc (str): Valid 12-digit UPC code
            
        Returns:
            str: Product information from USDA FDC or indication that product was not found
        """
        try:
            # Get API key from environment
            api_key = os.environ.get("USDA_API_KEY")
            if not api_key:
                return "Error: USDA_API_KEY not found in environment variables. Please set the API key to use this service."
            
            # USDA Food Data Central API endpoint for food search
            api_url = "https://api.nal.usda.gov/fdc/v1/foods/search"
            
            # Parameters for the API call
            params = {
                "query": upc,
                "dataType": "Branded",
                "pageSize": 25,
                "sortOrder": "asc",
                "api_key": api_key
            }
            
            response = requests.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Check if any foods were found
            if data.get('foods') and len(data['foods']) > 0:
                foods = data['foods']
                
                # Look for exact UPC match first
                exact_match = None
                for food in foods:
                    # Check if UPC matches in gtinUpc field
                    if food.get('gtinUpc') == upc:
                        exact_match = food
                        break
                
                if exact_match:
                    food = exact_match
                else:
                    # If no exact match, take the first result
                    food = foods[0]
                
                # Extract key information
                result = {
                    "found": True,
                    "fdc_id": food.get('fdcId', 'N/A'),
                    "description": food.get('description', 'N/A'),
                    "brand_owner": food.get('brandOwner', 'N/A'),
                    "brand_name": food.get('brandName', 'N/A'),
                    "data_type": food.get('dataType', 'N/A'),
                    "gtin_upc": food.get('gtinUpc', 'N/A'),
                    "published_date": food.get('publishedDate', 'N/A'),
                    "ingredients": food.get('ingredients', 'N/A'),
                    "serving_size": food.get('servingSize', 'N/A'),
                    "serving_size_unit": food.get('servingSizeUnit', 'N/A'),
                    "household_serving_full_text": food.get('householdServingFullText', 'N/A')
                }
                
                # Check for nutrients if available
                nutrients_info = ""
                if food.get('foodNutrients'):
                    key_nutrients = ['Energy', 'Protein', 'Total lipid (fat)', 'Carbohydrate', 'Total Sugars', 'Fiber', 'Sodium']
                    nutrients_found = []
                    
                    for nutrient in food['foodNutrients']:
                        nutrient_name = nutrient.get('nutrientName', '')
                        if any(key in nutrient_name for key in key_nutrients):
                            value = nutrient.get('value', 'N/A')
                            unit = nutrient.get('unitName', '')
                            nutrients_found.append(f"{nutrient_name}: {value} {unit}")
                    
                    if nutrients_found:
                        nutrients_info = "\n".join(nutrients_found[:10])  # Limit to top 10 nutrients
                
                response_text = f"""Product found in USDA Food Data Central:

FDC ID: {result['fdc_id']}
Description: {result['description']}
Brand Owner: {result['brand_owner']}
Brand Name: {result['brand_name']}
Data Type: {result['data_type']}
UPC/GTIN: {result['gtin_upc']}
Published Date: {result['published_date']}
Ingredients: {result['ingredients']}
Serving Size: {result['serving_size']} {result['serving_size_unit']}
Household Serving: {result['household_serving_full_text']}"""

                if nutrients_info:
                    response_text += f"\n\nKey Nutrients (per 100g):\n{nutrients_info}"

                response_text += f"\n\nTotal results found: {data.get('totalHits', 0)}"
                if not exact_match and len(foods) > 1:
                    response_text += f"\nNote: No exact UPC match found. Showing most relevant result."

                response_text += "\n\nThis information is sourced from the USDA Food Data Central database."
                
                return response_text
            
            else:
                return f"No products found for UPC {upc} in the USDA Food Data Central database. The UPC may be valid but the product is not cataloged in USDA's database."
                
        except requests.exceptions.RequestException as e:
            return f"Error accessing USDA Food Data Central API for UPC {upc}: {str(e)}"
        except KeyError as e:
            return f"Error parsing USDA Food Data Central response for UPC {upc}: Missing expected field {str(e)}"
        except Exception as e:
            return f"Unexpected error while looking up UPC {upc} in USDA Food Data Central: {str(e)}"