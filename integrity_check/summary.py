import json, os

out_dir = 'output'
for f in os.listdir(out_dir):
    if f.endswith('_audit.json'):
        path = os.path.join(out_dir, f)
        data = json.load(open(path, encoding='utf-8'))
        ra = data['risk_assessment']
        print(f"{f:30s} 风险:{ra['risk_level']:12s}  标记数:{len(data['flags']):2d}")