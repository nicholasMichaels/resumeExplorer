import logging
import numpy as np
from typing import List, Dict, Any
import faiss
import pickle
from sentence_transformers import SentenceTransformer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGUtils:
    def __init__(self, model_name="all-MiniLM-L6-v2", index_path="data/job_embeddings.faiss"):
        self.model = SentenceTransformer(model_name)
        self.index_path = index_path
        self.index = None
        self.job_data = []
        self._load_index()

    def _load_index(self):
        """Load FAISS index and job data"""
        try:
            self.index = faiss.read_index(self.index_path)
            with open(self.index_path.replace('.faiss', '_data.pkl'), 'rb') as f:
                self.job_data = pickle.load(f)
            logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")
        except FileNotFoundError:
            logger.warning("FAISS index not found. Creating empty index.")
            self._create_empty_index()

    def _create_empty_index(self):
        """Create empty FAISS index for development"""
        dimension = 384  # all-MiniLM-L6-v2 dimension
        self.index = faiss.IndexFlatIP(dimension)
        self.job_data = []

def retrieve_job_benchmarks(resume_text: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Use FAISS to retrieve relevant job criteria and benchmarks
    """
    try:
        rag = RAGUtils()

        if not resume_text.strip():
            raise ValueError("Resume text cannot be empty")

        # Encode resume text
        resume_embedding = rag.model.encode([resume_text])

        # Search similar job requirements
        if rag.index.ntotal == 0:
            logger.warning("No job benchmarks available, returning mock data")
            return _get_mock_benchmarks()

        scores, indices = rag.index.search(resume_embedding, top_k)

        # Retrieve matching job requirements
        benchmarks = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(rag.job_data):
                benchmark = rag.job_data[idx].copy()
                benchmark['similarity_score'] = float(score)
                benchmarks.append(benchmark)

        logger.info(f"Retrieved {len(benchmarks)} job benchmarks")

        return {
            'benchmarks': benchmarks,
            'total_found': len(benchmarks),
            'search_successful': True
        }

    except Exception as e:
        logger.error(f"Error in retrieve_job_benchmarks: {str(e)}")
        return {
            'benchmarks': _get_mock_benchmarks()['benchmarks'],
            'total_found': 0,
            'search_successful': False,
            'error': str(e)
        }

def _get_mock_benchmarks() -> Dict[str, Any]:
    """Return mock benchmarks for development"""
    return {
        'benchmarks': [
            {
                'job_title': 'Software Developer',
                'required_skills': ['Python', 'JavaScript', 'Git'],
                'experience_years': '2-3',
                'education': 'Bachelor\'s in Computer Science',
                'similarity_score': 0.85
            },
            {
                'job_title': 'Data Analyst',
                'required_skills': ['Python', 'SQL', 'Excel'],
                'experience_years': '1-2',
                'education': 'Bachelor\'s in related field',
                'similarity_score': 0.75
            }
        ],
        'total_found': 2,
        'search_successful': True
    }
