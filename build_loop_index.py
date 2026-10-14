# -*- coding: utf-8 -*-
"""全ソースのループから、スキル用の軽量な検索インデックスを生成する。

出力: .claude/skills/loop-advisor/loops_index.jsonl
  1行1ループ。提案に必要な最小限の項目だけを持つ（本文は dashboard 側を参照）。

使い方:
    python build_loop_index.py
"""
import json, sys, os, re

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, '.claude', 'skills', 'loop-advisor')

TYPES = {'turn', 'goal', 'time', 'proactive'}
_PRO = ["monitor", "telemetry", "incident", "production", "continuously", "triage",
        "unattended", "on failure", "alerting", " live ", "streaming", "24/7", "watch "]
_SCHED = ["scheduled", "every ", "nightly", " daily", "weekly", "hourly",
          "on a schedule", "cron", " cadence", "periodic", "recurring", "reliability pass"]
_GOAL = ["until", "passes", "tests pass", "threshold", " score", "coverage",
         "acceptance", "checklist", "verify", "converge", "benchmark", "regression"]


def classify(l):
    t = l.get('triggerType')
    if t in TYPES:
        return t
    if t:
        return {'event': 'proactive', 'interval': 'time'}.get(t, 'goal')
    if l.get('trigger') in ('manual', 'interval'):
        cat = l.get('category') or ''
        if l['trigger'] == 'interval':
            return 'proactive' if cat == '運用・最適化' else 'time'
        return 'turn' if cat in ('戦略立案', '調査・分析') else 'goal'
    cat = (l.get('category') or {})
    cat = cat.get('slug', '') if isinstance(cat, dict) else ''
    b = ' '.join(str(l.get(k, '')) for k in
                 ['title', 'useWhen', 'description', 'prompt', 'verification', 'why',
                  'implementationNote']).lower()
    if any(w in b for w in _PRO):
        return 'proactive'
    if any(w in b for w in _SCHED):
        return 'time'
    if cat == 'evaluation' or any(w in b for w in _GOAL):
        return 'goal'
    if cat in ('content', 'design'):
        return 'turn'
    return 'goal'


def catlabel(c):
    if isinstance(c, dict):
        return c.get('labelJa') or c.get('label') or ''
    return c or ''


def clip(s, n):
    s = re.sub(r'\s+', ' ', str(s or '')).strip()
    return s[:n]


rows = []

# --- DI（本体・日本語原本）---
di = json.load(open(os.path.join(HERE, 'loops_1000.json'), encoding='utf-8'))
for l in di['loops']:
    rows.append({
        'src': 'DI', 'id': l['id'], 'title': l['title'],
        'desc': clip(l.get('goal'), 160),
        'when': clip(l.get('triggerDetail'), 100),
        'exit': clip(l.get('exitCondition'), 120),
        'cat': l.get('category', ''), 'type': classify(l),
        'maxIter': l.get('maxIterations'),
        'tags': (l.get('tags') or [])[:6],
        'service': l.get('service', ''), 'industry': l.get('industry', ''),
    })

# --- 外部6ソース ---
EXT = [('FF', 'ff_catalog.json'), ('EL', 'el_catalog.json'), ('LE', 'le_catalog.json'),
       ('ALH', 'alh_catalog.json'), ('ALE', 'ale_catalog.json'), ('AW', 'aw_catalog.json')]
for tag, path in EXT:
    d = json.load(open(os.path.join(HERE, path), encoding='utf-8'))
    for l in d['loops']:
        rows.append({
            'src': tag, 'id': l['slug'],
            'title': l.get('titleJa') or l.get('title'),
            'desc': clip(l.get('descriptionJa') or l.get('description'), 160),
            'when': clip(l.get('useWhenJa') or l.get('useWhen') or l.get('triggerJa') or l.get('trigger'), 100),
            'exit': clip(l.get('exitConditionJa') or l.get('exitCondition') or
                         ((l.get('verificationJa') or {}).get('title') if isinstance(l.get('verificationJa'), dict) else ''), 120),
            'cat': catlabel(l.get('category')), 'type': classify(l),
            'maxIter': l.get('maxIterations') or l.get('maxRetries'),
            'tags': (l.get('keywords') or [])[:6],
            'url': l.get('url', ''),
        })

os.makedirs(OUT_DIR, exist_ok=True)
out = os.path.join(OUT_DIR, 'loops_index.jsonl')
with open(out, 'w', encoding='utf-8') as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')

size_kb = os.path.getsize(out) // 1024
import collections
print(f'wrote {out}')
print(f'  loops: {len(rows)} / size: {size_kb} KB')
print('  by source:', dict(collections.Counter(r['src'] for r in rows)))
print('  by type  :', dict(collections.Counter(r['type'] for r in rows)))
