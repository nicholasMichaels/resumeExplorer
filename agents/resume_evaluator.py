from crewai import Agent
from agents.groq_llm import GroqLLM  # NEW IMPORT
from utils.rag_utils import retrieve_job_benchmarks
from utils.debugging import debug_agent_state, debug_rag_retrieval
import logging
import time
import json
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

def evaluate_resume_quality(resume_data: Dict[str, Any]) -> Dict[str, Any]:
    """Score resume across multiple dimensions with Groq-enhanced evaluation"""
    start_time = time.time()

    try:
        if not resume_data or 'error' in resume_data:
            raise ValueError("Invalid resume data provided")

        logger.info("Starting Groq-enhanced resume quality evaluation")

        # Get job benchmarks
        resume_text = json.dumps(resume_data)
        benchmarks = retrieve_job_benchmarks(resume_text)

        debug_rag_retrieval(resume_text[:100], benchmarks.get('benchmarks', []), similarity_threshold=0.6)

        # Initialize Groq for advanced scoring
        groq_llm = GroqLLM()

        # Enhanced scoring with Groq
        detailed_analysis = _groq_enhanced_evaluation(groq_llm, resume_data, benchmarks)

        # Traditional scoring
        traditional_scores = {
            'self_evaluation': _score_self_evaluation(resume_data),
            'skills': _score_skills(resume_data, benchmarks),
            'experience': _score_experience(resume_data, benchmarks),
            'basic_info': _score_basic_info(resume_data),
            'education': _score_education(resume_data, benchmarks)
        }

        # Combine traditional and Groq analysis
        overall_score = sum(traditional_scores.values()) / len(traditional_scores)

        result = {
            'overall_score': overall_score,
            'dimension_scores': traditional_scores,
            'groq_analysis': detailed_analysis,
            'benchmarks_used': len(benchmarks.get('benchmarks', [])),
            'evaluation_successful': True,
            'recommendations': _generate_recommendations(traditional_scores),
            'evaluation_timestamp': time.time(),
            'rag_success': benchmarks.get('search_successful', False)
        }

        execution_time = time.time() - start_time
        debug_agent_state("ResumeEvaluator", str(resume_data)[:200], result, execution_time)

        logger.info(f"Enhanced resume evaluation completed. Overall score: {overall_score:.2f}")
        return result

    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Error in evaluate_resume_quality: {str(e)}")
        # Return fallback evaluation
        return _fallback_evaluation(resume_data, execution_time)

def _groq_enhanced_evaluation(groq_llm: GroqLLM, resume_data: Dict[str, Any], benchmarks: Dict[str, Any]) -> Dict[str, Any]:
    """Use Groq for enhanced resume evaluation"""
    try:
        evaluation_prompt = f"""
Analyze this resume data and provide detailed evaluation:

Resume Data: {json.dumps(resume_data, indent=2)}

Benchmarks: {json.dumps(benchmarks.get('benchmarks', []), indent=2)}

Provide analysis in this JSON format:
{{
    "strengths": ["strength1", "strength2", "strength3"],
    "weaknesses": ["weakness1", "weakness2"],
    "improvement_suggestions": ["suggestion1", "suggestion2"],
    "market_competitiveness": "high/medium/low",
    "recommended_roles": ["role1", "role2"],
    "confidence_score": 0.85
}}

Focus on actionable insights and specific recommendations.
"""

        response = groq_llm(evaluation_prompt)
        return json.loads(response)

    except Exception as e:
        logger.warning(f"Groq evaluation failed: {e}")
        return {
            "strengths": ["Basic information present"],
            "weaknesses": ["Analysis incomplete"],
            "improvement_suggestions": ["Consider professional review"],
            "market_competitiveness": "medium",
            "recommended_roles": ["Various"],
            "confidence_score": 0.5
        }

# Keep existing scoring functions but update agent
ResumeEvaluator = Agent(
    name="Resume Evaluator",
    role="Score resumes across key dimensions using industry benchmarks and AI analysis",
    goal="Provide accurate, data-driven resume evaluation with actionable insights using Groq",
    backstory="""You are an expert resume evaluator enhanced with advanced AI capabilities.
    You use both traditional scoring methods and modern language models to provide comprehensive analysis.""",
    tools=[evaluate_resume_quality, retrieve_job_benchmarks],
    llm=GroqLLM(),  # USE GROQ LLM
    verbose=True,
    allow_delegation=False
)
