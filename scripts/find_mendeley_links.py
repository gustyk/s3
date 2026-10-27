import urllib.request
import re

url = 'https://data.mendeley.com/datasets/49r2pmymrm/1'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

# Search for any JSON or links
links = re.findall(r'https?://[^\s\"\'<>]+', html)
for l in set(links):
    if '49r2pmymrm' in l or 'mendeley' in l or 'download' in l:
        print("Link:", l)

# Search for file objects or names
for m in re.finditer(r'\{[^{}]*\"name\"[^{}]*\}', html):
    print("Match:", m.group(0))
