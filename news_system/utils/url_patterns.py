#!/usr/bin/env python3
# utils/url_patterns.py - URL pattern recognition and generation utilities

import re
import logging
from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin
from typing import List, Dict, Any, Optional, Set, Tuple, Pattern
from collections import defaultdict, Counter

logger = logging.getLogger("NewsSystem.URLPatterns")

class URLPatterns:
    """
    URL pattern recognition and generation utility for discovering content
    systematically across news websites.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize URL patterns analyzer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # Pattern definitions
        self.date_patterns = [
            # Year/Month/Day patterns
            r'/(\d{4})/(\d{1,2})/(\d{1,2})/',
            r'/(\d{4})-(\d{1,2})-(\d{1,2})/',
            r'/(\d{4})_(\d{1,2})_(\d{1,2})/',
            
            # Year/Month patterns
            r'/(\d{4})/(\d{1,2})/',
            r'/(\d{4})-(\d{1,2})/',
            
            # Year only patterns
            r'/(\d{4})/',
            
            # Month/Day patterns (assuming current year)
            r'/(\d{1,2})/(\d{1,2})/',
            r'/(\d{1,2})-(\d{1,2})/',
        ]
        
        self.article_indicators = [
            'article', 'post', 'story', 'news', 'blog',
            'press-release', 'update', 'announcement',
            'feature', 'report', 'interview', 'review'
        ]
        
        self.category_indicators = [
            'tech', 'technology', 'business', 'finance',
            'politics', 'sports', 'entertainment', 'health',
            'science', 'world', 'local', 'opinion',
            'lifestyle', 'culture', 'travel', 'food'
        ]
        
        # Compiled patterns for better performance
        self.compiled_date_patterns = [re.compile(pattern) for pattern in self.date_patterns]
        
        # URL structure analysis
        self.domain_patterns: Dict[str, Dict[str, Any]] = {}
        
        logger.info("URLPatterns initialized")
    
    def analyze_urls(self, urls: List[str], domain: str = None) -> Dict[str, Any]:
        """
        Analyze a list of URLs to discover patterns.
        
        Args:
            urls: List of URLs to analyze
            domain: Optional domain context
            
        Returns:
            Analysis results with discovered patterns
        """
        if not urls:
            return {}
        
        analysis = {
            'total_urls': len(urls),
            'domain': domain or self._extract_domain(urls[0]),
            'path_patterns': [],
            'date_patterns': [],
            'category_patterns': [],
            'id_patterns': [],
            'common_prefixes': [],
            'common_suffixes': [],
            'url_structure': {}
        }
        
        # Analyze URL components
        paths = [urlparse(url).path for url in urls]
        
        # Find common path patterns
        analysis['path_patterns'] = self._find_path_patterns(paths)
        
        # Find date patterns
        analysis['date_patterns'] = self._find_date_patterns(paths)
        
        # Find category patterns
        analysis['category_patterns'] = self._find_category_patterns(paths)
        
        # Find ID patterns
        analysis['id_patterns'] = self._find_id_patterns(paths)
        
        # Find common prefixes and suffixes
        analysis['common_prefixes'] = self._find_common_prefixes(paths)
        analysis['common_suffixes'] = self._find_common_suffixes(paths)
        
        # Analyze URL structure
        analysis['url_structure'] = self._analyze_url_structure(paths)
        
        # Cache domain patterns
        if domain:
            self.domain_patterns[domain] = analysis
        
        logger.debug(f"Analyzed {len(urls)} URLs for domain {analysis['domain']}")
        return analysis
    
    def generate_urls(self, base_url: str, pattern_analysis: Dict[str, Any] = None,
                     date_range: int = 7) -> List[str]:
        """
        Generate potential URLs based on discovered patterns.
        
        Args:
            base_url: Base URL to generate from
            pattern_analysis: Previous pattern analysis (optional)
            date_range: Number of days to generate URLs for
            
        Returns:
            List of generated URLs
        """
        domain = urlparse(base_url).netloc
        
        # Use cached patterns if available
        if not pattern_analysis and domain in self.domain_patterns:
            pattern_analysis = self.domain_patterns[domain]
        
        generated_urls = []
        
        # Generate date-based URLs
        date_urls = self._generate_date_based_urls(base_url, pattern_analysis, date_range)
        generated_urls.extend(date_urls)
        
        # Generate category-based URLs
        category_urls = self._generate_category_based_urls(base_url, pattern_analysis)
        generated_urls.extend(category_urls)
        
        # Generate ID-based URLs
        id_urls = self._generate_id_based_urls(base_url, pattern_analysis)
        generated_urls.extend(id_urls)
        
        # Generate pattern-based URLs
        pattern_urls = self._generate_pattern_based_urls(base_url, pattern_analysis)
        generated_urls.extend(pattern_urls)
        
        # Remove duplicates and return
        unique_urls = list(set(generated_urls))
        logger.debug(f"Generated {len(unique_urls)} URLs for {domain}")
        
        return unique_urls
    
    def is_article_url(self, url: str) -> bool:
        """
        Determine if a URL is likely an article based on patterns.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL appears to be an article
        """
        url_lower = url.lower()
        path = urlparse(url).path.lower()
        
        # Check for article indicators
        for indicator in self.article_indicators:
            if indicator in path:
                return True
        
        # Check for date patterns (articles often have dates)
        for pattern in self.compiled_date_patterns:
            if pattern.search(path):
                return True
        
        # Check for numeric IDs (common in article URLs)
        if re.search(r'/\d{3,}', path):  # 3+ digit numbers
            return True
        
        # Check for slug patterns (articles often have readable slugs)
        if re.search(r'/[a-z0-9-]{10,}', path):  # Long slug-like strings
            return True
        
        return False
    
    def extract_date_from_url(self, url: str) -> Optional[datetime]:
        """
        Extract date from URL if present.
        
        Args:
            url: URL to extract date from
            
        Returns:
            Datetime object if date found, None otherwise
        """
        path = urlparse(url).path
        
        for pattern in self.compiled_date_patterns:
            match = pattern.search(path)
            if match:
                groups = match.groups()
                
                try:
                    if len(groups) == 3:  # Year, month, day
                        year, month, day = map(int, groups)
                        return datetime(year, month, day)
                    elif len(groups) == 2:
                        if int(groups[0]) > 31:  # Likely year, month
                            year, month = map(int, groups)
                            return datetime(year, month, 1)
                        else:  # Likely month, day (current year)
                            month, day = map(int, groups)
                            current_year = datetime.now().year
                            return datetime(current_year, month, day)
                    elif len(groups) == 1:  # Year only
                        year = int(groups[0])
                        return datetime(year, 1, 1)
                        
                except ValueError:
                    continue
        
        return None
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        return urlparse(url).netloc
    
    def _find_path_patterns(self, paths: List[str]) -> List[Dict[str, Any]]:
        """Find common path patterns in URLs."""
        patterns = []
        
        # Split paths into segments
        all_segments = []
        for path in paths:
            segments = [s for s in path.split('/') if s]
            all_segments.append(segments)
        
        if not all_segments:
            return patterns
        
        # Find common starting segments
        max_common_length = min(len(segments) for segments in all_segments)
        
        for i in range(max_common_length):
            segment_counter = Counter(segments[i] for segments in all_segments if i < len(segments))
            
            # If most paths have the same segment at this position
            most_common = segment_counter.most_common(1)[0]
            if most_common[1] >= len(paths) * 0.5:  # 50% threshold
                patterns.append({
                    'position': i,
                    'segment': most_common[0],
                    'frequency': most_common[1],
                    'percentage': most_common[1] / len(paths)
                })
        
        return patterns
    
    def _find_date_patterns(self, paths: List[str]) -> List[Dict[str, Any]]:
        """Find date patterns in URL paths."""
        date_patterns = []
        
        for i, pattern in enumerate(self.compiled_date_patterns):
            matches = []
            for path in paths:
                match = pattern.search(path)
                if match:
                    matches.append(match.groups())
            
            if matches:
                date_patterns.append({
                    'pattern': self.date_patterns[i],
                    'matches': len(matches),
                    'percentage': len(matches) / len(paths),
                    'examples': matches[:5]  # First 5 examples
                })
        
        # Sort by frequency
        date_patterns.sort(key=lambda x: x['matches'], reverse=True)
        return date_patterns
    
    def _find_category_patterns(self, paths: List[str]) -> List[Dict[str, Any]]:
        """Find category patterns in URL paths."""
        category_patterns = []
        
        for indicator in self.category_indicators:
            matches = [path for path in paths if indicator in path.lower()]
            
            if matches:
                category_patterns.append({
                    'category': indicator,
                    'matches': len(matches),
                    'percentage': len(matches) / len(paths),
                    'examples': matches[:3]
                })
        
        # Sort by frequency
        category_patterns.sort(key=lambda x: x['matches'], reverse=True)
        return category_patterns
    
    def _find_id_patterns(self, paths: List[str]) -> List[Dict[str, Any]]:
        """Find ID patterns in URL paths."""
        id_patterns = []
        
        # Different ID patterns to look for
        patterns = [
            (r'/(\d{3,})(?:/|$)', 'numeric_id'),
            (r'/id-(\d+)', 'prefixed_numeric_id'),
            (r'/(\d+)-', 'numeric_prefix'),
            (r'/([a-z0-9]{8,})', 'long_alphanumeric'),
            (r'/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})', 'uuid')
        ]
        
        for pattern_str, pattern_name in patterns:
            pattern = re.compile(pattern_str, re.IGNORECASE)
            matches = []
            
            for path in paths:
                match = pattern.search(path)
                if match:
                    matches.append(match.group(1))
            
            if matches:
                id_patterns.append({
                    'pattern_name': pattern_name,
                    'pattern': pattern_str,
                    'matches': len(matches),
                    'percentage': len(matches) / len(paths),
                    'examples': matches[:5]
                })
        
        # Sort by frequency
        id_patterns.sort(key=lambda x: x['matches'], reverse=True)
        return id_patterns
    
    def _find_common_prefixes(self, paths: List[str]) -> List[str]:
        """Find common path prefixes."""
        if not paths:
            return []
        
        # Find longest common prefix
        common_prefixes = []
        
        # Sort paths to make comparison easier
        sorted_paths = sorted(paths)
        
        if len(sorted_paths) < 2:
            return common_prefixes
        
        # Find common prefix between first and last (after sorting)
        first = sorted_paths[0]
        last = sorted_paths[-1]
        
        common = ""
        for i in range(min(len(first), len(last))):
            if first[i] == last[i]:
                common += first[i]
            else:
                break
        
        # Split by '/' and find meaningful prefixes
        if common and len(common) > 1:
            prefix_parts = common.rstrip('/').split('/')
            if len(prefix_parts) > 1:
                common_prefixes.append('/'.join(prefix_parts))
        
        return common_prefixes
    
    def _find_common_suffixes(self, paths: List[str]) -> List[str]:
        """Find common path suffixes."""
        suffixes = []
        
        # Count file extensions
        extensions = Counter()
        for path in paths:
            if '.' in path:
                ext = path.split('.')[-1].lower()
                if len(ext) <= 5:  # Reasonable extension length
                    extensions[ext] += 1
        
        # Add common extensions
        for ext, count in extensions.most_common(3):
            if count >= len(paths) * 0.1:  # At least 10% of URLs
                suffixes.append(f'.{ext}')
        
        return suffixes
    
    def _analyze_url_structure(self, paths: List[str]) -> Dict[str, Any]:
        """Analyze overall URL structure."""
        if not paths:
            return {}
        
        # Calculate average path depth
        depths = [len([s for s in path.split('/') if s]) for path in paths]
        avg_depth = sum(depths) / len(depths) if depths else 0
        
        # Find most common depth
        depth_counter = Counter(depths)
        most_common_depth = depth_counter.most_common(1)[0] if depth_counter else (0, 0)
        
        # Analyze path lengths
        lengths = [len(path) for path in paths]
        avg_length = sum(lengths) / len(lengths) if lengths else 0
        
        return {
            'average_depth': avg_depth,
            'most_common_depth': most_common_depth[0],
            'depth_consistency': most_common_depth[1] / len(paths),
            'average_length': avg_length,
            'min_length': min(lengths) if lengths else 0,
            'max_length': max(lengths) if lengths else 0
        }
    
    def _generate_date_based_urls(self, base_url: str, analysis: Dict[str, Any],
                                 date_range: int) -> List[str]:
        """Generate URLs based on discovered date patterns."""
        urls = []
        
        if not analysis or 'date_patterns' not in analysis:
            return urls
        
        date_patterns = analysis['date_patterns']
        if not date_patterns:
            return urls
        
        # Use the most common date pattern
        most_common_pattern = date_patterns[0]
        pattern_template = most_common_pattern['pattern']
        
        # Generate URLs for recent dates
        today = datetime.now()
        
        for days_back in range(date_range):
            date = today - timedelta(days=days_back)
            
            # Try different date format variations
            date_variations = [
                (date.year, date.month, date.day),
                (date.year, date.month),
                (date.year,)
            ]
            
            for date_parts in date_variations:
                # Try to construct URL based on pattern
                if len(date_parts) == 3:
                    date_paths = [
                        f'/{date_parts[0]}/{date_parts[1]:02d}/{date_parts[2]:02d}/',
                        f'/{date_parts[0]}-{date_parts[1]:02d}-{date_parts[2]:02d}/',
                        f'/{date_parts[0]}_{date_parts[1]:02d}_{date_parts[2]:02d}/'
                    ]
                elif len(date_parts) == 2:
                    date_paths = [
                        f'/{date_parts[0]}/{date_parts[1]:02d}/',
                        f'/{date_parts[0]}-{date_parts[1]:02d}/'
                    ]
                else:
                    date_paths = [f'/{date_parts[0]}/']
                
                for date_path in date_paths:
                    # Combine with common prefixes from analysis
                    if 'common_prefixes' in analysis:
                        for prefix in analysis['common_prefixes']:
                            url = urljoin(base_url, prefix + date_path)
                            urls.append(url)
                    else:
                        url = urljoin(base_url, date_path)
                        urls.append(url)
        
        return urls
    
    def _generate_category_based_urls(self, base_url: str, analysis: Dict[str, Any]) -> List[str]:
        """Generate URLs based on discovered category patterns."""
        urls = []
        
        if not analysis or 'category_patterns' not in analysis:
            return urls
        
        category_patterns = analysis['category_patterns']
        
        for category_info in category_patterns[:5]:  # Top 5 categories
            category = category_info['category']
            
            # Generate variations
            category_paths = [
                f'/category/{category}/',
                f'/tag/{category}/',
                f'/{category}/',
                f'/topics/{category}/',
                f'/section/{category}/'
            ]
            
            for path in category_paths:
                url = urljoin(base_url, path)
                urls.append(url)
        
        return urls
    
    def _generate_id_based_urls(self, base_url: str, analysis: Dict[str, Any]) -> List[str]:
        """Generate URLs based on discovered ID patterns."""
        urls = []
        
        if not analysis or 'id_patterns' not in analysis:
            return urls
        
        id_patterns = analysis['id_patterns']
        
        for id_info in id_patterns:
            if id_info['pattern_name'] == 'numeric_id':
                # Generate some recent numeric IDs
                examples = id_info.get('examples', [])
                if examples:
                    # Try to find the pattern in existing IDs
                    numeric_ids = [int(ex) for ex in examples if ex.isdigit()]
                    if numeric_ids:
                        max_id = max(numeric_ids)
                        # Generate URLs with recent IDs
                        for i in range(max(1, max_id - 50), max_id + 10):
                            url = urljoin(base_url, f'/{i}/')
                            urls.append(url)
                            url = urljoin(base_url, f'/article/{i}/')
                            urls.append(url)
                            url = urljoin(base_url, f'/post/{i}/')
                            urls.append(url)
        
        return urls[:50]  # Limit generated ID URLs
    
    def _generate_pattern_based_urls(self, base_url: str, analysis: Dict[str, Any]) -> List[str]:
        """Generate URLs based on discovered structural patterns."""
        urls = []
        
        if not analysis or 'path_patterns' not in analysis:
            return urls
        
        path_patterns = analysis['path_patterns']
        
        # Generate URLs based on common path structures
        for pattern_info in path_patterns:
            segment = pattern_info['segment']
            position = pattern_info['position']
            
            # Generate variations with article indicators
            for indicator in self.article_indicators[:3]:  # Top 3 indicators
                if position == 0:  # First segment
                    url = urljoin(base_url, f'/{segment}/{indicator}/')
                    urls.append(url)
                else:
                    url = urljoin(base_url, f'/{indicator}/{segment}/')
                    urls.append(url)
        
        return urls
    
    def get_domain_patterns(self, domain: str) -> Optional[Dict[str, Any]]:
        """Get cached patterns for a domain."""
        return self.domain_patterns.get(domain)
    
    def clear_cache(self):
        """Clear cached domain patterns."""
        self.domain_patterns.clear()
        logger.info("Cleared URL patterns cache")