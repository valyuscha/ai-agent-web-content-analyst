import requests
from bs4 import BeautifulSoup
from readability import Document
from youtube_transcript_api import YouTubeTranscriptApi
import re
from typing import Tuple, Optional
from core.interfaces import ContentExtractor

class ArticleExtractor(ContentExtractor):
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
    
    def extract(self, url: str) -> Tuple[str, str, Optional[str]]:
        html, error = self._fetch(url)
        if error:
            return "", url, error
        
        title = self._extract_title(html, url)
        content = self._extract_text(html)
        return content, title, None
    
    def _fetch(self, url: str) -> Tuple[str, Optional[str]]:
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.text, None
        except Exception as e:
            return "", f"Failed to fetch: {str(e)}"
    
    def _extract_title(self, html: str, fallback: str) -> str:
        if not html:
            return fallback
        try:
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.find('title')
            if title:
                return title.get_text().strip()
            h1 = soup.find('h1')
            if h1:
                return h1.get_text().strip()
        except:
            pass
        return fallback
    
    def _extract_text(self, html: str) -> str:
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
        except:
            soup = BeautifulSoup(html, 'html.parser')
            return soup.get_text(separator='\n', strip=True)

class YouTubeExtractor(ContentExtractor):
    def extract(self, url: str) -> Tuple[str, str, Optional[str]]:
        try:
            video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
            if not video_id_match:
                return "", url, "Invalid YouTube URL"
            
            video_id = video_id_match.group(1)
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            transcript = ' '.join([entry['text'] for entry in transcript_list])
            return transcript, url, None
        except Exception as e:
            return "", url, f"Transcript unavailable: {str(e)}"

class ContentExtractorFactory:
    @staticmethod
    def create(url: str, timeout: int = 10) -> ContentExtractor:
        if 'youtube.com' in url or 'youtu.be' in url:
            return YouTubeExtractor()
        return ArticleExtractor(timeout)
