import requests
from bs4 import BeautifulSoup
from readability import Document
from youtube_transcript_api import YouTubeTranscriptApi
import re
from typing import List, Tuple
from schemas import SourceContent

def fetch_url(url: str, timeout: int = 10) -> Tuple[str, str]:
    """Fetch URL content. Returns (html, error_msg)"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.text, None
    except Exception as e:
        return "", f"Failed to fetch: {str(e)}"

def extract_article_text(html: str, url: str) -> str:
    """Extract clean article text from HTML"""
    if not html:
        return ""
    try:
        doc = Document(html)
        soup = BeautifulSoup(doc.summary(), 'html.parser')
        
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        
        text = soup.get_text(separator='\n', strip=True)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)
    except Exception as e:
        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text(separator='\n', strip=True)

def extract_youtube_transcript(url: str) -> Tuple[str, str]:
    """Extract YouTube transcript. Returns (transcript, error_msg)"""
    try:
        video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
        if not video_id_match:
            return "", "Invalid YouTube URL"
        
        video_id = video_id_match.group(1)
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = ' '.join([entry['text'] for entry in transcript_list])
        return transcript, None
    except Exception as e:
        return "", f"Transcript unavailable: {str(e)}"

def extract_title_from_html(html: str, url: str) -> str:
    """Extract title from HTML"""
    if not html:
        return url
    try:
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('title')
        if title:
            return title.get_text().strip()
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        return url
    except:
        return url

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    """Split text into overlapping chunks"""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks if chunks else [text]

def ingest_source(url: str, manual_text: str = None) -> SourceContent:
    """Ingest a single source (YouTube or article)"""
    if manual_text:
        return SourceContent(
            url=url,
            title=url,
            type="article",
            content=manual_text,
            length=len(manual_text)
        )
    
    is_youtube = 'youtube.com' in url or 'youtu.be' in url
    
    if is_youtube:
        transcript, error = extract_youtube_transcript(url)
        if error:
            return SourceContent(
                url=url,
                title=url,
                type="youtube",
                content="",
                error=error,
                length=0
            )
        return SourceContent(
            url=url,
            title=url,
            type="youtube",
            content=transcript,
            length=len(transcript)
        )
    else:
        html, error = fetch_url(url)
        if error:
            return SourceContent(
                url=url,
                title=url,
                type="article",
                content="",
                error=error,
                length=0
            )
        
        title = extract_title_from_html(html, url)
        text = extract_article_text(html, url)
        
        return SourceContent(
            url=url,
            title=title,
            type="article",
            content=text,
            length=len(text)
        )
