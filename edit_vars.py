import json

path = r'C:\Users\Lucky\Desktop\제비뽑기\제비뽑기 룰렛 - Copy.json'
with open(path, encoding='utf-8') as f:
    data = json.load(f)

objects = data['layouts'][0]['objects']
for i in range(1, 13):
    name = f'Slot{i}'
    for obj in objects:
        if obj['name'] == name:
            if 'variables' not in obj:
                obj['variables'] = []
            # remove existing SlotIndex
            obj['variables'] = [v for v in obj['variables'] if v['name'] != 'SlotIndex']
            obj['variables'].append({'name': 'SlotIndex', 'type': 'number', 'value': i})
            break

# scene variables
if 'variables' not in data['layouts'][0]:
    data['layouts'][0]['variables'] = []
layout_vars = data['layouts'][0]['variables']

# PrizeCount
layout_vars = [v for v in layout_vars if v['name'] != 'PrizeCount']
layout_vars.append({'name': 'PrizeCount', 'type': 'number', 'value': 3})

# Prizes array
layout_vars = [v for v in layout_vars if v['name'] != 'Prizes']
prize_values = ['-5%', 'Retry', '-50%', '-30%', 'Loose', '-5%', '-30%', '-80%']
prizes = {
    'name': 'Prizes',
    'type': 'array',
    'children': [{'name': '', 'type': 'string', 'value': v} for v in prize_values]
}
layout_vars.append(prizes)

data['layouts'][0]['variables'] = layout_vars

with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('done')
