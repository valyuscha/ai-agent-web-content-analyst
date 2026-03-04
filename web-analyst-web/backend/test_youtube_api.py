#!/usr/bin/env python3
"""Test YouTube API connection"""
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

api_key = os.getenv('YOUTUBE_API_KEY')

if not api_key or api_key == 'your_youtube_api_key_here':
    print("❌ YOUTUBE_API_KEY not set in .env file")
    exit(1)

print(f"✓ API key found: {api_key[:10]}...")

try:
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    # Test with a simple search
    request = youtube.search().list(
        part='snippet',
        q='test',
        maxResults=1
    )
    response = request.execute()
    
    print("✓ YouTube API connection successful!")
    print(f"✓ API is working - found {response['pageInfo']['totalResults']} results")
    
    # Test captions list (this is what we'll use for transcripts)
    test_video_id = 'dQw4w9WgXcQ'  # Rick Astley - Never Gonna Give You Up
    captions = youtube.captions().list(part='snippet', videoId=test_video_id).execute()
    
    if captions.get('items'):
        print(f"✓ Captions API working - found {len(captions['items'])} caption tracks")
    else:
        print("⚠ Captions API accessible but test video has no captions")
    
    print("\n✅ YouTube API setup complete and working!")
    
except HttpError as e:
    print(f"❌ YouTube API error: {e}")
    if e.resp.status == 403:
        print("   Check if YouTube Data API v3 is enabled in Google Cloud Console")
    elif e.resp.status == 400:
        print("   Invalid API key")
except Exception as e:
    print(f"❌ Error: {e}")
