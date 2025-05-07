#!/usr/bin/env python3
# llm/formatter.py - Format and generate content with LLMs

import json
import logging
import os
import sys
import requests
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

import config
from llm.prompts import (
    create_article_prompt, 
    get_category_prompt,
    get_style_prompt
)

logger = logging.getLogger("LLMFormatter")

class ContentGenerator:
    """
    Generate content using LLMs.
    """
    
    def __init__(self, api_key=None, api_url=None):
        """
        Initialize the content generator.
        
        Args:
            api_key (str, optional): LLM API key
            api_url (str, optional): LLM API URL
        """
        self.api_key = api_key or config.LLM_API_KEY
        self.api_url = api_url or config.LLM_API_URL
        
    def generate_from_article(self, article_data, style=None):
        """
        Generate content from an article.
        
        Args:
            article_data (dict): Article data
            style (str, optional): Content style
            
        Returns:
            str: Generated content
        """
        # Create a summary for the article
        summary = self._create_summary(article_data)
        
        # Get the appropriate prompt
        category = article_data.get("category", "business_news")
        
        if style:
            prompt = get_style_prompt(style, summary)
        else:
            prompt = get_category_prompt(category, summary)
            
        # Generate content
        return self._generate_content(prompt)
        
    def generate_from_file(self, file_path, style=None):
        """
        Generate content from an article file.
        
        Args:
            file_path (str or Path): Path to article JSON file
            style (str, optional): Content style
            
        Returns:
            dict: Generated content and original article
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                article_data = json.load(f)
                
            content = self.generate_from_article(article_data, style)
            
            return {
                "generated_content": content,
                "article": article_data
            }
        except Exception as e:
            logger.error(f"Error generating content from {file_path}: {e}")
            return {
                "generated_content": None,
                "article": None,
                "error": str(e)
            }
            
    def _create_summary(self, article_data):
        """
        Create a summary of an article.
        
        Args:
            article_data (dict): Article data
            
        Returns:
            str: Article summary
        """
        # Use existing summary if available
        if article_data.get("summary"):
            return article_data["summary"]
            
        # Create summary from content
        content = article_data.get("content", "")
        if content:
            # Simple summarization: first few sentences or paragraphs
            paragraphs = content.split("\n\n")
            
            if len(paragraphs) > 2:
                # Use first two paragraphs
                return "\n\n".join(paragraphs[:2])
            elif len(content) > 500:
                # Use first 500 characters
                return content[:497] + "..."
            else:
                return content
                
        # Fallback to title
        return article_data.get("title", "")
        
    def _generate_content(self, prompt):
        """
        Generate content using an LLM API.
        
        Args:
            prompt (str): Prompt text
            
        Returns:
            str: Generated content
        """
        # Check if we're using OpenAI-compatible API
        if "openai.com" in self.api_url:
            return self._generate_with_openai(prompt)
        else:
            return self._generate_with_generic_api(prompt)
            
    def _generate_with_openai(self, prompt):
        """
        Generate content using OpenAI API.
        
        Args:
            prompt (str): Prompt text
            
        Returns:
            str: Generated content
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-4-turbo",  # Or other model
                "messages": [
                    {"role": "system", "content": prompt}
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                logger.error(f"API error: {response.status_code}, {response.text}")
                return f"Error generating content: {response.status_code}"
                
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            return f"Error generating content: {e}"
            
    def _generate_with_generic_api(self, prompt):
        """
        Generate content using a generic API.
        
        Args:
            prompt (str): Prompt text
            
        Returns:
            str: Generated content
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "prompt": prompt,
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract text based on API response format
                if "text" in result:
                    return result["text"].strip()
                elif "choices" in result and len(result["choices"]) > 0:
                    if isinstance(result["choices"][0], dict) and "text" in result["choices"][0]:
                        return result["choices"][0]["text"].strip()
                    else:
                        return str(result["choices"][0]).strip()
                else:
                    return str(result).strip()
            else:
                logger.error(f"API error: {response.status_code}, {response.text}")
                return f"Error generating content: {response.status_code}"
                
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            return f"Error generating content: {e}"

# Simple test
def test_generator():
    generator = ContentGenerator()
    
    test_article = {
        "title": "Google Enters Movie and TV Business with New Production Studio",
        "url": "https://www.businessinsider.com/google-enters-movie-tv-business",
        "summary": "Google has quietly launched a production studio called '100 Zeros' to create movies and TV shows. Their first film, a horror movie called 'Cuckoo', was released in 2024.",
        "content": "Google has begun making films — the company quietly launched its own production studio '100 Zeros'. Now they'll be making their own shows so that 'heroes there finally use Android, not iPhone'. Projects will be distributed on Netflix and other platforms. The first film, 100 Zeros horror film 'Cuckoo', was released in 2024. Seriously: Google went into cinema so that characters would use Android there. Other technologies, like Gemini and Google Maps, will also be featured.",
        "source": "Business Insider",
        "category": "it_news",
        "image_url": "https://example.com/google-image.jpg",
        "timestamp": "2024-05-01T12:34:56Z"
    }
    
    # Try different styles
    print("=== CATEGORY STYLE ===")
    content1 = generator.generate_from_article(test_article)
    print(content1)
    
    print("\n=== VIRAL STYLE ===")
    content2 = generator.generate_from_article(test_article, "viral")
    print(content2)
    
    print("\n=== QUICK STYLE ===")
    content3 = generator.generate_from_article(test_article, "quick")
    print(content3)

if __name__ == "__main__":
    # Mock API response for testing
    ContentGenerator._generate_with_openai = lambda self, prompt: f"[TEST CONTENT FOR PROMPT: {prompt[:30]}...]"
    ContentGenerator._generate_with_generic_api = lambda self, prompt: f"[TEST CONTENT FOR PROMPT: {prompt[:30]}...]"
    
    test_generator()