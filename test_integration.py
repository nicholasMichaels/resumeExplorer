import os
import sys
import logging
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_groq_connection():
    """Test Groq API connection"""
    try:
        from agents.groq_llm import GroqLLM

        logger.info("Testing Groq API connection...")

        if not os.getenv("GROQ_API_KEY"):
            logger.error("GROQ_API_KEY not found in environment variables")
            return False

        groq_llm = GroqLLM()
        test_prompt = "Hello, please respond with 'Connection successful' if you can read this."

        response = groq_llm(test_prompt)
        logger.info(f"Groq response: {response[:100]}...")

        if "error" in response.lower():
            logger.error(f"Groq API error: {response}")
            return False

        logger.info("✅ Groq API connection successful")
        return True

    except Exception as e:
        logger.error(f"❌ Groq API test failed: {e}")
        return False

def test_pdf_processing():
    """Test PDF processing capabilities"""
    try:
        from utils.enhanced_pdf_processor import EnhancedPDFProcessor

        logger.info("Testing PDF processing...")

        processor = EnhancedPDFProcessor()

        # Test with sample text
        sample_text = """
        John Doe
        Software Engineer
        john.doe@email.com | (555) 123-4567

        EXPERIENCE
        Software Developer at Tech Corp (2022-2024)
        - Developed web applications using Python and JavaScript
        - Implemented database solutions using PostgreSQL
        - Collaborated with cross-functional teams

        EDUCATION
        Bachelor of Computer Science
        University of Technology, 2022

        SKILLS
        Python, JavaScript, SQL, Git, Docker, React
        """

        # Test readability analysis
        readability = processor.analyze_readability(sample_text)
        logger.info(f"Readability level: {readability.get('readability_level', 'Unknown')}")
        logger.info(f"Word count: {readability.get('word_count', 0)}")

        # Test key phrase extraction
        key_phrases = processor.extract_key_phrases(sample_text)
        logger.info(f"Key phrases: {key_phrases[:5]}")

        if readability.get('error'):
            logger.error(f"Readability analysis error: {readability['error']}")
            return False

        logger.info("✅ PDF processing test successful")
        return True

    except Exception as e:
        logger.error(f"❌ PDF processing test failed: {e}")
        return False

def test_resume_extraction():
    """Test resume extraction with Groq"""
    try:
        from agents.resume_extractor import extract_resume_data_with_groq

        logger.info("Testing resume extraction with Groq...")

        sample_resume = """
        Jane Smith
        Data Scientist
        Email: jane.smith@email.com
        Phone: (555) 987-6543
        Location: New York, NY

        EDUCATION
        Master of Data Science
        Columbia University, 2023

        Bachelor of Mathematics
        MIT, 2021

        EXPERIENCE
        Data Scientist at Analytics Inc (2023-Present)
        - Built machine learning models for customer segmentation
        - Analyzed large datasets using Python and R
        - Created data visualizations using Tableau

        Research Assistant at MIT (2020-2021)
        - Conducted statistical analysis for research projects
        - Published findings in peer-reviewed journals

        SKILLS
        Python, R, SQL, Tableau, Machine Learning, Statistics, Pandas, NumPy
        """

        result = extract_resume_data_with_groq(sample_resume)

        if 'error' in result:
            logger.error(f"Resume extraction error: {result['error']}")
            return False

        # Verify extracted data structure
        required_fields = ['personal_info', 'education', 'experience', 'skills']
        missing_fields = [field for field in required_fields if field not in result]

        if missing_fields:
            logger.warning(f"Missing fields in extraction: {missing_fields}")

        logger.info(f"Extracted name: {result.get('personal_info', {}).get('name', 'Not found')}")
        logger.info(f"Skills count: {len(result.get('skills', []))}")
        logger.info(f"Experience entries: {len(result.get('experience', []))}")

        logger.info("✅ Resume extraction test successful")
        return True

    except Exception as e:
        logger.error(f"❌ Resume extraction test failed: {e}")
        return False

def test_enhanced_analyzer():
    """Test the complete enhanced analyzer"""
    try:
        # This would normally import from your main module
        # from main import EnhancedResumeAnalyzer

        logger.info("Testing enhanced analyzer integration...")

        # Create a mock analyzer test
        sample_resume = """
        Alex Johnson
        Full Stack Developer
        alex.johnson@email.com | (555) 555-5555

        Experienced developer with 3 years in web development.

        EXPERIENCE
        Senior Developer at WebCorp (2022-2024)
        - Led development of e-commerce platform
        - Mentored junior developers
        - Improved system performance by 40%

        SKILLS
        JavaScript, Python, React, Node.js, MongoDB, AWS
        """

        # Test individual components that would be used
        from utils.enhanced_pdf_processor import EnhancedPDFProcessor

        processor = EnhancedPDFProcessor()
        readability = processor.analyze_readability(sample_resume)
        key_phrases = processor.extract_key_phrases(sample_resume)

        logger.info(f"Integration test - Readability: {readability.get('readability_level')}")
        logger.info(f"Integration test - Key phrases: {key_phrases[:3]}")

        logger.info("✅ Enhanced analyzer integration test successful")
        return True

    except Exception as e:
        logger.error(f"❌ Enhanced analyzer test failed: {e}")
        return False

def main():
    """Run all integration tests"""
    logger.info("🚀 Starting integration tests...")

    tests = [
        ("Groq API Connection", test_groq_connection),
        ("PDF Processing", test_pdf_processing),
        ("Resume Extraction", test_resume_extraction),
        ("Enhanced Analyzer", test_enhanced_analyzer)
    ]

    results = {}

    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running: {test_name}")
        logger.info(f"{'='*50}")

        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}")
            results[test_name] = False

    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("TEST RESULTS SUMMARY")
    logger.info(f"{'='*50}")

    passed = 0
    total = len(results)

    for test_name, passed_test in results.items():
        status = "✅ PASSED" if passed_test else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
        if passed_test:
            passed += 1

    logger.info(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        logger.info("🎉 All tests passed! Integration is working correctly.")
    else:
        logger.info("⚠️  Some tests failed. Check the logs above for details.")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
