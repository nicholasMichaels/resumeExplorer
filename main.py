from crew.resume_crew import ResumeCrew
from utils.enhanced_pdf_processor import EnhancedPDFProcessor
import logging
import sys
from typing import Dict, Any, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('resume_system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class EnhancedResumeAnalyzer:
    """Enhanced resume analyzer with PDF processing and readability analysis"""

    def __init__(self):
        self.pdf_processor = EnhancedPDFProcessor()
        self.crew = ResumeCrew

    def analyze_resume_from_text(self, resume_text: str, user_profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze resume from plain text"""
        try:
            logger.info("Starting text-based resume analysis")

            if not resume_text.strip():
                raise ValueError("Resume text cannot be empty")

            # Analyze text readability
            readability = self.pdf_processor.analyze_readability(resume_text)
            key_phrases = self.pdf_processor.extract_key_phrases(resume_text)

            # Prepare inputs for crew
            inputs = {
                'resume_text': resume_text,
                'user_profile': user_profile or {},
                'readability_metrics': readability,
                'key_phrases': key_phrases
            }

            # Execute crew analysis
            crew_result = self.crew.kickoff(inputs=inputs)

            return {
                'success': True,
                'crew_analysis': crew_result,
                'readability_analysis': {
                    'metrics': readability,
                    'key_phrases': key_phrases,
                    'text_length': len(resume_text),
                    'readability_level': readability.get('readability_level', 'Unknown')
                },
                'input_type': 'text',
                'message': 'Analysis completed successfully'
            }

        except Exception as e:
            logger.error(f"Error in text-based analysis: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Text analysis failed'
            }

    def analyze_resume_from_pdf(self, pdf_path: str = None, pdf_bytes: bytes = None,
                               user_profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze resume from PDF file or bytes"""
        try:
            logger.info("Starting PDF-based resume analysis")

            # Process PDF
            pdf_data = self.pdf_processor.process_pdf(pdf_path=pdf_path, pdf_bytes=pdf_bytes)

            if not pdf_data.get('success', False):
                raise ValueError(f"PDF processing failed: {pdf_data.get('error', 'Unknown error')}")

            resume_text = pdf_data['cleaned_text']

            if not resume_text.strip():
                raise ValueError("No text could be extracted from the PDF")

            # Prepare inputs for crew
            inputs = {
                'resume_text': resume_text,
                'user_profile': user_profile or {},
                'readability_metrics': pdf_data['readability_metrics'],
                'key_phrases': pdf_data['key_phrases'],
                'pdf_metadata': {
                    'text_length': pdf_data['text_length'],
                    'word_count': pdf_data['word_count']
                }
            }

            # Execute crew analysis
            crew_result = self.crew.kickoff(inputs=inputs)

            return {
                'success': True,
                'crew_analysis': crew_result,
                'pdf_processing': pdf_data,
                'readability_analysis': {
                    'metrics': pdf_data['readability_metrics'],
                    'key_phrases': pdf_data['key_phrases'],
                    'readability_level': pdf_data['readability_metrics'].get('readability_level', 'Unknown')
                },
                'input_type': 'pdf',
                'message': 'PDF analysis completed successfully'
            }

        except Exception as e:
            logger.error(f"Error in PDF-based analysis: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'PDF analysis failed'
            }

def main():
    """Example usage of the enhanced system"""
    analyzer = EnhancedResumeAnalyzer()

    # Example 1: Text-based analysis
    sample_resume = """
    John Doe
    Software Developer
    Email: john.doe@email.com
    Phone: 555-0123
    Location: Allentown, PA

    Education:
    Bachelor of Science in Computer Science
    Muhlenberg College, 2023

    Experience:
    Software Intern at Tech Company (Summer 2022)
    - Developed web applications using Python and JavaScript
    - Collaborated with team on database design and optimization
    - Implemented RESTful APIs using Django framework

    Skills: Python, JavaScript, Git, SQL, React, Django, PostgreSQL
    """

    sample_profile = {
        'location': 'Allentown, PA',
        'experience_level': 'entry',
        'job_preferences': ['software development', 'web development'],
        'salary_range': '$50,000-$70,000'
    }

    # Run text analysis
    result = analyzer.analyze_resume_from_text(sample_resume, sample_profile)

    if result['success']:
        print("=== ANALYSIS SUCCESSFUL ===")
        print(f"Readability Level: {result['readability_analysis']['readability_level']}")
        print(f"Key Phrases: {result['readability_analysis']['key_phrases'][:5]}")
        print(f"Text Length: {result['readability_analysis']['text_length']} characters")
    else:
        print(f"Analysis failed: {result['message']}")

    # Example 2: PDF analysis (uncomment when you have a PDF file)
    # pdf_result = analyzer.analyze_resume_from_pdf(pdf_path="sample_resume.pdf", user_profile=sample_profile)
    # print(f"PDF Analysis result: {pdf_result['success']}")

if __name__ == "__main__":
    main()
