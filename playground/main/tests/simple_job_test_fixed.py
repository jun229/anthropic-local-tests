#!/usr/bin/env python3
"""
Fixed job embeddings test - properly extracts job info from content.
"""

import json
import re
from vector_db import VectorDB, ContextualVectorDB
import config

def extract_job_info(content):
    """Extract job title and department from the content string."""
    job_title = "Unknown"
    department = "Unknown"
    
    # Extract job title
    title_match = re.search(r"Job Title:\s*(.+)", content)
    if title_match:
        job_title = title_match.group(1).strip()
    
    # Extract department
    dept_match = re.search(r"Department:\s*(.+)", content)
    if dept_match:
        department = dept_match.group(1).strip()
    
    return job_title, department

# Load job descriptions data from regular embeddings
print("📖 Loading job descriptions data...")

# Initialize and load regular VectorDB (similar to your example)
job_db = VectorDB("job_descriptions")
job_db.load_db()  # This loads from ./data/job_descriptions/vector_db.pkl

print(f"✅ Loaded {len(job_db.embeddings)} chunks into job descriptions VectorDB")

# Test a search
query = "python software engineer"
results = job_db.search(query, k=5)

print(f"\n🔍 Search results for '{query}':")
for i, result in enumerate(results[:3], 1):
    metadata = result['metadata']
    similarity = result['similarity']
    content = metadata.get('content', '')
    
    # Extract job info from content
    job_title, department = extract_job_info(content)
    
    print(f"  {i}. {job_title} ({department}) - similarity: {similarity:.3f}")
    # Show a snippet of the content
    content_snippet = content[:150] + "..." if len(content) > 150 else content
    print(f"     Preview: {content_snippet}")

# Load contextual embeddings (optional)
print("\n📖 Loading contextual job descriptions data...")
contextual_job_db = ContextualVectorDB("job_descriptions_contextual") 
contextual_job_db.load_db()  # This loads from ./data/job_descriptions_contextual/contextual_vector_db.pkl

print(f"✅ Loaded {len(contextual_job_db.embeddings)} chunks into contextual job descriptions VectorDB")

# Test same search with contextual embeddings
contextual_results = contextual_job_db.search(query, k=5)

print(f"\n🧠 Contextual search results for '{query}':")
for i, result in enumerate(contextual_results[:3], 1):
    metadata = result['metadata']
    similarity = result['similarity']
    
    # For contextual, use original_content if available, otherwise content
    content = metadata.get('original_content', metadata.get('content', ''))
    job_title, department = extract_job_info(content)
    
    print(f"  {i}. {job_title} ({department}) - similarity: {similarity:.3f}")
    # Show a snippet of the content
    content_snippet = content[:150] + "..." if len(content) > 150 else content
    print(f"     Preview: {content_snippet}")

# Additional test queries
print("\n" + "="*60)
print("🎯 Testing various job search queries:")
print("="*60)

test_queries = [
    "frontend react developer",
    "data scientist machine learning", 
    "product manager",
    "marketing growth",
    "legal counsel"
]

for query in test_queries:
    print(f"\n🔎 Query: '{query}'")
    results = job_db.search(query, k=2)
    
    for i, result in enumerate(results, 1):
        metadata = result['metadata']
        similarity = result['similarity']
        content = metadata.get('content', '')
        job_title, department = extract_job_info(content)
        
        print(f"  {i}. {job_title} ({department}) - sim: {similarity:.3f}")

print(f"\n✨ Testing complete! You now have working examples of:")
print(f"- Regular embeddings: job_db.search('your query', k=5)")  
print(f"- Contextual embeddings: contextual_job_db.search('your query', k=5)")

# Return the databases for interactive use
globals()['job_db'] = job_db
globals()['contextual_job_db'] = contextual_job_db
print(f"\n💡 Databases are now available as 'job_db' and 'contextual_job_db' variables") 