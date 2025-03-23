import os
import json
import time
from flask import Flask, render_template, request, jsonify, send_from_directory
from modules.idea_generator import IdeaGenerator
from modules.voice_generator import VoiceGenerator
from modules.video_selector import VideoSelector
from modules.video_editor import VideoEditor

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'assets/output'

# Initialize modules
idea_gen = IdeaGenerator()
voice_gen = VoiceGenerator()
video_sel = VideoSelector()
video_ed = VideoEditor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_idea', methods=['POST'])
def generate_idea():
    try:
        category = request.form.get('category')
        audience = request.form.get('audience')
        trend = request.form.get('trend')
        
        idea = idea_gen.generate_video_idea(
            category=category if category else None,
            audience=audience if audience else None,
            trend=trend if trend else None
        )
        
        return jsonify({'success': True, 'idea': idea})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/generate_video', methods=['POST'])
def generate_video():
    try:
        data = request.get_json()
        script = data.get('script')
        
        # Generate voiceover
        audio_file = voice_gen.generate_from_script(script)
        if not audio_file:
            return jsonify({'success': False, 'error': 'Failed to generate voiceover'})
        
        # Select video clips
        video_files = video_sel.select_videos_for_script(script)
        if not video_files:
            return jsonify({'success': False, 'error': 'Failed to select video clips'})
        
        # Create final video
        timestamp = int(time.time())
        output_name = f"tiktok_{timestamp}.mp4"
        output_video = video_ed.create_video(script, video_files, audio_file, output_name=output_name)
        
        if output_video:
            video_url = f"/videos/{os.path.basename(output_video)}"
            return jsonify({'success': True, 'video_url': video_url})
        else:
            return jsonify({'success': False, 'error': 'Failed to create video'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})