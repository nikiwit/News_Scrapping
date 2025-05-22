import uncurl
import sys
import re
from urllib.parse import urlparse
import os

def extract_cookies(curl_command):
    """
    Extract cookies from the cURL command.
    """
    cookie_match = re.search(r"-b\s+'([^']+)'", curl_command)
    if cookie_match:
        cookie_str = cookie_match.group(1)
        cookies = {}
        for pair in cookie_str.split(';'):
            if '=' in pair:
                key, value = pair.strip().split('=', 1)
                cookies[key.strip()] = value.strip()
        return cookies
    return {}

def extract_url(curl_command):
    """
    Extract the URL from the cURL command.
    """
    url_match = re.search(r"curl\s+'([^']+)'", curl_command)
    if url_match:
        return url_match.group(1)
    return None

def generate_filename(url):
    """
    Generate a filename based on the domain of the URL.
    """
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    domain_parts = domain.split('.')
    if len(domain_parts) >= 2:
        filename = f"{domain_parts[-2]}_scrap_json.py"
    else:
        filename = f"{domain}_scrap_json.py"
    return filename

def convert_curl_to_python(curl_command):
    """
    Convert the cURL command to Python code using uncurl.
    """
    try:
        cleaned_command = curl_command.replace('\\', '').replace('\n', ' ')
        context = uncurl.parse_context(cleaned_command)

        # Check if OrderedDict is needed
        uses_ordereddict = "OrderedDict" in str(context.headers)

        # Generate imports
        imports = "import requests\nimport json\nimport os\n"
        if uses_ordereddict:
            imports += "from collections import OrderedDict\n"
        imports += "\n"

        # Build the request call
        request_block = f"""response = requests.request(
    method="{context.method.upper()}",
    url="{context.url}",
    headers={context.headers},
    cookies={context.cookies},
    data={repr(context.data)},
    auth={context.auth},
    verify=True
)\n"""

        # Build the result handler with JSON file saving
        result_block = """
if response.status_code == 200:
    try:
        data = response.json()
        print("✅ Data fetched successfully:")
        print(json.dumps(data, indent=4))
        
        # Save JSON data to file with same name as script but .json extension
        script_name = os.path.splitext(os.path.basename(__file__))[0]
        json_filename = f"{script_name}.json"
        
        with open(json_filename, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)
        
        print(f"\\n💾 Data saved to '{json_filename}'")
        
    except json.JSONDecodeError:
        print("❌ Failed to decode JSON response.")
    except Exception as e:
        print(f"❌ Error saving JSON file: {e}")
else:
    print(f"❌ Request failed with status code {response.status_code}")
"""

        return imports + request_block + result_block

    except Exception as e:
        return f"# Error parsing cURL command: {e}"

def main():
    print("Enter your cURL command (end with an empty line):")
    lines = []
    while True:
        line = sys.stdin.readline()
        if not line.strip():
            break
        lines.append(line.rstrip())

    curl_command = '\n'.join(lines)
    url = extract_url(curl_command)
    if not url:
        print("❌ Could not extract URL from the cURL command.")
        return

    filename = generate_filename(url)
    python_code = convert_curl_to_python(curl_command)

    # Write the script to a file
    with open(filename, 'w') as file:
        file.write(python_code)

    print(f"\n✅ Python script has been saved as '{filename}'.")
    print(f"📝 When you run the script, it will save the JSON data as '{os.path.splitext(filename)[0]}.json'")

if __name__ == "__main__":
    main()