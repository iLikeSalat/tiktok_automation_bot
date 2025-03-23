import os
import argparse
import json
import time
from dotenv import load_dotenv
from modules.idea_generator import IdeaGenerator
from modules.voice_generator import VoiceGenerator
from modules.video_selector import VideoSelector
from modules.video_editor import VideoEditor
from utils.logger import setup_logger

# Load environment variables
load_dotenv()

# Set up logger
logger = setup_logger('main')

def generate_single_video(args):
    """Generate a single TikTok video"""
    try:
        logger.info("Starting single video generation process")
        
        # Initialize modules
        idea_gen = IdeaGenerator()
        voice_gen = VoiceGenerator()
        video_sel = VideoSelector()
        video_ed = VideoEditor()
        
        # Generate video idea
        logger.info("Generating video idea")
        video_idea = idea_gen.generate_video_idea(
            category=args.category,
            audience=args.audience,
            trend=args.trend
        )
        
        if not video_idea:
            logger.error("Failed to generate video idea")
            return
        
        # Save idea to file
        with open(f"video_idea_{int(time.time())}.json", 'w') as f:
            json.dump(video_idea, f, indent=2)
        
        # Generate voiceover
        logger.info("Generating voiceover")
        audio_file = voice_gen.generate_from_script(video_idea['script'])
        
        if not audio_file:
            logger.error("Failed to generate voiceover")
            return
        
        # Select video clips
        logger.info("Selecting video clips")
        video_files = video_sel.select_videos_for_script(video_idea['script'])
        
        if not video_files:
            logger.error("Failed to select video clips")
            return
        
        # Create final video
        logger.info("Creating final video")
        output_video = video_ed.create_video(
            video_idea['script'],
            video_files,
            audio_file,
            output_name=args.output
        )
        
        if output_video:
            logger.info(f"Video generation complete: {output_video}")
            print(f"Video successfully generated: {output_video}")
        else:
            logger.error("Failed to create final video")
            
    except Exception as e:
        logger.error(f"Error in generate_single_video: {e}")

def generate_multiple_videos(args):
    """Generate multiple TikTok videos"""
    try:
        logger.info(f"Starting batch generation of {args.count} videos")
        
        # Initialize idea generator
        idea_gen = IdeaGenerator()
        
        # Generate multiple ideas
        ideas_file = f"video_ideas_{int(time.time())}.json"
        ideas = idea_gen.generate_multiple_ideas(count=args.count, output_file=ideas_file)
        
        logger.info(f"Generated {len(ideas)} video ideas, saved to {ideas_file}")
        
        if args.produce:
            # Initialize other modules
            voice_gen = VoiceGenerator()
            video_sel = VideoSelector()
            video_ed = VideoEditor()
            
            # Process each idea
            for i, idea in enumerate(ideas):
                try:
                    logger.info(f"Processing video {i+1}/{len(ideas)}: {idea['title']}")
                    
                    # Generate voiceover
                    audio_file = voice_gen.generate_from_script(idea['script'])
                    if not audio_file:
                        logger.error(f"Failed to generate voiceover for video {i+1}")
                        continue
                    
                    # Select video clips
                    video_files = video_sel.select_videos_for_script(idea['script'])
                    if not video_files:
                        logger.error(f"Failed to select video clips for video {i+1}")
                        continue
                    
                    # Create final video
                    output_name = f"tiktok_batch_{i+1}_{int(time.time())}.mp4"
                    output_video = video_ed.create_video(
                        idea['script'],
                        video_files,
                        audio_file,
                        output_name=output_name
                    )
                    
                    if output_video:
                        logger.info(f"Video {i+1} generation complete: {output_video}")
                    else:
                        logger.error(f"Failed to create video {i+1}")
                        
                except Exception as e:
                    logger.error(f"Error processing video {i+1}: {e}")
            
            logger.info("Batch video generation complete")
        else:
            logger.info("Ideas generated but videos not produced (use --produce to create videos)")
            
    except Exception as e:
        logger.error(f"Error in generate_multiple_videos: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='TikTok Video Generator')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Single video generation
    single_parser = subparsers.add_parser('single', help='Generate a single video')
    single_parser.add_argument('--category', help='Content category')
    single_parser.add_argument('--audience', help='Target audience')
    single_parser.add_argument('--trend', help='Trend type')
    single_parser.add_argument('--output', help='Output filename')
    
    # Multiple video generation
    multi_parser = subparsers.add_parser('multiple', help='Generate multiple videos')
    multi_parser.add_argument('--count', type=int, default=10, help='Number of videos to generate')
    multi_parser.add_argument('--produce', action='store_true', help='Produce videos (not just ideas)')
    
    args = parser.parse_args()
    
    if args.command == 'single':
        generate_single_video(args)
    elif args.command == 'multiple':
        generate_multiple_videos(args)
    else:
        parser.print_help()
