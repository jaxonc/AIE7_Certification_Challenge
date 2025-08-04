# RAG Document Generator for OpenFoodFacts

This tool creates synthetic documents from OpenFoodFacts API data that can be used for Retrieval Augmented Generation (RAG) applications. It takes a list of UPC (Universal Product Code) codes and generates comprehensive, one-page summaries for each product.

## Features

- **Comprehensive Product Information**: Extracts detailed product data including ingredients, nutrition facts, allergens, packaging, and certifications
- **RAG-Optimized Content**: Generates documents with rich, descriptive text perfect for retrieval systems
- **Error Handling**: Gracefully handles missing products and API errors
- **Rate Limiting**: Respects OpenFoodFacts API limits with configurable delays
- **Metadata Generation**: Creates collection metadata for tracking and analysis
- **Structured Output**: Organizes documents in a clean directory structure

## Files Created

### Core Module
- `rag_document_generator.py` - Main RAG document generator class

### Usage Scripts
- `generate_rag_data.ipynb` - Example script for generating documents from UPC lists

## Quick Start

1. **Prepare your UPC list**: Edit the `UPC_LIST` variable in `generate_rag_data.ipynb` with your UPC codes
2. **Run the interactive notebook**:
3. **Find your documents**: Generated documents will be in the `./../data/` directory

## Document Structure

Each generated document contains the following sections:

- **Product Overview**: Basic product information and description
- **Brand and Manufacturer**: Company information and brand details
- **Product Categorization**: Food categories and classifications
- **Ingredients and Composition**: Complete ingredients list with explanations
- **Nutritional Information**: Detailed nutrition facts per 100g
- **Nutrition Quality Assessment**: OpenFoodFacts nutrition grades (A-E)
- **Allergen Information**: Known allergens and dietary considerations
- **Packaging and Environmental Impact**: Packaging materials and environmental info
- **Availability and Sourcing**: Countries where product is sold
- **Quality and Certifications**: Organic, fair trade, and other certifications
- **Consumer Guidance**: Helpful information for consumers
- **Database Reference**: Links to original OpenFoodFacts data

## Example Usage

### Basic Usage
```python
from rag_document_generator import RAGDocumentGenerator

# Initialize generator
generator = RAGDocumentGenerator(rate_limit_delay=1.0)

# List of UPCs to process
upc_codes = ["028400433303", "028400596008", "012000173592"]

# Generate documents
successful, failed = generator.generate_rag_documents(upc_codes)
```

### Advanced Usage
```python
from rag_document_generator import RAGDocumentGenerator

# Custom configuration
generator = RAGDocumentGenerator(
    rate_limit_delay=0.5,  # Faster API calls
    timeout=15             # Longer timeout
)

# Generate with custom output directory
successful, failed = generator.generate_rag_documents(
    upc_list=upc_codes,
    output_dir="my_custom_documents"
)

# Generate metadata
metadata_path = generator.generate_collection_metadata(
    upc_list=upc_codes,
    successful_upcs=successful,
    failed_upcs=failed,
    output_dir="my_custom_documents"
)
```

## Output Structure

```
rag_documents/
├── Celsius_Peach_Vibe_product_summary.txt
├── Cheetos_Crunchy_xxtra_Flamin'_Hot_product_summary.txt
└── collection_metadata.json
```

### Sample Document Content
Each document is approximately 1 page long and contains rich, descriptive content like:

```
Product Information Summary
UPC: 028400433303
Product Name: Lay's Classic Potato Chips

OVERVIEW
Lay's Classic Potato Chips is a food product manufactured by Frito-Lay. This product 
is classified under the following categories: Snacks, Salty snacks, Appetizers, Chips and fries...

INGREDIENTS AND COMPOSITION
The following ingredients are listed for this product:
• Potatoes
• Vegetable Oil (Sunflower, Corn, and/or Canola Oil)
• Salt
...
```

## Configuration Options

### RAGDocumentGenerator Parameters
- `rate_limit_delay` (float): Delay between API calls in seconds (default: 1.0)
- `timeout` (int): Request timeout in seconds (default: 10)

### Output Customization
- `output_dir` (str): Directory to save generated documents (default: "./../data")

## Error Handling

The generator handles various error scenarios:
- **Product Not Found**: Creates a document explaining the UPC was not found
- **API Errors**: Handles network issues and API timeouts gracefully
- **Invalid UPCs**: Processes even malformed UPC codes
- **Rate Limiting**: Automatically adds delays between requests

## Use Cases

This tool is perfect for:
- **RAG Training Data**: Creating synthetic training documents for RAG systems
- **Product Information Retrieval**: Building searchable product databases
- **Food Safety Research**: Analyzing ingredients and allergen information
- **Nutrition Analysis**: Studying nutritional content across product categories
- **Market Research**: Understanding product categorization and availability

## Data Source

All product information is sourced from [OpenFoodFacts](https://world.openfoodfacts.org/), a collaborative, free and open database of food products from around the world.

## Best Practices

1. **Rate Limiting**: Use appropriate delays (1-2 seconds) between API calls
2. **Batch Processing**: Process UPCs in manageable batches
3. **Error Checking**: Always check the success/failure lists after generation
4. **Data Validation**: Verify UPC codes before processing
5. **Storage Management**: Regularly clean up old document collections

## Troubleshooting

### Common Issues
- **Slow Processing**: Increase `rate_limit_delay` if experiencing timeouts
- **Products Not Found**: Some UPCs may not be in the OpenFoodFacts database
- **Network Errors**: Check internet connection and API availability

### Performance Tips
- Start with small batches to test
- Use appropriate rate limiting for your network
- Consider running during off-peak hours for better API response times

## Integration with Existing Code

This generator is designed to work alongside the existing S.A.V.E. codebase:
- Uses similar patterns to the existing `OpenFoodFactsTool` in `src/utils/`
- Follows the project's code structure and conventions
- Generated documents are used by the RAG system in the main application
- Can be extended to work with the existing LangGraph tools

## License and Attribution

This tool uses the OpenFoodFacts API, which is provided under the Open Database License. Please ensure you comply with their terms of service and attribution requirements when using the generated documents.