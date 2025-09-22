from crewai import Agent
from utils.api_clients import fetch_job_listings
from utils.debugging import debug_agent_state
import logging
import time
from typing import Dict, Any, List
from agents.groq_llm import GroqLLM  # ADD THIS IMPORT

logger = logging.getLogger(__name__)

def search_relevant_jobs(resume_data: Dict[str, Any], user_profile: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Find relevant jobs based on resume and user profile with debugging
    """
    start_time = time.time()

    try:
        if not resume_data or 'error' in resume_data:
            raise ValueError("Valid resume data is required for job search")

        logger.info("Starting job search process")

        # Extract profile information
        profile_data = _build_search_profile(resume_data, user_profile or {})

        logger.info(f"Built search profile: {profile_data}")

        # Fetch job listings
        job_results = fetch_job_listings(profile_data)

        # Process and rank results
        processed_jobs = _process_job_results(job_results, resume_data)

        # Create final result
        search_result = {
            'jobs': processed_jobs.get('jobs', []),
            'total_found': processed_jobs.get('total_found', 0),
            'search_profile': profile_data,
            'api_success': job_results.get('api_success', False),
            'search_timestamp': time.time(),
            'recommendations': _generate_job_recommendations(processed_jobs.get('jobs', []))
        }

        # Debug job search
        execution_time = time.time() - start_time
        debug_agent_state("JobSearchAgent",
                         f"Profile: {profile_data}",
                         f"Found {search_result['total_found']} jobs",
                         execution_time)

        logger.info(f"Job search completed. Found {search_result['total_found']} relevant positions")

        return search_result

    except Exception as e:
        execution_time = time.time() - start_time
        error_result = {
            'jobs': [],
            'total_found': 0,
            'api_success': False,
            'error': str(e),
            'search_timestamp': time.time(),
            'execution_time': execution_time
        }

        debug_agent_state("JobSearchAgent", "Job search error", error_result, execution_time)
        logger.error(f"Error in search_relevant_jobs: {str(e)}")

        return error_result

def _build_search_profile(resume_data: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Build search profile from resume and user input"""
    logger.debug("Building search profile")

    # Extract from resume
    skills = resume_data.get('skills', [])
    personal_info = resume_data.get('personal_info', {})
    experience = resume_data.get('experience', [])

    # Determine experience level
    exp_level = 'entry'
    if len(experience) >= 3:
        exp_level = 'senior'
    elif len(experience) >= 1:
        exp_level = 'mid'

    # Build profile
    profile = {
        'skills': skills,
        'location': user_profile.get('location') or personal_info.get('location', 'Remote'),
        'experience_level': user_profile.get('experience_level', exp_level),
        'job_preferences': user_profile.get('job_preferences', _infer_job_preferences(skills)),
        'salary_range': user_profile.get('salary_range'),
        'job_type': user_profile.get('job_type', 'full-time')
    }

    logger.debug(f"Built profile: skills={len(skills)}, location={profile['location']}, level={profile['experience_level']}")

    return profile

def _infer_job_preferences(skills: List[str]) -> List[str]:
    """Infer job preferences from skills"""
    preferences = []

    # Programming skills
    prog_skills = ['python', 'javascript', 'java', 'react', 'node.js', 'django']
    if any(skill.lower() in prog_skills for skill in skills):
        preferences.append('software development')

    # Data skills
    data_skills = ['sql', 'pandas', 'numpy', 'tableau', 'excel']
    if any(skill.lower() in data_skills for skill in skills):
        preferences.append('data analysis')

    # Default
    if not preferences:
        preferences = ['general']

    return preferences

def _process_job_results(job_results: Dict[str, Any], resume_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process and enhance job results"""
    logger.debug("Processing job results")

    if not job_results.get('api_success', False):
        logger.warning("Job API call was not successful")
        return {
            'jobs': [],
            'total_found': 0,
            'processing_successful': False
        }

    jobs = job_results.get('jobs', [])
    resume_skills = [skill.lower() for skill in resume_data.get('skills', [])]

    # Enhance jobs with match scores
    enhanced_jobs = []
    for job in jobs:
        job_copy = job.copy()

        # Calculate skill match
        job_requirements = [req.lower() for req in job.get('requirements', [])]
        skill_overlap = len(set(resume_skills) & set(job_requirements))
        total_requirements = len(job_requirements)

        if total_requirements > 0:
            match_score = skill_overlap / total_requirements
        else:
            match_score = job.get('match_score', 0.5)  # Use existing or default

        job_copy['calculated_match_score'] = match_score
        job_copy['matching_skills'] = list(set(resume_skills) & set(job_requirements))

        enhanced_jobs.append(job_copy)

    # Sort by match score
    enhanced_jobs.sort(key=lambda x: x.get('calculated_match_score', 0), reverse=True)

    logger.debug(f"Enhanced {len(enhanced_jobs)} job listings with match scores")

    return {
        'jobs': enhanced_jobs,
        'total_found': len(enhanced_jobs),
        'processing_successful': True
    }

def _generate_job_recommendations(jobs: List[Dict[str, Any]]) -> List[str]:
    """Generate job application recommendations"""
    recommendations = []

    if not jobs:
        recommendations.append("No matching jobs found. Consider broadening your search criteria.")
        return recommendations

    high_match_jobs = [job for job in jobs if job.get('calculated_match_score', 0) > 0.7]
    medium_match_jobs = [job for job in jobs if 0.4 <= job.get('calculated_match_score', 0) <= 0.7]

    if high_match_jobs:
        recommendations.append(f"Apply immediately to {len(high_match_jobs)} high-match positions")

    if medium_match_jobs:
        recommendations.append(f"Consider applying to {len(medium_match_jobs)} positions after skill development")

    if len(jobs) > 5:
        recommendations.append("Focus on the top 5 matches to maximize success rate")

    return recommendations

JobSearchAgent = Agent(
    name="Job Search Agent",
    role="Find relevant jobs using AI-enhanced matching",
    goal="Use APIs and AI analysis to match candidates with suitable roles",
    backstory="""You are an expert career counselor enhanced with AI capabilities
    for advanced job matching and strategic guidance.""",
    tools=[fetch_job_listings, search_relevant_jobs],
    llm=GroqLLM(),  # ADD THIS LINE
    verbose=True,
    allow_delegation=False
)
