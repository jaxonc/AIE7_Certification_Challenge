"""
RAG Document Generator for OpenFoodFacts Product Information

This module creates synthetic documents from OpenFoodFacts API data that can be used
for Retrieval Augmented Generation (RAG) applications. It takes a list of UPC codes
and generates comprehensive, one-page summaries for each product.
"""

import requests
import json
import time
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import os
from dataclasses import dataclass


@dataclass
class ProductDocument:
    """Data class to store structured product information for document generation."""
    upc: str
    product_name: str
    brands: str
    categories: str
    ingredients_text: str
    nutrition_grades: str
    countries: str
    url: str
    raw_data: Dict
    found: bool


class RAGDocumentGenerator:
    """
    Generates synthetic documents from OpenFoodFacts API data for RAG applications.
    
    This class fetches product information from OpenFoodFacts API and creates
    comprehensive, human-readable documents that can be used for training
    or enhancing RAG systems.
    """
    
    def __init__(self, rate_limit_delay: float = 1.0, timeout: int = 10):
        """
        Initialize the RAG Document Generator.
        
        Args:
            rate_limit_delay (float): Delay between API calls to respect rate limits
            timeout (int): Request timeout in seconds
        """
        self.rate_limit_delay = rate_limit_delay
        self.timeout = timeout
        self.base_url = "https://world.openfoodfacts.org/api/v2/product"
    
    def fetch_product_data(self, upc: str) -> ProductDocument:
        """
        Fetch product data from OpenFoodFacts API for a given UPC.
        
        Args:
            upc (str): UPC code to look up
            
        Returns:
            ProductDocument: Structured product information
        """
        try:
            api_url = f"{self.base_url}/{upc}.json"
            response = requests.get(api_url, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 1 and 'product' in data:
                product = data['product']
                
                return ProductDocument(
                    upc=upc,
                    product_name=product.get('product_name', 'Unknown Product'),
                    brands=product.get('brand_owner', product.get('brands', 'Unknown Brand')),
                    categories=product.get('categories', 'Uncategorized'),
                    ingredients_text=product.get('ingredients_text', 'Ingredients not available'),
                    nutrition_grades=product.get('nutrition_grades', 'Not graded'),
                    countries=product.get('countries', 'Unknown origin'),
                    url=f"https://world.openfoodfacts.org/product/{upc}",
                    raw_data=product,
                    found=True
                )
            else:
                return ProductDocument(
                    upc=upc,
                    product_name="Product Not Found",
                    brands="N/A",
                    categories="N/A",
                    ingredients_text="N/A",
                    nutrition_grades="N/A",
                    countries="N/A",
                    url=f"https://world.openfoodfacts.org/product/{upc}",
                    raw_data={},
                    found=False
                )
                
        except Exception as e:
            print(f"Error fetching data for UPC {upc}: {str(e)}")
            return ProductDocument(
                upc=upc,
                product_name="Error Fetching Product",
                brands="N/A",
                categories="N/A", 
                ingredients_text="N/A",
                nutrition_grades="N/A",
                countries="N/A",
                url="N/A",
                raw_data={},
                found=False
            )
    
    def generate_product_summary(self, product: ProductDocument) -> str:
        """
        Generate a comprehensive one-page summary for a product.
        
        Args:
            product (ProductDocument): Product information to summarize
            
        Returns:
            str: Formatted product summary document
        """
        if not product.found:
            return f"""
Product Information Summary
UPC: {product.upc}
Status: Product Not Found

This product with UPC code {product.upc} could not be found in the OpenFoodFacts database. 
This may indicate that the product is not cataloged in the OpenFoodFacts system, 
the UPC code may be incorrect, or the product may be region-specific and not 
available in the global database.

For more information about this UPC code, you may want to:
- Verify the UPC code is correct
- Check if the product is available in regional databases
- Contact the manufacturer directly for product information

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        # Extract additional nutritional information if available
        nutrition_info = self._extract_nutrition_info(product.raw_data)
        allergen_info = self._extract_allergen_info(product.raw_data)
        packaging_info = self._extract_packaging_info(product.raw_data)
        
        summary = f"""
Product Information Summary
UPC: {product.upc}
Product Name: {product.product_name}

OVERVIEW
{product.product_name} is a food product manufactured by {product.brands}. This product 
is classified under the following categories: {product.categories}. The product is 
available in the following countries: {product.countries}.

BRAND AND MANUFACTURER
Brand: {product.brands}
This product is produced and distributed by {product.brands}, ensuring quality and 
consistency in manufacturing standards.

PRODUCT CATEGORIZATION
Categories: {product.categories}
The product falls under these specific food categories, which helps consumers 
understand the type of food product and its intended use in meal planning and 
dietary considerations.

INGREDIENTS AND COMPOSITION
{self._format_ingredients_section(product.ingredients_text)}

NUTRITIONAL INFORMATION
{nutrition_info}

NUTRITION QUALITY ASSESSMENT
Nutrition Grade: {product.nutrition_grades}
{self._explain_nutrition_grade(product.nutrition_grades)}

ALLERGEN INFORMATION
{allergen_info}

PACKAGING AND ENVIRONMENTAL IMPACT
{packaging_info}

AVAILABILITY AND SOURCING
Countries of Sale: {product.countries}
This product is available for purchase in the listed countries, indicating its 
market distribution and regional availability.

ADDITIONAL PRODUCT DETAILS
{self._extract_additional_details(product.raw_data)}

QUALITY AND CERTIFICATIONS
{self._extract_certifications(product.raw_data)}

CONSUMER GUIDANCE
This product summary is intended to help consumers make informed dietary choices. 
For the most current product information, including any recent formulation changes, 
consumers should refer to the actual product packaging and labels.

PRODUCT DATABASE REFERENCE
For more detailed information about this product, including user reviews, 
photos, and additional nutritional data, visit: {product.url}

This information is sourced from the OpenFoodFacts database, a collaborative 
project that aims to create a comprehensive database of food products worldwide.

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
UPC: {product.upc}
Source: OpenFoodFacts Database
"""
        return summary
    
    def _format_ingredients_section(self, ingredients_text: str) -> str:
        """Format the ingredients section with better readability."""
        if ingredients_text == "Ingredients not available" or not ingredients_text:
            return """Ingredients information is not available for this product. Consumers with 
allergies or dietary restrictions should check the actual product packaging 
for complete ingredients information."""
        
        # Clean up ingredients text and make it more readable
        ingredients = ingredients_text.replace(',', ',\n• ').strip()
        if not ingredients.startswith('•'):
            ingredients = '• ' + ingredients
            
        return f"""The following ingredients are listed for this product:

{ingredients}

Ingredients are typically listed in descending order by weight, with the most 
predominant ingredients appearing first. Consumers with specific dietary needs 
or allergies should carefully review this ingredients list."""
    
    def _extract_nutrition_info(self, raw_data: Dict) -> str:
        """Extract and format nutritional information."""
        nutrition_facts = []
        
        # Common nutrition fields to look for
        nutrition_fields = {
            'energy_100g': 'Energy',
            'energy-kcal_100g': 'Calories',
            'fat_100g': 'Total Fat',
            'saturated-fat_100g': 'Saturated Fat',
            'carbohydrates_100g': 'Total Carbohydrates',
            'sugars_100g': 'Total Sugars',
            'fiber_100g': 'Dietary Fiber',
            'proteins_100g': 'Protein',
            'salt_100g': 'Salt',
            'sodium_100g': 'Sodium'
        }
        
        nutriments = raw_data.get('nutriments', {})
        
        for field, label in nutrition_fields.items():
            if field in nutriments:
                value = nutriments[field]
                unit = 'g' if field != 'energy_100g' and field != 'energy-kcal_100g' else ('kJ' if field == 'energy_100g' else 'kcal')
                nutrition_facts.append(f"• {label}: {value} {unit} per 100g")
        
        if nutrition_facts:
            return f"""Per 100g serving, this product contains:

{chr(10).join(nutrition_facts)}

These nutritional values are provided per 100 grams of product and can help 
consumers make informed dietary decisions."""
        else:
            return """Detailed nutritional information is not available for this product. 
Consumers should refer to the product packaging for complete nutritional facts."""
    
    def _extract_allergen_info(self, raw_data: Dict) -> str:
        """Extract allergen information."""
        allergens = raw_data.get('allergens', '')
        allergens_tags = raw_data.get('allergens_tags', [])
        
        if allergens or allergens_tags:
            allergen_list = []
            if allergens:
                allergen_list.extend(allergens.split(','))
            if allergens_tags:
                allergen_list.extend([tag.replace('en:', '').replace('-', ' ').title() for tag in allergens_tags])
            
            unique_allergens = list(set([a.strip().title() for a in allergen_list if a.strip()]))
            
            if unique_allergens:
                return f"""This product contains or may contain the following allergens:
• {chr(10) + '• '.join(unique_allergens)}

Consumers with food allergies should carefully read product labels and consult 
with healthcare providers regarding safe consumption."""
            
        return """No specific allergen information is available in the database for this product. 
Consumers with food allergies should check the actual product packaging for 
complete allergen declarations."""
    
    def _extract_packaging_info(self, raw_data: Dict) -> str:
        """Extract packaging and environmental information."""
        packaging = raw_data.get('packaging', '')
        packaging_tags = raw_data.get('packaging_tags', [])
        
        packaging_info = []
        if packaging:
            packaging_info.append(f"Packaging: {packaging}")
        
        if packaging_tags:
            materials = [tag.replace('en:', '').replace('-', ' ').title() for tag in packaging_tags]
            packaging_info.append(f"Materials: {', '.join(materials)}")
        
        if packaging_info:
            return f"""{chr(10).join(packaging_info)}

Packaging information helps consumers make environmentally conscious choices 
and properly dispose of or recycle packaging materials."""
        else:
            return """Packaging information is not available for this product. Consumers 
should refer to the actual product packaging for recycling instructions."""
    
    def _explain_nutrition_grade(self, grade: str) -> str:
        """Provide explanation for nutrition grades."""
        grade_explanations = {
            'a': 'This product has received an "A" nutrition grade, indicating it is considered a healthy choice with good nutritional quality.',
            'b': 'This product has received a "B" nutrition grade, indicating it has good nutritional quality with some minor concerns.',
            'c': 'This product has received a "C" nutrition grade, indicating it has average nutritional quality.',
            'd': 'This product has received a "D" nutrition grade, indicating it has below-average nutritional quality and should be consumed in moderation.',
            'e': 'This product has received an "E" nutrition grade, indicating it has poor nutritional quality and should be consumed sparingly.',
        }
        
        if grade.lower() in grade_explanations:
            return grade_explanations[grade.lower()]
        else:
            return "No nutrition grade is available for this product, or the grade is not recognized."
    
    def _extract_additional_details(self, raw_data: Dict) -> str:
        """Extract additional product details."""
        details = []
        
        if 'quantity' in raw_data:
            details.append(f"Package Size: {raw_data['quantity']}")
        
        if 'serving_size' in raw_data:
            details.append(f"Serving Size: {raw_data['serving_size']}")
            
        if 'manufacturing_places' in raw_data:
            details.append(f"Manufacturing Location: {raw_data['manufacturing_places']}")
            
        if 'stores' in raw_data:
            details.append(f"Available at: {raw_data['stores']}")
        
        if details:
            return '\n'.join([f"• {detail}" for detail in details])
        else:
            return "Additional product details are not available in the database."
    
    def _extract_certifications(self, raw_data: Dict) -> str:
        """Extract quality certifications and labels."""
        labels = raw_data.get('labels', '')
        labels_tags = raw_data.get('labels_tags', [])
        
        certifications = []
        if labels:
            certifications.extend(labels.split(','))
        if labels_tags:
            certifications.extend([tag.replace('en:', '').replace('-', ' ').title() for tag in labels_tags])
        
        unique_certs = list(set([c.strip().title() for c in certifications if c.strip()]))
        
        if unique_certs:
            return f"""This product has the following certifications or quality labels:
• {chr(10) + '• '.join(unique_certs)}

These certifications indicate compliance with specific quality, environmental, 
or ethical standards."""
        else:
            return """No specific certifications or quality labels are recorded for this product 
in the database."""
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize a string to be safe for use as a filename.
        
        Args:
            filename (str): The original filename string
            
        Returns:
            str: Sanitized filename safe for filesystem use
        """
        # Replace problematic characters with underscores
        # Remove or replace characters that are problematic for filenames
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Replace multiple spaces with single underscore
        sanitized = re.sub(r'\s+', '_', sanitized)
        # Remove leading/trailing whitespace and dots
        sanitized = sanitized.strip('. ')
        # Limit length to avoid filesystem issues
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        # Ensure it's not empty
        if not sanitized:
            sanitized = "unknown_product"
        return sanitized
    
    def generate_rag_documents(self, upc_list: List[str], output_dir: str = "rag_documents") -> Tuple[List[str], List[str]]:
        """
        Generate RAG documents for a list of UPC codes.
        
        Args:
            upc_list (List[str]): List of UPC codes to process
            output_dir (str): Directory to save the generated documents
            
        Returns:
            Tuple[List[str], List[str]]: Lists of successfully processed and failed UPCs
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        successful_upcs = []
        failed_upcs = []
        
        print(f"Generating RAG documents for {len(upc_list)} UPC codes...")
        
        for i, upc in enumerate(upc_list, 1):
            print(f"Processing UPC {i}/{len(upc_list)}: {upc}")
            
            # Fetch product data
            product = self.fetch_product_data(upc)
            
            # Generate document
            document = self.generate_product_summary(product)
            
            # Save document
            sanitized_name = self._sanitize_filename(product.product_name)
            filename = f"{sanitized_name}_product_summary.txt"
            filepath = os.path.join(output_dir, filename)
            
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(document)
                
                if product.found:
                    successful_upcs.append(upc)
                    print(f"✅ Successfully generated document for UPC {upc}")
                else:
                    failed_upcs.append(upc)
                    print(f"⚠️ UPC {upc} not found in database, but document created")
                    
            except Exception as e:
                failed_upcs.append(upc)
                print(f"❌ Failed to save document for UPC {upc}: {str(e)}")
            
            # Rate limiting
            if i < len(upc_list):
                time.sleep(self.rate_limit_delay)
        
        print(f"\nDocument generation complete!")
        print(f"✅ Successfully processed: {len(successful_upcs)} UPCs")
        print(f"⚠️ Failed or not found: {len(failed_upcs)} UPCs")
        
        return successful_upcs, failed_upcs
    
    def generate_collection_metadata(self, upc_list: List[str], successful_upcs: List[str], 
                                   failed_upcs: List[str], output_dir: str) -> str:
        """
        Generate metadata file for the document collection.
        
        Args:
            upc_list (List[str]): Original UPC list
            successful_upcs (List[str]): Successfully processed UPCs
            failed_upcs (List[str]): Failed UPCs
            output_dir (str): Output directory
            
        Returns:
            str: Path to metadata file
        """
        metadata = {
            "collection_info": {
                "generated_on": datetime.now().isoformat(),
                "total_upcs_requested": len(upc_list),
                "successful_documents": len(successful_upcs),
                "failed_documents": len(failed_upcs),
                "success_rate": f"{(len(successful_upcs) / len(upc_list) * 100):.1f}%"
            },
            "successful_upcs": successful_upcs,
            "failed_upcs": failed_upcs,
            "source": "OpenFoodFacts API",
            "purpose": "RAG document collection for food product information"
        }
        
        metadata_path = os.path.join(output_dir, "collection_metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return metadata_path