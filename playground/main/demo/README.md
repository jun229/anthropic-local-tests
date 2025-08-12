# Demo Scripts

This directory contains interactive demo scripts that showcase different aspects of the RAG system.

## Available Demos

### 1. Interactive Job Description Generator (`jd_demo.py`)
**NEW!** ✨ An interactive terminal-based demo for generating professional job descriptions using AI.

**Features:**
- 🆕 Create AI-powered job descriptions with semantic search
- 🔍 Search similar jobs in the database for inspiration
- 📝 Refine and iterate on job descriptions
- 📋 View generation history
- 💾 Export to JSON and text formats with clear separators
- 🎨 Clean terminal interface with choice-driven menus
- 🎯 Clear visual separators between job content and AI instructions
- 📊 Metadata display showing generation parameters

**Usage:**
```bash
cd playground/main/demo/
python3 jd_demo.py
```

**Requirements:**
- Anthropic API key configured in `config.py`
- Job descriptions vector database (`job_descriptions.pkl`)
- All dependencies from `requirements.txt`

### 2. Simple Recruiting Demo (`dontUse_simple_recruiting_demo.py`)
A basic demo that shows recruiting workflows without requiring API keys.

**Features:**
- 📋 Role requirements analysis
- 📝 Basic job description templates
- 🎤 Interview preparation guides  
- 🔍 Sourcing strategy recommendations

**Usage:**
```bash
cd playground/main/demo/
python3 dontUse_simple_recruiting_demo.py
```

**Requirements:**
- No API keys needed
- Uses basic text search on existing data files

## Getting Started

1. **Set up your environment:**
   - Install requirements: `pip install -r ../../requirements.txt`
   - Configure API keys in `playground/main/config.py`

2. **Prepare vector databases:**
   - Run the notebook `playground/main/main.ipynb` to create embeddings
   - Or use existing `.pkl` files in the `data/` directory

3. **Run a demo:**
   - Choose the demo that matches your setup
   - Follow the interactive prompts

## Tips

- **Start with the Simple Recruiting Demo** if you don't have API keys set up yet
- **Use the Job Description Generator** for full AI-powered functionality
- Both demos feature similar clean terminal interfaces with numbered choices
- All generated content can be exported for real-world use
- **Clear Content Separation**: Job descriptions display with distinct sections for publishable content vs. AI metadata/instructions

## Content Organization

The Job Description Generator now uses **clear visual separators** to distinguish between:

### 🎯 Job Description Content (Ready to Post)
- The actual job description text that can be published directly
- Includes job title, description, responsibilities, requirements, and nice-to-haves
- This content is ready for posting on job boards or company websites

### 🤖 AI Model Metadata & Instructions  
- Generation parameters used by the AI (seniority level, target skills, etc.)
- Usage instructions for customizing the content
- Reminders about company-specific details to add
- Source attribution and compliance notes

This separation makes it easy to:
- **Copy the job content** for immediate use
- **Review generation settings** to understand how the AI created the description
- **Follow best practices** with built-in usage guidelines

## Troubleshooting

- **Import errors:** Make sure you're running from the correct directory and have all dependencies installed
- **API errors:** Check that your API keys are correctly configured in `config.py`
- **Missing data:** Run the main notebook to generate the required vector databases

---

💡 **Next Steps:** After trying the demos, explore the modular codebase in the parent directory to build your own RAG applications! 