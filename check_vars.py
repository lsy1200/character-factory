import json

path = r'C:\Users\Lucky\Desktop\제비뽑기\제비뽑기 룰렛 - Copy.json'
with open(path, encoding='utf-8') as f:
    data = json.load(f)

for obj in data['layouts'][0]['objects']:
    if obj['name'].startswith('Slot'):
        print(obj['name'], obj.get('variables', []))
