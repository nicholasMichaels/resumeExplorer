import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any
import traceback

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.enhanced_pdf_processor import EnhancedPDFProcessor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_test_pdf_content() -> bytes:
    """Create a simple test PDF using reportlab if available"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        import io

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Add test resume content
        y_position = height - 50

        resume_content = [
            "JOHN DOE",
            "Software Developer",
            "Email: john.doe@email.com",
            "Phone: (555) 123-4567",
            "Location: Allentown, PA",
            "",
            "PROFESSIONAL SUMMARY",
            "Experienced software developer with 5+ years in web development.",
            "Proficient in Python, JavaScript, and modern web frameworks.",
            "",
            "TECHNICAL SKILLS",
            "• Programming: Python, JavaScript, Java, C++",
            "• Web Technologies: React, Node.js, Django, Flask",
            "• Databases: PostgreSQL, MongoDB, Redis",
            "• Tools: Git, Docker, AWS, Jenkins",
            "",
            "PROFESSIONAL EXPERIENCE",
            "",
            "Senior Software Developer | Tech Corp Inc. | 2020 - Present",
            "• Led development of microservices architecture serving 1M+ users",
            "• Implemented CI/CD pipelines reducing deployment time by 60%",
            "• Mentored team of 3 junior developers",
            "",
            "Software Developer | StartupXYZ | 2018 - 2020",
            "• Developed RESTful APIs using Python Django framework",
            "• Built responsive web applications with React and TypeScript",
            "• Improved application performance by 40% through optimization",
            "",
            "EDUCATION",
            "Bachelor of Science in Computer Science",
            "University of Technology | 2018",
            "GPA: 3.8/4.0",
        ]

        for line in resume_content:
            p.drawString(50, y_position, line)
            y_position -= 20
            if y_position < 50:  # Start new page if needed
                p.showPage()
                y_position = height - 50

        p.save()
        buffer.seek(0)
        return buffer.read()

    except ImportError:
        logger.warning("reportlab not available, cannot create test PDF")
        return None

def test_pdf_extraction_methods():
    """Test different PDF extraction methods"""
    print("\n=== TESTING PDF EXTRACTION METHODS ===")

    processor = EnhancedPDFProcessor()

    # Test with created PDF content
    test_pdf_bytes = create_test_pdf_content()

    if test_pdf_bytes:
        print(f"✓ Created test PDF ({len(test_pdf_bytes)} bytes)")

        # Test processing
        result = processor.process_pdf(pdf_bytes=test_pdf_bytes)

        if result['success']:
            print(f"✓ PDF processing successful!")
            print(f"  Extraction method: {result.get('extraction_method', 'unknown')}")
            print(f"  Text length: {result['text_length']} characters")
            print(f"  Word count: {result['word_count']} words")
            print(f"  Key phrases: {result['key_phrases'][:5]}")
            print(f"  Readability: {result['readability_metrics'].get('readability_level', 'unknown')}")

            # Show first 200 characters of extracted text
            print(f"\n  Extracted text preview:")
            print(f"  {result['cleaned_text'][:200]}...")

        else:
            print(f"✗ PDF processing failed: {result.get('error', 'Unknown error')}")

    else:
        print("✗ Could not create test PDF (reportlab not available)")
        print("  To test with reportlab: pip install reportlab")

def test_with_existing_pdf():
    """Test with an existing PDF file"""
    print("\n=== TESTING WITH EXISTING PDF FILE ===")

    # Look for PDF files in current directory
    pdf_files = list(Path('.').glob('*.pdf'))

    if not pdf_files:
        print("ℹ No PDF files found in current directory")
        print("  Place a resume PDF file in the current directory to test")
        return

    pdf_path = pdf_files[0]
    print(f"Testing with: {pdf_path}")

    processor = EnhancedPDFProcessor()
    result = processor.process_pdf(pdf_path=str(pdf_path))

    if result['success']:
        print("✓ Real PDF processing successful!")
        print(f"  Text length: {result['text_length']} characters")
        print(f"  Word count: {result['word_count']} words")
        print(f"  Readability: {result['readability_metrics'].get('readability_level', 'unknown')}")
        print(f"  Key phrases: {result['key_phrases'][:8]}")

        # Show text sample
        cleaned_text = result['cleaned_text']
        if len(cleaned_text) > 300:
            print(f"\n  Text sample:")
            print(f"  {cleaned_text[:300]}...")
        else:
            print(f"\n  Full text:")
            print(f"  {cleaned_text}")

    else:
        print(f"✗ Real PDF processing failed: {result.get('error', 'Unknown error')}")

def test_full_crewai_integration():
    """Test full CrewAI integration with PDF"""
    print("\n=== TESTING FULL CREWAI INTEGRATION ===")

    if not os.getenv('GROQ_API_KEY'):
        print("✗ GROQ_API_KEY not found. Set it in .env file to test CrewAI integration")
        return

    try:
        from main import EnhancedResumeAnalyzer

        analyzer = EnhancedResumeAnalyzer()
        print("✓ EnhancedResumeAnalyzer initialized")

        # Test with created PDF
        test_pdf_bytes = create_test_pdf_content()

        if test_pdf_bytes:
            print("✓ Testing PDF analysis with CrewAI...")

            user_profile = {
                'location': 'Allentown, PA',
                'experience_level': 'senior',
                'job_preferences': ['software development', 'web development'],
                'salary_range': '$80,000-$120,000'
            }

            result = analyzer.analyze_resume_from_pdf(
                pdf_bytes=test_pdf_bytes,
                user_profile=user_profile
            )

            if result['success']:
                print("✓ Full CrewAI PDF analysis successful!")
                print(f"  Input type: {result['input_type']}")
                print(f"  Readability level: {result['readability_analysis']['readability_level']}")
                print(f"  Key phrases: {result['readability_analysis']['key_phrases'][:5]}")
                print(f"  Crew analysis type: {type(result.get('crew_analysis'))}")

            else:
                print(f"✗ CrewAI PDF analysis failed: {result.get('error', 'Unknown error')}")
                print(f"  Message: {result.get('message', 'No message')}")
        else:
            print("✗ Cannot test CrewAI integration without test PDF")

    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("  Make sure all required files are in place")
    except Exception as e:
        print(f"✗ CrewAI integration test failed: {e}")
        traceback.print_exc()

def test_error_handling():
    """Test error handling with various problematic inputs"""
    print("\n=== TESTING ERROR HANDLING ===")

    processor = EnhancedPDFProcessor()

    test_cases = [
        ("Empty bytes", b''),
        ("Invalid PDF bytes", b'This is not a PDF file'),
        ("None input", None),
    ]

    for test_name, test_input in test_cases:
        print(f"\nTesting: {test_name}")

        try:
            if test_input is None:
                result = processor.process_pdf()  # No arguments
            else:
                result = processor.process_pdf(pdf_bytes=test_input)

            if result['success']:
                print(f"  Unexpected success: {result.get('message', 'No message')}")
            else:
                print(f"  ✓ Properly handled error: {result.get('error', 'No error message')[:100]}")

        except Exception as e:
            print(f"  ✓ Exception properly caught: {str(e)[:100]}")

def main():
    """Run all PDF processing tests"""
    print("🔍 PDF PROCESSING TEST SUITE")
    print("=" * 50)

    try:
        test_pdf_extraction_methods()
        test_with_existing_pdf()
        test_error_handling()
        test_full_crewai_integration()

        print("\n" + "=" * 50)
        print("✅ All PDF tests completed!")
        print("\nNext steps:")
        print("1. If tests passed, your PDF processing is working")
        print("2. Add GROQ_API_KEY to .env file if not already done")
        print("3. Run: python main.py")
        print("4. Try with your own PDF files")

    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
