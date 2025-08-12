import json
import sys
import os
from typing import List, Dict, Any, Optional

import anthropic
from vector_db import VectorDB 
from config import ANTHROPIC_API_KEY, ANSWER_MODEL

class JobGenerator:
    """Generate job descriptions using existing jobs as context."""
    
    def __init__(self, vector_db_name: str = "job_descriptions", verbose: bool = True):
        self.anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.verbose = verbose
        
        if self.verbose:
            print(f"Loading vector database: {vector_db_name}")
        
        self.vector_db = VectorDB(name=vector_db_name)
        self.vector_db.load_db()
        
        if self.verbose:
            print(f"Loaded {len(self.vector_db.embeddings)} job descriptions")
    
    def generate(self, 
                job_title: str,
                department: str,
                key_requirements: List[str],
                seniority_level: str = None,
                key_skills: List[str] = None,
                num_context_jobs: int = 5) -> Dict[str, Any]:
        """Generate a job description with minimal parameters."""
        
        # Search for similar jobs
        search_query = f"{job_title} {department}"
        if key_skills:
            search_query += " " + " ".join(key_skills)
            
        results = self.vector_db.search(search_query, k=num_context_jobs)
        
        # Build context
        context_jobs = []
        for result in results:
            metadata = result['metadata']
            context_jobs.append(f"Job Title: {metadata.get('job_title', 'Unknown')}\n{metadata.get('content', '')}")
        
        # Generate with Claude
        prompt = f"""Create a job description using these examples as context:

{chr(10).join([f"=== EXAMPLE {i+1} ==={chr(10)}{job}{chr(10)}" for i, job in enumerate(context_jobs)])}

NEW JOB:
- Title: {job_title}
- Department: {department}
- Requirements: {", ".join(key_requirements)}
- Seniority: {seniority_level or 'Not specified'}
- Skills: {", ".join(key_skills or [])}

Consider the crypto/blockchain industry context - fast-paced, innovative, regulatory considerations, global/remote-friendly culture.

Format as:
**Job Description:**
[intro paragraph]

**Key Responsibilities:**
• [responsibility 1]
• [responsibility 2]

**Requirements:**
• [requirement 1] 
• [requirement 2]

**Nice to Have:**
• [nice to have 1]"""

        response = self.anthropic_client.messages.create(
            model=ANSWER_MODEL,
            max_tokens=2000,
            temperature=0,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse response
        generated_content = response.content[0].text
        job_description = self._parse_response(generated_content, job_title, department, seniority_level, key_skills or [])
        
        if self.verbose:
            self._display_job(job_description)
        
        return job_description
    
    def _parse_response(self, content: str, job_title: str, department: str, seniority: str, skills: List[str]) -> Dict[str, Any]:
        """Parse Claude's response into structured format."""
        sections = {'intro': '', 'responsibilities': [], 'requirements': [], 'nice_to_haves': []}
        
        current_section = None
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if '**Job Description:**' in line:
                current_section = 'intro'
            elif '**Key Responsibilities:**' in line:
                current_section = 'responsibilities'
            elif '**Requirements:**' in line:
                current_section = 'requirements'
            elif '**Nice to Have:**' in line:
                current_section = 'nice_to_haves'
            elif current_section == 'intro':
                sections['intro'] += line + ' '
            elif current_section in ['responsibilities', 'requirements', 'nice_to_haves']:
                clean_line = line.lstrip('•-*').strip()
                if clean_line:
                    sections[current_section].append(clean_line)
        
        return {
            'job_id': f"generated_{job_title.lower().replace(' ', '_')}",
            'title': job_title,
            'department': department,
            'metadata': {'seniority': seniority, 'skills': skills, 'generated': True},
            'sections': sections
        }
    
    def _display_job(self, job_desc: Dict[str, Any]):
        """Display job description nicely formatted."""
        print(f"\n{'='*60}")
        print(f"📄 {job_desc['title']} - {job_desc['department']}")
        print(f"{'='*60}")
        
        print(f"\n**Job Description:**\n{job_desc['sections']['intro'].strip()}")
        
        print(f"\n**Key Responsibilities:**")
        for resp in job_desc['sections']['responsibilities']:
            print(f"• {resp}")
        
        print(f"\n**Requirements:**")
        for req in job_desc['sections']['requirements']:
            print(f"• {req}")
        
        if job_desc['sections']['nice_to_haves']:
            print(f"\n**Nice to Have:**")
            for nice in job_desc['sections']['nice_to_haves']:
                print(f"• {nice}")

# Simple usage function for notebooks
def generate_job_description(job_title: str, 
                           department: str,
                           requirements: List[str],
                           seniority: str = None,
                           skills: List[str] = None) -> Dict[str, Any]:
    """Quick function to generate a job description."""
    generator = JobGenerator(verbose=True)
    return generator.generate(job_title, department, requirements, seniority, skills)