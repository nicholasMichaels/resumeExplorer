from crewai import Agent, Tool
from agents.groq_llm import GroqLLM  # NEW IMPORT
import logging
import json
import time
from typing import Dict, Any
from utils.debugging import debug_agent_state, validate_llm_output

logger = logging.getLogger(__name__)

def extract_resume_data(resume_text: str) -> Dict[str, Any]:
    """Extract structured data from resume text using Groq LLM"""
    start_time = time.time()

    try:
        if not resume_text.strip():
            raise ValueError("Resume text cannot be empty")

        logger.info("Starting Groq-powered resume extraction process")

        # Initialize Groq LLM
        groq_llm = GroqLLM()

        # Enhanced extraction prompt for Groq
        extraction_prompt = f"""
You are an expert resume parser. Extract structured information from the following resume text and return ONLY valid JSON.

Resume text:
{resume_text}

Extract information into this exact JSON structure:
{{
    "personal_info": {{
        "name": "full name or null if not found",
        "email": "email address or null if not found",
        "phone": "phone number or null if not found",
        "location": "city, state/country or null if not found",
        "linkedin": "linkedin URL or null if not found"
    }},
    "education": [
        {{
            "degree": "degree type",
            "major": "field of study",
            "school": "institution name",
            "graduation_year": "year as string",
            "gpa": "GPA if mentioned or null"
        }}
    ],
    "experience": [
        {{
            "title": "job title",
            "company": "company name",
            "duration": "time period (e.g., '2020-2022' or '2 years')",
            "description": "detailed job description and achievements",
            "location": "job location if mentioned"
        }}
    ],
    "skills": ["skill1", "skill2", "skill3"],
    "certifications": ["cert1", "cert2"] or [],
    "languages": ["language1", "language2"] or [],
    "extraction_confidence": 0.85
}}

Rules:
- Return ONLY the JSON object, no additional text
- Use null for missing information
- Keep skill names concise and standardized
- Include all work experience with detailed descriptions
- Extract education in reverse chronological order
"""

        # Get response from Groq
        response = groq_llm(extraction_prompt)

        # Parse JSON response with error handling
        try:
            extracted_data = json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                extracted_data = json.loads(json_match.group())
            else:
                # Fallback to original mock data structure
                logger.warning("Failed to parse Groq response, using fallback extraction")
                extracted_data = _fallback_extraction(resume_text)

        # Add metadata
        extracted_data.update({
            'extraction_timestamp': time.time(),
            'extraction_method': 'groq_llm',
            'processing_time': time.time() - start_time
        })

        # Validate output
        required_fields = ['personal_info', 'education', 'experience', 'skills']
        validation = validate_llm_output(json.dumps(extracted_data), required_fields)
        extracted_data['validation'] = validation

        # Debug agent state
        execution_time = time.time() - start_time
        debug_agent_state("ResumeExtractor", resume_text[:200], extracted_data, execution_time)

        logger.info("Resume extraction completed successfully with Groq")
        return extracted_data

    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Error in extract_resume_data: {str(e)}")

        # Return fallback data
        fallback_data = _fallback_extraction(resume_text)
        fallback_data.update({
            'error': str(e),
            'extraction_confidence': 0.3,
            'extraction_timestamp': time.time(),
            'extraction_method': 'fallback',
            'processing_time': execution_time
        })

        debug_agent_state("ResumeExtractor", resume_text[:200], f"ERROR: {str(e)}", execution_time)
        return fallback_data

def _fallback_extraction(resume_text: str) -> Dict[str, Any]:
    """Fallback extraction when Groq fails"""
    # Your existing mock extraction logic here
    return {
        'personal_info': {'name': 'Unknown', 'email': None, 'phone': None, 'location': None},
        'education': [],
        'experience': [],
        'skills': [],
        'extraction_confidence': 0.3
    }

# Update the agent to use Groq LLM
ResumeExtractor = Agent(
    name="Resume Extractor",
    role="Extract structured fields from resumes using advanced LLM",
    goal="Parse resumes into education, skills, experience, and metadata with high accuracy using Groq",
    backstory="""You are an expert resume parser powered by Groq's fast language models.
    You extract structured information from various resume formats with high precision.""",
    tools=[Tool(name="Extract Resume Data", func=extract_resume_data, description="Useful for extracting structured data from resume text.")],
    llm=GroqLLM(),  # USE GROQ LLM
    verbose=True,
    allow_delegation=False
)
