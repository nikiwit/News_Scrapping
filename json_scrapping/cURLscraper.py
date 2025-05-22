import uncurl
import sys
import re
import os
from urllib.parse import urlparse

def extract_url(curl_command):
    """Extract the URL from the cURL command."""
    url_match = re.search(r"curl\s+'([^']+)'", curl_command)
    if not url_match:
        url_match = re.search(r'curl\s+"([^"]+)"', curl_command)
    if not url_match:
        url_match = re.search(r'curl\s+([^\s]+)', curl_command)
    
    if url_match:
        return url_match.group(1)
    return None

def generate_filename(url, curl_command=None):
    """Generate a filename based on the domain of the URL or context clues."""
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.replace('www.', '')
    
    # Special case: If it's an AWS S3 URL, try to get the actual service name from Referer
    if 'amazonaws.com' in domain and curl_command:
        import re
        referer_match = re.search(r"Referer['\"]?\s*:\s*['\"]?https?://([^/'\"]+)", curl_command)
        if referer_match:
            referer_domain = referer_match.group(1)
            referer_parts = referer_domain.replace('www.', '').split('.')
            if len(referer_parts) >= 2:
                # Extract service name from referer (e.g., apspace from apspace.apu.edu.my)
                if len(referer_parts) >= 3 and referer_parts[-2] in ['edu', 'gov', 'co']:
                    website_name = referer_parts[0]  # apspace from apspace.apu.edu.my
                else:
                    website_name = referer_parts[-2]  # main domain from referer
            else:
                website_name = referer_parts[0]
        else:
            # Fallback to AWS if no referer found
            website_name = "aws_content"
    else:
        # Normal domain parsing
        domain_parts = domain.split('.')
        if len(domain_parts) >= 2:
            # For URLs like apspace.apu.edu.my, use 'apspace'
            # For URLs like api.github.com, use 'github'
            if len(domain_parts) >= 3 and domain_parts[-2] in ['edu', 'gov', 'co']:
                website_name = domain_parts[-3]  # apu from apu.edu.my
            else:
                website_name = domain_parts[-2]  # github from api.github.com
        else:
            website_name = domain_parts[0]
    
    return f"{website_name}_scraper.py"

def clean_curl_command(curl_command):
    """Clean and fix common cURL command issues."""
    import re
    
    # Split by lines and clean each one
    lines = curl_command.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Remove trailing backslashes
        if line.endswith(' \\'):
            line = line[:-2].strip()
            
        # Fix malformed headers
        if line.startswith('-H '):
            # Extract the header content between quotes
            header_match = re.search(r"-H\s+['\"]([^'\"]+)['\"]", line)
            if header_match:
                header_content = header_match.group(1)
                
                # Case 1: x-refresh; (ends with semicolon, no colon)
                if header_content.endswith(';') and ':' not in header_content:
                    header_name = header_content.replace(';', '')
                    line = f"-H '{header_name}: true'"
                    print(f"🔧 Fixed header: {header_content} → {header_name}: true")
                
                # Case 2: Headers without colons (but not ending with ;)
                elif ':' not in header_content and not header_content.endswith(';'):
                    print(f"⚠️  Skipping malformed header: {header_content}")
                    continue
                    
                # Case 3: Fix ?0 values
                elif '?0' in header_content:
                    fixed_content = header_content.replace('?0', '0')
                    line = f"-H '{fixed_content}'"
                    print(f"🔧 Fixed header: {header_content} → {fixed_content}")
        
        cleaned_lines.append(line)
    
    return ' '.join(cleaned_lines)

def convert_curl_to_python(curl_command):
    """Convert the cURL command to Python code using uncurl."""
    try:
        # Clean the command first
        cleaned_command = clean_curl_command(curl_command)
        cleaned_command = cleaned_command.replace('\\', '').replace('\n', ' ')
        
        print(f"🔧 Cleaned cURL command for parsing...")
        context = uncurl.parse_context(cleaned_command)

        uses_ordereddict = "OrderedDict" in str(context.headers)

        imports = "import requests\nimport json\nimport os\n"
        if uses_ordereddict:
            imports += "from collections import OrderedDict\n"
        imports += "\n"

        request_block = f"""def main():
    try:
        response = requests.request(
            method="{context.method.upper()}",
            url="{context.url}",
            headers={context.headers},
            cookies={context.cookies},
            data={repr(context.data)},
            auth={context.auth},
            verify=True,
            timeout=30
        )
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ Data fetched successfully!")
                
                # Save JSON data to file in same folder as script
                script_dir = os.path.dirname(os.path.abspath(__file__))
                script_name = os.path.splitext(os.path.basename(__file__))[0]
                json_filename = os.path.join(script_dir, f"{{script_name}}.json")
                
                with open(json_filename, 'w', encoding='utf-8') as json_file:
                    json.dump(data, json_file, indent=4, ensure_ascii=False)
                
                print(f"💾 Data saved to '{{os.path.basename(json_filename)}}'")
                print(f"📁 Location: {{script_dir}}")
                
                # Show data summary instead of full JSON
                if isinstance(data, dict):
                    print(f"📊 Summary: Object with {{len(data)}} keys")
                elif isinstance(data, list):
                    print(f"📊 Summary: Array with {{len(data)}} items")
                else:
                    print(f"📊 Summary: {{type(data).__name__}} data")
                
            except json.JSONDecodeError:
                print("❌ Failed to decode JSON response.")
                print("Response content preview:", response.text[:100])
                
                # Save as text file for inspection
                script_dir = os.path.dirname(os.path.abspath(__file__))
                script_name = os.path.splitext(os.path.basename(__file__))[0]
                txt_filename = os.path.join(script_dir, f"{{script_name}}_response.txt")
                
                with open(txt_filename, 'w', encoding='utf-8') as txt_file:
                    txt_file.write(response.text)
                
                print(f"📄 Response saved as text: {{os.path.basename(txt_filename)}}")
                
        elif response.status_code == 403:
            print("🚫 Access Forbidden (403)")
            print("💡 The request may need additional authentication or cookies")
        else:
            print(f"❌ Request failed with status code {{response.status_code}}")
            print(f"Response preview: {{response.text[:100]}}")
            
    except requests.RequestException as e:
        print(f"❌ Request error: {{e}}")
    except Exception as e:
        print(f"❌ Unexpected error: {{e}}")

if __name__ == "__main__":
    main()
"""

        return imports + request_block

    except Exception as e:
        return f"""# Error parsing cURL command: {e}
# 
# The cURL command might have formatting issues.
# Common problems:
# 1. Malformed headers (missing colons)
# 2. Special characters in values
# 3. Incomplete escape sequences
#
# Try cleaning up the cURL command manually, or
# regenerate it from your browser's developer tools.

import requests
import json
import os

def main():
    print("❌ Could not parse the cURL command automatically.")
    print("💡 Please check the cURL format and try again.")
    
if __name__ == "__main__":
    main()
"""

def main():
    print("📋 cURL to Python Script Generator")
    print("Enter your cURL command (end with an empty line):")
    
    lines = []
    while True:
        try:
            line = input()
            if not line.strip():
                break
            lines.append(line.rstrip())
        except (EOFError, KeyboardInterrupt):
            print("\n❌ Input cancelled.")
            return

    if not lines:
        print("❌ No input provided.")
        return
        
    curl_command = '\n'.join(lines)
    url = extract_url(curl_command)
    
    if not url:
        print("❌ Could not extract URL from the cURL command.")
        return

    filename = generate_filename(url, curl_command)  # Pass curl_command for context
    python_code = convert_curl_to_python(curl_command)

    try:
        # Save in same directory as this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(script_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(python_code)
        
        print(f"\n✅ Python script saved as '{filename}'")
        print(f"📁 Location: {script_dir}")
        print(f"📝 Run with: python {filename}")
        
        json_name = os.path.splitext(filename)[0] + '.json'
        print(f"💾 Output will be saved as: {json_name}")
        
    except Exception as e:
        print(f"❌ Error writing file: {e}")

if __name__ == "__main__":
    main()