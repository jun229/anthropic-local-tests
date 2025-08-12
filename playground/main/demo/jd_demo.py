#!/usr/bin/env python3
"""
Interactive Job Description Generator Demo

A terminal script that demonstrates interactive job description generation
using the JobGenerator class and vector database search.

Run with: python3 jd_demo.py
"""

import os
import sys
import json
import textwrap
from typing import Dict, List, Optional

# Get the directory of this script and navigate to parent directory for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)

# Change to the parent directory so VectorDB can find the data files
original_cwd = os.getcwd()
os.chdir(parent_dir)

# Import the job generator and vector database
try:
    from jd_items.job_description_generator import JobGenerator, generate_job_description
    from vector_db import VectorDB
    GENERATOR_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warning: Could not import job generator: {e}")
    GENERATOR_AVAILABLE = False

def safe_exit(code=0):
    """Exit safely while restoring the original working directory."""
    os.chdir(original_cwd)
    sys.exit(code)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_header(current_job=""):
    print("=" * 70)
    print("🎯 INTERACTIVE JOB DESCRIPTION GENERATOR")
    if current_job:
        print(f"📋 Current Job: {current_job}")
    print("=" * 70)
    print()

def get_user_choice(prompt: str, choices: List[str]) -> int:
    """Display choices and get user selection"""
    print(prompt)
    print()
    for i, choice in enumerate(choices, 1):
        print(f"{i}. {choice}")
    print()
    
    while True:
        try:
            choice = int(input("Enter your choice (number): "))
            if 1 <= choice <= len(choices):
                return choice - 1
            else:
                print(f"Please enter a number between 1 and {len(choices)}")
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            safe_exit(0)

def get_user_input(prompt: str, required: bool = True) -> str:
    """Get user input with optional requirement check"""
    while True:
        try:
            value = input(prompt).strip()
            if required and not value:
                print("This field is required. Please enter a value.")
                continue
            return value
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            safe_exit(0)

def get_list_input(prompt: str, min_items: int = 1) -> List[str]:
    """Get comma-separated list input from user"""
    while True:
        try:
            print(prompt)
            print("Enter items separated by commas:")
            value = input("> ").strip()
            if not value and min_items > 0:
                print(f"Please enter at least {min_items} item(s).")
                continue
            
            items = [item.strip() for item in value.split(',') if item.strip()]
            if len(items) < min_items:
                print(f"Please enter at least {min_items} item(s).")
                continue
            
            return items
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            safe_exit(0)

def display_job_description(job_desc: Dict):
    """Display a job description in formatted style with clear separators"""
    print(f"\n{'='*70}")
    print(f"📄 {job_desc['title']} - {job_desc['department']}")
    print(f"{'='*70}")
    
    # Separator for the actual job description content
    print(f"\n{'🎯 JOB DESCRIPTION CONTENT':^70}")
    print(f"{'─'*70}")
    
    if job_desc['sections'].get('intro'):
        print(f"\n**Job Description:**")
        print(f"{job_desc['sections']['intro'].strip()}")
    
    if job_desc['sections'].get('responsibilities'):
        print(f"\n**Key Responsibilities:**")
        for resp in job_desc['sections']['responsibilities']:
            print(f"• {resp}")
    
    if job_desc['sections'].get('requirements'):
        print(f"\n**Requirements:**")
        for req in job_desc['sections']['requirements']:
            print(f"• {req}")
    
    if job_desc['sections'].get('nice_to_haves'):
        print(f"\n**Nice to Have:**")
        for nice in job_desc['sections']['nice_to_haves']:
            print(f"• {nice}")

    print(f"\n{'─'*70}")


def search_similar_jobs(generator: JobGenerator, job_title: str, department: str, skills: List[str] = None) -> List[Dict]:
    """Search for similar jobs in the vector database"""
    search_query = f"{job_title} {department}"
    if skills:
        search_query += " " + " ".join(skills)
    
    results = generator.vector_db.search(search_query, k=3)
    return results

"""
======================================================================================================================================================================
Main Demo Function
======================================================================================================================================================================
"""

def main():
    """Main demo function"""
    try:
        clear_screen()
        display_header()
        
        if not GENERATOR_AVAILABLE:
            print("Job Generator not available. Please check your setup.")
            print("Make sure you have the required modules and API keys configured.")
            os.chdir(original_cwd)  # Restore directory before returning
            return
        
        print("🚀 Initializing Job Description Generator...")
        try:
            generator = JobGenerator(verbose=False)
            print(f"✅ Generator ready with {len(generator.vector_db.embeddings)} job descriptions in database")
        except Exception as e:
            print(f"❌ Failed to initialize generator: {e}")
            print("Please check your API keys and vector database setup.")
            os.chdir(original_cwd)  # Restore directory before returning
            return
        
        print("\n👋 Welcome to the Interactive Job Description Generator!")
        print("This tool helps you create professional job descriptions using AI and existing job data.\n")
        
        # Store current job information
        current_job = {}
        generated_jobs = []
        
        # Main loop
        while True:
            clear_screen()
            current_job_str = f"{current_job.get('title', '')} - {current_job.get('department', '')}" if current_job else ""
            display_header(current_job_str)
            
            choices = [
                "🆕 Create new job description",
                "🔍 Search similar jobs for inspiration", 
                "📝 Refine current job description",
                "📋 View generated jobs history",
                "💾 Export job description",
                "❌ Exit"
            ]
            
            choice = get_user_choice("What would you like to do?", choices)
            
# ============================================================================================================================================
# Create new job description
# ============================================================================================================================================
            prompt = textwrap.dedent("""\
                Department (e.g., choose from):
                - Engineering
                - Data Science
                - Product Management
                - Design
                - Business Development
                - Business Operations & Strategy
                - People
                - Marketing
                - Customer Experience
                - Communications
                - Legal & Policy
                - Research
            Enter your department: """)

            if choice == 0:  # Create new job
                clear_screen()
                display_header()
                print("Creating a new job description...\n")
                
                # Get basic information
                job_title = get_user_input("Job Title (e.g., 'Senior Software Engineer'): ")
                department = get_user_input(prompt)

                print(f"\n✅ Job: {job_title} in {department}")
                
                # Get requirements
                requirements = get_list_input("\n📋 Key Requirements:")
                print(f"Requirements: {', '.join(requirements)}")
                
                # Get optional information
                seniority = get_user_input("\nSeniority Level (e.g., 'Senior', 'Junior', or press Enter to skip): ", required=False)
                skills = get_list_input("\n🛠️  Key Skills (or press Enter to skip):", min_items=0)
                
                print(f"\n Generating job description for {job_title}...")
                
                try:
                    job_desc = generator.generate(
                        job_title=job_title,
                        department=department,
                        key_requirements=requirements,
                        seniority_level=seniority if seniority else None,
                        key_skills=skills if skills else None
                    )
                    
                    current_job = job_desc
                    generated_jobs.append(job_desc)
                    
                    print("\nJob description generated successfully!")
                    display_job_description(job_desc)
                    
                except Exception as e:
                    print(f"❌ Error generating job description: {e}")
                
                input("\nPress Enter to continue...")
            
# ============================================================================================================================================
# Search similar jobs for inspiration
# ============================================================================================================================================
            elif choice == 1:  # Search similar jobs
                clear_screen()
                display_header()
                print("🔍 Searching for similar jobs...\n")
                
                search_title = get_user_input("Job title to search for: ")
                search_dept = get_user_input("Department: ")
                search_skills = get_list_input("Skills to search for (optional):", min_items=0)
                
                print(f"\n🔍 Searching for jobs similar to '{search_title}' in {search_dept}...")
                
                try:
                    results = search_similar_jobs(generator, search_title, search_dept, search_skills)
                    
                    print(f"\n📊 Found {len(results)} similar jobs:\n")
                    
                    for i, result in enumerate(results, 1):
                        metadata = result['metadata']
                        similarity = result['similarity']
                        print(f"{i}. {metadata.get('job_title', 'Unknown')} ({metadata.get('department', 'Unknown')})")
                        print(f"   Similarity: {similarity:.3f}")
                        print(f"   Preview: {metadata.get('content', '')[:100]}...")
                        print()
                    
                    # Option to view full job
                    if results:
                        view_choice = get_user_input(f"\nEnter job number to view full description (1-{len(results)}, or press Enter to skip): ", required=False)
                        if view_choice and view_choice.isdigit():
                            job_num = int(view_choice) - 1
                            if 0 <= job_num < len(results):
                                print(f"\n{'='*70}")
                                print(results[job_num]['metadata'].get('content', 'No content available'))
                
                except Exception as e:
                    print(f"❌ Error searching jobs: {e}")
                
                input("\nPress Enter to continue...")
            
# ============================================================================================================================================
# Refine current job description
# ============================================================================================================================================
            elif choice == 2:  # Refine current job
                if not current_job:
                    print("\nNo current job to refine. Please create a job description first.")
                    input("Press Enter to continue...")
                    continue
                
                clear_screen()
                display_header(f"{current_job['title']} - {current_job['department']}")
                print("📝 Refining current job description...\n")
                
                # Show current job
                display_job_description(current_job)
                
                refine_choices = [
                    "✏️ Edit job title and department",
                    "📋 Modify requirements",
                    "🛠️ Update skills",
                    "🔄 Regenerate with different approach",
                    "🔙 Back to main menu"
                ]
                
                refine_choice = get_user_choice("\nWhat would you like to refine?", refine_choices)
                
                if refine_choice == 0:  # Edit title/department
                    new_title = get_user_input(f"New job title (current: {current_job['title']}): ")
                    new_dept = get_user_input(f"New department (current: {current_job['department']}): ")
                    current_job['title'] = new_title
                    current_job['department'] = new_dept
                    print("✅ Title and department updated!")
                
                elif refine_choice == 1:  # Modify requirements
                    print(f"\nCurrent requirements:")
                    for req in current_job['sections'].get('requirements', []):
                        print(f"• {req}")
                    new_reqs = get_list_input("\nEnter new requirements:")
                    current_job['sections']['requirements'] = new_reqs
                    print("✅ Requirements updated!")
                
                elif refine_choice == 2:  # Update skills
                    current_skills = current_job['metadata'].get('skills', [])
                    print(f"\nCurrent skills: {', '.join(current_skills) if current_skills else 'None'}")
                    new_skills = get_list_input("\nEnter new skills:", min_items=0)
                    current_job['metadata']['skills'] = new_skills
                    print("✅ Skills updated!")
                
                elif refine_choice == 3:  # Regenerate
                    print("\n🔄 Regenerating job description...")
                    try:
                        regenerated = generator.generate(
                            job_title=current_job['title'],
                            department=current_job['department'],
                            key_requirements=current_job['sections'].get('requirements', []),
                            seniority_level=current_job['metadata'].get('seniority'),
                            key_skills=current_job['metadata'].get('skills', [])
                        )
                        current_job = regenerated
                        generated_jobs.append(regenerated)
                        print("✅ Job description regenerated!")
                        display_job_description(current_job)
                    except Exception as e:
                        print(f"❌ Error regenerating: {e}")
                
                if refine_choice != 4:
                    input("\nPress Enter to continue...")
            
# ============================================================================================================================================
# View generated jobs history
# ============================================================================================================================================
            elif choice == 3:  # View history
                clear_screen()
                display_header()
                print("📋 Generated Jobs History\n")
                
                if not generated_jobs:
                    print("No jobs generated yet.")
                else:
                    for i, job in enumerate(generated_jobs, 1):
                        print(f"{i}. {job['title']} - {job['department']}")
                        if job['metadata'].get('generated'):
                            print("   (AI Generated)")
                        print()
                    
                    view_choice = get_user_input(f"\nEnter job number to view (1-{len(generated_jobs)}, or press Enter to skip): ", required=False)
                    if view_choice and view_choice.isdigit():
                        job_num = int(view_choice) - 1
                        if 0 <= job_num < len(generated_jobs):
                            display_job_description(generated_jobs[job_num])
                
                input("\nPress Enter to continue...")
            
# ============================================================================================================================================
# Export job description
# ============================================================================================================================================
            elif choice == 4:  # Export job
                if not current_job:
                    print("\n⚠️  No current job to export. Please create a job description first.")
                    input("Press Enter to continue...")
                    continue
                
                clear_screen()
                display_header()
                print("💾 Exporting job description...\n")
                
                filename = f"{current_job['title'].replace(' ', '_').lower()}_job_description.json"
                
                try:
                    with open(filename, 'w') as f:
                        json.dump(current_job, f, indent=2)
                    print(f"✅ Job description exported to: {filename}")
                    
                    # Also create a readable text version with separators
                    text_filename = filename.replace('.json', '.txt')
                    with open(text_filename, 'w') as f:
                        f.write(f"{current_job['title']} - {current_job['department']}\n")
                        f.write("=" * 70 + "\n\n")
                        
                        # Job Description Content Section
                        f.write("🎯 JOB DESCRIPTION CONTENT (Ready to Post)\n")
                        f.write("─" * 70 + "\n\n")
                        
                        if current_job['sections'].get('intro'):
                            f.write(f"Job Description:\n{current_job['sections']['intro'].strip()}\n\n")
                        
                        if current_job['sections'].get('responsibilities'):
                            f.write("Key Responsibilities:\n")
                            for resp in current_job['sections']['responsibilities']:
                                f.write(f"• {resp}\n")
                            f.write("\n")
                        
                        if current_job['sections'].get('requirements'):
                            f.write("Requirements:\n")
                            for req in current_job['sections']['requirements']:
                                f.write(f"• {req}\n")
                            f.write("\n")
                        
                        if current_job['sections'].get('nice_to_haves'):
                            f.write("Nice to Have:\n")
                            for nice in current_job['sections']['nice_to_haves']:
                                f.write(f"• {nice}\n")
                        
                        f.write("\n" + "─" * 70 + "\n")
      
                    print(f"✅ Readable version exported to: {text_filename}")
                    
                except Exception as e:
                    print(f"❌ Error exporting: {e}")
                
                input("\nPress Enter to continue...")
            
            elif choice == 5:  # Exit
                print("\n👋 Thanks for using the Job Description Generator!")
                print("🚀 Your generated job descriptions are ready for use!")
                break
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    
    finally:
        # Restore original working directory
        os.chdir(original_cwd)

if __name__ == "__main__":
    main() 