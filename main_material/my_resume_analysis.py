#!/usr/bin/env python3
"""
Enhanced Resume Analysis Script
Uses Groq Cloud API for resume analysis from PDFs or text
Now with AI-powered job recommendations based on resume content
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
import logging
from typing import Dict, Optional, Any, List
import PyPDF2
import io
from groq import Groq
import re

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Enhanced job categories and preferences
JOB_CATEGORIES = {
    'Software Development': [
        'Full Stack Developer', 'Frontend Developer', 'Backend Developer',
        'Mobile App Developer', 'DevOps Engineer', 'Software Architect',
        'Game Developer', 'Embedded Systems Developer', 'API Developer'
    ],
    'Data & Analytics': [
        'Data Scientist', 'Data Analyst', 'Machine Learning Engineer',
        'Data Engineer', 'Business Intelligence Analyst', 'Research Scientist',
        'Statistician', 'Quantitative Analyst', 'AI Engineer'
    ],
    'Cybersecurity': [
        'Security Analyst', 'Penetration Tester', 'Security Engineer',
        'CISO', 'Compliance Officer', 'Incident Response Specialist',
        'Security Architect', 'Risk Analyst'
    ],
    'Cloud & Infrastructure': [
        'Cloud Engineer', 'AWS Solutions Architect', 'Azure Architect',
        'Site Reliability Engineer', 'Infrastructure Engineer',
        'Platform Engineer', 'Cloud Security Specialist'
    ],
    'Product & Design': [
        'Product Manager', 'UX Designer', 'UI Designer', 'Product Owner',
        'Design System Manager', 'User Researcher', 'Growth Product Manager'
    ],
    'Management & Leadership': [
        'Engineering Manager', 'Technical Lead', 'CTO', 'VP Engineering',
        'Team Lead', 'Scrum Master', 'Technical Program Manager'
    ],
    'Sales & Marketing': [
        'Sales Representative', 'Account Manager', 'Marketing Manager',
        'Digital Marketing Specialist', 'Business Development',
        'Customer Success Manager', 'Sales Engineer'
    ],
    'Finance & Business': [
        'Financial Analyst', 'Business Analyst', 'Consultant',
        'Investment Banker', 'Accountant', 'Controller', 'CFO',
        'Operations Manager', 'Project Manager'
    ],
    'Healthcare & Life Sciences': [
        'Nurse', 'Doctor', 'Medical Researcher', 'Biomedical Engineer',
        'Healthcare Administrator', 'Pharmacist', 'Medical Device Engineer'
    ],
    'Education & Training': [
        'Teacher', 'Professor', 'Training Specialist', 'Educational Consultant',
        'Curriculum Designer', 'Academic Researcher'
    ],
    'Creative & Media': [
        'Graphic Designer', 'Content Creator', 'Video Editor',
        'Copywriter', 'Social Media Manager', 'Brand Designer'
    ],
    'Operations & Support': [
        'Customer Support', 'Technical Support', 'Operations Analyst',
        'Quality Assurance', 'Administrative Assistant', 'Office Manager'
    ]
}

# Salary ranges by experience level and location type
SALARY_RANGES = {
    'entry': {
        'major_metro': ['$45,000-$65,000', '$50,000-$70,000', '$55,000-$75,000', '$60,000-$80,000'],
        'mid_metro': ['$40,000-$60,000', '$45,000-$65,000', '$50,000-$70,000', '$55,000-$75,000'],
        'small_city': ['$35,000-$55,000', '$40,000-$60,000', '$45,000-$65,000', '$50,000-$70,000'],
        'remote': ['$45,000-$70,000', '$50,000-$75,000', '$55,000-$80,000', '$60,000-$85,000']
    },
    'mid': {
        'major_metro': ['$70,000-$95,000', '$80,000-$110,000', '$90,000-$125,000', '$100,000-$140,000'],
        'mid_metro': ['$65,000-$90,000', '$75,000-$100,000', '$85,000-$115,000', '$95,000-$125,000'],
        'small_city': ['$60,000-$85,000', '$70,000-$95,000', '$80,000-$105,000', '$90,000-$115,000'],
        'remote': ['$70,000-$100,000', '$80,000-$115,000', '$90,000-$130,000', '$100,000-$145,000']
    },
    'senior': {
        'major_metro': ['$120,000-$160,000', '$140,000-$180,000', '$160,000-$220,000', '$180,000-$250,000'],
        'mid_metro': ['$110,000-$150,000', '$130,000-$170,000', '$150,000-$200,000', '$170,000-$230,000'],
        'small_city': ['$100,000-$140,000', '$120,000-$160,000', '$140,000-$180,000', '$160,000-$210,000'],
        'remote': ['$120,000-$170,000', '$140,000-$190,000', '$160,000-$220,000', '$180,000-$260,000']
    },
    'executive': {
        'major_metro': ['$200,000-$300,000', '$250,000-$400,000', '$300,000-$500,000', '$400,000+'],
        'mid_metro': ['$180,000-$280,000', '$230,000-$370,000', '$280,000-$450,000', '$350,000+'],
        'small_city': ['$160,000-$250,000', '$210,000-$330,000', '$260,000-$400,000', '$320,000+'],
        'remote': ['$200,000-$320,000', '$250,000-$420,000', '$300,000-$520,000', '$400,000+']
    }
}

# Work preferences
WORK_TYPES = ['Full-time', 'Part-time', 'Contract', 'Freelance', 'Internship', 'Consulting']
WORK_ARRANGEMENTS = ['On-site', 'Remote', 'Hybrid', 'Flexible']
COMPANY_SIZES = ['Startup (1-50)', 'Small (51-200)', 'Medium (201-1000)', 'Large (1000+)', 'Enterprise (5000+)']
INDUSTRIES = [
    'Technology', 'Finance', 'Healthcare', 'Education', 'Retail', 'Manufacturing',
    'Media & Entertainment', 'Government', 'Non-profit', 'Consulting',
    'Real Estate', 'Transportation', 'Energy', 'Telecommunications'
]

class ResumeAnalyzer:
    """Enhanced Resume analyzer using Groq Cloud API with content-based job recommendations"""
    
    def __init__(self):
        """Initialize the analyzer with Groq client"""
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=self.groq_api_key)
        # Using Llama 3.3 70B model - adjust if needed
        self.model = "llama-3.3-70b-versatile"
        
    def extract_text_from_pdf(self, pdf_path: str) -> dict:
        """Extract text from PDF file"""
        try:
            text = ""
            word_count = 0
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    text += page_text + "\n"
                
                # Count words
                word_count = len(text.split())
                
            return {
                'success': True,
                'text': text.strip(),
                'word_count': word_count,
                'text_length': len(text),
                'pages': len(pdf_reader.pages)
            }
            
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'word_count': 0,
                'text_length': 0
            }

    def analyze_resume_content(self, resume_text: str) -> dict:
        """Analyze resume content to extract profile information automatically"""
        try:
            # Create profile extraction prompt
            profile_prompt = self._create_profile_extraction_prompt(resume_text)
            
            # Call Groq API for profile analysis
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert resume analyzer and career counselor. Analyze the resume content and extract a professional profile in JSON format. Be precise and objective based only on what's stated or clearly implied in the resume."
                    },
                    {
                        "role": "user", 
                        "content": profile_prompt
                    }
                ],
                model=self.model,
                temperature=0.1,
                max_tokens=2000,
                top_p=1,
                stream=False,
                stop=None,
            )
            
            profile_result = chat_completion.choices[0].message.content
            
            # Parse JSON response
            try:
                # Extract JSON from the response
                json_match = re.search(r'\{.*\}', profile_result, re.DOTALL)
                if json_match:
                    profile_data = json.loads(json_match.group())
                else:
                    # If no JSON found, create default profile
                    profile_data = self._create_default_profile(resume_text)
            except json.JSONDecodeError:
                logger.warning("Failed to parse profile JSON, using text analysis")
                profile_data = self._create_default_profile(resume_text)
            
            return {
                'success': True,
                'profile': profile_data,
                'raw_analysis': profile_result
            }
            
        except Exception as e:
            logger.error(f"Profile extraction error: {e}")
            return {
                'success': False,
                'error': str(e),
                'profile': self._create_default_profile(resume_text)
            }

    def _create_profile_extraction_prompt(self, resume_text: str) -> str:
        """Create prompt for extracting profile information from resume"""
        job_categories_str = "\n".join([f"- {cat}: {', '.join(roles[:3])}..." for cat, roles in JOB_CATEGORIES.items()])
        
        prompt = f"""
Analyze this resume and extract the candidate's professional profile. Return ONLY a JSON object with the following structure:

{{
    "experience_level": "entry|mid|senior|executive",
    "current_location": "city, state/country or 'Not specified'",
    "job_categories": ["category1", "category2", ...],
    "target_roles": ["role1", "role2", "role3", ...],
    "key_skills": ["skill1", "skill2", "skill3", ...],
    "industries": ["industry1", "industry2", ...],
    "work_arrangement_preference": "Remote|Hybrid|On-site|Flexible",
    "estimated_salary_range": "$X,000-$Y,000",
    "years_of_experience": number,
    "education_level": "High School|Bachelor's|Master's|PhD|Professional",
    "career_focus": "brief description of career focus",
    "willing_to_relocate": true|false
}}

Available job categories:
{job_categories_str}

Guidelines for analysis:
1. Experience level: entry (0-2 years), mid (3-7 years), senior (8-15 years), executive (15+ years)
2. Job categories: Select 2-4 most relevant categories based on skills, experience, and job titles
3. Target roles: List 3-8 specific job titles the candidate is most qualified for
4. Key skills: Extract 5-10 most important technical and professional skills
5. Industries: Identify 2-5 industries the candidate has worked in or is suited for
6. Work arrangement: Infer from resume or default to "Flexible"
7. Salary: Estimate based on experience level, skills, and location
8. Base all analysis strictly on resume content

RESUME TEXT:
{resume_text}

Return only the JSON object, no additional text or explanations.
"""
        return prompt

    def _create_default_profile(self, resume_text: str) -> dict:
        """Create a basic profile using simple text analysis as fallback"""
        text_lower = resume_text.lower()
        
        # Simple keyword-based analysis
        years_experience = self._estimate_years_experience(resume_text)
        
        # Determine experience level
        if years_experience <= 2:
            exp_level = 'entry'
        elif years_experience <= 7:
            exp_level = 'mid'
        elif years_experience <= 15:
            exp_level = 'senior'
        else:
            exp_level = 'executive'
        
        # Basic skill extraction
        tech_skills = []
        skill_keywords = [
            'python', 'java', 'javascript', 'react', 'angular', 'node.js', 'sql',
            'aws', 'azure', 'docker', 'kubernetes', 'git', 'machine learning',
            'data analysis', 'project management', 'agile', 'scrum'
        ]
        
        for skill in skill_keywords:
            if skill in text_lower:
                tech_skills.append(skill.title())
        
        # Basic job category detection
        job_categories = []
        if any(word in text_lower for word in ['developer', 'programming', 'software', 'coding']):
            job_categories.append('Software Development')
        if any(word in text_lower for word in ['data', 'analytics', 'machine learning', 'statistics']):
            job_categories.append('Data & Analytics')
        if any(word in text_lower for word in ['manager', 'lead', 'director']):
            job_categories.append('Management & Leadership')
        
        # Default to Software Development if no categories detected
        if not job_categories:
            job_categories = ['Software Development']
        
        return {
            'experience_level': exp_level,
            'current_location': 'Not specified',
            'job_categories': job_categories,
            'target_roles': ['Software Developer', 'Analyst', 'Specialist'],
            'key_skills': tech_skills[:8] if tech_skills else ['Communication', 'Problem Solving'],
            'industries': ['Technology'],
            'work_arrangement_preference': 'Flexible',
            'estimated_salary_range': self._estimate_salary_range(exp_level),
            'years_of_experience': years_experience,
            'education_level': 'Bachelor\'s',
            'career_focus': 'Professional growth and development',
            'willing_to_relocate': False
        }

    def _estimate_years_experience(self, resume_text: str) -> int:
        """Estimate years of experience from resume text"""
        # Look for year patterns
        import datetime
        current_year = datetime.datetime.now().year
        
        # Find years in resume
        years = re.findall(r'\b(19|20)\d{2}\b', resume_text)
        years = [int(year) for year in years if 1990 <= int(year) <= current_year]
        
        if years:
            # Estimate based on earliest year mentioned
            min_year = min(years)
            estimated_years = max(0, current_year - min_year)
            return min(estimated_years, 40)  # Cap at 40 years
        
        # Fallback: look for experience keywords
        text_lower = resume_text.lower()
        if 'senior' in text_lower or 'lead' in text_lower:
            return 8
        elif 'junior' in text_lower or 'entry' in text_lower:
            return 2
        else:
            return 5  # Default to mid-level

    def _estimate_salary_range(self, experience_level: str, location_type: str = 'major_metro') -> str:
        """Estimate salary range based on experience level"""
        if experience_level in SALARY_RANGES and location_type in SALARY_RANGES[experience_level]:
            ranges = SALARY_RANGES[experience_level][location_type]
            return ranges[1]  # Return middle range
        return '$50,000-$80,000'  # Default range

    def analyze_resume_with_groq(self, resume_text: str, user_profile: dict) -> dict:
        """Analyze resume using Groq API with enhanced user profile"""
        try:
            # Create analysis prompt
            analysis_prompt = self._create_enhanced_analysis_prompt(resume_text, user_profile)
            
            # Call Groq API
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert HR professional, career counselor, and resume analyzer with deep knowledge of current job markets, salary trends, and industry requirements. Provide detailed, constructive, and market-relevant analysis based on the candidate's actual resume content and extracted profile."
                    },
                    {
                        "role": "user", 
                        "content": analysis_prompt
                    }
                ],
                model=self.model,
                temperature=0.1,
                max_tokens=4000,
                top_p=1,
                stream=False,
                stop=None,
            )
            
            analysis_result = chat_completion.choices[0].message.content
            
            return {
                'success': True,
                'analysis': analysis_result,
                'model_used': self.model,
                'tokens_used': chat_completion.usage.total_tokens if hasattr(chat_completion, 'usage') else 0
            }
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return {
                'success': False,
                'error': str(e),
                'analysis': None
            }

    def _create_enhanced_analysis_prompt(self, resume_text: str, user_profile: dict) -> str:
        """Create comprehensive analysis prompt with AI-extracted profile"""
        prompt = f"""
Please analyze the following resume comprehensively based on the AI-extracted candidate profile. Provide market-relevant insights and actionable recommendations.

AI-EXTRACTED CANDIDATE PROFILE:
- Experience Level: {user_profile.get('experience_level', 'Not specified')}
- Current Location: {user_profile.get('current_location', 'Not specified')}
- Years of Experience: {user_profile.get('years_of_experience', 'Not specified')}
- Key Skills: {', '.join(user_profile.get('key_skills', []))}
- Target Job Categories: {', '.join(user_profile.get('job_categories', []))}
- Recommended Roles: {', '.join(user_profile.get('target_roles', []))}
- Industry Focus: {', '.join(user_profile.get('industries', []))}
- Education Level: {user_profile.get('education_level', 'Not specified')}
- Estimated Salary Range: {user_profile.get('estimated_salary_range', 'Not specified')}
- Work Preference: {user_profile.get('work_arrangement_preference', 'Not specified')}
- Career Focus: {user_profile.get('career_focus', 'Not specified')}
- Open to Relocation: {user_profile.get('willing_to_relocate', 'Not specified')}

RESUME TEXT:
{resume_text}

Please provide a comprehensive analysis covering these areas:

1. MARKET COMPETITIVENESS ASSESSMENT:
   - Overall market readiness score (1-10) for the identified target roles
   - Competitiveness analysis for each recommended job category
   - Salary expectation reality check based on current skills and experience
   - Geographic market alignment (if location specified)

2. TARGET ROLE FIT ANALYSIS:
   - Detailed analysis of fit for each recommended target role
   - Skills gap analysis for specific positions
   - Experience relevance to target positions
   - Industry transition feasibility assessment

3. TECHNICAL & PROFESSIONAL SKILLS EVALUATION:
   - Current skill inventory validation and enhancement
   - Skills demand in target market for recommended roles
   - Emerging skills to develop for career progression
   - Certifications that would add significant value

4. EXPERIENCE & ACHIEVEMENT ANALYSIS:
   - Career progression assessment and trajectory
   - Achievement quantification and business impact
   - Leadership and project management evidence
   - Industry-specific experience depth evaluation

5. RESUME OPTIMIZATION FOR TARGET ROLES:
   - ATS (Applicant Tracking System) compatibility for recommended roles
   - Keyword optimization for specific target positions
   - Content structure and formatting improvements
   - Missing critical sections for target roles

6. SALARY & COMPENSATION INSIGHTS:
   - Validation of estimated salary range
   - Current market rates for recommended roles at this experience level
   - Salary negotiation positioning and strategies
   - Total compensation considerations and benefits

7. CAREER DEVELOPMENT ROADMAP:
   - Immediate improvement actions (0-3 months)
   - Medium-term development goals (3-12 months) for target roles
   - Long-term career path progression (1-3 years)
   - Networking and professional development recommendations

8. JOB SEARCH STRATEGY FOR RECOMMENDED ROLES:
   - Best job boards and platforms for specific target roles
   - Company types and sizes to target based on profile
   - Application strategy for recommended positions
   - Interview preparation focus areas for target roles

9. RISK ASSESSMENT & MITIGATION:
    - Potential concerns employers might have
    - Career gaps or transitions that need addressing
    - Over/under-qualification risks for target roles
    - Market timing and industry trend considerations

10. PRIORITIZED ACTION PLAN:
    - Top 5 immediate priorities for improving candidacy
    - Specific resources and tools to leverage
    - Timeline for improvements with milestones
    - Success metrics and progress tracking methods

Focus on providing specific, data-driven recommendations that align with the candidate's actual background and the current job market for their recommended roles. Base all salary and market insights on 2024-2025 market conditions.
"""
        return prompt

    def analyze_resume_from_pdf(self, pdf_path: str) -> dict:
        """Complete analysis pipeline for PDF resume with content-based recommendations"""
        logger.info(f"Starting comprehensive PDF analysis for: {pdf_path}")
        
        # Extract text from PDF
        pdf_result = self.extract_text_from_pdf(pdf_path)
        
        if not pdf_result['success']:
            return {
                'success': False,
                'message': 'Failed to extract text from PDF',
                'pdf_processing': pdf_result
            }
        
        resume_text = pdf_result['text']
        
        if len(resume_text.strip()) < 50:
            return {
                'success': False,
                'message': 'Extracted text too short - PDF may be image-based or corrupted',
                'pdf_processing': pdf_result
            }
        
        # Analyze resume content to extract profile
        profile_result = self.analyze_resume_content(resume_text)
        user_profile = profile_result['profile']
        
        # Analyze with Groq using extracted profile
        analysis_result = self.analyze_resume_with_groq(resume_text, user_profile)
        
        # Compile final result
        result = {
            'success': analysis_result['success'],
            'pdf_processing': pdf_result,
            'profile_extraction': profile_result,
            'groq_analysis': analysis_result,
            'extracted_profile': user_profile,
            'resume_text_length': len(resume_text),
            'resume_word_count': len(resume_text.split())
        }
        
        if not analysis_result['success']:
            result['message'] = 'Analysis failed'
            result['error'] = analysis_result.get('error')
        
        return result

    def analyze_resume_from_text(self, resume_text: str) -> dict:
        """Complete analysis pipeline for text resume with content-based recommendations"""
        logger.info("Starting comprehensive text analysis")
        
        if len(resume_text.strip()) < 50:
            return {
                'success': False,
                'message': 'Resume text too short for meaningful analysis'
            }
        
        # Analyze resume content to extract profile
        profile_result = self.analyze_resume_content(resume_text)
        user_profile = profile_result['profile']
        
        # Analyze with Groq using extracted profile
        analysis_result = self.analyze_resume_with_groq(resume_text, user_profile)
        
        # Compile final result
        result = {
            'success': analysis_result['success'],
            'profile_extraction': profile_result,
            'groq_analysis': analysis_result,
            'extracted_profile': user_profile,
            'resume_text_length': len(resume_text),
            'resume_word_count': len(resume_text.split())
        }
        
        if not analysis_result['success']:
            result['message'] = 'Analysis failed'
            result['error'] = analysis_result.get('error')
        
        return result

def save_analysis_to_file(result: dict, output_path: str = None) -> str:
    """Save analysis results to a file"""
    if output_path is None:
        import datetime
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f"resume_analysis_{timestamp}.json"
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        return output_path
    except Exception as e:
        logger.error(f"Failed to save analysis: {e}")
        return None

def analyze_pdf_resume(pdf_path: str, save_results: bool = False):
    """Analyze a resume from PDF file with AI-based profile extraction"""
    print(f"\n📄 Analyzing PDF with AI-powered job recommendations: {pdf_path}")

    # Check if file exists
    if not Path(pdf_path).exists():
        print(f"❌ File not found: {pdf_path}")
        return None

    # Initialize analyzer
    try:
        analyzer = ResumeAnalyzer()
    except ValueError as e:
        print(f"❌ Setup error: {e}")
        return None

    print("🧠 Extracting candidate profile from resume content...")

    # Run the analysis
    try:
        result = analyzer.analyze_resume_from_pdf(pdf_path)

        if result['success']:
            print("✅ Analysis completed successfully!")
            
            # Show extracted profile
            if 'extracted_profile' in result:
                print_extracted_profile(result['extracted_profile'])
            
            print_results(result)
            
            # Save results if requested
            if save_results:
                output_file = save_analysis_to_file(result)
                if output_file:
                    print(f"\n💾 Results saved to: {output_file}")
            
            return result
        else:
            print(f"❌ Analysis failed: {result.get('message', 'Unknown error')}")
            if 'error' in result:
                print(f"Error details: {result['error']}")
            return None

    except Exception as e:
        print(f"❌ Exception during analysis: {e}")
        return None

def analyze_text_resume(resume_text: str, save_results: bool = False):
    """Analyze a resume from text with AI-based profile extraction"""
    print("\n📝 Analyzing text resume with AI-powered job recommendations...")

    if not resume_text.strip():
        print("❌ Resume text is empty")
        return None

    # Initialize analyzer
    try:
        analyzer = ResumeAnalyzer()
    except ValueError as e:
        print(f"❌ Setup error: {e}")
        return None

    print("🧠 Extracting candidate profile from resume content...")

    try:
        result = analyzer.analyze_resume_from_text(resume_text)

        if result['success']:
            print("✅ Text analysis completed!")
            
            # Show extracted profile
            if 'extracted_profile' in result:
                print_extracted_profile(result['extracted_profile'])
            
            print_results(result)
            
            # Save results if requested
            if save_results:
                output_file = save_analysis_to_file(result)
                if output_file:
                    print(f"\n💾 Results saved to: {output_file}")
            
            return result
        else:
            print(f"❌ Text analysis failed: {result.get('message', 'Unknown error')}")
            return None

    except Exception as e:
        print(f"❌ Exception during text analysis: {e}")
        return None

def print_extracted_profile(profile: dict):
    """Print the AI-extracted profile summary"""
    print("\n" + "="*60)
    print("🤖 AI-EXTRACTED CANDIDATE PROFILE")
    print("="*60)
    
    print(f"Experience Level: {profile.get('experience_level', 'N/A')}")
    print(f"Years of Experience: {profile.get('years_of_experience', 'N/A')}")
    print(f"Location: {profile.get('current_location', 'N/A')}")
    print(f"Education: {profile.get('education_level', 'N/A')}")
    print(f"Work Preference: {profile.get('work_arrangement_preference', 'N/A')}")
    
    if profile.get('job_categories'):
        print(f"Target Job Categories: {', '.join(profile['job_categories'])}")
    
    if profile.get('target_roles'):
        print(f"Recommended Roles: {', '.join(profile['target_roles'])}")
    
    if profile.get('key_skills'):
        print(f"Key Skills: {', '.join(profile['key_skills'])}")
    
    if profile.get('industries'):
        print(f"Target Industries: {', '.join(profile['industries'])}")
    
    print(f"Estimated Salary Range: {profile.get('estimated_salary_range', 'N/A')}")
    print(f"Career Focus: {profile.get('career_focus', 'N/A')}")

def print_results(result: dict):
    """Print analysis results in a readable format"""

    print("\n" + "="*60)
    print("📊 COMPREHENSIVE AI-POWERED RESUME ANALYSIS")
    print("="*60)

    # Profile Extraction Status
    profile_extraction = result.get('profile_extraction', {})
    print(f"\n🤖 AI PROFILE EXTRACTION:")
    print(f"   Success: {profile_extraction.get('success', False)}")
    if not profile_extraction.get('success', False) and 'error' in profile_extraction:
        print(f"   Error: {profile_extraction['error']}")

    # Basic Info
    print(f"\n📋 DOCUMENT INFO:")
    print(f"   Word Count: {result.get('resume_word_count', 0)}")
    print(f"   Text Length: {result.get('resume_text_length', 0)} characters")

    # PDF Processing Info (if from PDF)
    if 'pdf_processing' in result:
        pdf_info = result['pdf_processing']
        print(f"\n📄 PDF PROCESSING:")
        print(f"   Success: {pdf_info.get('success', False)}")
        print(f"   Pages: {pdf_info.get('pages', 0)}")
        print(f"   Extracted Words: {pdf_info.get('word_count', 0)}")

    # Groq Analysis
    print(f"\n🤖 AI ANALYSIS:")
    groq_analysis = result.get('groq_analysis')
    if groq_analysis and groq_analysis.get('success'):
        print(f"   Model Used: {groq_analysis.get('model_used', 'Unknown')}")
        print(f"   Tokens Used: {groq_analysis.get('tokens_used', 0)}")
        print(f"\n📝 DETAILED CONTENT-BASED ANALYSIS:")
        print("-" * 50)
        analysis_text = groq_analysis.get('analysis', 'No analysis available')
        print(analysis_text)
    else:
        print("   Analysis failed or not available")
        if groq_analysis and 'error' in groq_analysis:
            print(f"   Error: {groq_analysis['error']}")

    print("\n" + "="*60)

def interactive_mode():
    """Run in interactive mode with AI-powered job recommendations"""
    print("\n🚀 AI-POWERED RESUME ANALYSIS WITH CONTENT-BASED JOB RECOMMENDATIONS")
    print("="*70)
    print("🧠 Jobs and salaries are now automatically determined from your resume content!")
    print("="*70)

    # Check API key first
    if not os.getenv('GROQ_API_KEY'):
        print("❌ GROQ_API_KEY not found!")
        print("Please set your Groq API key in the .env file:")
        print("GROQ_API_KEY=your_groq_api_key_here")
        return

    while True:
        print("\nChoose analysis type:")
        print("1. Analyze PDF file (AI will extract your profile)")
        print("2. Analyze text input (AI will extract your profile)")
        print("3. View available job categories and salary ranges")
        print("4. Exit")

        choice = input("\nEnter choice (1-4): ").strip()

        if choice == '1':
            pdf_path = input("Enter PDF file path: ").strip()
            save_option = input("Save results to file? (y/n): ").strip().lower() == 'y'
            analyze_pdf_resume(pdf_path, save_results=save_option)

        elif choice == '2':
            print("\nPaste your resume text (press Enter twice when done):")
            lines = []
            while True:
                line = input()
                if line == '' and lines and lines[-1] == '':
                    break
                lines.append(line)

            resume_text = '\n'.join(lines[:-1])  # Remove the last empty line

            if resume_text.strip():
                save_option = input("Save results to file? (y/n): ").strip().lower() == 'y'
                analyze_text_resume(resume_text, save_results=save_option)
            else:
                print("❌ No text provided")

        elif choice == '3':
            print_job_info()

        elif choice == '4':
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")

def print_job_info():
    """Display available job categories and sample salary ranges"""
    print("\n📋 AVAILABLE JOB CATEGORIES:")
    print("="*50)
    print("(AI automatically selects the most relevant categories for your resume)")
    
    for category, roles in JOB_CATEGORIES.items():
        print(f"\n{category}:")
        for role in roles[:5]:  # Show first 5 roles
            print(f"  • {role}")
        if len(roles) > 5:
            print(f"  ... and {len(roles) - 5} more")
    
    print(f"\n💰 SAMPLE SALARY RANGES BY EXPERIENCE:")
    print("="*50)
    print("(AI estimates your level and provides market-appropriate ranges)")
    print("Entry Level (Major Metro): $45k-$80k")
    print("Mid Level (Major Metro): $70k-$140k") 
    print("Senior Level (Major Metro): $120k-$250k")
    print("Executive Level (Major Metro): $200k+")
    print("\n(Actual ranges vary by location, role, and market conditions)")

def print_usage():
    """Print usage information"""
    print("""
Usage: python resume_analyzer.py [options]

Options:
  --file, -f PATH         Analyze PDF file at PATH
  --text, -t TEXT         Analyze text directly (quote the text)
  --save, -s              Save analysis results to file
  --interactive, -i       Run in interactive mode (default)
  --help, -h              Show this help message

Examples:
  python resume_analyzer.py --file "my_resume.pdf" --save
  python resume_analyzer.py --text "John Doe Software Engineer..." 
  python resume_analyzer.py --interactive
  python resume_analyzer.py  # Default: interactive mode

Key Features:
  🧠 AI automatically extracts job recommendations from resume content
  🎯 Content-based job category and role suggestions
  💰 Market-appropriate salary estimates based on experience
  📊 Comprehensive analysis tailored to your actual background

Environment Setup:
  Create a .env file with: GROQ_API_KEY=your_groq_api_key_here
  Get your API key from: https://console.groq.com/

Dependencies:
  pip install groq PyPDF2 python-dotenv
""")

def main():
    """Main function - entry point"""
    print("🎯 AI-POWERED RESUME ANALYZER WITH INTELLIGENT JOB RECOMMENDATIONS")
    print("Using Llama 3.3 70B model via Groq API")
    print("🧠 Jobs and salaries automatically determined from resume content!")
    print("="*70)

    # Check environment setup
    if not os.getenv('GROQ_API_KEY'):
        print("❌ GROQ_API_KEY not found in environment")
        print("   Create a .env file with: GROQ_API_KEY=your_groq_api_key_here")
        print("   Get your API key from: https://console.groq.com/")
        
        proceed = input("\nContinue anyway? (y/n): ").strip().lower()
        if proceed != 'y':
            print("Setup your .env file first, then try again")
            return

    # Parse command line arguments
    if len(sys.argv) > 1:
        # Command line mode
        args = sys.argv[1:]
        
        # Handle help
        if '--help' in args or '-h' in args:
            print_usage()
            return
        
        # Parse arguments
        pdf_file = None
        text_input = None
        save_results = '--save' in args or '-s' in args
        
        # Get file path
        if '--file' in args or '-f' in args:
            try:
                file_idx = args.index('--file') if '--file' in args else args.index('-f')
                pdf_file = args[file_idx + 1] if file_idx + 1 < len(args) else None
            except (ValueError, IndexError):
                print("❌ Missing file path after --file/-f")
                return
        
        # Get text input
        if '--text' in args or '-t' in args:
            try:
                text_idx = args.index('--text') if '--text' in args else args.index('-t')
                text_input = args[text_idx + 1] if text_idx + 1 < len(args) else None
            except (ValueError, IndexError):
                print("❌ Missing text after --text/-t")
                return
        
        # Process based on input type
        if pdf_file:
            print("🧠 AI will automatically extract your job profile from the resume...")
            analyze_pdf_resume(pdf_file, save_results)
        elif text_input:
            print("🧠 AI will automatically extract your job profile from the resume...")
            analyze_text_resume(text_input, save_results)
        else:
            print("❌ No input provided. Use --file or --text, or run without arguments for interactive mode.")
            print("Use --help for usage information.")
    
    else:
        # Interactive mode (default)
        interactive_mode()

if __name__ == "__main__":
    main()