import json

with open('/tmp/claude_debug/last_response.txt', 'r', encoding='utf-8') as f:
    data = f.read()

# Remove code blocks
if '```json' in data:
    data = data[data.find('```json')+7:]
if '```' in data:
    data = data[:data.find('```')]

try:
    parsed = json.loads(data)
    print('✅ JSON is valid!')
    print(f'Keys: {list(parsed.keys())}')
    if 'questions' in parsed:
        print(f'Questions count: {len(parsed["questions"])}')
except json.JSONDecodeError as e:
    print(f'❌ JSON Error at line {e.lineno}, col {e.colno}: {e.msg}')
    print(f'Position {e.pos}')
    print(f'Context: ...{data[max(0,e.pos-100):e.pos+100]}...')
