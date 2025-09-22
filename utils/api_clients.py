import requests
import logging
from typing import Dict, List, Any
import time
from functools import wraps

logger = logging.getLogger(__name__)

def retry_on_failure(max_retries=3, delay=1):
    """Decorator for retrying API calls"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying...")
                    time.sleep(delay * (attempt + 1))
            return None
        return wrapper
    return decorator

class JobAPIClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; ResumeBot/1.0)'
        })

@retry_on_failure(max_retries=3)
def fetch_job_listings(profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call job search APIs and return matched listings
    """
    try:
        if not profile_data:
            raise ValueError("Profile data cannot be empty")

        # Validate required fields
        required_fields = ['skills', 'experience_level', 'location']
        missing_fields = [field for field in required_fields if field not in profile_data]
        if missing_fields:
            logger.warning(f"Missing profile fields: {missing_fields}")

        # Extract search parameters
        keywords = profile_data.get('skills', [])
        location = profile_data.get('location', 'Remote')
        experience = profile_data.get('experience_level', 'entry')

        logger.info(f"Searching jobs for: {keywords} in {location}")

        # Mock API calls for development (replace with real APIs)
        job_listings = _mock_job_search(keywords, location, experience)

        return {
            'jobs': job_listings,
            'total_found': len(job_listings),
            'search_parameters': {
                'keywords': keywords,
                'location': location,
                'experience': experience
            },
            'api_success': True
        }

    except Exception as e:
        logger.error(f"Error in fetch_job_listings: {str(e)}")
        return {
            'jobs': [],
            'total_found': 0,
            'api_success': False,
            'error': str(e)
        }

def _mock_job_search(keywords: List[str], location: str, experience: str) -> List[Dict]:
    """Mock job search results for development"""
    mock_jobs = [
        {
            'title': 'Python Developer',
            'company': 'Tech Corp',
            'location': location,
            'description': 'Looking for a Python developer with experience in web development.',
            'requirements': ['Python', 'Django', 'PostgreSQL'],
            'experience_level': experience,
            'match_score': 0.92,
            'url': 'https://example.com/job1'
        },
        {
            'title': 'Software Engineer',
            'company': 'StartupXYZ',
            'location': location,
            'description': 'Full-stack engineer role with modern tech stack.',
            'requirements': ['JavaScript', 'React', 'Node.js'],
            'experience_level': experience,
            'match_score': 0.87,
            'url': 'https://example.com/job2'
        }
    ]

    # Filter jobs based on keywords
    if keywords:
        filtered_jobs = []
        for job in mock_jobs:
            job_keywords = job['requirements'] + [job['title'].lower()]
            if any(keyword.lower() in ' '.join(job_keywords).lower() for keyword in keywords):
                filtered_jobs.append(job)
        return filtered_jobs

    return mock_jobs
