import json

path = r'C:\Users\Lucky\Desktop\제비뽑기\제비뽑기 룰렛 - Copy.json'
with open(path, encoding='utf-8') as f:
    data = json.load(f)

# Find existing event indices
# Event 19 is the Slots click event we added
events = data['layouts'][0]['events']

# Modify event 19: Slots click
slot_click = events[19]
slot_click['actions'] = [
    {
        'type': {'value': 'SetNumberVariable'},
        'parameters': ['SelectedSlotIndex', '=', 'Slots.Variable(SlotIndex)']
    },
    {
        'type': {'value': 'SetNumberVariable'},
        'parameters': ['PrizeCount', '=', 'RandomInRange(1, 3)']
    },
    {
        'type': {'value': 'SetNumberVariable'},
        'parameters': ['Result1', '=', 'RandomInRange(0, 7)']
    },
    {
        'type': {'value': 'SetNumberVariable'},
        'parameters': ['Result2', '=', 'RandomInRange(0, 7)']
    },
    {
        'type': {'value': 'SetNumberVariable'},
        'parameters': ['Result3', '=', 'RandomInRange(0, 7)']
    },
    {
        'type': {'value': 'PlaySound'},
        'parameters': ['', 'VariableString(SpinSound)', 'no', '100', '']
    },
    {
        'type': {'value': 'SetBooleanVariable'},
        'parameters': ['IsSpinning', 'True', '']
    },
    {
        'type': {'value': 'SetNumberVariable'},
        'parameters': ['SpinAngle', '=', '룰렛원반그림.Angle() + 1080 + mod(Variable(SelectedSlotIndex), 8) * 45']
    },
    {
        'type': {'value': 'TextObject::String'},
        'parameters': ['ResultText', '"돌림판을 돌리는 중...\\n잠시만 기다려주세요!"', '']
    },
    {
        'type': {'value': 'Tween::TweenBehavior::AddObjectAngleTween2'},
        'parameters': ['룰렛원반그림', 'Tween', '"spin"', 'SpinAngle', '"easeOutCubic"', '3', 'no']
    },
    {
        'type': {'value': 'ParticleSystem::StartEmission'},
        'parameters': ['SparkleEmitter']
    }
]

# Modify event 4: SpinButton click (random slot)
spin_click = events[4]
spin_click['events'][0]['actions'] = [
    {
        'type': {'value': 'SetNumberVariable'},
        'parameters': ['SelectedSlotIndex', '=', 'RandomInRange(1, 12)']
    },
    {
        'type': {'value': 'SetNumberVariable'},
        'parameters': ['PrizeCount', '=', 'RandomInRange(1, 3)']
    },
    {
        'type': {'value': 'SetNumberVariable'},
        'parameters': ['Result1', '=', 'RandomInRange(0, 7)']
    },
    {
        'type': {'value': 'SetNumberVariable'},
        'parameters': ['Result2', '=', 'RandomInRange(0, 7)']
    },
    {
        'type': {'value': 'SetNumberVariable'},
        'parameters': ['Result3', '=', 'RandomInRange(0, 7)']
    },
    {
        'type': {'value': 'PlaySound'},
        'parameters': ['', 'VariableString(SpinSound)', 'no', '100', '']
    },
    {
        'type': {'value': 'SetBooleanVariable'},
        'parameters': ['IsSpinning', 'True', '']
    },
    {
        'type': {'value': 'SetNumberVariable'},
        'parameters': ['SpinAngle', '=', '룰렛원반그림.Angle() + 1080 + mod(Variable(SelectedSlotIndex), 8) * 45']
    },
    {
        'type': {'value': 'TextObject::String'},
        'parameters': ['ResultText', '"돌림판을 돌리는 중...\\n잠시만 기다려주세요!"', '']
    },
    {
        'type': {'value': 'Tween::TweenBehavior::AddObjectAngleTween2'},
        'parameters': ['룰렛원반그림', 'Tween', '"spin"', 'SpinAngle', '"easeOutCubic"', '3', 'no']
    },
    {
        'type': {'value': 'ParticleSystem::StartEmission'},
        'parameters': ['SparkleEmitter']
    }
]

# Modify event 6: wheel stopped -> show results
stop_event = events[6]
# clear sub events
stop_event['events'] = []
# add new sub event to build result text
result_sub = {
    'type': 'BuiltinCommonInstructions::Standard',
    'conditions': [],
    'actions': [
        {
            'type': {'value': 'SetBooleanVariable'},
            'parameters': ['IsSpinning', 'False', '']
        },
        {
            'type': {'value': 'SetNumberVariable'},
            'parameters': ['WinningIndex', '=', 'mod(Variable(SelectedSlotIndex), 8)']
        },
        {
            'type': {'value': 'TextObject::String'},
            'parameters': ['ResultText', """"🎉 당첨 결과 🎉\\n\\n" + VariableString(Prizes[Variable(Result1)]) + (Variable(PrizeCount) >= 2 ? "\\n" + VariableString(Prizes[Variable(Result2)]) : "") + (Variable(PrizeCount) >= 3 ? "\\n" + VariableString(Prizes[Variable(Result3)]) : "")""", '']
        }
    ],
    'events': []
}
stop_event['events'].append(result_sub)

# highlight selected slot
highlight_sub = {
    'type': 'BuiltinCommonInstructions::ForEach',
    'object': 'Slots',
    'objectsToPick': 'Slots',
    'conditions': [
        {
            'type': {'value': 'PosX'},
            'parameters': ['Slots', '=', '780 + ((Variable(SelectedSlotIndex) - 1) % 3) * 140']
        },
        {
            'type': {'value': 'PosY'},
            'parameters': ['Slots', '=', '60 + floor((Variable(SelectedSlotIndex) - 1) / 3) * 130']
        }
    ],
    'actions': [
        {
            'type': {'value': 'Tween::TweenBehavior::AddObjectScaleTween2'},
            'parameters': ['Slots', 'Tween', '"highlight"', '1.3', '1.3', '"easeOutBack"', '0.6', 'yes']
        }
    ],
    'events': []
}
stop_event['events'].append(highlight_sub)

with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('done')
