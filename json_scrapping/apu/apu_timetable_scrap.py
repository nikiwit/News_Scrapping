import requests
import json

headers = {
    'sec-ch-ua-platform': '"macOS"',
    'Referer': 'https://apspace.apu.edu.my/',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
    'x-refresh': '',
    'Accept': 'application/json, text/plain, */*',
    'sec-ch-ua': '"Brave";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    'sec-ch-ua-mobile': '?0',
}

url = 'https://s3-ap-southeast-1.amazonaws.com/open-ws/weektimetable'

response = requests.get(url, headers=headers)

if response.status_code == 200:
    try:
        data = response.json()
        with open('weektimetable.json', 'w') as f:
            json.dump(data, f, indent=4)
        print("✅ JSON data saved to 'weektimetable.json'")
    except json.JSONDecodeError:
        print("❌ Response is not valid JSON.")
else:
    print(f"❌ Request failed with status code {response.status_code}")
