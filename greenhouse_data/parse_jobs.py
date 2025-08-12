#!/usr/bin/env python3

import pandas as pd
import os
import re
from bs4 import BeautifulSoup
import unicodedata

def clean_folder_name(name):
    """Convert department name to clean folder name"""
    # Remove special characters and convert to lowercase
    cleaned = re.sub(r'[^\w\s-]', '', name.lower())
    # Replace spaces and hyphens with underscores
    cleaned = re.sub(r'[-\s]+', '_', cleaned)
    return cleaned.strip('_')

def clean_filename(title):
    """Clean job title for filename while keeping it readable"""
    # Remove or replace problematic characters for filenames
    cleaned = re.sub(r'[<>:"/\\|?*]', '', title)
    # Replace multiple spaces with single space
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()

def extract_text_from_html(html_content):
    """Extract clean text from HTML while preserving structure"""
    if not html_content or pd.isna(html_content):
        return ""
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract text but keep some structure
    text = ""
    for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'ul', 'ol', 'li']):
        if element.name in ['h1', 'h2', 'h3', 'h4']:
            text += f"\n{element.get_text().strip()}\n"
        elif element.name in ['ul', 'ol']:
            text += "\n"
        elif element.name == 'li':
            text += f"- {element.get_text().strip()}\n"
        else:  # p tags
            text += f"{element.get_text().strip()}\n"
    
    return text.strip()

def parse_job_sections(html_content):
    """Parse HTML job description into structured sections"""
    if not html_content or pd.isna(html_content):
        return {"intro": "", "responsibilities": [], "requirements": [], "nice_to_haves": []}
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    sections = {
        "intro": "",
        "responsibilities": [],
        "requirements": [],
        "nice_to_haves": []
    }
    
    # Get all elements
    elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'ul', 'ol', 'li'])
    
    current_section = "intro"
    current_list_items = []
    
    for element in elements:
        text = element.get_text().strip()
        if not text:
            continue
            
        # Check if this is a section header
        if element.name in ['h1', 'h2', 'h3', 'h4']:
            # Save any pending list items
            if current_list_items and current_section != "intro":
                sections[current_section].extend(current_list_items)
                current_list_items = []
            
            # Determine new section based on header text
            text_lower = text.lower()
            if any(word in text_lower for word in ['responsibilities', 'responsibi', 'duties', 'what you', 'you will']):
                current_section = "responsibilities"
            elif any(word in text_lower for word in ['requirements', 'qualifications', 'must have', 'required', 'minimum', 'essential']):
                current_section = "requirements"
            elif any(word in text_lower for word in ['nice to have', 'bonus', 'preferred', 'plus', 'nice-to-have', 'would be nice']):
                current_section = "nice_to_haves"
            else:
                # If we haven't seen any sections yet, this might still be intro
                if not any(sections[key] for key in ['responsibilities', 'requirements', 'nice_to_haves']):
                    current_section = "intro"
                # Otherwise, try to guess based on content
                elif any(word in text_lower for word in ['experience', 'years', 'degree', 'skill']):
                    current_section = "requirements"
                else:
                    current_section = "responsibilities"
                    
        elif element.name == 'li':
            if current_section == "intro":
                # If we're still in intro but see a list item, probably responsibilities
                current_section = "responsibilities"
            current_list_items.append(text)
            
        elif element.name == 'p':
            if current_section == "intro":
                sections["intro"] += f"{text} "
            else:
                # Paragraph in a non-intro section, treat as a single item
                if current_section in sections:
                    sections[current_section].append(text)
        
        # Handle end of ul/ol
        elif element.name in ['ul', 'ol']:
            if current_list_items:
                sections[current_section].extend(current_list_items)
                current_list_items = []
    
    # Save any remaining list items
    if current_list_items and current_section != "intro":
        sections[current_section].extend(current_list_items)
    
    # Clean up intro
    sections["intro"] = sections["intro"].strip()
    
    return sections

def format_job_description(job_data, template_content):
    """Format job data using the template"""
    sections = parse_job_sections(job_data['job_description'])
    
    # Start with template
    output = template_content
    
    # Replace placeholders
    output = output.replace('{job_title}', job_data['job_title'])
    output = output.replace('{job_department}', job_data['job_department'])
    
    # Find sections in template and replace content
    template_lines = output.split('\n')
    new_lines = []
    current_template_section = None
    
    for line in template_lines:
        if line.strip() == '---INTRO---':
            new_lines.append(line)
            current_template_section = 'intro'
        elif line.strip() == '---RESPONSIBILITIES---':
            new_lines.append(line)
            current_template_section = 'responsibilities'
        elif line.strip() == '---REQUIREMENTS---':
            new_lines.append(line)
            current_template_section = 'requirements'
        elif line.strip() == '---NICE_TO_HAVES---':
            new_lines.append(line)
            current_template_section = 'nice_to_haves'
        elif line.strip().startswith('---') or line.strip().startswith('==='):
            new_lines.append(line)
            current_template_section = None
        elif current_template_section:
            # Replace template content with parsed content
            if current_template_section == 'intro':
                if sections['intro']:
                    new_lines.append(sections['intro'])
                else:
                    new_lines.append("We're looking for an enthusiastic, self-motivated professional to join our team.")
            elif current_template_section in ['responsibilities', 'requirements']:
                items = sections[current_template_section]
                if items:
                    for item in items:
                        new_lines.append(f"- {item}")
                else:
                    # Keep template content if no parsed content
                    new_lines.append(line)
            elif current_template_section == 'nice_to_haves':
                items = sections['nice_to_haves']
                if items:
                    for item in items:
                        new_lines.append(f"- {item}")
                else:
                    # Default nice-to-have
                    new_lines.append("- Love for unicorns :)")
            current_template_section = None  # Only replace first line of each section
        else:
            new_lines.append(line)
    
    return '\n'.join(new_lines)

def main():
    # Read the template
    with open('template.txt', 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Read the cleaned job dataset
    print("📖 Reading job dataset...")
    df = pd.read_csv('data/cleaned_job_dataset.csv')
    print(f"📊 Found {len(df)} jobs")
    
    # Create main output directory
    output_dir = 'parsed_jobs'
    if os.path.exists(output_dir):
        print(f"🗑️  Removing existing {output_dir} directory...")
        import shutil
        shutil.rmtree(output_dir)
    
    os.makedirs(output_dir, exist_ok=True)
    print(f"📁 Created {output_dir} directory")
    
    # Get unique departments and create folders
    departments = df['job_department'].unique()
    print(f"\n📂 Creating folders for {len(departments)} departments:")
    
    for dept in departments:
        folder_name = clean_folder_name(dept)
        folder_path = os.path.join(output_dir, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        print(f"  ✅ {dept} → {folder_name}/")
    
    # Process each job
    print(f"\n🔄 Processing {len(df)} jobs...")
    success_count = 0
    error_count = 0
    
    for idx, job in df.iterrows():
        try:
            # Generate filename
            filename = f"{clean_filename(job['job_title'])}.txt"
            
            # Get department folder
            dept_folder = clean_folder_name(job['job_department'])
            filepath = os.path.join(output_dir, dept_folder, filename)
            
            # Handle duplicate filenames
            counter = 1
            original_filepath = filepath
            while os.path.exists(filepath):
                name, ext = os.path.splitext(original_filepath)
                filepath = f"{name}_{counter}{ext}"
                counter += 1
            
            # Format job description
            formatted_content = format_job_description(job, template_content)
            
            # Write file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(formatted_content)
            
            success_count += 1
            if success_count % 10 == 0:
                print(f"  ✅ Processed {success_count} jobs...")
                
        except Exception as e:
            print(f"  ❌ Error processing {job['job_title']}: {str(e)}")
            error_count += 1
    
    print(f"\n🎉 Completed!")
    print(f"✅ Successfully processed: {success_count} jobs")
    if error_count > 0:
        print(f"❌ Errors: {error_count} jobs")
    
    # Print summary
    print(f"\n📈 Summary by department:")
    for dept in departments:
        folder_name = clean_folder_name(dept)
        folder_path = os.path.join(output_dir, folder_name)
        file_count = len([f for f in os.listdir(folder_path) if f.endswith('.txt')])
        print(f"  {dept}: {file_count} jobs")

if __name__ == "__main__":
    main() 