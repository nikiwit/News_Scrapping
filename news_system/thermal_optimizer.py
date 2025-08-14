#!/usr/bin/env python3
"""
Thermal-Optimized News Summarizer
Prevents Mac overheating while maintaining good performance
"""

import json
import logging
import requests
import sys
import subprocess
import psutil
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))
try:
    import config
except ImportError:
    # Fallback import path
    import os
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, parent_dir)
    import config

logger = logging.getLogger("ThermalOptimizedSummarizer")

class ThermalManager:
    """Monitors and manages system thermal state"""
    
    def __init__(self):
        self.max_cpu_temp = 85.0  # °C - throttle above this
        self.max_cpu_usage = 80.0  # % - throttle above this
        self.cooling_break_temp = 75.0  # °C - take break above this
        self.check_interval = 5.0  # seconds between checks
        self.last_check = 0
        
    def get_cpu_temperature(self) -> Optional[float]:
        """Get CPU temperature on macOS"""
        try:
            # Use powermetrics for accurate temperature on macOS
            result = subprocess.run(
                ["sudo", "powermetrics", "--samplers", "smc", "-n", "1", "-i", "1000"],
                capture_output=True, text=True, timeout=10
            )
            
            for line in result.stdout.split('\n'):
                if 'CPU die temperature' in line:
                    # Extract temperature value
                    temp_str = line.split(':')[1].strip().replace('C', '').strip()
                    return float(temp_str)
            
            # Fallback: estimate from CPU usage (rough approximation)
            cpu_usage = psutil.cpu_percent(interval=1)
            estimated_temp = 40 + (cpu_usage * 0.5)  # Very rough estimate
            return estimated_temp
            
        except Exception as e:
            logger.warning(f"Cannot read CPU temperature: {e}")
            # Use CPU usage as proxy (very rough)
            cpu_usage = psutil.cpu_percent(interval=1)
            return 40 + (cpu_usage * 0.5)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory_percent': psutil.virtual_memory().percent,
            'cpu_temp': self.get_cpu_temperature(),
            'cpu_freq': psutil.cpu_freq().current if psutil.cpu_freq() else 0,
            'timestamp': time.time()
        }
    
    def should_throttle(self) -> tuple[bool, str]:
        """Check if system should be throttled"""
        now = time.time()
        if now - self.last_check < self.check_interval:
            return False, ""
        
        self.last_check = now
        stats = self.get_system_stats()
        
        # Check temperature
        if stats['cpu_temp'] and stats['cpu_temp'] > self.max_cpu_temp:
            return True, f"CPU temperature too high: {stats['cpu_temp']:.1f}°C"
        
        # Check CPU usage
        if stats['cpu_percent'] > self.max_cpu_usage:
            return True, f"CPU usage too high: {stats['cpu_percent']:.1f}%"
        
        # Check memory
        if stats['memory_percent'] > 90:
            return True, f"Memory usage critical: {stats['memory_percent']:.1f}%"
        
        return False, ""
    
    def should_take_cooling_break(self) -> tuple[bool, Dict[str, Any]]:
        """Check if system needs a cooling break"""
        stats = self.get_system_stats()
        
        reasons = []
        if stats['cpu_temp'] and stats['cpu_temp'] > self.cooling_break_temp:
            reasons.append(f"Temperature: {stats['cpu_temp']:.1f}°C")
        
        if stats['cpu_percent'] > 70:
            reasons.append(f"CPU: {stats['cpu_percent']:.1f}%")
        
        if stats['memory_percent'] > 85:
            reasons.append(f"Memory: {stats['memory_percent']:.1f}%")
        
        return len(reasons) > 0, {
            'stats': stats,
            'reasons': reasons
        }
    
    def cooling_break(self, duration: float = 30.0, reason: str = ""):
        """Take a cooling break with progress indication"""
        print(f"    🌡️  Cooling break: {reason}")
        print(f"    ❄️  Waiting {duration:.0f}s for system to cool...")
        
        start_time = time.time()
        while time.time() - start_time < duration:
            elapsed = time.time() - start_time
            remaining = duration - elapsed
            
            # Update progress bar
            progress = elapsed / duration
            bar_length = 20
            filled_length = int(bar_length * progress)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            
            # Get current stats
            stats = self.get_system_stats()
            temp_str = f"{stats['cpu_temp']:.1f}°C" if stats['cpu_temp'] else "N/A"
            cpu_str = f"{stats['cpu_percent']:.1f}%"
            
            print(f"\r    ❄️  Cooling: {bar} {progress*100:6.1f}% | Temp: {temp_str} | CPU: {cpu_str} | {remaining:.0f}s left", end="")
            time.sleep(1)
        
        print("\n    ✅ Cooling break complete")


class OptimizedLlamaSummarizer:
    """Thermal-optimized version of LlamaNewsSummarizer"""
    
    def __init__(self, ollama_url="http://localhost:11434", model="llama3.1:8b"):
        self.ollama_url = ollama_url.rstrip('/')
        self.model = model
        self.thermal_manager = ThermalManager()
        
        # Conservative settings to prevent overheating
        self.max_context_tokens = 100000  # Reduced from 120K
        self.max_articles_per_batch = 8   # Reduced from 20
        self.base_delay_between_calls = 2.0  # Base delay between API calls
        self.adaptive_delay = 2.0  # Current adaptive delay
        
        # Configure for thermal optimization
        self._configure_thermal_optimization()
        self._test_connection()
        
    def _configure_thermal_optimization(self):
        """Configure Ollama for thermal optimization"""
        import os
        import platform
        
        if platform.system() == 'Darwin':
            # Conservative GPU settings to prevent overheating
            os.environ['OLLAMA_GPU_LAYERS'] = '20'  # Use only 20 GPU layers (vs -1)
            os.environ['OLLAMA_KEEP_ALIVE'] = '5m'   # Reduced keep-alive time
            os.environ['OLLAMA_NUM_THREAD'] = '4'    # Limit to 4 threads (vs 8)
            os.environ['PYTORCH_MPS_HIGH_WATERMARK_RATIO'] = '0.6'  # Conservative memory
            
            print("🌡️  Thermal optimization configured:")
            print("   - GPU Layers: 20 (conservative)")
            print("   - Threads: 4 (thermal-limited)")
            print("   - Memory: Conservative usage")
            print("   - Keep Alive: 5 minutes")
        
    def _test_connection(self):
        """Test connection to Ollama"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = [model['name'] for model in response.json().get('models', [])]
                if self.model in models:
                    print(f"✅ Connected to Ollama. Model {self.model} available.")
                else:
                    print(f"⚠️  Model {self.model} not found. Run: ollama pull {self.model}")
            else:
                print(f"❌ Failed to connect to Ollama at {self.ollama_url}")
        except Exception as e:
            print(f"❌ Error connecting to Ollama: {e}")
    
    def _estimate_tokens(self, text: str) -> int:
        """Conservative token estimation"""
        return len(text) // 3
    
    def _adaptive_delay_management(self, processing_time: float, error_occurred: bool = False):
        """Dynamically adjust delays based on system performance"""
        if error_occurred:
            self.adaptive_delay = min(self.adaptive_delay * 1.5, 10.0)
            print(f"    ⚠️  Increased delay to {self.adaptive_delay:.1f}s due to error")
        elif processing_time > 30:
            self.adaptive_delay = min(self.adaptive_delay * 1.2, 8.0)
            print(f"    🐌 Increased delay to {self.adaptive_delay:.1f}s (slow processing)")
        elif processing_time < 10 and self.adaptive_delay > self.base_delay_between_calls:
            self.adaptive_delay = max(self.adaptive_delay * 0.9, self.base_delay_between_calls)
        
        # Apply thermal throttling
        should_throttle, reason = self.thermal_manager.should_throttle()
        if should_throttle:
            throttle_delay = self.adaptive_delay * 2
            print(f"    🌡️  Thermal throttling: {reason}")
            time.sleep(throttle_delay)
        else:
            time.sleep(self.adaptive_delay)
    
    def _call_ollama_with_thermal_management(self, prompt: str, max_tokens: int = 4000, article_title: str = "") -> Optional[str]:
        """Call Ollama with thermal management and detailed progress"""
        try:
            # Pre-call thermal check
            should_throttle, reason = self.thermal_manager.should_throttle()
            if should_throttle:
                print(f"    🌡️  Pre-call throttling: {reason}")
                time.sleep(5.0)
            
            # Prepare request data with thermal-optimized settings
            data = {
                "model": self.model,
                "prompt": prompt,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "stop": ["</s>", "<|end|>"],
                    "num_gpu": 20,  # Conservative GPU usage
                    "num_thread": 4,  # Thermal-limited threads
                    "repeat_penalty": 1.1,
                    "use_mlock": True,
                },
                "stream": False,
                "keep_alive": "5m"
            }
            
            # Show what we're processing
            if article_title:
                display_title = article_title[:50] + "..." if len(article_title) > 50 else article_title
                print(f"    📄 Processing: {display_title}")
            
            start_time = time.time()
            
            # Make the API call with progress indication
            print(f"    🦙 Sending to Llama 3.1:8B ({self._estimate_tokens(prompt)} tokens)...")
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=data,
                timeout=300
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '').strip()
                
                # Show processing stats
                words_per_sec = len(response_text.split()) / processing_time if processing_time > 0 else 0
                print(f"    ✅ Complete: {processing_time:.1f}s ({words_per_sec:.1f} words/sec)")
                
                # Manage adaptive delays based on performance
                self._adaptive_delay_management(processing_time, False)
                
                return response_text
            else:
                print(f"    ❌ API Error: {response.status_code}")
                self._adaptive_delay_management(processing_time, True)
                return None
                
        except Exception as e:
            print(f"    ❌ Exception: {str(e)[:50]}...")
            self._adaptive_delay_management(0, True)
            return None
    
    def _create_single_prompt(self, article: Dict[str, Any]) -> str:
        """Create prompt for single article"""
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
    
    def _print_article_progress(self, current: int, total: int, article_title: str, start_time: float):
        """Print detailed per-article progress"""
        percent = 100.0 * current / total
        bar_length = 25
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
        
        # Truncate title
        display_title = article_title[:45] + "..." if len(article_title) > 45 else article_title
        
        # System stats
        stats = self.thermal_manager.get_system_stats()
        temp_str = f"{stats['cpu_temp']:.1f}°C" if stats['cpu_temp'] else "N/A"
        cpu_str = f"{stats['cpu_percent']:.1f}%"
        
        progress_line = f"\r📊 {bar} {percent:5.1f}% ({current}/{total}) | {eta_str} | Temp: {temp_str} | CPU: {cpu_str}"
        
        # Clear line and print
        print('\033[K', end='')  # Clear line
        print(progress_line, end='')
        
        if current == total:
            print()  # New line when complete
    
    def summarize_articles_individually_with_thermal_management(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Summarize articles individually with thermal management and detailed progress"""
        results = []
        start_time = time.time()
        
        print(f"🚀 Starting thermal-optimized summarization of {len(articles)} articles")
        print(f"🌡️  Monitoring: CPU temp, usage, memory")
        print(f"⚙️  Settings: {self.max_articles_per_batch} articles/batch, {self.adaptive_delay:.1f}s delays")
        print()
        
        for i, article in enumerate(articles, 1):
            title = article.get('title', 'Untitled')
            
            # Update progress bar with article title
            self._print_article_progress(i-1, len(articles), title, start_time)
            
            # Check if we need a cooling break
            needs_break, break_info = self.thermal_manager.should_take_cooling_break()
            if needs_break and i > 1:  # Don't break on first article
                print()  # New line after progress bar
                reasons = ", ".join(break_info['reasons'])
                self.thermal_manager.cooling_break(30.0, reasons)
                print()  # Space after cooling break
            
            # Process the article
            prompt = self._create_single_prompt(article)
            response = self._call_ollama_with_thermal_management(prompt, max_tokens=1000, article_title=title)
            
            if response:
                result = {
                    "original_article": article,
                    "summary": response,
                    "key_points": [],
                    "generated_at": datetime.now().isoformat(),
                    "model_used": self.model,
                    "processing_method": "thermal_optimized_individual"
                }
                results.append(result)
                
                # Show quick summary
                summary_preview = response[:80] + "..." if len(response) > 80 else response
                print(f"    ✅ Summary: {summary_preview}")
            else:
                print(f"    ❌ Failed to summarize: {title[:50]}...")
                # Add fallback result
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
            
            print()  # Space between articles
        
        # Final progress update
        self._print_article_progress(len(articles), len(articles), "Complete!", start_time)
        
        total_time = time.time() - start_time
        success_rate = (len([r for r in results if r.get('processing_method') != 'failed']) / len(results)) * 100
        
        print(f"\n🎉 Summarization complete!")
        print(f"   ⏱️  Total time: {total_time/60:.1f} minutes")
        print(f"   ✅ Success rate: {success_rate:.1f}%")
        print(f"   📊 Average: {total_time/len(articles):.1f}s per article")
        
        return results
    
    def process_multiple_directories(self, data_dirs: List[Path], output_file: Optional[Path] = None) -> List[Dict[str, Any]]:
        """Process articles from multiple directories with thermal optimization"""
        print(f"📁 Loading articles from {len(data_dirs)} directories...")
        
        # Find all article files
        all_article_files = []
        for data_dir in data_dirs:
            article_files = list(data_dir.glob("**/extracted_*.json"))
            all_article_files.extend(article_files)
        
        if not all_article_files:
            print("❌ No article files found")
            return []
        
        print(f"📄 Found {len(all_article_files)} article files")
        
        # Load all articles with progress
        articles = []
        print("📖 Loading articles...")
        for i, file_path in enumerate(all_article_files, 1):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    article = json.load(f)
                    articles.append(article)
                
                # Simple loading progress
                if i % 10 == 0 or i == len(all_article_files):
                    print(f"    📖 Loaded {i}/{len(all_article_files)} files...")
                    
            except Exception as e:
                print(f"    ❌ Error loading {file_path.name}: {e}")
        
        if not articles:
            print("❌ No valid articles loaded")
            return []
        
        print(f"✅ Loaded {len(articles)} articles successfully")
        print()
        
        # Process articles with thermal management
        results = self.summarize_articles_individually_with_thermal_management(articles)
        
        # Save results
        if output_file:
            self._save_results(results, output_file)
            print(f"💾 Results saved to: {output_file}")
            print(f"📄 Markdown version: {output_file.with_suffix('.md')}")
        
        return results
    
    def _save_results(self, results: List[Dict[str, Any]], output_file: Path):
        """Save results with thermal optimization metadata"""
        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Add thermal optimization metadata
            output_data = {
                "generated_at": datetime.now().isoformat(),
                "model_used": self.model,
                "processing_method": "thermal_optimized",
                "total_articles": len(results),
                "success_count": len([r for r in results if r.get('processing_method') != 'failed']),
                "thermal_settings": {
                    "max_articles_per_batch": self.max_articles_per_batch,
                    "adaptive_delay": self.adaptive_delay,
                    "thermal_monitoring": True
                },
                "summaries": results
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            # Create markdown version
            self._create_markdown_summary(results, output_file.with_suffix('.md'))
            
        except Exception as e:
            print(f"❌ Error saving results: {e}")
    
    def _create_markdown_summary(self, results: List[Dict[str, Any]], md_file: Path):
        """Create markdown summary with thermal optimization notes"""
        try:
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(f"# 🌡️ Thermal-Optimized News Summary\n\n")
                f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  \n")
                f.write(f"**Model:** {self.model}  \n")
                f.write(f"**Total Articles:** {len(results)}  \n")
                f.write(f"**Processing:** Thermal-optimized with cooling breaks  \n\n")
                
                success_count = len([r for r in results if r.get('processing_method') != 'failed'])
                f.write(f"**Success Rate:** {(success_count/len(results)*100):.1f}% ({success_count}/{len(results)})  \n\n")
                
                for i, result in enumerate(results, 1):
                    original = result['original_article']
                    f.write(f"## {i}. {original.get('title', 'Untitled')}\n\n")
                    f.write(f"**Source:** {original.get('source', 'Unknown')}  \n")
                    f.write(f"**Category:** {original.get('category', 'news')}  \n")
                    f.write(f"**URL:** [{original.get('url', '')}]({original.get('url', '')})  \n")
                    f.write(f"**Processing:** {result.get('processing_method', 'unknown')}  \n\n")
                    f.write(f"**Summary:**  \n{result['summary']}\n\n")
                    
                    if result.get('error'):
                        f.write(f"**Error:** {result['error']}  \n\n")
                    
                    f.write("---\n\n")
        
        except Exception as e:
            print(f"❌ Error creating markdown: {e}")


def main():
    """Main function with thermal optimization"""
    print("🌡️ Thermal-Optimized Llama News Summarizer")
    print("=" * 50)
    print("Features:")
    print("  🌡️  Real-time thermal monitoring")
    print("  ❄️  Automatic cooling breaks")
    print("  📊 Per-article progress tracking")
    print("  ⚙️  Adaptive performance tuning")
    print("  🛡️  System protection from overheating")
    print("=" * 50)
    
    # Check if running with sudo (needed for accurate temperature monitoring)
    import os
    if os.geteuid() != 0:
        print("⚠️  Running without sudo - temperature monitoring will be limited")
        print("   For accurate thermal monitoring, run: sudo python thermal_optimizer.py")
        print()
    
    # Initialize thermal-optimized summarizer
    print("🔧 Initializing thermal-optimized summarizer...")
    summarizer = OptimizedLlamaSummarizer()
    
    # Find latest data directory (same logic as original script)
    data_base = config.DATA_DIR
    if not data_base.exists():
        print(f"❌ Data directory not found: {data_base}")
        return 1
    
    # Get latest date directory
    date_dirs = []
    for d in data_base.iterdir():
        if d.is_dir() and d.name.count('_') == 2 and all(part.isdigit() for part in d.name.split('_')):
            date_dirs.append(d)
    
    date_dirs = sorted(date_dirs, reverse=True)
    if not date_dirs:
        print(f"❌ No date directories found in {data_base}")
        return 1
    
    latest_date = date_dirs[0]
    print(f"📅 Using latest date: {latest_date.name}")
    
    # Get all time directories
    time_dirs = []
    for d in latest_date.iterdir():
        if d.is_dir() and d.name.isdigit() and len(d.name) >= 3:
            time_dirs.append(d)
    
    time_dirs = sorted(time_dirs, reverse=True)
    if not time_dirs:
        print(f"❌ No time directories found in {latest_date}")
        return 1
    
    print(f"⏰ Found {len(time_dirs)} time directories")
    
    # Process timestamps from the latest scraping session
    # A scraping session can span multiple timestamps (e.g., 1038, 1039)
    latest_time = int(time_dirs[0].name)
    session_time_dirs = []
    
    for time_dir in time_dirs:
        time_value = int(time_dir.name)
        # Include timestamps within 10 minutes of the latest
        if latest_time - time_value <= 10:  # 10 minute window
            session_time_dirs.append(time_dir)
    
    print(f"🕐 Processing latest session timestamps: {[d.name for d in session_time_dirs]}")
    
    # Collect articles from all timestamps in the latest session
    all_time_dirs = []
    total_article_count = 0
    
    for time_dir in session_time_dirs:
        article_count_in_dir = 0
        categories_found = []
        
        for category_dir in time_dir.iterdir():
            if category_dir.is_dir():
                articles = list(category_dir.glob("extracted_*.json"))
                if articles:
                    article_count_in_dir += len(articles)
                    categories_found.append(f"{category_dir.name}({len(articles)})")
        
        if article_count_in_dir > 0:
            all_time_dirs.append(time_dir)
            total_article_count += article_count_in_dir
            print(f"  ⏰ {time_dir.name}: {article_count_in_dir} articles [{', '.join(categories_found)}]")
    
    if total_article_count == 0:
        print("❌ No articles found")
        return 1
    
    print(f"📊 Total articles to process: {total_article_count}")
    print(f"💡 Note: Only processing latest session ({len(all_time_dirs)} timestamps) to avoid re-summarizing old articles")
    print()
    
    # Process with thermal optimization
    output_file = config.DATA_DIR / f"thermal_optimized_summaries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    results = summarizer.process_multiple_directories(all_time_dirs, output_file)
    
    if results:
        print(f"\n🎉 Processing complete!")
        print(f"✅ Successfully processed {len(results)} articles")
        print(f"💾 Results saved to: {output_file}")
        print(f"📄 Markdown summary: {output_file.with_suffix('.md')}")
        
        # Show quick preview
        print(f"\n📰 Preview of summaries:")
        for i, result in enumerate(results[:3], 1):
            article = result['original_article']
            title = article.get('title', 'Untitled')[:60]
            summary = result['summary'][:100]
            print(f"{i}. {title}...")
            print(f"   Summary: {summary}...")
            print(f"   URL: {article.get('url', '')}")
            print()
        
        if len(results) > 3:
            print(f"... and {len(results) - 3} more articles")
    else:
        print("❌ No articles processed")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())