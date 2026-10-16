import json

path = r'C:\Users\Lucky\Desktop\제비뽑기\제비뽑기_룰렛_완성.json'
with open(path, encoding='utf-8') as f:
    data = json.load(f)

# Fix text content
for obj in data['layouts'][0]['objects']:
    if obj['type'] == 'TextObject::Text':
        obj['content']['text'] = obj.get('text', '')
        obj['content']['bold'] = obj.get('bold', False)
        obj['content']['italic'] = obj.get('italic', False)
        obj['content']['characterSize'] = obj.get('characterSize', 20)
        color = obj.get('color', {'r': 255, 'g': 255, 'b': 255})
        obj['content']['color'] = f"{color['r']};{color['g']};{color['b']}"
        obj['content']['textAlignment'] = 'center'

# Add SlotIndex variable to each slot
for i in range(1, 13):
    name = f'Slot{i}'
    for obj in data['layouts'][0]['objects']:
        if obj['name'] == name:
            obj['variables'] = [{'name': 'SlotIndex', 'type': 'number', 'value': i}]
            break

# Ensure Slots group exists and contains all slots
groups = data['layouts'][0].get('objectsGroups', [])
slots_group = None
for g in groups:
    if g['name'] == 'Slots':
        slots_group = g
        break

if slots_group is None:
    groups.append({'name': 'Slots', 'objects': [f'Slot{i}' for i in range(1, 13)]})
else:
    slots_group['objects'] = [f'Slot{i}' for i in range(1, 13)]

data['layouts'][0]['objectsGroups'] = groups

# Fix events: ensure proper variable names and no trailing comma issues
with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('fixed')
