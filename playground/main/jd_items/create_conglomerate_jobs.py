#!/usr/bin/env python3
"""
Script to create a conglomerate JSON file from all job description files.
Combines all department-specific job description JSON files into one unified file.
"""

import json
import os
from typing import List, Dict, Any
from pathlib import Path

def combine_job_files(input_dir: str = "data/job_descriptions", output_file: str = "data/job_descriptions_conglomerate.json") -> None:
    """
    Combine all JSON files in the job_descriptions directory into one conglomerate file.
    
    Args:
        input_dir: Directory containing the individual job description JSON files
        output_file: Path for the combined output file
    """
    
    # Get all JSON files in the directory
    job_files = []
    input_path = Path(input_dir)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input directory {input_dir} does not exist")
    
    for file_path in input_path.glob("*.json"):
        job_files.append(file_path)
    
    print(f"Found {len(job_files)} JSON files to combine:")
    for file_path in sorted(job_files):
        print(f"  - {file_path.name}")
    
    # Combine all jobs into one list
    all_jobs = []
    department_stats = {}
    
    for file_path in sorted(job_files):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                jobs_data = json.load(f)
            
            # Add jobs from this file
            if isinstance(jobs_data, list):
                for job in jobs_data:
                    all_jobs.append(job)
                    
                    # Track department statistics
                    dept = job.get('department', 'Unknown')
                    department_stats[dept] = department_stats.get(dept, 0) + 1
                
                print(f"  ✅ {file_path.name}: {len(jobs_data)} jobs loaded")
            else:
                print(f"  ⚠️  {file_path.name}: Expected list format, skipping")
                
        except Exception as e:
            print(f"  ❌ Error loading {file_path.name}: {e}")
    
    # Create output directory if it doesn't exist
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save the combined file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_jobs, f, indent=2, ensure_ascii=False)
    
    # Print summary statistics
    print(f"\n📊 Summary:")
    print(f"Total jobs combined: {len(all_jobs)}")
    print(f"Output file: {output_file}")
    print(f"File size: {output_path.stat().st_size / 1024:.1f} KB")
    
    print(f"\n📈 Jobs by Department:")
    for dept, count in sorted(department_stats.items()):
        print(f"  {dept}: {count} jobs")
    
    # Validate the combined file
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            validation_data = json.load(f)
        print(f"\n✅ Validation: Successfully created conglomerate file with {len(validation_data)} jobs")
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")

def main():
    """Main function to run the combination process."""
    print("🚀 Creating conglomerate job descriptions file...\n")
    
    # Run the combination
    combine_job_files()
    
    print("\n✨ Conglomerate file creation complete!")

if __name__ == "__main__":
    main() 