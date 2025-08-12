#!/usr/bin/env python3

import pandas as pd
import os
import re
from bs4 import BeautifulSoup

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

def is_section_header(element):
    """Check if an element represents a section header"""
    if not element:
        return False, ""
    
    text = element.get_text().strip().lower()
    if not text:
        return False, ""
    
    # Check if it's a header tag
    if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        return True, text
    
    # Check if it's bold/strong text that looks like a header
    if element.name in ['strong', 'b'] or (element.find('strong') or element.find('b')):
        # If the text is short and looks like a header
        if len(text.split()) <= 5 and any(word in text for word in ['responsibilities', 'requirements', 'qualifications', 'nice to have', 'bonus', 'preferred']):
            return True, text
    
    # Check if it's a div with only strong/b content
    if element.name == 'div':
        strong_content = element.find(['strong', 'b'])
        if strong_content and strong_content.get_text().strip().lower() == text:
            return True, text
    
    return False, ""

def determine_section(header_text):
    """Determine which section a header belongs to"""
    header_text = header_text.lower().strip()
    
    if any(word in header_text for word in ['responsibilities', 'responsibi', 'duties', 'what you', 'you will', 'role', 'key responsibilities']):
        return "responsibilities"
    elif any(word in header_text for word in ['requirements', 'qualifications', 'must have', 'required', 'minimum', 'essential', 'experience', 'skills', 'what we need']):
        return "requirements"
    elif any(word in header_text for word in ['nice to have', 'bonus', 'preferred', 'plus', 'nice-to-have', 'would be nice', 'great to have', 'bonus points']):
        return "nice_to_haves"
    elif any(word in header_text for word in ['about', 'who we', 'we are', 'company', 'team', 'overview', 'intro']):
        return "intro"
    else:
        return None

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
    
    # Get all elements in order
    all_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'div', 'strong', 'b'])
    
    current_section = "intro"
    intro_paragraphs = []
    
    i = 0
    while i < len(all_elements):
        element = all_elements[i]
        
        # Check if this is a section header
        is_header, header_text = is_section_header(element)
        
        if is_header:
            # Before switching sections, save intro if we have it
            if current_section == "intro" and intro_paragraphs:
                sections["intro"] = " ".join(intro_paragraphs)
                intro_paragraphs = []
            
            # Determine new section
            new_section = determine_section(header_text)
            if new_section:
                current_section = new_section
        
        # Handle lists
        elif element.name in ['ul', 'ol']:
            list_items = element.find_all('li')
            for li in list_items:
                item_text = li.get_text().strip()
                if item_text and current_section != "intro":
                    sections[current_section].append(item_text)
        
        # Handle paragraphs
        elif element.name == 'p':
            para_text = element.get_text().strip()
            if para_text:
                if current_section == "intro":
                    intro_paragraphs.append(para_text)
                else:
                    # If we're not in intro and it's a paragraph, add as single item
                    sections[current_section].append(para_text)
        
        i += 1
    
    # Don't forget the last intro if we ended there
    if intro_paragraphs:
        sections["intro"] = " ".join(intro_paragraphs)
    
    # Clean up empty strings and duplicates
    for section_name in sections:
        if isinstance(sections[section_name], list):
            sections[section_name] = [item for item in sections[section_name] if item.strip()]
    
    return sections

def create_job_file_content(job_data):
    """Create the complete job file content using the template structure"""
    sections = parse_job_sections(job_data['job_description'])
    
    # Build the content
    content = []
    content.append("===JD_START===")
    content.append(f"TITLE: {job_data['job_title']}")
    content.append(f"DEPARTMENT: {job_data['job_department']}")
    content.append("")
    
    # INTRO section
    content.append("---INTRO---")
    if sections['intro']:
        # Limit intro length to avoid it being too long
        intro_text = sections['intro']
        if len(intro_text) > 800:  # Truncate very long intros
            intro_text = intro_text[:800] + "..."
        content.append(intro_text)
    else:
        content.append("We're looking for an enthusiastic, self-motivated professional to join our team.")
    content.append("")
    
    # RESPONSIBILITIES section
    content.append("---RESPONSIBILITIES---")
    if sections['responsibilities']:
        for item in sections['responsibilities'][:10]:  # Limit to 10 items
            content.append(f"- {item}")
    else:
        # Default responsibilities
        content.append("- Collaborate with team members to achieve goals")
        content.append("- Contribute to project planning and execution")
        content.append("- Maintain high quality standards in all work")
    content.append("")
    
    # REQUIREMENTS section
    content.append("---REQUIREMENTS---")
    if sections['requirements']:
        for item in sections['requirements'][:10]:  # Limit to 10 items
            content.append(f"- {item}")
    else:
        # Default requirements
        content.append("- Relevant experience in the field")
        content.append("- Strong communication and collaboration skills")
        content.append("- Ability to work in a fast-paced environment")
    content.append("")
    
    # NICE TO HAVES section
    content.append("---NICE_TO_HAVES---")
    if sections['nice_to_haves']:
        for item in sections['nice_to_haves'][:5]:  # Limit to 5 items
            content.append(f"- {item}")
    else:
        content.append("- Love for unicorns :)")
    content.append("")
    
    content.append("===JD_END===")
    
    return '\n'.join(content)

def main():
    # Read the cleaned job dataset
    print("📖 Reading job dataset...")
    df = pd.read_csv('data/cleaned_job_dataset.csv')
    print(f"📊 Found {len(df)} jobs")
    
    # Create main output directory
    output_dir = 'parsed_jobs_final'
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
            
            # Create job file content
            file_content = create_job_file_content(job)
            
            # Write file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(file_content)
            
            success_count += 1
            if success_count % 25 == 0:
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
    
    print(f"\n📁 All job files created in: {output_dir}/")

if __name__ == "__main__":
    main() 