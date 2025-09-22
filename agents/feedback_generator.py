from crewai import Agent
import logging
import time
from typing import Dict, Any, List
from utils.debugging import debug_agent_state
from agents.groq_llm import GroqLLM  # ADD THIS IMPORT

logger = logging.getLogger(__name__)

def generate_personalized_feedback(resume_data: Dict[str, Any], evaluation_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate actionable feedback from multiple perspectives with debugging
    """
    start_time = time.time()

    try:
        if not resume_data or not evaluation_data:
            raise ValueError("Resume data and evaluation data are required")

        logger.info("Starting feedback generation")

        overall_score = evaluation_data.get('overall_score', 0)
        dimension_scores = evaluation_data.get('dimension_scores', {})
        recommendations = evaluation_data.get('recommendations', [])

        # Generate feedback from different perspectives
        ceo_feedback = _generate_ceo_feedback(overall_score, dimension_scores)
        cto_feedback = _generate_cto_feedback(resume_data, dimension_scores)
        hr_feedback = _generate_hr_feedback(resume_data, recommendations)

        feedback_result = {
            'overall_assessment': _get_overall_assessment(overall_score),
            'perspectives': {
                'ceo': ceo_feedback,
                'cto': cto_feedback,
                'hr': hr_feedback
            },
            'priority_improvements': _get_priority_improvements(dimension_scores),
            'next_steps': _get_next_steps(recommendations),
            'feedback_timestamp': time.time(),
            'based_on_score': overall_score
        }

        # Debug feedback generation
        execution_time = time.time() - start_time
        debug_agent_state("FeedbackGenerator",
                         f"Score: {overall_score}, Dimensions: {list(dimension_scores.keys())}",
                         feedback_result, execution_time)

        logger.info(f"Feedback generation completed. Overall assessment: {feedback_result['overall_assessment']}")

        return feedback_result

    except Exception as e:
        execution_time = time.time() - start_time
        error_result = {
            'error': str(e),
            'feedback_timestamp': time.time(),
            'execution_time': execution_time
        }

        debug_agent_state("FeedbackGenerator", "Error in feedback generation", error_result, execution_time)
        logger.error(f"Error in generate_personalized_feedback: {str(e)}")

        return error_result

def _generate_ceo_feedback(overall_score: float, dimension_scores: Dict[str, float]) -> Dict[str, Any]:
    """Generate CEO perspective feedback"""
    logger.debug("Generating CEO feedback")

    if overall_score >= 0.8:
        tone = "impressed"
        message = "This candidate shows strong potential and would likely fit well in our organization."
    elif overall_score >= 0.6:
        tone = "optimistic"
        message = "This candidate has good foundations but needs some development in key areas."
    else:
        tone = "cautious"
        message = "This candidate would need significant improvement before being considered for most roles."

    return {
        'tone': tone,
        'message': message,
        'key_concern': _get_lowest_scoring_dimension(dimension_scores),
        'recommendation': 'proceed' if overall_score >= 0.7 else 'improve_first'
    }

def _generate_cto_feedback(resume_data: Dict[str, Any], dimension_scores: Dict[str, float]) -> Dict[str, Any]:
    """Generate CTO perspective feedback"""
    logger.debug("Generating CTO feedback")

    skills = resume_data.get('skills', [])
    experience = resume_data.get('experience', [])

    technical_strength = dimension_scores.get('skills', 0) + dimension_scores.get('experience', 0)

    if technical_strength >= 1.4:
        assessment = "Strong technical profile"
        focus = "Consider for technical interviews"
    elif technical_strength >= 1.0:
        assessment = "Adequate technical background"
        focus = "May need technical skill development"
    else:
        assessment = "Limited technical experience"
        focus = "Requires significant technical training"

    return {
        'assessment': assessment,
        'focus_area': focus,
        'technical_skills_count': len(skills),
        'experience_relevance': 'high' if dimension_scores.get('experience', 0) > 0.7 else 'moderate'
    }

def _generate_hr_feedback(resume_data: Dict[str, Any], recommendations: List[str]) -> Dict[str, Any]:
    """Generate HR perspective feedback"""
    logger.debug("Generating HR feedback")

    personal_info = resume_data.get('personal_info', {})
    education = resume_data.get('education', [])

    completeness_issues = []
    if not personal_info.get('phone'):
        completeness_issues.append('phone number')
    if not personal_info.get('email'):
        completeness_issues.append('email address')
    if not education:
        completeness_issues.append('education details')

    return {
        'application_readiness': 'ready' if len(completeness_issues) == 0 else 'needs_improvement',
        'missing_elements': completeness_issues,
        'formatting_notes': 'Standard format detected' if personal_info else 'Format needs improvement',
        'recommendations_count': len(recommendations),
        'next_action': 'Schedule interview' if len(completeness_issues) == 0 else 'Request updated resume'
    }

def _get_overall_assessment(score: float) -> str:
    """Get overall assessment based on score"""
    if score >= 0.85:
        return "Excellent"
    elif score >= 0.75:
        return "Good"
    elif score >= 0.65:
        return "Fair"
    elif score >= 0.5:
        return "Needs Improvement"
    else:
        return "Poor"

def _get_lowest_scoring_dimension(dimension_scores: Dict[str, float]) -> str:
    """Find the dimension with the lowest score"""
    if not dimension_scores:
        return "Unknown"

    lowest_dim = min(dimension_scores.items(), key=lambda x: x[1])
    return lowest_dim[0].replace('_', ' ').title()

def _get_priority_improvements(dimension_scores: Dict[str, float]) -> List[str]:
    """Get priority improvements based on lowest scores"""
    if not dimension_scores:
        return []

    # Sort dimensions by score (ascending)
    sorted_dims = sorted(dimension_scores.items(), key=lambda x: x[1])

    # Return bottom 3 or those below 0.6
    priority = []
    for dim, score in sorted_dims:
        if score < 0.6 and len(priority) < 3:
            priority.append(dim.replace('_', ' ').title())

    return priority

def _get_next_steps(recommendations: List[str]) -> List[str]:
    """Convert recommendations to actionable next steps"""
    if not recommendations:
        return ["Your resume looks good! Consider minor formatting improvements."]

    return [f"Action: {rec}" for rec in recommendations[:5]]  # Limit to top 5

FeedbackGenerator = Agent(
    name="Feedback Generator",
    role="Generate actionable resume feedback from multiple perspectives",
    goal="Simulate CEO, CTO, and HR perspectives using advanced AI analysis",
    backstory="""You are a seasoned hiring consultant enhanced with AI capabilities.
    You provide multi-perspective feedback using advanced language models.""",
    tools=[generate_personalized_feedback],
    llm=GroqLLM(),  # ADD THIS LINE
    verbose=True,
    allow_delegation=False
)
