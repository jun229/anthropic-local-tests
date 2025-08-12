#!/usr/bin/env python3
"""
Simple job embeddings test - similar to the notebook example format.
"""

import json
from vector_db import VectorDB, ContextualVectorDB
import config

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
    job_title = metadata.get('job_title', 'Unknown')
    department = metadata.get('department', 'Unknown')
    print(f"  {i}. {job_title} ({department}) - similarity: {similarity:.3f}")

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
    job_title = metadata.get('job_title', 'Unknown')
    department = metadata.get('department', 'Unknown')
    print(f"  {i}. {job_title} ({department}) - similarity: {similarity:.3f}") 