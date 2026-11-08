"""Exercise cloud prediction and keep network results as reproducible JSON evidence."""
from pathlib import Path
from urllib.parse import urlparse
import json, sys
import requests

ROOT = Path(__file__).resolve().parents[1]
ENV = ROOT / '.env'
url = ''
if ENV.is_file():
    for line in ENV.read_text(encoding='utf-8').splitlines():
        if line.startswith('PREDICTION_API_URL='):
            url = line.split('=',1)[1].strip()
if not url:
    url = input('Paste public URL for cloud API: ').strip().rstrip('/')
if not url.endswith('/predict'):
    url += '/predict'

print('Cloud API:', url)
health = requests.get(url.rsplit('/',1)[0]+'/health', timeout=100)
health.raise_for_status()
print('GET /health:', health.status_code, health.json())

# Use user-supplied test image, or find one in the downloaded dataset.
paths=[]
if len(sys.argv)>1:
    paths.append(Path(sys.argv[1]))
else:
    for root in (ROOT/'data'/'raw'/'RealArt', ROOT/'data'/'raw'/'AiArtData'):
        if root.exists():
            paths += [p for p in root.rglob('*') if p.is_file() and p.suffix.lower() in {'.png','.jpg','.jpeg','.webp'}][:1]
if not paths:
    raise SystemExit('Choose a sample with: python cloud/test_cloud.py C:\\path\\to\\sample.jpg')
results=[]
for p in paths:
    with p.open('rb') as f:
        response=requests.post(url, files={'file':(p.name,f)}, timeout=100)
    print('POST /predict', p.name, response.status_code, response.text[:500])
    response.raise_for_status()
    output=response.json()
    expected={'label','confidence','ai_probability','threshold','model_version'}
    if not expected.issubset(output):
        raise SystemExit('Prediction response missing required fields')
    results.append({'source_category':p.parent.name,'filename':p.name,'response':output})
out=ROOT/'outputs'/'cloud_api_test.json'
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps({'health':health.json(),'tests':results},indent=2),encoding='utf-8')
print('SUCCESS: Saved real cloud API responses to',out)
