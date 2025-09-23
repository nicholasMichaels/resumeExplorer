import os

# Enhanced LLM Configuration for Groq
LLM_MODEL = "llama-3.1-405b-reasoning"
# Before (secure method)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# After (direct paste)
GROQ_API_KEY = "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"
GROQ_MAX_TOKENS = 4000
GROQ_TEMPERATURE = 0.7

# Keep existing configurations
VECTOR_DB = "faiss"
JOB_APIS = ["Indeed", "LinkedIn"]

# Enhanced Processing Configuration
PDF_PROCESSOR = "enhanced"
READABILITY_THRESHOLD = 0.6
ENABLE_GROQ_ANALYSIS = True
ENABLE_PDF_READABILITY = True  
