from openai import OpenAI
from supabase import create_client
from dotenv import load_dotenv
import json
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def embed_benefits_chunks():
    """
    Embed the first 3 chunks from benefits_wellbeing_with_context.json 
    into Supabase test_chunks table
    """
    
    # Initialize clients
    print("🔧 Initializing clients...")
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Load the benefits data
    print("📂 Loading benefits data...")
    with open("data/benefits_wellbeing_with_context.json", "r") as f:
        benefits_data = json.load(f)
    
    # Take first 3 chunks for testing
    test_chunks = benefits_data[:3]
    print(f"📊 Processing {len(test_chunks)} chunks...")
    
    # Process each chunk
    for i, chunk in enumerate(test_chunks):
        print(f"\n🔄 Processing chunk {i+1}: {chunk['chunk_heading']}")
        
        # Prepare content for embedding (combine heading + text for better context)
        embedding_content = f"{chunk['chunk_heading']}\n\n{chunk['text']}"
        
        # Generate embedding
        print(f"🧠 Generating embedding for '{chunk['chunk_heading']}'...")
        try:
            response = openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=embedding_content
            )
            embedding = response.data[0].embedding
            print(f"✅ Generated embedding with {len(embedding)} dimensions")
            
        except Exception as e:
            print(f"❌ Error generating embedding: {e}")
            continue
        
        # Prepare data for insertion
        chunk_data = {
            "source_file": "benefits_wellbeing_with_context.json",
            "chunk_index": i,
            "chunk_heading": chunk["chunk_heading"],
            "content": chunk["text"],
            "situational_context": chunk["situational_context"],
            "embedding": embedding
        }
        
        # Insert into Supabase
        print(f"💾 Inserting chunk into Supabase...")
        try:
            result = supabase.table("test_chunks").insert(chunk_data).execute()
            print(f"✅ Successfully inserted chunk: {chunk['chunk_heading']}")
            
        except Exception as e:
            print(f"❌ Error inserting into Supabase: {e}")
            continue
    
    print(f"\n🎉 Completed embedding {len(test_chunks)} chunks into Supabase!")
    
    # Test a simple query
    print("\n🔍 Testing retrieval...")
    try:
        test_query = supabase.table("test_chunks").select("*").execute()
        print(f"📊 Found {len(test_query.data)} chunks in database")
        for chunk in test_query.data:
            print(f"  - {chunk['chunk_heading']} (ID: {chunk['id'][:8]}...)")
            
    except Exception as e:
        print(f"❌ Error testing retrieval: {e}")

def test_similarity_search(query_text="health insurance plans"):
    """
    Test similarity search functionality
    """
    print(f"\n🔍 Testing similarity search for: '{query_text}'")
    
    # Initialize clients
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    try:
        # Generate embedding for query
        print("🧠 Generating query embedding...")
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=query_text
        )
        query_embedding = response.data[0].embedding
        
        # Search using SQL function (you'll need to create this function in Supabase)
        print("🔍 Searching for similar chunks...")
        
        # For now, let's just get all chunks and calculate similarity in Python
        # In production, you'd use pgvector's similarity functions
        all_chunks = supabase.table("test_chunks").select("*").execute()
        
        print(f"📊 Retrieved {len(all_chunks.data)} chunks for similarity comparison")
        
        # Calculate similarities (basic dot product for demonstration)
        import numpy as np
        similarities = []
        
        for chunk in all_chunks.data:
            if chunk['embedding']:
                similarity = np.dot(query_embedding, chunk['embedding'])
                similarities.append({
                    'chunk': chunk,
                    'similarity': similarity
                })
        
        # Sort by similarity
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        print(f"\n🎯 Top matches for '{query_text}':")
        for i, match in enumerate(similarities[:3]):
            chunk = match['chunk']
            score = match['similarity']
            print(f"  {i+1}. {chunk['chunk_heading']} (similarity: {score:.3f})")
            
    except Exception as e:
        print(f"❌ Error in similarity search: {e}")

if __name__ == "__main__":
    # Run the embedding function
    embed_benefits_chunks()
    
    # Test similarity search
    test_similarity_search("health insurance plans")
    test_similarity_search("vacation time off")





