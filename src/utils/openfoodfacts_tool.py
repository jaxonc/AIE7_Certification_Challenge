from langchain.tools import BaseTool
from typing import Optional
import requests
import json

class OpenFoodFactsTool(BaseTool):
    name: str = "openfoodfacts_lookup"
    description: str = "Looks up product information directly from OpenFoodFacts API using a valid UPC code. Input should be a valid UPC code as a string."
    
    def _run(self, upc: str) -> str:
        """
        Look up product information from OpenFoodFacts API.
        
        Args:
            upc (str): Valid UPC code
            
        Returns:
            str: Product information from OpenFoodFacts or indication that product was not found
        """
        try:
            # OpenFoodFacts API endpoint
            api_url = f"https://world.openfoodfacts.org/api/v2/product/{upc}.json"
            
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 1 and 'product' in data:
                product = data['product']
                
                # Extract key information
                result = {
                    "found": True,
                    "product_name": product.get('product_name', 'N/A'),
                    "brands": product.get('brand_owner', product.get('brands', 'N/A')),
                    "categories": product.get('categories', 'N/A'),
                    "ingredients_text": product.get('ingredients_text', 'N/A'),
                    "nutrition_grades": product.get('nutrition_grades', 'N/A'),
                    "countries": product.get('countries', 'N/A'),
                    "url": f"https://world.openfoodfacts.org/product/{upc}"
                }
                
                return f"""Product found on OpenFoodFacts:
                
Product Name: {result['product_name']}
Brands: {result['brands']}
Categories: {result['categories']}
Ingredients: {result['ingredients_text']}
Nutrition Grade: {result['nutrition_grades']}
Countries: {result['countries']}
OpenFoodFacts URL: {result['url']}

This information is sourced directly from the OpenFoodFacts database."""
            
            else:
                return f"Product with UPC {upc} was not found in the OpenFoodFacts database. The UPC may be valid but the product is not cataloged on OpenFoodFacts."
                
        except requests.exceptions.RequestException as e:
            return f"Error accessing OpenFoodFacts API for UPC {upc}: {str(e)}"
        except Exception as e:
            return f"Unexpected error while looking up UPC {upc} on OpenFoodFacts: {str(e)}"