import os
import json
import time
import argparse
import concurrent.futures
from modules.idea_generator import IdeaGenerator
from modules.voice_generator import VoiceGenerator
from modules.video_selector import VideoSelector
from modules.video_editor import VideoEditor
from utils.logger import setup_logger

# Set up logger
logger = setup_logger('batch_processor')

class BatchProcessor:
    def __init__(self, max_workers=4):
        self.max_workers = max_workers
        self.idea_gen = IdeaGenerator()
        self.voice_gen = VoiceGenerator()
        self.video_sel = VideoSelector()
        self.video_ed = VideoEditor()
        logger.info(f"BatchProcessor initialized with {max_workers} workers")
    
    def generate_ideas(self, count, output_file=None):
        """Generate multiple video ideas"""
        logger.info(f"Generating {count} video ideas")
        ideas = self.idea_gen.generate_multiple_ideas(count=count, output_file=output_file)
        return ideas
    
    def process_idea(self, idea):
        """Process a single idea into a video"""
        try:
            idea_id = idea.get('id', 'unknown')
            logger.info(f"Processing idea {idea_id}: {idea['title']}")
            
            # Generate voiceover
            audio_file = self.voice_gen.generate_from_script(idea['script'])
            if not audio_file:
                logger.error(f"Failed to generate voiceover for idea {idea_id}")
                return None
            
            # Select video clips
            video_files = self.video_sel.select_videos_for_script(idea['script'])
            if not video_files:
                logger.error(f"Failed to select video clips for idea {idea_id}")
                return None
            
            # Create final video
            output_name = f"tiktok_{idea_id}_{int(time.time())}.mp4"
            output_video = self.video_ed.create_video(
                idea['script'],
                video_files,
                audio_file,
                output_name=output_name
            )
            
            if output_video:
                logger.info(f"Video for idea {idea_id} created: {output_video}")
                return output_video
            else:
                logger.error(f"Failed to create video for idea {idea_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error processing idea: {e}")
            return None
    
    def process_batch(self, ideas):
        """Process a batch of ideas in parallel"""
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_idea = {executor.submit(self.process_idea, idea): idea for idea in ideas}
            
            for future in concurrent.futures.as_completed(future_to_idea):
                idea = future_to_idea[future]
                try:
                    result = future.result()
                    if result:
                        results.append({
                            'idea_id': idea.get('id', 'unknown'),
                            'title': idea['title'],
                            'video_path': result
                        })
                except Exception as e:
                    logger.error(f"Error processing idea {idea.get('id', 'unknown')}: {e}")
        
        return results
    
    def run(self, count=10, ideas_file=None):
        """Run the batch processor"""
        start_time = time.time()
        logger.info(f"Starting batch processing of {count} videos")
        
        # Generate or load ideas
        if ideas_file and os.path.exists(ideas_file):
            logger.info(f"Loading ideas from {ideas_file}")
            with open(ideas_file, 'r') as f:
                ideas = json.load(f)
        else:
            ideas_file = f"video_ideas_{int(time.time())}.json"
            ideas = self.generate_ideas(count, output_file=ideas_file)
        
        # Process ideas
        results = self.process_batch(ideas[:count])
        
        # Save results
        results_file = f"batch_results_{int(time.time())}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        elapsed_time = time.time() - start_time
        logger.info(f"Batch processing completed in {elapsed_time:.2f} seconds")
        logger.info(f"Successfully created {len(results)} videos out of {count} ideas")
        logger.info(f"Results saved to {results_file}")
        
        return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='TikTok Video Batch Processor')
    parser.add_argument('--count', type=int, default=10, help='Number of videos to generate')
    parser.add_argument('--workers', type=int, default=4, help='Number of worker threads')
    parser.add_argument('--ideas', help='Path to existing ideas JSON file')
    
    args = parser.parse_args()
    
    processor = BatchProcessor(max_workers=args.workers)
    processor.run(count=args.count, ideas_file=args.ideas)