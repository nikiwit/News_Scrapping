#!/usr/bin/env python3
"""
Llama 3.1:8B Summarizer for News Articles
Uses Ollama to process scraped articles with context window management
"""

import json
import logging
import requests
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import time

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
try:
    import config
except ImportError:
    # Fallback import path
    import os
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, parent_dir)
    import config

logger = logging.getLogger("LlamaSummarizer")

class LlamaNewsSummarizer:
    """
    Summarize news articles using Llama 3.1:8B via Ollama
    """
    
    def __init__(self, ollama_url="http://localhost:11434", model="llama3.1:8b"):
        """
        Initialize the Llama summarizer with macOS M2 MPS optimizations.
        
        Args:
            ollama_url (str): Ollama API endpoint
            model (str): Ollama model name
        """
        self.ollama_url = ollama_url.rstrip('/')
        self.model = model
        self.max_context_tokens = 120000  # Conservative limit for Llama 3.1:8B (128K context)
        self.max_articles_per_batch = 20   # Increased for MPS acceleration
        self.concurrent_batches = 2        # Process 2 batches concurrently on M2
        
        # Configure MPS optimizations for macOS M2
        self._configure_mps_optimizations()
        
        # Test connection
        self._test_connection()
    
    def _configure_mps_optimizations(self):
        """Configure MPS GPU acceleration optimizations for macOS M2"""
        import os
        import platform
        
        # Only apply optimizations on macOS
        if platform.system() == 'Darwin':
            # Enable MPS GPU acceleration
            os.environ['OLLAMA_GPU_LAYERS'] = '-1'  # Use all GPU layers
            os.environ['OLLAMA_KEEP_ALIVE'] = '10m'  # Keep model loaded longer
            os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'  # Enable MPS fallback
            os.environ['PYTORCH_MPS_HIGH_WATERMARK_RATIO'] = '0.0'  # Optimize memory
            
            logger.info("🚀 MPS GPU acceleration configured for macOS M2")
            logger.info("   - GPU Layers: All (-1)")
            logger.info("   - Keep Alive: 10 minutes") 
            logger.info("   - MPS Fallback: Enabled")
            logger.info("   - Memory Optimization: Enabled")
        else:
            logger.info("ℹ️  MPS optimizations skipped (not macOS)")
        
    def _test_connection(self):
        """Test connection to Ollama"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = [model['name'] for model in response.json().get('models', [])]
                if self.model in models:
                    logger.info(f"✅ Connected to Ollama. Model {self.model} is available.")
                else:
                    logger.warning(f"⚠️ Model {self.model} not found. Available models: {models}")
                    logger.info(f"To download the model, run: ollama pull {self.model}")
            else:
                logger.error(f"❌ Failed to connect to Ollama at {self.ollama_url}")
        except Exception as e:
            logger.error(f"❌ Error connecting to Ollama: {e}")
            logger.info("Make sure Ollama is running: `ollama serve`")
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimation (1 token ≈ 4 characters for English)"""
        return len(text) // 3  # Conservative estimate
    
    def _create_batch_prompt(self, articles: List[Dict[str, Any]]) -> str:
        """
        Create a prompt for batch processing multiple articles.
        
        Args:
            articles (List[Dict]): List of article data
            
        Returns:
            str: Formatted prompt
        """
        prompt = """You are a professional news summarizer. Your task is to create concise, informative summaries of news articles.

For each article provided, create a summary that:
1. Captures the key points and main message (2-3 sentences)
2. Maintains a neutral, professional tone
3. Includes the most important facts and context
4. Is engaging but not sensationalized

Format your response as a JSON array with this structure:
[
    {
        "article_id": "article_1",
        "summary": "Your concise summary here...",
        "key_points": ["point 1", "point 2", "point 3"],
        "category": "original_category",
        "original_url": "original_url_here"
    }
]

Here are the articles to summarize:

"""
        
        for i, article in enumerate(articles, 1):
            prompt += f"""
ARTICLE {i}:
ID: article_{i}
Title: {article.get('title', 'Untitled')}
Source: {article.get('source', 'Unknown')}
Category: {article.get('category', 'news')}
URL: {article.get('url', '')}
Content: {article.get('content', article.get('summary', ''))[:2000]}

---
"""
        
        prompt += "\nPlease provide summaries in the JSON format specified above."
        return prompt
    
    def _create_single_prompt(self, article: Dict[str, Any]) -> str:
        """
        Create a prompt for single article processing.
        
        Args:
            article (Dict): Article data
            
        Returns:
            str: Formatted prompt
        """
        return f"""You are a professional news summarizer. Create a concise, informative summary of this news article.

Your summary should:
1. Capture the key points and main message in 2-3 sentences
2. Maintain a neutral, professional tone  
3. Include the most important facts and context
4. Be engaging but not sensationalized

Article Details:
Title: {article.get('title', 'Untitled')}
Source: {article.get('source', 'Unknown')}
Category: {article.get('category', 'news')}
URL: {article.get('url', '')}

Content: {article.get('content', article.get('summary', ''))[:3000]}

Please provide just the summary text, nothing else."""
    
    def _call_ollama(self, prompt: str, max_tokens: int = 4000) -> Optional[str]:
        """
        Call Ollama API to generate text with MPS optimizations.
        
        Args:
            prompt (str): Input prompt
            max_tokens (int): Maximum tokens to generate
            
        Returns:
            Optional[str]: Generated text or None if failed
        """
        try:
            data = {
                "model": self.model,
                "prompt": prompt,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.3,  # Lower temperature for more consistent summaries
                    "top_p": 0.9,
                    "stop": ["</s>", "<|end|>"],
                    # MPS optimizations for macOS M2
                    "num_gpu": -1,  # Use all GPU layers
                    "num_thread": 8,  # Optimize for M2 8-core
                    "repeat_penalty": 1.1,
                    "tfs_z": 1.0,
                    "mirostat": 0,  # Disable mirostat for speed
                    "use_mlock": True,  # Lock model in memory
                    "flash_attn": True,  # Enable Flash Attention (2025 feature)
                },
                "stream": False,
                "keep_alive": "10m"  # Keep model loaded
            }
            
            # Calling Ollama API (progress shown in progress bar)
            start_time = time.time()
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=data,
                timeout=300  # 5 minute timeout for large requests
            )
            
            elapsed = time.time() - start_time
            # Response received (timing shown in progress bar)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            return None
    
    def summarize_articles_batch(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Summarize multiple articles in a single batch.
        
        Args:
            articles (List[Dict]): List of articles to summarize
            
        Returns:
            List[Dict]: Summarized articles with metadata
        """
        if not articles:
            return []
        
        # Processing batch (progress shown in progress bar)
        
        # Create batch prompt
        prompt = self._create_batch_prompt(articles)
        
        # Check if prompt is too large
        estimated_tokens = self._estimate_tokens(prompt)
        if estimated_tokens > self.max_context_tokens:
            logger.warning(f"Batch too large ({estimated_tokens} tokens), splitting...")
            # Split into smaller batches
            mid = len(articles) // 2
            batch1 = self.summarize_articles_batch(articles[:mid])
            batch2 = self.summarize_articles_batch(articles[mid:])
            return batch1 + batch2
        
        # Call Ollama
        response = self._call_ollama(prompt, max_tokens=6000)
        if not response:
            logger.error("Failed to get response from Ollama for batch")
            # Fallback to individual processing
            return self.summarize_articles_individual(articles)
        
        # Try to parse JSON response
        try:
            # Extract JSON from response (handle cases where model adds extra text)
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                summaries = json.loads(json_str)
                
                # Validate and enrich results
                results = []
                for i, summary in enumerate(summaries):
                    if i < len(articles):
                        original = articles[i]
                        result = {
                            "original_article": original,
                            "summary": summary.get('summary', ''),
                            "key_points": summary.get('key_points', []),
                            "generated_at": datetime.now().isoformat(),
                            "model_used": self.model,
                            "processing_method": "batch"
                        }
                        results.append(result)
                
                # Batch processed successfully (count shown in progress bar)
                return results
            else:
                logger.warning("Could not find valid JSON in response, falling back to individual processing")
                return self.summarize_articles_individual(articles)
                
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            logger.info("Falling back to individual article processing...")
            return self.summarize_articles_individual(articles)
    
    def _print_progress(self, current, total, prefix="Progress", start_time=None, article_title=""):
        """Print a dynamic progress bar on a single line"""
        import sys
        
        percent = 100.0 * current / total
        bar_length = 30
        filled_length = int(bar_length * current / total)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        # Calculate time estimates
        time_info = ""
        if start_time and current > 0:
            elapsed = time.time() - start_time
            avg_time = elapsed / current
            remaining = avg_time * (total - current)
            
            if remaining > 60:
                time_info = f" | ETA: {remaining/60:.1f}m"
            else:
                time_info = f" | ETA: {remaining:.0f}s"
        
        # Truncate article title
        if article_title:
            article_title = article_title[:40] + "..." if len(article_title) > 40 else article_title
            article_info = f" | {article_title}"
        else:
            article_info = ""
        
        # Create progress line
        progress_line = f"\r{prefix}: {bar} {percent:6.1f}% ({current}/{total}){time_info}{article_info}"
        
        # Clear the line and print
        sys.stdout.write('\033[K')  # Clear line
        sys.stdout.write(progress_line)
        sys.stdout.flush()
        
        # Print newline when complete
        if current == total:
            print()  # Move to next line when done

    def summarize_articles_individual(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Summarize articles individually (fallback method).
        
        Args:
            articles (List[Dict]): List of articles to summarize
            
        Returns:
            List[Dict]: Summarized articles with metadata
        """
        # Processing articles individually (progress shown in progress bar)
        results = []
        start_time = time.time()
        
        for i, article in enumerate(articles, 1):
            title = article.get('title', 'Untitled')
            
            # Update progress bar
            self._print_progress(i-1, len(articles), "Summarizing", start_time, title)
            
            prompt = self._create_single_prompt(article)
            response = self._call_ollama(prompt, max_tokens=1000)
            
            if response:
                result = {
                    "original_article": article,
                    "summary": response,
                    "key_points": [],  # Could be extracted separately if needed
                    "generated_at": datetime.now().isoformat(),
                    "model_used": self.model,
                    "processing_method": "individual"
                }
                results.append(result)
            else:
                logger.error(f"❌ Failed to summarize: {title[:30]}...")
                # Add failed result with original content
                result = {
                    "original_article": article,
                    "summary": article.get('summary', article.get('content', '')[:500]) + "...",
                    "key_points": [],
                    "generated_at": datetime.now().isoformat(),
                    "model_used": "fallback",
                    "processing_method": "failed",
                    "error": "Failed to generate summary"
                }
                results.append(result)
            
            # Small delay to be respectful to the API
            time.sleep(0.5)
        
        # Final progress update
        self._print_progress(len(articles), len(articles), "Summarizing", start_time)
        
        return results
    
    def summarize_articles_individual_with_enhanced_progress(self, articles: List[Dict[str, Any]], start_time: float) -> List[Dict[str, Any]]:
        """
        Summarize articles individually with enhanced progress tracking and thermal management.
        """
        results = []
        
        for i, article in enumerate(articles, 1):
            title = article.get('title', 'Untitled')
            
            # Update progress bar with detailed info
            self._print_enhanced_progress(i-1, len(articles), title, start_time)
            
            # Check for thermal throttling (simplified version)
            if i % 5 == 0:  # Check every 5 articles
                # Small delay to prevent overheating
                time.sleep(1.0)
            
            # Process the article
            prompt = self._create_single_prompt(article)
            
            # Show what we're processing
            print(f"    🔄 Processing article {i}/{len(articles)}: {title[:60]}...")
            
            call_start = time.time()
            response = self._call_ollama(prompt, max_tokens=1000)
            call_time = time.time() - call_start
            
            if response:
                result = {
                    "original_article": article,
                    "summary": response,
                    "key_points": [],
                    "generated_at": datetime.now().isoformat(),
                    "model_used": self.model,
                    "processing_method": "individual_enhanced"
                }
                results.append(result)
                
                # Show completion with timing
                words_per_sec = len(response.split()) / call_time if call_time > 0 else 0
                print(f"    ✅ Complete: {call_time:.1f}s ({words_per_sec:.1f} words/sec)")
            else:
                print(f"    ❌ Failed to summarize: {title[:30]}...")
                # Add failed result with original content
                result = {
                    "original_article": article,
                    "summary": article.get('summary', article.get('content', '')[:500]) + "...",
                    "key_points": [],
                    "generated_at": datetime.now().isoformat(),
                    "model_used": "fallback",
                    "processing_method": "failed",
                    "error": "Failed to generate summary"
                }
                results.append(result)
            
            # Small delay between articles
            time.sleep(0.5)
        
        # Final progress update
        self._print_enhanced_progress(len(articles), len(articles), "Complete!", start_time)
        
        total_time = time.time() - start_time
        success_rate = (len([r for r in results if r.get('processing_method') != 'failed']) / len(results)) * 100
        
        print(f"\n🎉 Processing complete!")
        print(f"   ⏱️  Total time: {total_time/60:.1f} minutes")
        print(f"   ✅ Success rate: {success_rate:.1f}%")
        print(f"   📊 Average: {total_time/len(articles):.1f}s per article")
        
        return results
    
    def _print_enhanced_progress(self, current: int, total: int, article_title: str, start_time: float):
        """Print enhanced progress bar with article info and timing"""
        percent = 100.0 * current / total
        bar_length = 30
        filled_length = int(bar_length * current / total)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        # Time calculations
        elapsed = time.time() - start_time
        if current > 0:
            avg_time = elapsed / current
            remaining_time = avg_time * (total - current)
            eta_str = f"ETA: {remaining_time/60:.1f}m" if remaining_time > 60 else f"ETA: {remaining_time:.0f}s"
        else:
            eta_str = "ETA: calculating..."
        
        # Truncate title for display
        display_title = article_title[:50] + "..." if len(article_title) > 50 else article_title
        
        # Create progress line
        progress_line = f"\r📊 {bar} {percent:5.1f}% ({current}/{total}) | {eta_str} | {display_title}"
        
        # Clear line and print
        print('\033[K', end='')  # Clear line
        print(progress_line, end='')
        
        if current == total:
            print()  # New line when complete
    
    def process_multiple_directories(self, data_dirs: List[Path], output_file: Optional[Path] = None) -> List[Dict[str, Any]]:
        """
        Process all articles from multiple data directories.
        
        Args:
            data_dirs (List[Path]): List of directories containing article JSON files
            output_file (Optional[Path]): Where to save results
            
        Returns:
            List[Dict]: All summarized articles
        """
        logger.info(f"Processing {len(data_dirs)} data directories")
        
        # Find all article files across directories
        all_article_files = []
        for data_dir in data_dirs:
            article_files = list(data_dir.glob("**/extracted_*.json"))
            all_article_files.extend(article_files)
        
        if not all_article_files:
            logger.warning(f"No article files found in any directories")
            return []
        
        logger.info(f"Found {len(all_article_files)} article files across {len(data_dirs)} directories")
        
        # Load all articles
        articles = []
        for file_path in all_article_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    article = json.load(f)
                    articles.append(article)
            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")
        
        if not articles:
            logger.warning("No valid articles loaded")
            return []
        
        logger.info(f"Loaded {len(articles)} articles")
        
        # Process using the improved batch system
        return self._process_articles_with_enhanced_progress(articles, output_file)
    
    def process_data_directory(self, data_dir: Path, output_file: Optional[Path] = None) -> List[Dict[str, Any]]:
        """
        Process all articles in a data directory.
        
        Args:
            data_dir (Path): Directory containing article JSON files
            output_file (Optional[Path]): Where to save results
            
        Returns:
            List[Dict]: All summarized articles
        """
        # Processing data directory (info shown in output)
        
        # Find all article files
        article_files = list(data_dir.glob("**/extracted_*.json"))
        if not article_files:
            logger.warning(f"No article files found in {data_dir}")
            return []
        
        # Found article files (count shown in output)
        
        # Load all articles
        articles = []
        for file_path in article_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    article = json.load(f)
                    articles.append(article)
            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")
        
        if not articles:
            logger.warning("No valid articles loaded")
            return []
        
        # Loaded articles (count shown in output)
        
        # Use enhanced progress processing
        return self._process_articles_with_enhanced_progress(articles, output_file)
    
    def _process_articles_with_enhanced_progress(self, articles: List[Dict[str, Any]], output_file: Optional[Path] = None) -> List[Dict[str, Any]]:
        """
        Process articles with enhanced progress tracking.
        
        Args:
            articles (List[Dict]): Articles to process
            output_file (Optional[Path]): Where to save results
            
        Returns:
            List[Dict]: Summarized articles
        """
        if not articles:
            return []
        
        # Process in batches with enhanced progress
        all_results = []
        batch_size = min(self.max_articles_per_batch, len(articles))
        total_batches = (len(articles) - 1) // batch_size + 1
        start_time = time.time()
        
        print(f"📊 Processing {len(articles)} articles individually for better progress tracking...")
        print(f"🚀 Using MPS GPU acceleration with thermal management")
        
        # Use individual processing with enhanced progress tracking
        all_results = self.summarize_articles_individual_with_enhanced_progress(articles, start_time)
        
        # Progress tracking is handled within the individual processing method
        
        # Save results if output file specified
        if output_file:
            self._save_results(all_results, output_file)
        
        return all_results
    
    def _process_batches_sequential(self, articles: List[Dict[str, Any]], batch_size: int, total_batches: int, start_time: float) -> List[Dict[str, Any]]:
        """Process batches sequentially (fallback method)"""
        all_results = []
        
        for i in range(0, len(articles), batch_size):
            batch_num = i // batch_size + 1
            batch = articles[i:i + batch_size]
            
            # Show current batch info
            batch_info = f"Batch {batch_num}/{total_batches} ({len(batch)} articles)"
            self._print_progress(batch_num - 1, total_batches, "Processing", start_time, batch_info)
            
            # Process batch with internal progress
            batch_start_time = time.time()
            batch_results = self._summarize_batch_with_progress(batch, batch_num, total_batches)
            batch_time = time.time() - batch_start_time
            
            all_results.extend(batch_results)
            
            # Show batch completion
            avg_time_per_article = batch_time / len(batch) if len(batch) > 0 else 0
            print(f"    ✅ Batch {batch_num} complete: {len(batch_results)}/{len(batch)} articles in {batch_time:.1f}s ({avg_time_per_article:.1f}s/article)")
        
        return all_results
    
    def _process_batches_parallel(self, articles: List[Dict[str, Any]], batch_size: int, total_batches: int, start_time: float) -> List[Dict[str, Any]]:
        """Process batches with limited parallelization for MPS GPU"""
        import concurrent.futures
        import threading
        
        all_results = []
        completed_batches = 0
        results_lock = threading.Lock()
        
        def process_batch_wrapper(batch_data):
            batch, batch_num = batch_data
            batch_start_time = time.time()
            batch_results = self._summarize_batch_with_progress(batch, batch_num, total_batches)
            batch_time = time.time() - batch_start_time
            
            with results_lock:
                nonlocal completed_batches
                completed_batches += 1
                avg_time_per_article = batch_time / len(batch) if len(batch) > 0 else 0
                print(f"    ✅ Batch {batch_num} complete: {len(batch_results)}/{len(batch)} articles in {batch_time:.1f}s ({avg_time_per_article:.1f}s/article)")
                self._print_progress(completed_batches, total_batches, "Processing", start_time, f"Completed {completed_batches}/{total_batches} batches")
            
            return batch_results, batch_num
        
        # Create batch tasks
        batch_tasks = []
        for i in range(0, len(articles), batch_size):
            batch_num = i // batch_size + 1
            batch = articles[i:i + batch_size]
            batch_tasks.append((batch, batch_num))
        
        print(f"    🔄 Starting parallel processing with max {self.concurrent_batches} concurrent batches...")
        
        # Process with limited concurrency to avoid overwhelming the GPU
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.concurrent_batches) as executor:
            # Submit tasks in smaller groups to avoid memory issues
            futures = []
            for batch_task in batch_tasks:
                future = executor.submit(process_batch_wrapper, batch_task)
                futures.append(future)
            
            # Collect results in order
            batch_results_dict = {}
            for future in concurrent.futures.as_completed(futures):
                try:
                    batch_results, batch_num = future.result()
                    batch_results_dict[batch_num] = batch_results
                except Exception as e:
                    print(f"    ❌ Batch processing error: {e}")
            
            # Combine results in order
            for batch_num in sorted(batch_results_dict.keys()):
                all_results.extend(batch_results_dict[batch_num])
        
        return all_results
    
    def _summarize_batch_with_progress(self, articles: List[Dict[str, Any]], batch_num: int, total_batches: int) -> List[Dict[str, Any]]:
        """
        Summarize a batch with internal progress tracking.
        
        Args:
            articles (List[Dict]): Articles in this batch
            batch_num (int): Current batch number
            total_batches (int): Total batches
            
        Returns:
            List[Dict]: Summarized articles
        """
        print(f"    🔄 Batch {batch_num}/{total_batches}: Preparing {len(articles)} articles for LLM...")
        
        # Create batch prompt
        prompt = self._create_batch_prompt(articles)
        
        # Check if prompt is too large
        estimated_tokens = self._estimate_tokens(prompt)
        if estimated_tokens > self.max_context_tokens:
            print(f"    ⚠️  Batch {batch_num} too large ({estimated_tokens} tokens), splitting...")
            # Split into smaller batches
            mid = len(articles) // 2
            batch1 = self._summarize_batch_with_progress(articles[:mid], f"{batch_num}a", total_batches)
            batch2 = self._summarize_batch_with_progress(articles[mid:], f"{batch_num}b", total_batches)
            return batch1 + batch2
        
        print(f"    🦙 Batch {batch_num}/{total_batches}: Calling Llama 3.1:8B ({estimated_tokens} tokens)...")
        
        # Call Ollama
        call_start = time.time()
        response = self._call_ollama(prompt, max_tokens=6000)
        call_time = time.time() - call_start
        
        if not response:
            print(f"    ❌ Batch {batch_num} failed, falling back to individual processing...")
            return self._process_articles_individually_with_progress(articles, batch_num)
        
        print(f"    📝 Batch {batch_num}/{total_batches}: Parsing response ({call_time:.1f}s)...")
        
        # Try to parse JSON response
        try:
            # Extract JSON from response (handle cases where model adds extra text)
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                summaries = json.loads(json_str)
                
                # Validate and enrich results
                results = []
                for i, summary in enumerate(summaries):
                    if i < len(articles):
                        original = articles[i]
                        result = {
                            "original_article": original,
                            "summary": summary.get('summary', ''),
                            "key_points": summary.get('key_points', []),
                            "generated_at": datetime.now().isoformat(),
                            "model_used": self.model,
                            "processing_method": "batch"
                        }
                        results.append(result)
                
                return results
            else:
                print(f"    ⚠️  Batch {batch_num}: Invalid JSON format, falling back to individual processing...")
                return self._process_articles_individually_with_progress(articles, batch_num)
                
        except json.JSONDecodeError as e:
            print(f"    ⚠️  Batch {batch_num}: JSON parse error, falling back to individual processing...")
            return self._process_articles_individually_with_progress(articles, batch_num)
    
    def _process_articles_individually_with_progress(self, articles: List[Dict[str, Any]], batch_id: str) -> List[Dict[str, Any]]:
        """
        Process articles individually with progress (fallback method).
        
        Args:
            articles (List[Dict]): Articles to process
            batch_id (str): Batch identifier for logging
            
        Returns:
            List[Dict]: Summarized articles
        """
        results = []
        
        for i, article in enumerate(articles, 1):
            title = article.get('title', 'Untitled')[:30]
            print(f"    📄 Batch {batch_id}: Processing article {i}/{len(articles)}: {title}...")
            
            prompt = self._create_single_prompt(article)
            response = self._call_ollama(prompt, max_tokens=1000)
            
            if response:
                result = {
                    "original_article": article,
                    "summary": response,
                    "key_points": [],  # Could be extracted separately if needed
                    "generated_at": datetime.now().isoformat(),
                    "model_used": self.model,
                    "processing_method": "individual"
                }
                results.append(result)
            else:
                print(f"    ❌ Failed to summarize: {title}...")
                # Add failed result with original content
                result = {
                    "original_article": article,
                    "summary": article.get('summary', article.get('content', '')[:500]) + "...",
                    "key_points": [],
                    "generated_at": datetime.now().isoformat(),
                    "model_used": "fallback",
                    "processing_method": "failed",
                    "error": "Failed to generate summary"
                }
                results.append(result)
            
            # Small delay to be respectful to the API
            time.sleep(0.5)
        
        return results
    
    def _save_results(self, results: List[Dict[str, Any]], output_file: Path):
        """Save summarized results to organized folder structure"""
        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Create a comprehensive output format with enhanced metadata
            success_count = len([r for r in results if r.get('processing_method') != 'failed'])
            output_data = {
                "session_info": {
                    "generated_at": datetime.now().isoformat(),
                    "total_articles": len(results),
                    "successful_summaries": success_count,
                    "success_rate": f"{(success_count/len(results)*100):.1f}%" if results else "0%",
                    "model_used": self.model,
                    "folder_name": output_file.parent.name
                },
                "summaries": results
            }
            
            # Save main JSON file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            # Create additional useful files in the same folder
            folder = output_file.parent
            
            # 1. Create markdown summary
            md_file = folder / "summary.md"
            self._create_markdown_summary(results, md_file)
            
            # 2. Create a simple text summary list
            txt_file = folder / "article_list.txt"
            self._create_text_list(results, txt_file)
            
            # 3. Create session info file
            info_file = folder / "session_info.json"
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(output_data["session_info"], f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
    
    def _create_text_list(self, results: List[Dict[str, Any]], txt_file: Path):
        """Create a simple text list of articles and summaries"""
        try:
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(f"News Articles Summary - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"Total Articles: {len(results)}\n")
                success_count = len([r for r in results if r.get('processing_method') != 'failed'])
                f.write(f"Successfully Summarized: {success_count}\n")
                f.write(f"Success Rate: {(success_count/len(results)*100):.1f}%\n\n")
                
                for i, result in enumerate(results, 1):
                    original = result['original_article']
                    f.write(f"{i}. {original.get('title', 'Untitled')}\n")
                    f.write(f"   Source: {original.get('source', 'Unknown')}\n")
                    f.write(f"   Category: {original.get('category', 'news')}\n")
                    f.write(f"   URL: {original.get('url', '')}\n")
                    f.write(f"   Summary: {result['summary']}\n")
                    if result.get('error'):
                        f.write(f"   Error: {result['error']}\n")
                    f.write("\n" + "-" * 60 + "\n\n")
                        
        except Exception as e:
            logger.error(f"Error creating text list: {e}")
    
    def _create_markdown_summary(self, results: List[Dict[str, Any]], md_file: Path):
        """Create a readable markdown summary"""
        try:
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(f"# News Summary - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
                f.write(f"**Total Articles:** {len(results)}  \n")
                f.write(f"**Generated by:** {self.model}  \n\n")
                
                for i, result in enumerate(results, 1):
                    original = result['original_article']
                    f.write(f"## {i}. {original.get('title', 'Untitled')}\n\n")
                    f.write(f"**Source:** {original.get('source', 'Unknown')}  \n")
                    f.write(f"**Category:** {original.get('category', 'news')}  \n")
                    f.write(f"**URL:** [{original.get('url', '')}]({original.get('url', '')})  \n\n")
                    f.write(f"**Summary:**  \n{result['summary']}\n\n")
                    
                    if result.get('key_points'):
                        f.write("**Key Points:**\n")
                        for point in result['key_points']:
                            f.write(f"- {point}\n")
                        f.write("\n")
                    
                    f.write("---\n\n")
            
            # Markdown summary saved (path shown in output)
            
        except Exception as e:
            logger.error(f"Error creating markdown summary: {e}")

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Summarize news articles using Llama 3.1:8B")
    parser.add_argument("data_dir", help="Directory containing article JSON files")
    parser.add_argument("--output", "-o", help="Output file for results")
    parser.add_argument("--model", default="llama3.1:8b", help="Ollama model to use")
    parser.add_argument("--ollama-url", default="http://localhost:11434", help="Ollama API URL")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize summarizer
    summarizer = LlamaNewsSummarizer(
        ollama_url=args.ollama_url,
        model=args.model
    )
    
    # Process directory
    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        logger.error(f"Data directory does not exist: {data_dir}")
        return 1
    
    output_file = Path(args.output) if args.output else None
    results = summarizer.process_data_directory(data_dir, output_file)
    
    print(f"\n✅ Processing complete!")
    print(f"📊 Processed {len(results)} articles")
    if output_file:
        print(f"💾 Results saved to {output_file}")
        print(f"📄 Markdown summary: {output_file.with_suffix('.md')}")
    
    return 0

if __name__ == "__main__":
    exit(main())