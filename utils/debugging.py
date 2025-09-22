# utils/debugging.py
import logging
import time
import json
import functools
from typing import Any, List, Dict, Callable
from datetime import datetime

logger = logging.getLogger(__name__)

def debug_agent_state(agent_name: str, input_data: Any, output_data: Any, execution_time: float = None):
    """Log agent input/output for debugging"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    logger.info(f"[{timestamp}] [{agent_name}] === AGENT EXECUTION ===")
    logger.info(f"[{agent_name}] Input: {str(input_data)[:200]}...")
    logger.info(f"[{agent_name}] Output: {str(output_data)[:200]}...")

    if execution_time:
        logger.info(f"[{agent_name}] Execution time: {execution_time:.2f}s")

    logger.info(f"[{agent_name}] === END EXECUTION ===\n")

def validate_llm_output(output: str, expected_fields: List[str]) -> Dict[str, Any]:
    """Validate that LLM output contains required fields"""
    validation_result = {
        'is_valid': False,
        'missing_fields': [],
        'parsed_data': None,
        'error': None
    }

    try:
        # Try to parse JSON
        parsed = json.loads(output) if isinstance(output, str) else output
        validation_result['parsed_data'] = parsed

        # Check for required fields
        if isinstance(parsed, dict):
            missing = [field for field in expected_fields if field not in parsed]
            validation_result['missing_fields'] = missing
            validation_result['is_valid'] = len(missing) == 0
        else:
            validation_result['error'] = "Output is not a dictionary"

    except json.JSONDecodeError as e:
        validation_result['error'] = f"JSON decode error: {str(e)}"
    except Exception as e:
        validation_result['error'] = f"Validation error: {str(e)}"

    return validation_result

def debug_task_flow(task_name: str):
    """Decorator to debug task execution flow"""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            logger.info(f"🚀 Starting task: {task_name}")
            logger.info(f"📥 Task input args: {len(args)} args, {len(kwargs)} kwargs")

            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time

                logger.info(f"✅ Task completed: {task_name}")
                logger.info(f"⏱️  Execution time: {execution_time:.2f}s")
                logger.info(f"📤 Task output type: {type(result)}")

                return result

            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"❌ Task failed: {task_name}")
                logger.error(f"⏱️  Failed after: {execution_time:.2f}s")
                logger.error(f"🐛 Error: {str(e)}")
                raise

        return wrapper
    return decorator

def debug_rag_retrieval(query: str, results: List[Dict], similarity_threshold: float = 0.5):
    """Debug RAG retrieval quality"""
    logger.info(f"🔍 RAG Query: {query[:100]}...")
    logger.info(f"📊 Retrieved {len(results)} results")

    if not results:
        logger.warning("⚠️  No results retrieved!")
        return

    # Analyze similarity scores
    scores = [r.get('similarity_score', 0) for r in results]
    avg_score = sum(scores) / len(scores) if scores else 0

    logger.info(f"📈 Average similarity: {avg_score:.3f}")
    logger.info(f"📈 Score range: {min(scores):.3f} - {max(scores):.3f}")

    # Check quality
    high_quality = [r for r in results if r.get('similarity_score', 0) > similarity_threshold]
    logger.info(f"✨ High quality results: {len(high_quality)}/{len(results)}")

    if len(high_quality) < len(results) * 0.5:
        logger.warning("⚠️  Low retrieval quality detected!")

def debug_crew_execution(crew_name: str, inputs: Dict[str, Any], outputs: Any):
    """Debug entire crew execution"""
    logger.info(f"🎬 === CREW EXECUTION START: {crew_name} ===")
    logger.info(f"📥 Crew inputs: {list(inputs.keys()) if isinstance(inputs, dict) else type(inputs)}")

    # Log input details
    for key, value in (inputs.items() if isinstance(inputs, dict) else []):
        logger.info(f"   {key}: {str(value)[:100]}...")

    logger.info(f"📤 Crew output type: {type(outputs)}")
    logger.info(f"🎬 === CREW EXECUTION END: {crew_name} ===\n")

def debug_groq_call(prompt: str, response: str, execution_time: float = None):
    """Debug Groq API calls"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    logger.info(f"[{timestamp}] [GROQ] === API CALL ===")
    logger.info(f"[GROQ] Prompt length: {len(prompt)} chars")
    logger.info(f"[GROQ] Prompt preview: {prompt[:150]}...")
    logger.info(f"[GROQ] Response length: {len(response)} chars")
    logger.info(f"[GROQ] Response preview: {response[:150]}...")

    if execution_time:
        logger.info(f"[GROQ] API response time: {execution_time:.2f}s")

    logger.info(f"[GROQ] === END API CALL ===\n")
