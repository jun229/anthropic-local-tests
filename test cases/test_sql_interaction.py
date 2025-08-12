#!/usr/bin/env python3
"""
Simple script to interact with your SQL database using Claude
Ask natural language questions and get SQL queries + results
"""

import os
import sqlite3
import anthropic

# Set up Claude
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

class SQLAssistant:
    def __init__(self, db_path="skills/text_to_sql/data/data.db"):
        self.db_path = db_path
        self.connect_db()
        self.get_schema()
    
    def connect_db(self):
        """Connect to the SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            print(f"✅ Connected to database: {self.db_path}")
        except Exception as e:
            print(f"❌ Error connecting to database: {e}")
            exit(1)
    
    def get_schema(self):
        """Get the database schema"""
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()
        
        schema_info = "Database Schema:\n\n"
        for table in tables:
            table_name = table[0]
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            columns = self.cursor.fetchall()
            
            schema_info += f"Table: {table_name}\n"
            for col in columns:
                col_name, col_type = col[1], col[2]
                schema_info += f"  - {col_name} ({col_type})\n"
            schema_info += "\n"
        
        self.schema = schema_info
        print(self.schema)
    
    def ask_question(self, question):
        """Convert natural language question to SQL and execute"""
        print(f"\n🔍 Processing: {question}")
        
        # Ask Claude to generate SQL
        sql_prompt = f"""Given this database schema:

{self.schema}

Convert this natural language question to a SQL query:
"{question}"

Return ONLY the SQL query, no explanations or formatting. Make sure the query is valid SQLite syntax."""
        
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=500,
            messages=[{"role": "user", "content": sql_prompt}]
        )
        
        sql_query = response.content[0].text.strip()
        print(f"\n🔧 Generated SQL:\n{sql_query}")
        
        # Execute the query
        try:
            self.cursor.execute(sql_query)
            results = self.cursor.fetchall()
            
            # Get column names
            column_names = [description[0] for description in self.cursor.description]
            
            print(f"\n📊 Results ({len(results)} rows):")
            if results:
                # Print header
                print(" | ".join(column_names))
                print("-" * (len(" | ".join(column_names))))
                
                # Print results (limit to first 10 rows)
                for i, row in enumerate(results[:10]):
                    print(" | ".join(str(val) for val in row))
                
                if len(results) > 10:
                    print(f"... and {len(results) - 10} more rows")
            else:
                print("No results found")
                
            return results, column_names
            
        except Exception as e:
            print(f"❌ SQL Error: {e}")
            return None, None
    
    def close(self):
        """Close database connection"""
        self.conn.close()

def main():
    print("🤖 Claude SQL Assistant")
    print("Ask natural language questions about your database!")
    print("Type 'quit' to exit\n")
    
    sql_assistant = SQLAssistant()
    
    while True:
        question = input("\n❓ Your question: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not question:
            continue
            
        try:
            sql_assistant.ask_question(question)
        except Exception as e:
            print(f"❌ Error: {e}")
    
    sql_assistant.close()

if __name__ == "__main__":
    main() 