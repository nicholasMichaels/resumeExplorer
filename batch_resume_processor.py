"""
Batch Resume Processor
Analyzes all PDF resumes in a folder using the existing pipeline
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import logging
import json
import time
from datetime import datetime
import csv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('batch_processing.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Import the main analyzer
try:
    from main import EnhancedResumeAnalyzer
    print("Successfully imported EnhancedResumeAnalyzer")
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all pipeline files are in the same directory")
    sys.exit(1)

class BatchResumeProcessor:
    """Process multiple resume PDFs in batch"""

    def __init__(self, folder_path: str, output_folder: str = "batch_results"):
        self.folder_path = Path(folder_path)
        self.output_folder = Path(output_folder)
        self.analyzer = EnhancedResumeAnalyzer()
        self.results = []

        # Create output directory
        self.output_folder.mkdir(exist_ok=True)

        # Setup results tracking
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def find_pdf_files(self):
        """Find all PDF files in the folder"""
        pdf_files = list(self.folder_path.glob('**/*.pdf'))
        pdf_files.extend(list(self.folder_path.glob("**/*.PDF")))  # Handle uppercase

        print(f"Found {len(pdf_files)} PDF files in {self.folder_path}")
        return pdf_files

    def get_default_user_profile(self):
        """Get default user profile for batch processing"""
        return {
            'location': 'Remote',
            'experience_level': 'mid',
            'job_preferences': ['software development', 'general'],
            'salary_range': '$60,000-$100,000',
            'job_type': 'full-time'
        }

    def process_single_pdf(self, pdf_path: Path, user_profile: dict = None):
        """Process a single PDF file"""
        print(f"\nProcessing: {pdf_path.name}")
        start_time = time.time()

        if user_profile is None:
            user_profile = self.get_default_user_profile()

        try:
            # Run analysis
            result = self.analyzer.analyze_resume_from_pdf(
                pdf_path=str(pdf_path),
                user_profile=user_profile
            )

            processing_time = time.time() - start_time

            # Create summary
            summary = {
                'filename': pdf_path.name,
                'filepath': str(pdf_path),
                'success': result.get('success', False),
                'processing_time': round(processing_time, 2),
                'timestamp': datetime.now().isoformat()
            }

            if result.get('success'):
                # Extract key metrics
                readability = result.get('readability_analysis', {})
                pdf_info = result.get('pdf_processing', {})

                summary.update({
                    'readability_level': readability.get('readability_level', 'Unknown'),
                    'word_count': readability.get('metrics', {}).get('word_count', 0),
                    'text_length': readability.get('text_length', 0),
                    'key_phrases': readability.get('key_phrases', [])[:5],
                    'pdf_extraction_success': pdf_info.get('success', False),
                    'crew_analysis_available': bool(result.get('crew_analysis'))
                })

                print(f"  SUCCESS - Level: {summary['readability_level']}, Words: {summary['word_count']}")

                # Save detailed results
                self.save_detailed_result(pdf_path.name, result)

            else:
                error_msg = result.get('error', 'Unknown error')
                summary['error'] = error_msg
                print(f"  FAILED - {error_msg}")

            self.results.append(summary)
            return summary

        except Exception as e:
            processing_time = time.time() - start_time
            error_summary = {
                'filename': pdf_path.name,
                'filepath': str(pdf_path),
                'success': False,
                'error': str(e),
                'processing_time': round(processing_time, 2),
                'timestamp': datetime.now().isoformat()
            }

            print(f"  EXCEPTION - {str(e)}")
            self.results.append(error_summary)
            return error_summary

    def save_detailed_result(self, filename: str, result: dict):
        """Save detailed analysis result to JSON file"""
        safe_filename = filename.replace('.pdf', '').replace(' ', '_')
        output_file = self.output_folder / f"{safe_filename}_analysis.json"

        try:
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save detailed result for {filename}: {e}")

    def process_all_pdfs(self, user_profile: dict = None):
        """Process all PDFs in the folder"""
        pdf_files = self.find_pdf_files()

        if not pdf_files:
            print("No PDF files found to process")
            return

        print(f"\nStarting batch processing of {len(pdf_files)} files...")
        print(f"Results will be saved to: {self.output_folder}")
        print("-" * 60)

        total_start_time = time.time()

        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"\n[{i}/{len(pdf_files)}] Processing: {pdf_file.name}")
            self.process_single_pdf(pdf_file, user_profile)

        total_time = time.time() - total_start_time

        print(f"\n{'='*60}")
        print(f"BATCH PROCESSING COMPLETE")
        print(f"{'='*60}")
        print(f"Total files processed: {len(pdf_files)}")
        print(f"Total time: {total_time:.2f} seconds")
        print(f"Average time per file: {total_time/len(pdf_files):.2f} seconds")

        # Generate summary report
        self.generate_summary_report()

    def generate_summary_report(self):
        """Generate summary report of batch processing"""
        successful = [r for r in self.results if r['success']]
        failed = [r for r in self.results if not r['success']]

        print(f"\nSUMMARY:")
        print(f"  Successful: {len(successful)}")
        print(f"  Failed: {len(failed)}")
        print(f"  Success rate: {len(successful)/len(self.results)*100:.1f}%")

        if successful:
            avg_words = sum(r.get('word_count', 0) for r in successful) / len(successful)
            print(f"  Average word count: {avg_words:.0f}")

            # Readability distribution
            readability_levels = {}
            for r in successful:
                level = r.get('readability_level', 'Unknown')
                readability_levels[level] = readability_levels.get(level, 0) + 1

            print(f"  Readability distribution:")
            for level, count in readability_levels.items():
                print(f"    {level}: {count}")

        # Save CSV summary
        self.save_csv_summary()

        # Save detailed JSON summary
        self.save_json_summary()

    def save_csv_summary(self):
        """Save summary as CSV file"""
        csv_file = self.output_folder / f"batch_summary_{self.timestamp}.csv"

        try:
            with open(csv_file, 'w', newline='') as f:
                if self.results:
                    writer = csv.DictWriter(f, fieldnames=self.results[0].keys())
                    writer.writeheader()
                    writer.writerows(self.results)

            print(f"CSV summary saved: {csv_file}")
        except Exception as e:
            logger.error(f"Failed to save CSV summary: {e}")

    def save_json_summary(self):
        """Save detailed summary as JSON file"""
        json_file = self.output_folder / f"batch_summary_{self.timestamp}.json"

        summary_data = {
            'processing_timestamp': self.timestamp,
            'folder_processed': str(self.folder_path),
            'total_files': len(self.results),
            'successful_files': len([r for r in self.results if r['success']]),
            'failed_files': len([r for r in self.results if not r['success']]),
            'results': self.results
        }

        try:
            with open(json_file, 'w') as f:
                json.dump(summary_data, f, indent=2, default=str)

            print(f"JSON summary saved: {json_file}")
        except Exception as e:
            logger.error(f"Failed to save JSON summary: {e}")

def main():
    """Main function"""
    print("BATCH RESUME PROCESSOR")
    print("Process all PDF resumes in a folder")
    print("="*50)

    # Check environment setup
    if not os.getenv('GROQ_API_KEY'):
        print("WARNING: GROQ_API_KEY not found in environment")
        print("Create a .env file with: GROQ_API_KEY=your_key_here")

        proceed = input("\nContinue anyway? (y/n): ").strip().lower()
        if proceed != 'y':
            return

    # Get folder path
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
    else:
        folder_path = input("Enter path to folder containing PDF resumes: ").strip()

    if not folder_path or not Path(folder_path).exists():
        print(f"Folder not found: {folder_path}")
        return

    # Optional: Get output folder
    output_folder = "batch_results"
    if len(sys.argv) > 2:
        output_folder = sys.argv[2]
    else:
        custom_output = input(f"Output folder (press Enter for '{output_folder}'): ").strip()
        if custom_output:
            output_folder = custom_output

    # Optional: Customize user profile for all resumes
    print("\nUser profile settings (used for all resumes):")
    location = input("Location (or Enter for 'Remote'): ").strip() or 'Remote'
    exp_level = input("Experience level (entry/mid/senior, or Enter for 'mid'): ").strip() or 'mid'

    user_profile = {
        'location': location,
        'experience_level': exp_level,
        'job_preferences': ['software development', 'general'],
        'salary_range': '$60,000-$100,000',
        'job_type': 'full-time'
    }

    print(f"\nUsing profile: {user_profile}")

    # Create processor and run
    processor = BatchResumeProcessor(folder_path, output_folder)
    processor.process_all_pdfs(user_profile)

    print(f"\nResults saved in: {output_folder}")
    print("Files created:")
    print("  - Individual analysis JSON files")
    print("  - batch_summary_YYYYMMDD_HHMMSS.csv")
    print("  - batch_summary_YYYYMMDD_HHMMSS.json")

if __name__ == "__main__":
    main()
