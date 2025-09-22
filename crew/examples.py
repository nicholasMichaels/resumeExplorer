import os
from dotenv import load_dotenv
from main import EnhancedResumeAnalyzer
import json

# Load environment variables
load_dotenv()

def example_text_analysis():
    """Example: Analyzing resume from text"""
    print("=== TEXT ANALYSIS EXAMPLE ===")

    analyzer = EnhancedResumeAnalyzer()

    resume_text = """
    Sarah Williams
    Senior Data Scientist
    sarah.williams@email.com | (555) 123-9876 | LinkedIn: linkedin.com/in/sarahw
    San Francisco, CA

    PROFESSIONAL SUMMARY
    Experienced data scientist with 5+ years developing machine learning solutions for Fortune 500 companies.
    Expertise in predictive modeling, statistical analysis, and deploying ML models to production environments.

    TECHNICAL SKILLS
    • Programming: Python, R, SQL, Scala
    • ML/AI: Scikit-learn, TensorFlow, PyTorch, Keras
    • Data Tools: Pandas, NumPy, Matplotlib, Seaborn, Tableau
    • Cloud: AWS (S3, EC2, SageMaker), Google Cloud Platform
    • Databases: PostgreSQL, MongoDB, Redis

    PROFESSIONAL EXPERIENCE

    Senior Data Scientist | TechCorp Inc. | 2021 - Present
    • Led development of customer churn prediction model, reducing churn by 23%
    • Built recommendation system serving 2M+ users daily with 15% CTR improvement
    • Mentored team of 4 junior data scientists and established ML best practices
    • Deployed 12+ models to production using MLOps pipelines

    Data Scientist | Analytics Solutions | 2019 - 2021
    • Developed fraud detection system processing 100K+ transactions daily
    • Created automated reporting dashboard reducing manual work by 80%
    • Collaborated with product teams to define KPIs and success metrics
    • Improved model accuracy by 12% through feature engineering and hyperparameter tuning

    Junior Data Analyst | StartupXYZ | 2018 - 2019
    • Performed exploratory data analysis on customer behavior datasets
    • Created visualizations and reports for executive leadership
    • Automated data collection processes, saving 20 hours per week

    EDUCATION
    Master of Science in Data Science
    Stanford University | 2018 | GPA: 3.8/4.0

    Bachelor of Science in Statistics
    UC Berkeley | 2016 | Magna Cum Laude

    CERTIFICATIONS
    • AWS Certified Machine Learning - Specialty (2022)
    • Google Professional Data Engineer (2021)
    • Certified Analytics Professional (CAP) (2020)

    PROJECTS
    • Stock Price Prediction: Built LSTM model achieving 85% directional accuracy
    • NLP Sentiment Analysis: Processed 1M+ social media posts with 92% accuracy
    • Computer Vision: Developed image classification system for medical diagnostics
    """

    user_profile = {
        'location': 'San Francisco, CA',
        'experience_level': 'senior',
        'job_preferences': ['data science', 'machine learning', 'AI'],
        'salary_range': '$130,000-$180,000',
        'job_type': 'full-time',
        'remote_preference': 'hybrid'
    }

    # Run analysis
    result = analyzer.analyze_resume_from_text(resume_text, user_profile)

    if result['success']:
        print("✅ Analysis completed successfully!")

        # Print readability analysis
        readability = result['readability_analysis']
        print(f"\n📊 READABILITY ANALYSIS:")
        print(f"Level: {readability['readability_level']}")
        print(f"Word Count: {readability['metrics'].get('word_count', 'N/A')}")
        print(f"Reading Ease Score: {readability['metrics'].get('flesch_reading_ease', 'N/A'):.1f}")

        # Print key phrases
        print(f"\n🔑 KEY PHRASES: {', '.join(readability['key_phrases'][:8])}")

        print(f"\n📝 CREW ANALYSIS:")
        print(f"Type: {type(result['crew_analysis'])}")

    else:
        print(f"❌ Analysis failed: {result['message']}")
        print(f"Error: {result.get('error', 'Unknown error')}")

def example_pdf_analysis():
    """Example: Analyzing resume from PDF"""
    print("\n=== PDF ANALYSIS EXAMPLE ===")

    analyzer = EnhancedResumeAnalyzer()

    # Example with PDF file path
    pdf_path = "sample_resume.pdf"  # Replace with actual PDF path

    user_profile = {
        'location': 'Remote',
        'experience_level': 'mid',
        'job_preferences': ['software development', 'backend'],
        'salary_range': '$80,000-$120,000'
    }

    # Check if PDF file exists
    if os.path.exists(pdf_path):
        result = analyzer.analyze_resume_from_pdf(pdf_path=pdf_path, user_profile=user_profile)

        if result['success']:
            print("✅ PDF Analysis completed!")

            # PDF processing info
            pdf_info = result['pdf_processing']
            print(f"\n📄 PDF PROCESSING:")
            print(f"Text Length: {pdf_info['text_length']} characters")
            print(f"Word Count: {pdf_info['word_count']} words")
            print(f"Key Phrases: {', '.join(pdf_info['key_phrases'][:5])}")

            # Readability
            readability = result['readability_analysis']
            print(f"\n📊 READABILITY:")
            print(f"Level: {readability['readability_level']}")

        else:
            print(f"❌ PDF Analysis failed: {result['message']}")
    else:
        print(f"⚠️ PDF file not found: {pdf_path}")
        print("Creating a sample PDF analysis simulation...")

        # Simulate PDF analysis with extracted text
        sample_pdf_text = """
        Michael Chen
        DevOps Engineer
        michael.chen@email.com

        EXPERIENCE
        DevOps Engineer at CloudTech (2020-2024)
        - Managed AWS infrastructure for 50+ microservices
        - Implemented CI/CD pipelines reducing deployment time by 60%
        - Automated monitoring and alerting systems

        SKILLS
        Docker, Kubernetes, AWS, Terraform, Python, Jenkins
        """

        result = analyzer.analyze_resume_from_text(sample_pdf_text, user_profile)
        if result['success']:
            print("✅ Simulated PDF analysis completed!")

def example_batch_processing():
    """Example: Processing multiple resumes"""
    print("\n=== BATCH PROCESSING EXAMPLE ===")

    analyzer = EnhancedResumeAnalyzer()

    # Sample resume data
    resumes = [
        {
            'name': 'Frontend Developer',
            'text': """
            Alex Rodriguez
            Frontend Developer
            alex@email.com | (555) 001-0001

            SKILLS: React, JavaScript, TypeScript, CSS, HTML5, Git

            EXPERIENCE:
            Frontend Developer at WebCorp (2022-2024)
            - Built responsive web applications using React
            - Improved page load speeds by 40%
            """
        },
        {
            'name': 'Backend Developer',
            'text': """
            Jamie Kim
            Backend Developer
            jamie@email.com | (555) 002-0002

            SKILLS: Python, Django, PostgreSQL, Redis, Docker

            EXPERIENCE:
            Backend Developer at DataCorp (2021-2024)
            - Developed RESTful APIs serving 100K+ requests daily
            - Optimized database queries improving response time by 50%
            """
        }
    ]

    results = []
    for resume in resumes:
        print(f"\nProcessing: {resume['name']}")
        result = analyzer.analyze_resume_from_text(resume['text'])

        if result['success']:
            readability = result['readability_analysis']
            summary = {
                'name': resume['name'],
                'success': True,
                'readability_level': readability['readability_level'],
                'word_count': readability['metrics'].get('word_count', 0),
                'key_phrases': readability['key_phrases'][:3]
            }
        else:
            summary = {
                'name': resume['name'],
                'success': False,
                'error': result.get('error', 'Unknown error')
            }

        results.append(summary)

    # Print batch results
    print(f"\n📊 BATCH RESULTS:")
    for result in results:
        status = "✅" if result['success'] else "❌"
        print(f"{status} {result['name']}")
        if result['success']:
            print(f"   Readability: {result['readability_level']}")
            print(f"   Words: {result['word_count']}")
            print(f"   Key Phrases: {', '.join(result['key_phrases'])}")

def example_api_integration():
    """Example: Integration with web API"""
    print("\n=== API INTEGRATION EXAMPLE ===")

    # Simulate API request data
    api_request = {
        'resume_text': """
        Dr. Emma Watson
        Research Scientist
        emma.watson@research.edu

        PhD in Machine Learning, MIT (2020)
        MS in Computer Science, Stanford (2017)

        EXPERIENCE:
        Senior Research Scientist | AI Lab Inc. | 2020-2024
        - Published 15 peer-reviewed papers in top-tier conferences
        - Led research team developing novel deep learning architectures
        - Secured $2M in research funding from NSF and industry partners

        SKILLS: Python, TensorFlow, PyTorch, Research, Publications, Grant Writing
        """,
        'user_preferences': {
            'target_roles': ['research scientist', 'AI researcher', 'ML engineer'],
            'location': 'Boston, MA',
            'salary_expectation': '$150,000+'
        }
    }

    analyzer = EnhancedResumeAnalyzer()

    try:
        # Process the API request
        result = analyzer.analyze_resume_from_text(
            api_request['resume_text'],
            api_request['user_preferences']
        )

        # Format API response
        api_response = {
            'status': 'success' if result['success'] else 'error',
            'data': {
                'readability': result.get('readability_analysis', {}),
                'analysis': result.get('crew_analysis', {}),
                'processing_time': '2.3s',  # Would be calculated in real implementation
                'confidence_score': 0.92
            } if result['success'] else None,
            'error': result.get('error') if not result['success'] else None
        }

        print(f"API Response Status: {api_response['status']}")
        if api_response['status'] == 'success':
            data = api_response['data']
            print(f"Readability Level: {data['readability'].get('readability_level', 'Unknown')}")
            print(f"Confidence Score: {data['confidence_score']}")
            print(f"Processing Time: {data['processing_time']}")

    except Exception as e:
        print(f"❌ API Integration error: {e}")

def main():
    """Run all examples"""
    print("🚀 RUNNING INTEGRATION EXAMPLES")
    print("=" * 50)

    # Check environment
    if not os.getenv('GROQ_API_KEY'):
        print("⚠️ Warning: GROQ_API_KEY not found in environment")
        print("Some examples may not work without proper API configuration")

    try:
        example_text_analysis()
        example_pdf_analysis()
        example_batch_processing()
        example_api_integration()

        print("\n🎉 All examples completed!")

    except Exception as e:
        print(f"\n❌ Examples failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
