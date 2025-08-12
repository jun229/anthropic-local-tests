#!/usr/bin/env python3
"""
Job Description Converter
Converts structured .txt job files into JSON format for RAG processing
"""

import os
import json
import re
from typing import Dict, List, Any
from pathlib import Path

def extract_skills_from_text(text: str) -> List[str]:
    """Extract potential skills from text using common patterns"""
    if not text:
        return []
    
    # Common tech skills and tools
    skill_patterns = [
        r'\b(?:Python|JavaScript|TypeScript|Java|Go|Golang|Rust|C\+\+|React|Vue|Angular|Node\.js)\b',
        r'\b(?:AWS|Azure|GCP|Docker|Kubernetes|Jenkins|Git|SQL|NoSQL|MongoDB|PostgreSQL)\b',
        r'\b(?:API|REST|GraphQL|Microservices|Machine Learning|AI|Data Science|Analytics)\b',
        r'\b(?:Figma|Sketch|Adobe|Photoshop|Design|UX|UI|Product Management|Agile|Scrum)\b',
        r'\b(?:Marketing|Sales|Business Development|Strategy|Operations|Finance|Legal)\b'
    ]
    
    skills = set()
    text_upper = text  # Keep original case for extraction
    
    for pattern in skill_patterns:
        matches = re.findall(pattern, text_upper, re.IGNORECASE)
        skills.update([match.strip() for match in matches])
    
    # Also look for "X+ years" patterns to extract experience requirements
    exp_matches = re.findall(r'(\d+)\+?\s*years?\s+(?:of\s+)?(?:experience|exp)', text, re.IGNORECASE)
    if exp_matches:
        skills.add(f"{max(exp_matches)}+ years experience")
    
    return sorted(list(skills))

def determine_seniority(title: str, requirements: List[str]) -> str:
    """Determine seniority level from title and requirements"""
    title_lower = title.lower()
    
    if any(word in title_lower for word in ['senior', 'sr', 'lead', 'principal', 'staff']):
        return 'senior'
    elif any(word in title_lower for word in ['junior', 'jr', 'entry', 'associate', 'intern']):
        return 'junior'
    
    # Check requirements for experience indicators
    requirements_text = ' '.join(requirements).lower()
    exp_matches = re.findall(r'(\d+)\+?\s*years?', requirements_text)
    if exp_matches:
        max_exp = max([int(x) for x in exp_matches])
        if max_exp >= 5:
            return 'senior'
        elif max_exp >= 2:
            return 'mid'
        else:
            return 'junior'
    
    return 'mid'  # default

def extract_salary_info(text: str) -> str:
    """Extract salary information from text"""
    # Look for salary patterns
    salary_patterns = [
        r'\$[\d,]+k?-\$[\d,]+k?',
        r'\$[\d,]+\s*-\s*\$[\d,]+',
        r'salary.*\$[\d,]+',
        r'\$[\d,]+k?\+?'
    ]
    
    for pattern in salary_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    
    return ""

def parse_job_file(file_path: str) -> Dict[str, Any]:
    """Parse a single job .txt file into structured data"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Initialize structure
    job_data = {
        "job_id": "",
        "title": "",
        "department": "",
        "sections": {
            "intro": "",
            "responsibilities": [],
            "requirements": [],
            "nice_to_haves": []
        },
        "metadata": {
            "seniority": "",
            "skills": [],
            "salary_range": "",
            "file_path": file_path
        }
    }
    
    # Extract title and department
    title_match = re.search(r'TITLE:\s*(.+)', content)
    dept_match = re.search(r'DEPARTMENT:\s*(.+)', content)
    
    if title_match:
        job_data["title"] = title_match.group(1).strip()
        job_data["job_id"] = re.sub(r'[^\w\s-]', '', job_data["title"].lower().replace(' ', '_'))
    
    if dept_match:
        job_data["department"] = dept_match.group(1).strip()
    
    # Extract sections
    sections = content.split('---')
    current_section = None
    
    for i, section in enumerate(sections):
        section = section.strip()
        if not section:
            continue
            
        if section.startswith('INTRO'):
            # Find the content after this section header
            remaining_content = '---'.join(sections[i+1:])
            next_section_pos = remaining_content.find('---')
            if next_section_pos != -1:
                content_part = remaining_content[:next_section_pos].strip()
            else:
                content_part = remaining_content.strip()
            job_data["sections"]["intro"] = content_part
            
        elif section.startswith('RESPONSIBILITIES'):
            # Find the content after this section header
            remaining_content = '---'.join(sections[i+1:])
            next_section_pos = remaining_content.find('---')
            if next_section_pos != -1:
                content_part = remaining_content[:next_section_pos].strip()
            else:
                content_part = remaining_content.strip()
            # Split by lines starting with '-'
            items = [line.strip()[1:].strip() for line in content_part.split('\n') 
                    if line.strip().startswith('-') and len(line.strip()) > 1]
            job_data["sections"]["responsibilities"] = items
            
        elif section.startswith('REQUIREMENTS'):
            # Find the content after this section header
            remaining_content = '---'.join(sections[i+1:])
            next_section_pos = remaining_content.find('---')
            if next_section_pos != -1:
                content_part = remaining_content[:next_section_pos].strip()
            else:
                content_part = remaining_content.strip()
            items = [line.strip()[1:].strip() for line in content_part.split('\n') 
                    if line.strip().startswith('-') and len(line.strip()) > 1]
            job_data["sections"]["requirements"] = items
            
        elif section.startswith('NICE_TO_HAVES'):
            # Find the content after this section header
            remaining_content = '---'.join(sections[i+1:])
            next_section_pos = remaining_content.find('---')
            if next_section_pos != -1:
                content_part = remaining_content[:next_section_pos].strip()
            else:
                # Find the end marker
                end_pos = remaining_content.find('===JD_END===')
                if end_pos != -1:
                    content_part = remaining_content[:end_pos].strip()
                else:
                    content_part = remaining_content.strip()
            items = [line.strip()[1:].strip() for line in content_part.split('\n') 
                    if line.strip().startswith('-') and len(line.strip()) > 1]
            job_data["sections"]["nice_to_haves"] = items
    
    # Extract metadata
    all_text = f"{job_data['sections']['intro']} {' '.join(job_data['sections']['requirements'])} {' '.join(job_data['sections']['responsibilities'])}"
    
    job_data["metadata"]["skills"] = extract_skills_from_text(all_text)
    job_data["metadata"]["seniority"] = determine_seniority(job_data["title"], job_data["sections"]["requirements"])
    job_data["metadata"]["salary_range"] = extract_salary_info(all_text)
    
    return job_data

def convert_department_folder(folder_path: str, department_name: str) -> List[Dict[str, Any]]:
    """Convert all .txt files in a department folder to structured data"""
    
    jobs = []
    txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
    
    print(f"  📄 Processing {len(txt_files)} jobs in {department_name}")
    
    for txt_file in txt_files:
        file_path = os.path.join(folder_path, txt_file)
        try:
            job_data = parse_job_file(file_path)
            jobs.append(job_data)
        except Exception as e:
            print(f"    ❌ Error processing {txt_file}: {e}")
    
    return jobs

def main():
    """Main conversion function"""
    
    # Paths (relative to the main/ directory where this script runs)
    source_dir = "../../greenhouse_data/parsed_jobs_final"
    output_dir = "data/job_descriptions"  # Create subfolder for job descriptions
    
    print("🔄 Converting job description files to JSON format...")
    print(f"📁 Source: {source_dir}")
    print(f"📁 Output: {output_dir}")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all department folders
    department_folders = [d for d in os.listdir(source_dir) 
                         if os.path.isdir(os.path.join(source_dir, d))]
    
    print(f"\n📂 Found {len(department_folders)} departments to convert:")
    
    total_jobs = 0
    conversion_summary = {}
    
    for dept_folder in sorted(department_folders):
        folder_path = os.path.join(source_dir, dept_folder)
        
        # Convert department name back to readable format
        dept_display = dept_folder.replace('_', ' ').title()
        print(f"\n🏢 Converting {dept_display}...")
        
        # Convert all jobs in this department
        jobs = convert_department_folder(folder_path, dept_display)
        
        if jobs:
            # Save as JSON
            output_file = os.path.join(output_dir, f"{dept_folder}.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(jobs, f, indent=2, ensure_ascii=False)
            
            conversion_summary[dept_display] = len(jobs)
            total_jobs += len(jobs)
            print(f"  ✅ Saved {len(jobs)} jobs to job_descriptions/{dept_folder}.json")
        else:
            print(f"  ⚠️  No jobs found in {dept_folder}")
    
    # Print summary
    print(f"\n🎉 Conversion Complete!")
    print(f"📊 Total jobs converted: {total_jobs}")
    print(f"📁 JSON files created in: {output_dir}/")
    
    print(f"\n📈 Jobs by department:")
    for dept, count in sorted(conversion_summary.items()):
        print(f"  {dept}: {count} jobs")
    
    # Show sample of first department for verification
    if conversion_summary:
        sample_dept = list(conversion_summary.keys())[0]
        sample_file = os.path.join(output_dir, f"{sample_dept.lower().replace(' ', '_')}.json")
        
        if os.path.exists(sample_file):
            with open(sample_file, 'r') as f:
                sample_data = json.load(f)
            
            print(f"\n🔍 Sample from {sample_dept}:")
            if sample_data:
                sample_job = sample_data[0]
                print(f"  Title: {sample_job.get('title', 'N/A')}")
                print(f"  Skills: {sample_job.get('metadata', {}).get('skills', [])[:5]}")
                print(f"  Seniority: {sample_job.get('metadata', {}).get('seniority', 'N/A')}")
                
        print(f"\n📂 Files are now organized in: data/job_descriptions/")
        print("   This keeps job data separate from other RAG datasets!")

if __name__ == "__main__":
    main() 