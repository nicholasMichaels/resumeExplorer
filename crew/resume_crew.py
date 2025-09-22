from crewai import Crew, Task
from agents.resume_extractor import ResumeExtractor
from agents.resume_evaluator import ResumeEvaluator
from agents.feedback_generator import FeedbackGenerator
from agents.job_search import JobSearchAgent
from utils.debugging import debug_crew_execution
import logging

logger = logging.getLogger(__name__)

# Enhanced task descriptions for Groq integration
extract_task = Task(
    description="""Extract comprehensive structured information from the provided resume text using advanced AI.
    Parse the resume into organized sections including personal information, education, work experience,
    skills, certifications, and languages. Validate extracted data for completeness and accuracy.
    Pay special attention to technical skills and quantified achievements.""",
    agent=ResumeExtractor,
    expected_output="Comprehensive structured resume data with personal info, education, experience, skills, certifications, and metadata in JSON format with confidence scores"
)

evaluate_task = Task(
    description="""Conduct thorough resume evaluation using AI-enhanced analysis and job market benchmarks.
    Score the resume across multiple dimensions including content quality, skills alignment, experience relevance,
    and market competitiveness. Provide detailed scoring breakdown with specific improvement areas.
    Use RAG system for current market insights and industry standards.""",
    agent=ResumeEvaluator,
    expected_output="Detailed resume evaluation with dimensional scores, AI analysis, market competitiveness assessment, and specific improvement recommendations",
    context=[extract_task]
)

feedback_task = Task(
    description="""Generate comprehensive, actionable feedback using AI-powered multi-perspective analysis.
    Simulate detailed viewpoints from CEO (strategic fit), CTO (technical competency), and HR (process readiness).
    Create personalized improvement suggestions based on evaluation results and market analysis.
    Focus on specific, actionable next steps with prioritized recommendations.""",
    agent=FeedbackGenerator,
    expected_output="Multi-perspective feedback with specific improvement suggestions, priority rankings, and detailed next steps from executive viewpoints",
    context=[extract_task, evaluate_task]
)

job_search_task = Task(
    description="""Find and rank relevant job opportunities using AI-enhanced matching algorithms.
    Use job search APIs combined with resume analysis to identify optimal positions.
    Calculate match scores based on skills alignment, experience level, and location preferences.
    Provide strategic application recommendations with success probability analysis.""",
    agent=JobSearchAgent,
    expected_output="Ranked list of matched job opportunities with detailed match analysis, success probability scores, and strategic application recommendations",
    context=[extract_task, evaluate_task]
)

class DebuggedResumeCrew:
    def __init__(self):
        self.crew = Crew(
            agents=[
                ResumeExtractor,
                ResumeEvaluator,
                FeedbackGenerator,
                JobSearchAgent
            ],
            tasks=[
                extract_task,
                evaluate_task,
                feedback_task,
                job_search_task
            ],
            verbose=True,
            memory=True
        )

    def kickoff(self, inputs: dict):
        """Execute crew with debugging"""
        logger.info("🚀 Starting ResumeCrew execution")

        # Debug crew inputs
        debug_crew_execution("ResumeCrew", inputs, "Starting execution...")

        try:
            result = self.crew.kickoff(inputs=inputs)

            # Debug crew completion
            debug_crew_execution("ResumeCrew", inputs, result)

            logger.info("✅ ResumeCrew execution completed successfully")
            return result

        except Exception as e:
            logger.error(f"❌ ResumeCrew execution failed: {str(e)}")
            debug_crew_execution("ResumeCrew", inputs, f"ERROR: {str(e)}")
            raise

# Create the crew instance
ResumeCrew = DebuggedResumeCrew()
