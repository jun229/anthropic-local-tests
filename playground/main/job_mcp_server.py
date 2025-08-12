#!/usr/bin/env python3
import sys
import os
import json
import asyncio

# Debug output - make sure this appears in Claude's logs
print("=== MCP Server Debug Start ===", file=sys.stderr)
print(f"Python executable: {sys.executable}", file=sys.stderr)
print(f"Python version: {sys.version}", file=sys.stderr)
print(f"Python path: {sys.path}", file=sys.stderr)
print(f"Current directory: {os.getcwd()}", file=sys.stderr)
print(f"Environment PATH: {os.environ.get('PATH', 'Not set')}", file=sys.stderr)

# Add the current directory to Python path to ensure local imports work
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)
    print(f"Added to Python path: {script_dir}", file=sys.stderr)

try:
    print("=== Starting imports ===", file=sys.stderr)
    
    print("Importing MCP modules...", file=sys.stderr)
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    print("MCP modules imported successfully", file=sys.stderr)
    
    print("Importing local modules...", file=sys.stderr)
    from jd_items.job_description_generator import JobGenerator
    from vector_db import VectorDB
    print("Local modules imported successfully", file=sys.stderr)
    
    print("=== All imports successful ===", file=sys.stderr)
    
except Exception as e:
    print(f"=== CRITICAL IMPORT ERROR: {e} ===", file=sys.stderr)
    print(f"Error type: {type(e).__name__}", file=sys.stderr)
    import traceback
    print(f"Traceback:\n{traceback.format_exc()}", file=sys.stderr)
    sys.exit(1)

print("=== Creating server instance ===", file=sys.stderr)
try:
    server = Server("job-generator")
    print("Server instance created successfully", file=sys.stderr)
except Exception as e:
    print(f"=== SERVER CREATION ERROR: {e} ===", file=sys.stderr)
    import traceback
    print(f"Traceback:\n{traceback.format_exc()}", file=sys.stderr)
    sys.exit(1)

print("=== Initializing JobGenerator ===", file=sys.stderr)
try:
    generator = JobGenerator(verbose=False)
    print("JobGenerator initialized successfully", file=sys.stderr)
except Exception as e:
    print(f"=== JOBGENERATOR INIT ERROR: {e} ===", file=sys.stderr)
    import traceback
    print(f"Traceback:\n{traceback.format_exc()}", file=sys.stderr)
    sys.exit(1)

# Define available tools
@server.list_tools()
async def list_tools():
    print("=== list_tools() called ===", file=sys.stderr)
    try:
        tools = [
            Tool(
                name="generate_job_description",
                description="Generate a new job description",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "job_title": {"type": "string", "description": "Job title"},
                        "department": {"type": "string", "description": "Department name"},
                        "requirements": {"type": "string", "description": "Comma-separated key requirements"}
                    },
                    "required": ["job_title", "department", "requirements"]
                }
            ),
            Tool(
                name="search_similar_jobs",
                description="Search for similar jobs in the database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"]
                }
            )
        ]
        print(f"=== Returning {len(tools)} tools ===", file=sys.stderr)
        return tools
    except Exception as e:
        print(f"=== ERROR in list_tools(): {e} ===", file=sys.stderr)
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}", file=sys.stderr)
        raise

# Handle tool calls
@server.call_tool()
async def call_tool(name: str, arguments: dict):
    print(f"=== call_tool() called with: {name}, args: {arguments} ===", file=sys.stderr)
    
    try:
        if name == "generate_job_description":
            job_title = arguments["job_title"]
            department = arguments["department"]
            requirements = arguments["requirements"]
            
            req_list = [r.strip() for r in requirements.split(',')]
            print(f"=== Generating job description for: {job_title} ===", file=sys.stderr)
            result = generator.generate(job_title, department, req_list)
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "search_similar_jobs":
            query = arguments["query"]
            print(f"=== Searching similar jobs for: {query} ===", file=sys.stderr)
            results = generator.vector_db.search(query, k=5)
            
            return [TextContent(
                type="text", 
                text=json.dumps(results, indent=2)
            )]
        
        else:
            error_msg = f"Unknown tool: {name}"
            print(f"=== ERROR: {error_msg} ===", file=sys.stderr)
            raise ValueError(error_msg)
            
    except Exception as e:
        print(f"=== ERROR in call_tool(): {e} ===", file=sys.stderr)
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}", file=sys.stderr)
        raise

async def main():
    print("=== Starting main() function ===", file=sys.stderr)
    try:
        print("=== Creating stdio_server ===", file=sys.stderr)
        async with stdio_server() as streams:
            print("=== stdio_server created, starting server.run() ===", file=sys.stderr)
            await server.run(
                streams[0], streams[1], 
                initialization_options={}
            )
            print("=== server.run() completed ===", file=sys.stderr)
    except Exception as e:
        print(f"=== ERROR in main(): {e} ===", file=sys.stderr)
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}", file=sys.stderr)
        raise

if __name__ == "__main__":
    print("=== Starting asyncio.run(main()) ===", file=sys.stderr)
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"=== FINAL ERROR: {e} ===", file=sys.stderr)
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}", file=sys.stderr)
        sys.exit(1)
    print("=== MCP Server exiting normally ===", file=sys.stderr)