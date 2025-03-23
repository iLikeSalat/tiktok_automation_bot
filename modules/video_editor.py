import os
import sys
import time
import moviepy.editor as mp
import numpy as np
sys.path.append('..')
from utils.logger import setup_logger
from utils.helpers import load_json

# Set up logger
logger = setup_logger('video_editor')

class VideoEditor:
    def __init__(self, config_file='config.json'):
        self.config = load_json(config_file).get('video_settings', {})
        self.output_dir = "assets/output"
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info("VideoEditor initialized")
    
    def create_video(self, script, video_files, audio_file, output_name=None):
        """Create final video with all elements"""
        try:
            if not output_name:
                timestamp = int(time.time())
                output_name = f"tiktok_{timestamp}.mp4"
            
            output_path = os.path.join(self.output_dir, output_name)
            
            # Load audio
            audio = mp.AudioFileClip(audio_file)
            audio_duration = audio.duration
            
            logger.info(f"Creating video with {len(video_files)} clips and audio duration {audio_duration}s")
            
            # Create clips from video files
            clips = []
            remaining_duration = audio_duration
            
            for video_file in video_files:
                if remaining_duration <= 0:
                    break
                    
                video = mp.VideoFileClip(video_file)
                
                # Ensure vertical orientation (9:16 aspect ratio)
                if video.w > video.h:
                    video = video.resize(height=1920)
                    video = video.crop(x_center=video.w/2, width=1080, height=1920)
                else:
                    video = video.resize(width=1080)
                    
                # Determine clip duration
                clip_duration = min(video.duration, remaining_duration)
                video = video.subclip(0, clip_duration)
                
                # Skip effects for now
                # video = self._add_effects(video)
                
                clips.append(video)
                remaining_duration -= clip_duration
            
            # If we don't have enough video content, loop the last clip
            if remaining_duration > 0 and clips:
                last_clip = clips[-1]
                loops_needed = int(np.ceil(remaining_duration / last_clip.duration))
                
                for _ in range(loops_needed):
                    if remaining_duration <= 0:
                        break
                    
                    clip_duration = min(last_clip.duration, remaining_duration)
                    looped_clip = last_clip.subclip(0, clip_duration)
                    clips.append(looped_clip)
                    remaining_duration -= clip_duration
            
            # Concatenate clips
            if clips:
                final_video = mp.concatenate_videoclips(clips)
                
                # Add audio
                final_video = final_video.set_audio(audio)
                
                # Add captions
                final_video = self._add_captions(final_video, script)
                
                # Write final video
                logger.info(f"Writing video to {output_path}")
                final_video.write_videofile(
                    output_path,
                    codec="libx264",
                    audio_codec="aac",
                    fps=self.config.get('fps', 30),
                    bitrate=self.config.get('bitrate', "8000k")
                )
                
                logger.info(f"Video created successfully: {output_path}")
                return output_path
            else:
                logger.error("No video clips available to create video")
                return None
                
        except Exception as e:
            logger.error(f"Error creating video: {e}")
            return None
    
    def _add_effects(self, clip):
        """Add visual effects to video clip"""
        # Simplified version - just return the clip for now
        return clip
    
    def _add_captions(self, video, script):
        """Add captions to video"""
        try:
            # Hook caption (first 3 seconds)
            hook_txt_clip = mp.TextClip(
                script['hook'],
                fontsize=70,
                color='white',
                bg_color='black',
                font='Arial-Bold',
                size=(video.w - 40, None),
                method='caption'
            ).set_position(('center', 'center')).set_duration(3)
            
            # Body captions (middle section)
            body_txt_clip = mp.TextClip(
                script['body'][:100] + "...",
                fontsize=50,
                color='white',
                font='Arial',
                size=(video.w - 80, None),
                method='caption'
            ).set_position(('center', 'bottom')).set_start(3).set_duration(video.duration - 13)
            
            # CTA caption (last 10 seconds)
            cta_txt_clip = mp.TextClip(
                script['cta'],
                fontsize=60,
                color='yellow',
                font='Arial-Bold',
                size=(video.w - 40, None),
                method='caption'
            ).set_position(('center', 'center')).set_start(video.duration - 10).set_duration(10)
            
            # Composite video with captions
            final = mp.CompositeVideoClip([
                video,
                hook_txt_clip,
                body_txt_clip,
                cta_txt_clip
            ])
            
            return final
        except Exception as e:
            logger.error(f"Error adding captions: {e}")
            return video
