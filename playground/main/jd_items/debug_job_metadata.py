#!/usr/bin/env python3
"""
Debug script to check metadata structure in job embeddings.
"""

import json
from vector_db import VectorDB, ContextualVectorDB

# Load and inspect regular embeddings
print("🔍 Debugging regular embeddings metadata...")
job_db = VectorDB("job_descriptions")
job_db.load_db()

print(f"Total chunks: {len(job_db.metadata)}")
print("\nFirst chunk metadata:")
print(json.dumps(job_db.metadata[0], indent=2))

print("\nSecond chunk metadata:")
print(json.dumps(job_db.metadata[1], indent=2))

# Search and inspect results
results = job_db.search("python engineer", k=3)
print(f"\nSearch results metadata:")
for i, result in enumerate(results):
    print(f"\nResult {i+1}:")
    print(f"Similarity: {result['similarity']:.3f}")
    print(f"Metadata keys: {list(result['metadata'].keys())}")
    print(f"Metadata: {json.dumps(result['metadata'], indent=2)}")
    
# Load contextual and check
print("\n" + "="*50)
print("🧠 Debugging contextual embeddings metadata...")
contextual_db = ContextualVectorDB("job_descriptions_contextual")
contextual_db.load_db()

print(f"Total chunks: {len(contextual_db.metadata)}")
print("\nFirst chunk metadata:")
print(json.dumps(contextual_db.metadata[0], indent=2)) 