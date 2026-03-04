import requests
from bs4 import BeautifulSoup
from readability import Document
import re
import ipaddress
from urllib.parse import urlparse
from typing import List, Tuple
from core.schemas import SourceContent
import os

def is_safe_url(url: str) -> Tuple[bool, str]:
    """Check if URL is safe (SSRF protection)"""
    try:
        parsed = urlparse(url)
        
        # Only allow http/https
        if parsed.scheme not in ['http', 'https']:
            return False, "Only http/https protocols allowed"
        
        # Get hostname
        hostname = parsed.hostname
        if not hostname:
            return False, "Invalid hostname"
        
        # Block localhost
        if hostname.lower() in ['localhost', '127.0.0.1', '::1']:
            return False, "Localhost access blocked"
        
        # Try to resolve to IP and check if private
        try:
            import socket
            ip = socket.gethostbyname(hostname)
            ip_obj = ipaddress.ip_address(ip)
            
            # Block private IP ranges
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local:
                return False, "Private IP access blocked"
        except:
            pass  # If can't resolve, allow (might be valid external domain)
        
        return True, ""
    except Exception as e:
        return False, f"Invalid URL: {str(e)}"

def fetch_url(url: str, timeout: int = 10) -> Tuple[str, str]:
    """Fetch URL content with SSRF protection. Returns (html, error_msg)"""
    # SSRF protection
    is_safe, error_msg = is_safe_url(url)
    if not is_safe:
        return "", f"Security: {error_msg}"
    
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

def ingest_source(url: str, manual_text: str = None, api_key: str = None) -> SourceContent:
    """Ingest a single source (text article or pasted text)"""
    if manual_text:
        # Limit manual text length
        if len(manual_text) > 25000:
            manual_text = manual_text[:25000]
        return SourceContent(
            url=url or "pasted_text",
            title="Pasted Text",
            type="text",
            content=manual_text,
            length=len(manual_text)
        )
    
    # Only support web articles
    if not url or not url.startswith(('http://', 'https://')):
        return SourceContent(
            url=url or "",
            title="",
            type="article",
            content="",
            error="Invalid URL. Please provide a valid http/https URL or paste text directly.",
            length=0
        )
    
    # Fetch and extract article text
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
    
    # Limit text length
    if len(text) > 25000:
        text = text[:25000]
    
    return SourceContent(
        url=url,
        title=title,
        type="article",
        content=text,
        length=len(text)
    )
