import json

path = r'C:\Users\Lucky\Desktop\제비뽑기\제비뽑기 룰렛 - Copy.json'
with open(path, encoding='utf-8') as f:
    data = json.load(f)

events = data['layouts'][0]['events']
for i, e in enumerate(events):
    conds = e.get('conditions', [])
    first_cond = conds[0] if conds else {}
    cond_type = first_cond.get('type', {}).get('value', '')
    acts = e.get('actions', [])
    first_act = acts[0] if acts else {}
    act_type = first_act.get('type', {}).get('value', '')
    print(i, cond_type, act_type)
