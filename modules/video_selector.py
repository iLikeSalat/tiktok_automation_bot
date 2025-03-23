import os
import requests
import time
import sys
sys.path.append('..')
from utils.logger import setup_logger
from utils.helpers import extract_keywords

# Set up logger
logger = setup_logger('video_selector')

class VideoSelector:
    def __init__(self):
        self.pexels_api_key = os.getenv("PEXELS_API_KEY")
        self.pixabay_api_key = os.getenv("PIXABAY_API_KEY")
        self.output_dir = "assets/video"
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info("VideoSelector initialized")
    
    def search_pexels(self, keyword, orientation="portrait", per_page=1):
        """Search Pexels API for videos"""
        try:
            headers = {"Authorization": self.pexels_api_key}
            url = f"https://api.pexels.com/videos/search?query={keyword}&orientation={orientation}&per_page={per_page}"
            
            logger.info(f"Searching Pexels for: {keyword}") 
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "videos" in data and len(data["videos"]) > 0:
                    return data["videos"]
                else:
                    logger.warning(f"No videos found for keyword: {keyword}")
                    return []
            else:
                logger.error(f"Pexels API error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Exception in search_pexels: {e}")
            return []
    
    def download_video(self, video_url, keyword):
        """Download video from URL"""
        try:
            timestamp = int(time.time())
            local_path = os.path.join(self.output_dir, f"{keyword}_{timestamp}.mp4")
            
            logger.info(f"Downloading video: {video_url}")
            response = requests.get(video_url, stream=True)
            
            if response.status_code == 200:
                with open(local_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                
                logger.info(f"Video saved to {local_path}")
                return local_path
            else:
                logger.error(f"Error downloading video: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Exception in download_video: {e}")
            return None
    
    def select_videos_for_script(self, script, num_videos=3):
        """Select videos based on script content"""
        try:
            # Extract text from script
            text = f"{script['hook']} {script['body']} {script['cta']}"
            
            # Extract keywords
            keywords = extract_keywords(text, max_keywords=num_videos)
            logger.info(f"Extracted keywords: {keywords}")
            
            video_files = []
            
            for keyword in keywords:
                videos = self.search_pexels(keyword)
                
                if videos:
                    video = videos[0]  # Get first result
                    video_url = None
                    
                    # Find HD or SD video file
                    for video_file in video["video_files"]:
                        if video_file["quality"] == "hd" and video_file["width"] >= 720:
                            video_url = video_file["link"]
                            break
                    
                    if not video_url and len(video["video_files"]) > 0:
                        video_url = video["video_files"][0]["link"]
                    
                    if video_url:
                        local_path = self.download_video(video_url, keyword)
                        if local_path:
                            video_files.append(local_path)
            
            logger.info(f"Selected {len(video_files)} videos for script")
            return video_files
            
        except Exception as e:
            logger.error(f"Error selecting videos for script: {e}")
            return []
