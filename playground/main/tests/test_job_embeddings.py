#!/usr/bin/env python3
"""
Script to test loading and searching job description embeddings from pickle files.
Similar to the notebook example but for job descriptions.
"""

import json
from vector_db import VectorDB, ContextualVectorDB
import config

def test_regular_job_embeddings():
    """Test loading and searching regular job embeddings from pickle file."""
    
    print("📖 Loading job descriptions data from regular embeddings...")
    
    # Initialize VectorDB - it will automatically load from pickle if it exists
    job_db = VectorDB("job_descriptions")
    
    # The pickle file should already exist, so this will load from disk
    # If you want to force loading from disk, you can call job_db.load_db() directly
    try:
        job_db.load_db()  # Load from ./data/job_descriptions/vector_db.pkl
        print(f"✅ Loaded job descriptions from pickle file")
        print(f"📊 Total chunks: {len(job_db.embeddings)}")
        
        return job_db
        
    except Exception as e:
        print(f"❌ Error loading regular embeddings: {e}")
        return None

def test_contextual_job_embeddings():
    """Test loading and searching contextual job embeddings from pickle file."""
    
    print("\n📖 Loading job descriptions data from contextual embeddings...")
    
    # Initialize ContextualVectorDB - it will automatically load from pickle if it exists  
    contextual_job_db = ContextualVectorDB("job_descriptions_contextual")
    
    try:
        contextual_job_db.load_db()  # Load from ./data/job_descriptions_contextual/contextual_vector_db.pkl
        print(f"✅ Loaded contextual job descriptions from pickle file")
        print(f"📊 Total chunks: {len(contextual_job_db.embeddings)}")
        
        return contextual_job_db
        
    except Exception as e:
        print(f"❌ Error loading contextual embeddings: {e}")
        return None

def run_search_tests(db, db_type="regular"):
    """Run search tests on the loaded database."""
    
    if db is None:
        print(f"❌ Cannot run tests - {db_type} database not loaded")
        return
    
    print(f"\n🔍 Testing {db_type} job search functionality...")
    print("=" * 50)
    
    # Test queries
    test_queries = [
        "python software engineer",
        "frontend react developer", 
        "product manager remote",
        "marketing manager growth",
        "data scientist machine learning",
        "business development sales",
        "ui ux designer",
        "legal counsel crypto",
    ]
    
    for query in test_queries:
        print(f"\n🔎 Query: '{query}'")
        try:
            results = db.search(query, k=5)
            
            for i, result in enumerate(results[:3], 1):
                metadata = result['metadata']
                similarity = result['similarity']
                
                # Extract job information from metadata
                job_title = metadata.get('job_title', metadata.get('content', 'Unknown')[:50])
                department = metadata.get('department', 'Unknown')
                section_type = metadata.get('section_type', 'Unknown')
                seniority = metadata.get('seniority', 'N/A')
                
                print(f"  {i}. {job_title}")
                print(f"     Department: {department} | Section: {section_type} | Level: {seniority}")
                print(f"     Similarity: {similarity:.3f}")
                
        except Exception as e:
            print(f"     ❌ Search error: {e}")
    
    return results

def compare_search_results(regular_db, contextual_db, query):
    """Compare search results between regular and contextual embeddings."""
    
    if not regular_db or not contextual_db:
        print("❌ Both databases needed for comparison")
        return
    
    print(f"\n🆚 Comparing search results for: '{query}'")
    print("=" * 60)
    
    try:
        regular_results = regular_db.search(query, k=3)
        contextual_results = contextual_db.search(query, k=3)
        
        print("\n📊 REGULAR EMBEDDINGS:")
        for i, result in enumerate(regular_results, 1):
            metadata = result['metadata']
            job_title = metadata.get('job_title', 'Unknown')[:40]
            similarity = result['similarity']
            print(f"  {i}. {job_title} (sim: {similarity:.3f})")
        
        print("\n🧠 CONTEXTUAL EMBEDDINGS:")
        for i, result in enumerate(contextual_results, 1):
            metadata = result['metadata']
            job_title = metadata.get('job_title', 'Unknown')[:40]
            similarity = result['similarity']
            print(f"  {i}. {job_title} (sim: {similarity:.3f})")
            
    except Exception as e:
        print(f"❌ Comparison error: {e}")

def main():
    """Main function to demonstrate loading and testing job embeddings."""
    
    print("🎯 Job Descriptions Embedding Tester")
    print("=" * 50)
    
    # Test regular embeddings
    regular_db = test_regular_job_embeddings()
    
    # Test contextual embeddings  
    contextual_db = test_contextual_job_embeddings()
    
    # Run search tests on regular embeddings
    if regular_db:
        run_search_tests(regular_db, "regular")
    
    # Run search tests on contextual embeddings
    if contextual_db:
        run_search_tests(contextual_db, "contextual")
    
    # Compare results for a specific query
    if regular_db and contextual_db:
        compare_search_results(regular_db, contextual_db, "senior frontend engineer react")
    
    print("\n✨ Testing complete!")
    
    # Return databases for interactive use
    return regular_db, contextual_db

if __name__ == "__main__":
    # Run the tests
    regular_db, contextual_db = main()
    
    # Example of how to use the databases interactively
    print("\n" + "=" * 60)
    print("💡 Interactive Usage Examples:")
    print("=" * 60)
    print("# Search regular embeddings:")
    print("regular_results = regular_db.search('python developer', k=5)")
    print()
    print("# Search contextual embeddings:")  
    print("contextual_results = contextual_db.search('python developer', k=5)")
    print()
    print("# Access result metadata:")
    print("for result in regular_results:")
    print("    metadata = result['metadata']")
    print("    print(f\"Job: {metadata.get('job_title', 'Unknown')}\")")
    print("    print(f\"Department: {metadata.get('department', 'Unknown')}\")")
    print("    print(f\"Similarity: {result['similarity']:.3f}\")") 