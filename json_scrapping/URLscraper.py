import requests
import json
import sys
import os
from urllib.parse import urlparse
import time

def is_valid_url(url):
    """Check if the provided string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def get_website_name(url):
    """Extract clean website name from URL."""
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.replace('www.', '')
    domain_parts = domain.split('.')
    
    # Handle different domain structures
    if len(domain_parts) >= 2:
        # For URLs like apspace.apu.edu.my, use 'apspace'
        # For URLs like api.github.com, use 'github'
        if len(domain_parts) >= 3 and domain_parts[-2] in ['edu', 'gov', 'co']:
            website_name = domain_parts[-3]  # apu from apu.edu.my -> but we want the subdomain
            if len(domain_parts) >= 4:
                website_name = domain_parts[0]  # apspace from apspace.apu.edu.my
            else:
                website_name = domain_parts[-3]  # fallback to main domain
        else:
            website_name = domain_parts[-2]  # github from api.github.com
    else:
        website_name = domain_parts[0]
    
    return website_name

def scrape_url_to_json(url, file_counter=1):
    """Scrape URL and save as JSON file."""
    
    # Enhanced headers to better mimic a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create a session for better handling
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        print(f"🔄 Fetching data from: {url}")
        response = session.get(url, timeout=30, allow_redirects=True)
        
        # Handle different status codes
        if response.status_code == 200:
            try:
                # Try to parse as JSON
                data = response.json()
                
                website_name = get_website_name(url)
                if file_counter == 1:
                    filename = f"{website_name}.json"
                else:
                    filename = f"{website_name}_{file_counter}.json"
                
                # Save in same directory as script
                filepath = os.path.join(script_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as json_file:
                    json.dump(data, json_file, indent=4, ensure_ascii=False)
                
                print(f"✅ JSON data saved to '{filename}'")
                print(f"📁 Location: {script_dir}")
                
                # Show data summary instead of full preview
                if isinstance(data, dict):
                    print(f"📊 Summary: Object with {len(data)} keys")
                elif isinstance(data, list):
                    print(f"📊 Summary: Array with {len(data)} items")
                else:
                    print(f"📊 Summary: {type(data).__name__} data")
                
                return filename
                
            except json.JSONDecodeError:
                # If not JSON, try to find JSON in HTML or save as text
                content = response.text
                print("⚠️  Response is not JSON format")
                
                # Check if it's a login page or error page
                if any(keyword in content.lower() for keyword in ['login', 'sign in', 'authentication', 'unauthorized']):
                    print("🔐 This appears to be a login-protected page")
                    print("💡 You may need to:")
                    print("   - Use browser developer tools to get authenticated cURL command")
                    print("   - Copy cookies from logged-in session")
                    print("   - Use the cURL scraper instead with authentication headers")
                
                # Try to extract JSON from HTML/JavaScript
                import re
                json_matches = re.findall(r'({[^{}]*(?:{[^{}]*}[^{}]*)*})', content)
                
                if json_matches:
                    print(f"🔍 Found {len(json_matches)} potential JSON objects in content")
                    
                    for i, match in enumerate(json_matches[:3]):  # Limit to first 3
                        try:
                            parsed = json.loads(match)
                            website_name = get_website_name(url)
                            filename = f"{website_name}_extracted_{i+1}.json"
                            filepath = os.path.join(script_dir, filename)
                            
                            with open(filepath, 'w', encoding='utf-8') as json_file:
                                json.dump(parsed, json_file, indent=4, ensure_ascii=False)
                            
                            print(f"✅ Extracted JSON saved to '{filename}'")
                            print(f"📁 Location: {script_dir}")
                            
                        except json.JSONDecodeError:
                            continue
                else:
                    # Save as text file for manual inspection
                    website_name = get_website_name(url)
                    filename = f"{website_name}_content.txt"
                    filepath = os.path.join(script_dir, filename)
                    
                    with open(filepath, 'w', encoding='utf-8') as txt_file:
                        txt_file.write(content)
                    
                    print(f"📄 Content saved as text file: '{filename}'")
                    print(f"📁 Location: {script_dir}")
                    print("💡 You may need to inspect the content manually for data extraction")
        
        elif response.status_code == 403:
            print(f"🚫 Access Forbidden (403) - Website is blocking the request")
            print("💡 Possible solutions:")
            print("   1. 🔐 Site requires login - use browser to login, then copy cURL command")
            print("   2. 🤖 Anti-bot protection - try using cURL scraper with browser headers")
            print("   3. 🌍 Geographic restriction - may need VPN")
            print("   4. 🔑 API key required - check if site has public API")
            print("\n📋 To get authenticated cURL:")
            print("   • Login to site in browser")
            print("   • Open Developer Tools (F12)")
            print("   • Go to Network tab")
            print("   • Go to Response")
            print("   • Reload page")
            print("   • Right-click request → Copy → Copy as cURL")
            
        elif response.status_code == 401:
            print(f"🔐 Authentication Required (401)")
            print("💡 You need to provide login credentials or API key")
            
        elif response.status_code == 429:
            print(f"⏰ Rate Limited (429) - Too many requests")
            print("💡 Wait a few minutes and try again")
            
        elif response.status_code == 404:
            print(f"❌ Page Not Found (404) - Check if URL is correct")
            
        else:
            print(f"❌ Request failed with status code {response.status_code}")
            print(f"Response preview: {response.text[:300]}")
            
    except requests.RequestException as e:
        print(f"❌ Network error: {e}")
        print("💡 Check your internet connection or try a different URL")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    finally:
        session.close()

def main():
    print("🌐 Direct URL to JSON Scraper")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        # URL provided as command line argument
        url = sys.argv[1]
    else:
        # Interactive mode
        url = input("Enter URL to scrape: ").strip()
    
    if not url:
        print("❌ No URL provided.")
        return
    
    # Add http:// if no protocol specified
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    if not is_valid_url(url):
        print("❌ Invalid URL format.")
        return
    
    # Check if user wants to scrape multiple endpoints
    urls_to_scrape = [url]
    
    while True:
        another = input("\n🔗 Add another URL from the same site? (y/n): ").strip().lower()
        if another in ['y', 'yes']:
            additional_url = input("Enter additional URL: ").strip()
            if additional_url:
                if not additional_url.startswith(('http://', 'https://')):
                    # Try to build relative URL
                    base_url = '/'.join(url.split('/')[:3])
                    if additional_url.startswith('/'):
                        additional_url = base_url + additional_url
                    else:
                        additional_url = base_url + '/' + additional_url
                urls_to_scrape.append(additional_url)
        else:
            break
    
    print(f"\n🚀 Starting scraping {len(urls_to_scrape)} URL(s)...")
    
    for i, url_to_scrape in enumerate(urls_to_scrape, 1):
        print(f"\n📥 Processing URL {i}/{len(urls_to_scrape)}")
        scrape_url_to_json(url_to_scrape, i)
        
        if i < len(urls_to_scrape):
            time.sleep(1)  # Be nice to the server
    
    print(f"\n🎉 Scraping completed!")

if __name__ == "__main__":
    main()