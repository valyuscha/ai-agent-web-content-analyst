#!/usr/bin/env python3
"""Test YouTube OAuth caption download"""
import sys
sys.path.insert(0, '/home/vsyd/capstone-project/web-analyst-web/backend')

from core.tools import extract_youtube_captions_oauth

# Test with a video that has captions
video_id = 'dQw4w9WgXcQ'  # Rick Astley - Never Gonna Give You Up
token_file = 'youtube_token.pickle'

print(f"Testing OAuth caption download for video: {video_id}")
transcript, error = extract_youtube_captions_oauth(video_id, token_file)

if error:
    print(f"❌ Error: {error}")
else:
    print(f"✅ Success! Got {len(transcript)} characters")
    print(f"\nFirst 200 chars:\n{transcript[:200]}...")
