import urllib.request
import re
import json

url = 'https://data.mendeley.com/datasets/49r2pmymrm/1'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

for script in re.findall(r'<script[^>]*>(window\.INITIAL_STATE\s*=\s*.*?);</script>', html, re.DOTALL):
    clean = re.sub(r'^window\.INITIAL_STATE\s*=\s*', '', script).strip()
    data = json.loads(clean)
    files = data.get('files', {}).get('data', [])
    print(f"Total files in Mendeley dataset: {len(files)}")
    for f in files:
        fname = f.get('name')
        fsize = f.get('size')
        fhash = f.get('sha256') or f.get('content_details', {}).get('sha256') or f.get('metrics', {})
        print(f"File: {fname} | Size: {fsize} bytes | Details: {f}")
