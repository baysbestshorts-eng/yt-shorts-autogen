"""
Content scraping module for gathering interesting content from various sources
"""

import os
import logging
import requests
import praw
import time
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
from dataclasses import dataclass
from datetime import datetime, timedelta
import random

from utils import clean_text, generate_content_hash, retry_with_backoff

@dataclass
class ScrapedContent:
    """Data class for scraped content"""
    title: str
    content: str
    source: str
    url: str
    timestamp: datetime
    score: int = 0
    tags: List[str] = None
    content_hash: str = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.content_hash is None:
            self.content_hash = generate_content_hash(self.content)

class ContentScraper:
    """Main content scraping class"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.scraped_hashes = set()  # Track to avoid duplicates
        
        # Initialize Reddit client if configured
        self.reddit = None
        if 'reddit' in config and os.getenv('REDDIT_CLIENT_ID'):
            self._init_reddit()
    
    def _init_reddit(self):
        """Initialize Reddit API client"""
        try:
            self.reddit = praw.Reddit(
                client_id=os.getenv('REDDIT_CLIENT_ID'),
                client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                user_agent=os.getenv('REDDIT_USER_AGENT', 'YTShortsBot/1.0')
            )
            self.logger.info("Reddit client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Reddit client: {e}")
    
    def scrape_content(self) -> List[ScrapedContent]:
        """
        Main method to scrape content from all configured sources
        
        Returns:
            List[ScrapedContent]: List of scraped content items
        """
        all_content = []
        sources = self.config.get('sources', ['reddit'])
        
        for source in sources:
            try:
                if source == 'reddit' and self.reddit:
                    content = self._scrape_reddit()
                    all_content.extend(content)
                elif source == 'news_api':
                    content = self._scrape_news_api()
                    all_content.extend(content)
                elif source == 'wikipedia':
                    content = self._scrape_wikipedia()
                    all_content.extend(content)
                else:
                    self.logger.warning(f"Unknown or unconfigured source: {source}")
                    
            except Exception as e:
                self.logger.error(f"Error scraping from {source}: {e}")
        
        # Filter and deduplicate
        filtered_content = self._filter_content(all_content)
        self.logger.info(f"Scraped {len(filtered_content)} unique content items")
        
        return filtered_content
    
    def _scrape_reddit(self) -> List[ScrapedContent]:
        """Scrape content from Reddit"""
        content_list = []
        reddit_config = self.config.get('reddit', {})
        subreddits = reddit_config.get('subreddits', ['todayilearned'])
        max_posts = reddit_config.get('max_posts', 10)
        time_filter = reddit_config.get('time_filter', 'day')
        
        for subreddit_name in subreddits:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # Get hot posts from the subreddit
                posts = subreddit.hot(limit=max_posts)
                
                for post in posts:
                    # Skip if already processed
                    content_hash = generate_content_hash(post.selftext or post.title)
                    if content_hash in self.scraped_hashes:
                        continue
                    
                    # Create content object
                    content = ScrapedContent(
                        title=post.title,
                        content=post.selftext or post.title,
                        source=f"reddit_r_{subreddit_name}",
                        url=f"https://reddit.com{post.permalink}",
                        timestamp=datetime.fromtimestamp(post.created_utc),
                        score=post.score,
                        content_hash=content_hash
                    )
                    
                    content_list.append(content)
                    self.scraped_hashes.add(content_hash)
                    
                    # Rate limiting
                    time.sleep(0.5)
                    
            except Exception as e:
                self.logger.error(f"Error scraping subreddit {subreddit_name}: {e}")
        
        return content_list
    
    def _scrape_news_api(self) -> List[ScrapedContent]:
        """Scrape content from news APIs"""
        content_list = []
        
        # Example with a free news API (you'd need to implement specific APIs)
        try:
            # This is a placeholder - implement specific news API integration
            self.logger.info("News API scraping not fully implemented yet")
            
            # Example structure for news API integration:
            # response = requests.get('https://api.example.com/news', params={...})
            # news_data = response.json()
            # for article in news_data['articles']:
            #     content = ScrapedContent(...)
            #     content_list.append(content)
            
        except Exception as e:
            self.logger.error(f"Error scraping news API: {e}")
        
        return content_list
    
    def _scrape_wikipedia(self) -> List[ScrapedContent]:
        """Scrape interesting content from Wikipedia"""
        content_list = []
        
        try:
            # Get featured articles or random articles
            wiki_url = "https://en.wikipedia.org/api/rest_v1/feed/featured/"
            today = datetime.now().strftime("%Y/%m/%d")
            
            response = requests.get(f"{wiki_url}{today}")
            if response.status_code == 200:
                data = response.json()
                
                # Process featured articles
                if 'tfa' in data:  # Today's featured article
                    article = data['tfa']
                    content = ScrapedContent(
                        title=article.get('title', ''),
                        content=article.get('extract', ''),
                        source="wikipedia_featured",
                        url=article.get('content_urls', {}).get('desktop', {}).get('page', ''),
                        timestamp=datetime.now(),
                        score=100  # High score for featured articles
                    )
                    content_list.append(content)
                
                # Process on this day articles
                if 'onthisday' in data:
                    for event in data['onthisday'][:3]:  # Take first 3 events
                        content = ScrapedContent(
                            title=f"On This Day: {event.get('text', '')}",
                            content=event.get('text', ''),
                            source="wikipedia_onthisday",
                            url=event.get('pages', [{}])[0].get('content_urls', {}).get('desktop', {}).get('page', ''),
                            timestamp=datetime.now(),
                            score=75
                        )
                        content_list.append(content)
                        
        except Exception as e:
            self.logger.error(f"Error scraping Wikipedia: {e}")
        
        return content_list
    
    def _filter_content(self, content_list: List[ScrapedContent]) -> List[ScrapedContent]:
        """Filter content based on configuration rules"""
        filters = self.config.get('content_filters', {})
        min_length = filters.get('min_length', 100)
        max_length = filters.get('max_length', 500)
        exclude_nsfw = filters.get('exclude_nsfw', True)
        exclude_politics = filters.get('exclude_politics', True)
        
        filtered_content = []
        
        for content in content_list:
            # Length check
            content_text = content.content.strip()
            if len(content_text) < min_length or len(content_text) > max_length:
                continue
            
            # Content quality check
            if not self._is_quality_content(content):
                continue
            
            # NSFW/Politics filter (basic keyword matching)
            if exclude_nsfw and self._contains_nsfw_content(content):
                continue
            
            if exclude_politics and self._contains_political_content(content):
                continue
            
            # Clean the content
            content.content = clean_text(content.content)
            content.title = clean_text(content.title)
            
            filtered_content.append(content)
        
        # Sort by score and return top items
        filtered_content.sort(key=lambda x: x.score, reverse=True)
        return filtered_content[:10]  # Return top 10 items
    
    def _is_quality_content(self, content: ScrapedContent) -> bool:
        """Check if content meets quality standards"""
        # Check for minimum word count
        word_count = len(content.content.split())
        if word_count < 20:
            return False
        
        # Check for repetitive content
        words = content.content.lower().split()
        unique_words = set(words)
        if len(unique_words) / len(words) < 0.5:  # Less than 50% unique words
            return False
        
        # Check for proper sentences
        sentences = content.content.split('.')
        if len(sentences) < 2:
            return False
        
        return True
    
    def _contains_nsfw_content(self, content: ScrapedContent) -> bool:
        """Check if content contains NSFW material"""
        nsfw_keywords = [
            'nsfw', 'porn', 'sex', 'adult', 'nude', 'naked', 'explicit',
            'sexual', 'mature', 'xxx', 'erotic', 'intimate'
        ]
        
        text_lower = (content.title + ' ' + content.content).lower()
        return any(keyword in text_lower for keyword in nsfw_keywords)
    
    def _contains_political_content(self, content: ScrapedContent) -> bool:
        """Check if content contains political material"""
        political_keywords = [
            'trump', 'biden', 'politics', 'democrat', 'republican', 'election',
            'vote', 'congress', 'senate', 'government', 'policy', 'politician'
        ]
        
        text_lower = (content.title + ' ' + content.content).lower()
        return any(keyword in text_lower for keyword in political_keywords)
    
    def get_random_content(self) -> Optional[ScrapedContent]:
        """Get a random piece of content from scraped items"""
        all_content = self.scrape_content()
        if all_content:
            return random.choice(all_content)
        return None
    
    def search_content_by_keyword(self, keyword: str) -> List[ScrapedContent]:
        """Search for content containing specific keywords"""
        all_content = self.scrape_content()
        matching_content = []
        
        for content in all_content:
            if keyword.lower() in content.title.lower() or keyword.lower() in content.content.lower():
                matching_content.append(content)
        
        return matching_content