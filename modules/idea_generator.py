import os
import json
import random
import openai
import sys
sys.path.append('..')
from utils.logger import setup_logger
from utils.helpers import load_json, save_json

# Set up logger
logger = setup_logger('idea_generator')

class IdeaGenerator:
    def __init__(self, templates_dir='data/templates', trends_file='data/trends.json'):
        # Initialize OpenAI API
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        # Load templates
        self.hook_templates = load_json(os.path.join(templates_dir, 'hook_templates.json'))
        self.body_templates = load_json(os.path.join(templates_dir, 'body_templates.json'))
        self.cta_templates = load_json(os.path.join(templates_dir, 'cta_templates.json'))
        
        # Load data
        self.trends = load_json(trends_file)
        self.categories = load_json('data/categories/categories.json')
        self.audiences = load_json('data/categories/audiences.json')
        
        logger.info("IdeaGenerator initialized")
    
    def generate_video_idea(self, category=None, audience=None, trend=None):
        """Generate a complete video idea with script"""
        try:
            # Select random elements if not specified
            category = category or random.choice(self.categories)
            audience = audience or random.choice(self.audiences)
            trend = trend or random.choice(self.trends)
            
            # Generate title
            title_templates = [
                "How to {trend} for {category}",
                "Why you should {trend} for {category}",
                "The secret to {trend} for {category}",
                "3 ways to {trend} for {category}",
                "I tried {trend} for {category}"
            ]
            title = random.choice(title_templates).format(
                trend=trend.lower(),
                category=category.lower()
            )
            
            # Generate script sections using GPT-4
            prompt = f"""
            Create a TikTok script with three sections:
            1. A hook (max 15 words) about {trend} for {category} targeting {audience}
            2. A body section (max 100 words) explaining 3 key points about {trend}
            3. A call-to-action (max 20 words) encouraging engagement
            
            Format as JSON with keys: "hook", "body", "cta"
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
            
            script = json.loads(response.choices[0].message.content)
            
            # Generate hashtags
            hashtags = [
                f"#{category.replace(' ', '')}",
                f"#{trend.replace(' ', '').replace('-', '')}",
                "#TikTokTips",
                f"#{audience.split()[0].replace('(', '').replace(')', '').replace('-', '')}",
                "#viral",
                "#trending"
            ]
            
            # Create complete video idea
            video_idea = {
                "title": title,
                "category": category,
                "target_audience": audience,
                "trend_type": trend,
                "script": script,
                "visual_elements": f"Show {trend.lower()} in action with text overlays highlighting key points",
                "audio_suggestions": f"Upbeat background music suitable for {category.lower()} content",
                "hashtags": hashtags
            }
            
            logger.info(f"Generated video idea: {title}")
            return video_idea
            
        except Exception as e:
            logger.error(f"Error generating video idea: {e}")
            return None
    
    def generate_multiple_ideas(self, count=10, output_file=None):
        """Generate multiple video ideas"""
        ideas = []
        
        for i in range(count):
            idea = self.generate_video_idea()
            if idea:
                idea['id'] = i + 1
                ideas.append(idea)
        
        if output_file:
            save_json(ideas, output_file)
            logger.info(f"Saved {len(ideas)} ideas to {output_file}")
        
        return ideas