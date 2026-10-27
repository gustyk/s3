import urllib.request
import re
import json

url = 'https://data.mendeley.com/datasets/49r2pmymrm/1'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8', errors='ignore')

    # Look for files data or script tags
    found = False
    for script in re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL):
        if 'files' in script or 'results.csv' in script:
            print("Found script containing files/results.csv (len=" + str(len(script)) + "):")
            print(script[:1000])
            found = True
            break
    if not found:
        print("No script matched. Searching all text for results.csv or orders:")
        for line in html.split('\n'):
            if 'results' in line.lower() or 'order' in line.lower() or 'csv' in line.lower() or 'sha' in line.lower():
                print("Line:", line.strip()[:200])
except Exception as e:
    print("Error:", e)
