"""Data utilities for preprocessing and transformation."""

import json
import os
from typing import List, Dict, Any
from tqdm import tqdm
import anthropic

from config import (
    ANTHROPIC_API_KEY, CONTEXT_MODEL, MAX_TOKENS_CONTEXT,
    BENEFITS_WELLBEING_PATH, EMPLOYEE_HANDBOOK_PATH,
    BENEFITS_MARKDOWN_PATH, EMPLOYEE_HANDBOOK_MARKDOWN_PATH
)
from prompts import BENEFITS_DOCUMENT_CONTEXT_PROMPT, CHUNK_CONTEXT_PROMPT


def transform_data_for_vectordb(raw_data: List[Dict[str, Any]], doc_id: str = "benefits_wellbeing") -> List[Dict[str, Any]]:
    """Transform raw data to match VectorDB structure."""
    transformed = []
    
    doc = {
        "doc_id": doc_id,
        "original_uuid": f"{doc_id}_doc",
        "chunks": []
    }
    
    for i, item in enumerate(raw_data):
        chunk = {
            "chunk_id": f"chunk_{i}",
            "original_index": i,
            "content": item["text"],
            "heading": item["chunk_heading"],
            "link": item["chunk_link"]
        }
        doc["chunks"].append(chunk)
    
    transformed.append(doc)
    return transformed


def situate_benefits_context(full_benefits_doc: str, chunk_heading: str, chunk_content: str) -> str:
    """Generate contextual information for a benefits chunk within the full benefits document."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    response = client.messages.create(
        model=CONTEXT_MODEL,
        max_tokens=MAX_TOKENS_CONTEXT,
        temperature=0.0,
        messages=[
            {
                "role": "user", 
                "content": [
                    {
                        "type": "text",
                        "text": BENEFITS_DOCUMENT_CONTEXT_PROMPT.format(doc_content=full_benefits_doc),
                        "cache_control": {"type": "ephemeral"}
                    },
                    {
                        "type": "text",
                        "text": CHUNK_CONTEXT_PROMPT.format(
                            chunk_heading=chunk_heading,
                            chunk_content=chunk_content
                        ),
                    }
                ]
            }
        ],
        extra_headers={"anthropic-beta": "prompt-caching-2024-07-31"}
    )
    return response.content[0].text.strip()


def add_contextual_information(input_file: str, output_file: str, original_markdown_file: str) -> List[Dict[str, Any]]:
    """Process all benefits chunks to add contextual information."""
    with open(input_file, 'r') as f:
        chunks = json.load(f)
    
    with open(original_markdown_file, 'r') as f:
        full_benefits_doc = f.read()
    
    print(f"Processing {len(chunks)} benefits chunks...")
    
    enhanced_chunks = []
    
    for chunk in tqdm(chunks, desc="Adding contextual information"):
        try:
            situational_context = situate_benefits_context(
                full_benefits_doc=full_benefits_doc,
                chunk_heading=chunk['chunk_heading'],
                chunk_content=chunk['text']
            )
            
            enhanced_chunk = {
                "chunk_link": chunk["chunk_link"],
                "chunk_heading": chunk["chunk_heading"],
                "text": chunk["text"],
                "situational_context": situational_context
            }
            
            enhanced_chunks.append(enhanced_chunk)
            
        except Exception as e:
            print(f"Error processing chunk '{chunk['chunk_heading']}': {e}")
            enhanced_chunks.append(chunk)
    
    with open(output_file, 'w') as f:
        json.dump(enhanced_chunks, f, indent=2)
    
    print(f"Contextual information added! Enhanced chunks saved to {output_file}")
    return enhanced_chunks


def create_contextual_dataset() -> List[Dict[str, Any]]:
    """Transform benefits_wellbeing_with_context data to match ContextualVectorDB expected format."""
    with open('data/benefits_wellbeing_with_context.json', 'r') as f:
        chunks_data = json.load(f)
    
    with open(BENEFITS_MARKDOWN_PATH, 'r') as f:
        full_document_content = f.read()
    
    print(f"Loaded {len(chunks_data)} chunks from benefits_wellbeing.json")
    print(f"Full document length: {len(full_document_content)} characters")
    
    contextual_dataset = [{
        "doc_id": "benefits_wellbeing",
        "original_uuid": "benefits_wellbeing_uuid", 
        "content": full_document_content,
        "chunks": []
    }]
    
    for i, chunk in enumerate(chunks_data):
        formatted_chunk = {
            "chunk_id": f"chunk_{i}",
            "original_index": i,
            "content": chunk["text"],
            "heading": chunk["chunk_heading"],
            "link": chunk["chunk_link"]
        }
        contextual_dataset[0]["chunks"].append(formatted_chunk)
    
    output_file = 'data/benefits_wellbeing_contextual_format.json'
    with open(output_file, 'w') as f:
        json.dump(contextual_dataset, f, indent=2)
    
    print(f"✅ Created contextual dataset with {len(contextual_dataset[0]['chunks'])} chunks")
    print(f"✅ Saved to: {output_file}")
    
    return contextual_dataset


def create_combined_dataset() -> List[Dict[str, Any]]:
    """Create a combined dataset with both benefits_wellbeing and employee_handbook documents."""
    with open(BENEFITS_WELLBEING_PATH, 'r') as f:
        benefits_data = json.load(f)
    
    with open(EMPLOYEE_HANDBOOK_PATH, 'r') as f:
        handbook_data = json.load(f)
    
    print(f"Loaded {len(benefits_data)} benefits chunks")
    print(f"Loaded {len(handbook_data)} handbook chunks")
    
    def transform_to_combined_format(raw_data: List[Dict[str, Any]], doc_id: str, doc_type: str) -> Dict[str, Any]:
        """Transform data to VectorDB format with document identification."""
        doc = {
            "doc_id": doc_id,
            "original_uuid": f"{doc_id}_uuid",
            "doc_type": doc_type,
            "chunks": []
        }
        
        for i, item in enumerate(raw_data):
            chunk = {
                "chunk_id": f"{doc_id}_chunk_{i}",
                "original_index": i,
                "content": item["text"],
                "heading": item["chunk_heading"],
                "link": item["chunk_link"],
                "doc_type": doc_type,
                "source_doc": doc_id
            }
            doc["chunks"].append(chunk)
        
        return doc
    
    benefits_doc = transform_to_combined_format(benefits_data, "benefits_wellbeing", "benefits")
    handbook_doc = transform_to_combined_format(handbook_data, "employee_handbook", "handbook")
    
    combined_dataset = [benefits_doc, handbook_doc]
    
    output_file = 'data/combined_documents.json'
    with open(output_file, 'w') as f:
        json.dump(combined_dataset, f, indent=2)
    
    total_chunks = len(benefits_doc["chunks"]) + len(handbook_doc["chunks"])
    print(f"✅ Created combined dataset with {total_chunks} total chunks")
    print(f"   - Benefits & Wellbeing: {len(benefits_doc['chunks'])} chunks")
    print(f"   - Employee Handbook: {len(handbook_doc['chunks'])} chunks")
    print(f"✅ Saved to: {output_file}")
    
    return combined_dataset


def create_combined_contextual_dataset() -> List[Dict[str, Any]]:
    """Create a combined dataset for contextual embeddings with both documents."""
    with open(BENEFITS_WELLBEING_PATH, 'r') as f:
        benefits_data = json.load(f)
    
    with open(EMPLOYEE_HANDBOOK_PATH, 'r') as f:
        handbook_data = json.load(f)
    
    with open(BENEFITS_MARKDOWN_PATH, 'r') as f:
        full_benefits_doc = f.read()
    
    with open(EMPLOYEE_HANDBOOK_MARKDOWN_PATH, 'r') as f:
        full_handbook_doc = f.read()
    
    def transform_to_contextual_format(raw_data: List[Dict[str, Any]], doc_id: str, doc_type: str, full_content: str) -> Dict[str, Any]:
        """Transform data to ContextualVectorDB format with document identification."""
        doc = {
            "doc_id": doc_id,
            "original_uuid": f"{doc_id}_uuid",
            "doc_type": doc_type,
            "content": full_content,
            "chunks": []
        }
        
        for i, item in enumerate(raw_data):
            chunk = {
                "chunk_id": f"{doc_id}_chunk_{i}",
                "original_index": i,
                "content": item["text"],
                "heading": item["chunk_heading"],
                "link": item["chunk_link"],
                "doc_type": doc_type,
                "source_doc": doc_id
            }
            doc["chunks"].append(chunk)
        
        return doc
    
    benefits_doc = transform_to_contextual_format(
        benefits_data, "benefits_wellbeing", "benefits", full_benefits_doc
    )
    handbook_doc = transform_to_contextual_format(
        handbook_data, "employee_handbook", "handbook", full_handbook_doc
    )
    
    combined_contextual_dataset = [benefits_doc, handbook_doc]
    
    output_file = 'data/combined_contextual_documents.json'
    with open(output_file, 'w') as f:
        json.dump(combined_contextual_dataset, f, indent=2)
    
    total_chunks = len(benefits_doc["chunks"]) + len(handbook_doc["chunks"])
    print(f"✅ Created combined contextual dataset with {total_chunks} total chunks")
    print(f"   - Benefits & Wellbeing: {len(benefits_doc['chunks'])} chunks")
    print(f"   - Employee Handbook: {len(handbook_doc['chunks'])} chunks")
    print(f"✅ Saved to: {output_file}")
    
    return combined_contextual_dataset


def safe_extract_source_info(chunk_metadata: Dict[str, Any]) -> tuple[str, str]:
    """Safely extract source info from metadata, handling different structures."""
    source_doc = chunk_metadata.get('source_doc')
    heading = chunk_metadata.get('heading')
    
    if source_doc and heading:
        return source_doc, heading
    
    doc_id = chunk_metadata.get('doc_id', 'unknown_doc')
    chunk_id = chunk_metadata.get('chunk_id', 'unknown_chunk')
    
    if 'benefits' in doc_id.lower():
        source_doc = 'benefits_wellbeing'
    elif 'handbook' in doc_id.lower() or 'employee' in doc_id.lower():
        source_doc = 'employee_handbook'
    else:
        source_doc = doc_id
    
    if not heading:
        content = chunk_metadata.get('content', '')
        heading = 'Unknown Section'
        content_lines = content.split('\n')
        for line in content_lines[:3]:
            if line.strip().startswith('#'):
                heading = line.strip().replace('#', '').strip()
                break
        
        if heading == 'Unknown Section':
            heading = chunk_id
    
    return source_doc, heading 

def add_contextual_information_general(
    input_file: str, 
    output_file: str, 
    original_markdown_file: str,
    doc_type: str,
    doc_description: str
) -> List[Dict[str, Any]]:
    """
    Process any document chunks to add contextual information.
    
    Args:
        input_file: Path to chunked JSON file
        output_file: Path for output with context
        original_markdown_file: Path to original markdown document
        doc_type: Type of document (e.g., "Employee Handbook", "Benefits Guide")
        doc_description: Brief description of what the document covers
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    # Load chunks and full document
    with open(input_file, 'r') as f:
        chunks = json.load(f)
    
    with open(original_markdown_file, 'r') as f:
        full_doc_content = f.read()
    
    print(f"Processing {len(chunks)} {doc_type} chunks...")
    
    # Generic document context prompt
    document_context_prompt = f"""
<document>
This is {doc_type} documentation.
{doc_description}

{{doc_content}}
</document>
"""
    
    # Generic chunk context prompt
    chunk_context_prompt = """
Here is a specific section from the documentation that we want to situate within the overall document:

<chunk>
Section: {chunk_heading}
{chunk_content}
</chunk>

Please provide a short, succinct context to situate this section within the overall document. This context will help users find this information when searching for related topics.

Answer only with the succinct context and nothing else.
"""
    
    enhanced_chunks = []
    
    for chunk in tqdm(chunks, desc=f"Adding contextual information to {doc_type}"):
        try:
            response = client.messages.create(
                model=CONTEXT_MODEL,
                max_tokens=MAX_TOKENS_CONTEXT,
                temperature=0.0,
                messages=[
                    {
                        "role": "user", 
                        "content": [
                            {
                                "type": "text",
                                "text": document_context_prompt.format(doc_content=full_doc_content),
                                "cache_control": {"type": "ephemeral"}
                            },
                            {
                                "type": "text",
                                "text": chunk_context_prompt.format(
                                    chunk_heading=chunk['chunk_heading'],
                                    chunk_content=chunk['text']
                                ),
                            }
                        ]
                    }
                ],
                extra_headers={"anthropic-beta": "prompt-caching-2024-07-31"}
            )
            
            situational_context = response.content[0].text.strip()
            
            enhanced_chunk = {
                "chunk_link": chunk["chunk_link"],
                "chunk_heading": chunk["chunk_heading"],
                "text": chunk["text"],
                "situational_context": situational_context
            }
            
            enhanced_chunks.append(enhanced_chunk)
            
        except Exception as e:
            print(f"Error processing chunk '{chunk['chunk_heading']}': {e}")
            enhanced_chunks.append(chunk)
    
    with open(output_file, 'w') as f:
        json.dump(enhanced_chunks, f, indent=2)
    
    print(f"✅ Contextual information added for {doc_type}!")
    print(f"📄 Enhanced chunks saved to {output_file}")
    return enhanced_chunks


def setup_contextual_embeddings(document_name: str):
    """
    Setup contextual embeddings for a document. Creates them if they don't exist, loads them if they do.
    
    Args:
        document_name: Base name of the document (e.g., 'benefits_wellbeing', 'employee_handbook')
    
    Returns:
        tuple: (raw_chunks, enhanced_chunks) - the original and contextually enhanced chunks
    """
    import os
    
    # Define document configurations
    doc_configs = {
        'benefits_wellbeing': {
            'json_file': '../data/benefits_wellbeing.json',
            'markdown_file': '../../raw_data_and_data_cleaning/md files/Benefits & Wellbeing.md',
            'doc_type': 'Benefits & Wellbeing Guide',
            'doc_description': 'Comprehensive employee benefits including health insurance, leave policies, perks, financial benefits, and wellness programs'
        },
        'employee_handbook': {
            'json_file': '../data/employee_handbook.json', 
            'markdown_file': '../../raw_data_and_data_cleaning/md files/Employee Handbook.md',
            'doc_type': 'Employee Handbook',
            'doc_description': 'Company policies, procedures, and guidelines for employees'
        }
    }
    
    if document_name not in doc_configs:
        raise ValueError(f"Unknown document: {document_name}. Available: {list(doc_configs.keys())}")
    
    config = doc_configs[document_name]
    
    # Derive file paths
    input_file = config['json_file']
    output_file = f'../data/{document_name}_with_context.json'
    markdown_file = config['markdown_file']
    
    # Load original data
    print(f"📖 Loading {config['doc_type']} data for contextual RAG...")
    with open(input_file, 'r') as f:
        raw_chunks = json.load(f)
    
    # Check if contextual embeddings already exist, if not create them
    if not os.path.exists(output_file):
        print(f"🔄 Creating contextual embeddings for {config['doc_type']}...")
        
        enhanced_chunks = add_contextual_information_general(
            input_file=input_file,
            output_file=output_file,
            original_markdown_file=markdown_file,
            doc_type=config['doc_type'],
            doc_description=config['doc_description']
        )
        print(f"✅ Created contextual embeddings with {len(enhanced_chunks)} chunks")
    else:
        print(f"📋 Contextual embeddings already exist for {config['doc_type']}, loading from file...")
        with open(output_file, 'r') as f:
            enhanced_chunks = json.load(f)
        print(f"✅ Loaded {len(enhanced_chunks)} contextual chunks")
    
    return raw_chunks, enhanced_chunks 


    