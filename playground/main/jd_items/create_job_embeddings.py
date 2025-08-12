#!/usr/bin/env python3
"""
Script to create vector embeddings for job descriptions.
Transforms job descriptions into vector database format and creates embeddings.
"""

import json
import os
from typing import List, Dict, Any
from pathlib import Path

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vector_db import VectorDB 
from config import OPENAI_API_KEY

"""
============================================================================================
Transform jobs for vector database
============================================================================================
"""
def transform_jobs_for_vectordb(jobs_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    doc = {
        "doc_id": "all_jobs",
        "original_uuid": "all_jobs_uuid",
        "chunks": []
    }
    
    for i, job in enumerate(jobs_data):
        full_content = create_full_job_text(job)
        doc["chunks"].append({
            "chunk_id": job['job_id'],
            "original_index": i,
            "content": full_content,
            "job_id": job['job_id'],
            "job_title": job['title'],
            "department": job['department']
        })
    
    return [doc]

"""
============================================================================================
Create full job text
============================================================================================
"""
def create_full_job_text(job: Dict[str, Any]) -> str:
    """Create a comprehensive text representation of a job."""
    
    sections = []
    
    # Header
    sections.append(f"Job Title: {job['title']}")
    sections.append(f"Department: {job['department']}")
    
    # Metadata
    metadata = job.get('metadata', {})
    if metadata.get('seniority'):
        sections.append(f"Seniority Level: {metadata['seniority']}")
    if metadata.get('skills'):
        sections.append(f"Skills: {', '.join(metadata['skills'])}")
    
    sections.append("")  # Empty line
    
    # Introduction
    if job['sections'].get('intro'):
        sections.append("Job Description:")
        sections.append(job['sections']['intro'])
        sections.append("")
    
    # Responsibilities
    if job['sections'].get('responsibilities'):
        sections.append("Key Responsibilities:")
        for resp in job['sections']['responsibilities']:
            sections.append(f"• {resp}")
        sections.append("")
    
    # Requirements
    if job['sections'].get('requirements'):
        sections.append("Requirements:")
        for req in job['sections']['requirements']:
            sections.append(f"• {req}")
        sections.append("")
    
    # Nice to haves
    if job['sections'].get('nice_to_haves'):
        sections.append("Nice to Have:")
        for nice in job['sections']['nice_to_haves']:
            sections.append(f"• {nice}")
        sections.append("")
    
    return "\n".join(sections)

"""
============================================================================================
Create job embeddings
============================================================================================
"""
def create_job_embeddings(input_file: str = "data/job_descriptions_conglomerate.json"):
    """Create vector embeddings for job descriptions."""
    
    print("🚀 Creating job description embeddings...\n")
    
    # Load job descriptions
    print(f"📖 Loading job descriptions from {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        jobs_data = json.load(f)
    
    print(f"✅ Loaded {len(jobs_data)} job descriptions")
    
    # Transform data for vector database
    print("\n🔄 Transforming job data for vector database...")
    transformed_data = transform_jobs_for_vectordb(jobs_data)
    
    total_chunks = sum(len(doc['chunks']) for doc in transformed_data)
    print(f"✅ Created 1 document with {total_chunks} total chunks")
    
    # Create vector database
    print(f"\n🗄️ Creating vector database: job_descriptions")
    db = VectorDB(name="job_descriptions")
    db.load_data(transformed_data)
    
    print(f"✅ Vector database created and saved!")
    
    # Test search functionality
    print(f"\n🔍 Testing search functionality...")
    test_queries = [
        "software engineer python",
        "marketing manager", 
        "product design",
        "business development sales"
    ]

    for query in test_queries:
        results = db.search(query, k=3)
        print(f"\nQuery: '{query}'")
        for i, result in enumerate(results[:2], 1):
            metadata = result['metadata']
            similarity = result['similarity']
            job_title = metadata.get('job_title', 'Unknown')
            department = metadata.get('department', 'Unknown')
            print(f"  {i}. {job_title} ({department}) (similarity: {similarity:.3f})")
    
    return db

"""
============================================================================================
Call the main function
============================================================================================
"""

def main():
    print("🎯 Job Descriptions Embedding Creator")
    print("=" * 50)
    
    print("\n1️⃣ Creating vector embeddings...")
    db = create_job_embeddings()
    
    print("\n✨ Job embedding creation complete!")

if __name__ == "__main__":
    main() 