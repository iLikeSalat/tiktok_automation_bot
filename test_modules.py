import os
import json
from dotenv import load_dotenv
from modules.idea_generator import IdeaGenerator
from modules.voice_generator import VoiceGenerator
from modules.video_selector import VideoSelector
from modules.video_editor import VideoEditor

# Load environment variables
load_dotenv()

def test_idea_generator():
    print("Testing Idea Generator...")
    generator = IdeaGenerator()
    idea = generator.generate_video_idea()
    print(f"Generated idea: {idea['title']}")
    print(f"Hook: {idea['script']['hook']}")
    print(f"Body: {idea['script']['body']}")
    print(f"CTA: {idea['script']['cta']}")
    return idea

def test_voice_generator(script):
    print("\nTesting Voice Generator...")
    generator = VoiceGenerator()
    audio_file = generator.generate_from_script(script)
    print(f"Generated audio file: {audio_file}")
    return audio_file

def test_video_selector(script):
    print("\nTesting Video Selector...")
    selector = VideoSelector()
    video_files = selector.select_videos_for_script(script)
    print(f"Selected video files: {video_files}")
    return video_files

def test_video_editor(script, video_files, audio_file):
    print("\nTesting Video Editor...")
    editor = VideoEditor()
    output_video = editor.create_video(script, video_files, audio_file)
    print(f"Created video: {output_video}")
    return output_video

if __name__ == "__main__":
    # Test each module in sequence
    idea = test_idea_generator()
    
    if idea:
        audio_file = test_voice_generator(idea['script'])
        
        if audio_file:
            video_files = test_video_selector(idea['script'])
            
            if video_files:
                output_video = test_video_editor(idea['script'], video_files, audio_file)
                
                if output_video:
                    print("\n✅ All tests completed successfully!")
                else:
                    print("\n❌ Video editor test failed")
            else:
                print("\n❌ Video selector test failed")
        else:
            print("\n❌ Voice generator test failed")
    else:
        print("\n❌ Idea generator test failed")
