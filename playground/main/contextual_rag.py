import json
from anthropic import Anthropic
from tqdm import tqdm

# Initialize Anthropic client
client = Anthropic()

def situate_benefits_context(full_benefits_doc: str, chunk_heading: str, chunk_content: str) -> str:
    """
    Generate contextual information for a benefits chunk within the full benefits document
    """
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=150,  # Keep context concise
        temperature=0.0,
        messages=[
            {
                "role": "user", 
                "content": [
                    {
                        "type": "text",
                        "text": BENEFITS_DOCUMENT_CONTEXT_PROMPT.format(doc_content=full_benefits_doc),
                        "cache_control": {"type": "ephemeral"}  # Cache the full benefits doc
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

def add_contextual_information(input_file, output_file, original_markdown_file):
    """
    Process all benefits chunks to add contextual information
    """
    # Load the chunked JSON data
    with open(input_file, 'r') as f:
        chunks = json.load(f)
    
    # Load the original full markdown document for context
    with open(original_markdown_file, 'r') as f:
        full_benefits_doc = f.read()
    
    print(f"Processing {len(chunks)} benefits chunks...")
    
    enhanced_chunks = []
    
    for chunk in tqdm(chunks, desc="Adding contextual information"):
        try:
            # Generate situational context
            situational_context = situate_benefits_context(
                full_benefits_doc=full_benefits_doc,
                chunk_heading=chunk['chunk_heading'],
                chunk_content=chunk['text']
            )
            
            # Create enhanced chunk
            enhanced_chunk = {
                "chunk_link": chunk["chunk_link"],
                "chunk_heading": chunk["chunk_heading"],
                "text": chunk["text"],
                "situational_context": situational_context
            }
            
            enhanced_chunks.append(enhanced_chunk)
            
        except Exception as e:
            print(f"Error processing chunk '{chunk['chunk_heading']}': {e}")
            # Add chunk without context if there's an error
            enhanced_chunks.append(chunk)
    
    # Save the enhanced chunks
    with open(output_file, 'w') as f:
        json.dump(enhanced_chunks, f, indent=2)
    
    print(f"Contextual information added! Enhanced chunks saved to {output_file}")
    return enhanced_chunks

def preview_contextual_chunks(chunks, num_chunks=2):
    """Preview the contextual information added to chunks"""
    print(f"\nPreview of contextual information for first {num_chunks} chunks:")
    print("=" * 60)
    
    for i, chunk in enumerate(chunks[:num_chunks]):
        print(f"\nChunk {i+1}: {chunk['chunk_heading']}")
        print(f"Original text length: {len(chunk['text'])} characters")
        if 'situational_context' in chunk:
            print(f"Situational Context: {chunk['situational_context']}")
        print("-" * 40)
