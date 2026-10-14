# -*- coding: utf-8 -*-
"""全ソース横断の品質監査：翻訳漏れ・必須フィールド欠落・分類漏れ・重複を検出する。"""
import json, sys, collections, re, os
sys.stdout.reconfigure(encoding='utf-8')

SOURCES = [
    ('FF ', 'ff_catalog.json'),
    ('EL ', 'el_catalog.json'),
    ('LE ', 'le_catalog.json'),
    ('ALH', 'alh_catalog.json'),
    ('ALE', 'ale_catalog.json'),
    ('AW ', 'aw_catalog.json'),
]
TYPES = {'turn', 'goal', 'time', 'proactive'}
issues = []

# index.html の classifyLoopType と同じロジック（ソースごとに判定材料が異なる）
_PRO = ["monitor", "telemetry", "incident", "production", "continuously", "triage",
        "unattended", "on failure", "alerting", " live ", "streaming", "24/7", "watch "]
_SCHED = ["scheduled", "every ", "nightly", " daily", "weekly", "hourly",
          "on a schedule", "cron", " cadence", "periodic", "recurring", "reliability pass"]
_GOAL = ["until", "passes", "tests pass", "threshold", " score", "coverage",
         "acceptance", "checklist", "verify", "converge", "benchmark", "regression"]


def classify(l):
    # EL/ALH/ALE/AW/LE: triggerType を4タイプへ写像
    t = l.get('triggerType')
    if t in TYPES:
        return t
    if t:  # manual / interval / event（EL のソース値）
        return {'event': 'proactive', 'interval': 'time'}.get(t, 'goal')
    # FF: テキストから実行時に分類
    cat = (l.get('category') or {}).get('slug', '')
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

print('=' * 62)
print(' 全ソース横断 品質監査')
print('=' * 62)

for tag, path in SOURCES:
    d = json.load(open(path, encoding='utf-8'))
    loops = d['loops']
    n = len(loops)
    # 1) 日本語訳の網羅
    no_title = [l['slug'] for l in loops if not l.get('titleJa')]
    no_desc = [l['slug'] for l in loops if not l.get('descriptionJa')]
    # 2) 4タイプ分類（index.html の classifyLoopType と同じ判定を再現）
    bad_type = [l['slug'] for l in loops if classify(l) not in TYPES]
    # 3) カテゴリの日本語ラベル
    no_catja = [l['slug'] for l in loops
                if not (l.get('category') or {}).get('labelJa')]
    # 4) 一意性
    dup = [s for s, c in collections.Counter(l['slug'] for l in loops).items() if c > 1]
    # 5) 通し番号の連続性
    # 番号は 2桁/3桁ゼロ埋めのいずれでもよい。連番であることだけ確認する
    nums = [l.get('number') for l in loops]
    bad_num = ([] if all(nums) and [int(x) for x in nums] == list(range(1, n + 1))
               else ['非連番または欠番'])
    # 6) 出典URL
    no_url = [l['slug'] for l in loops if not l.get('url')]
    # 7) コピー用本文（kickoff / fields / steps いずれか）
    no_body = [l['slug'] for l in loops
               if not (l.get('kickoffPrompt') or l.get('steps') or l.get('fields') or l.get('gates'))]

    checks = [('翻訳(title)', no_title), ('翻訳(desc)', no_desc), ('4タイプ分類', bad_type),
              ('カテゴリ日本語', no_catja), ('slug重複', dup), ('通し番号', bad_num),
              ('出典URL', no_url), ('本文', no_body)]
    ng = [(name, v) for name, v in checks if v]
    mark = 'OK ' if not ng else 'NG '
    print(f'{mark}{tag} {path:20} {n:>4}本')
    for name, v in ng:
        issues.append((tag, name, v))
        print(f'      ! {name}: {len(v)}件 {v[:5]}')

# DI（本体）
di = json.load(open('loops_1000.json', encoding='utf-8'))
dl = di['loops']
print(f'OK  DI  loops_1000.json      {len(dl):>4}本 （日本語原本）')

print('-' * 62)
tot = sum(len(json.load(open(p, encoding='utf-8'))['loops']) for _, p in SOURCES) + len(dl)
print(f' 合計 {tot} 本 / 7ソース')
# スキル用の索引が最新かを確認する（カタログを更新したのに索引が古いと提案に反映されない）
IDX = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   '.claude', 'skills', 'loop-advisor', 'loops_index.jsonl')
if os.path.exists(IDX):
    with open(IDX, encoding='utf-8') as f:
        n_idx = sum(1 for l in f if l.strip())
    if n_idx != tot:
        issues.append(('IDX', 'スキル索引が古い', [f'索引{n_idx}件 / カタログ{tot}件']))
        print(f'NG  索引 loops_index.jsonl      {n_idx:>4}本 '
              f'→ カタログと不一致。python build_loop_index.py を実行すること')
    else:
        print(f'OK  索引 loops_index.jsonl      {n_idx:>4}本 （スキル loop-advisor 用）')
else:
    print('--  索引 loops_index.jsonl      未生成（python build_loop_index.py で作成）')

print(f' 監査結果: {"問題なし" if not issues else str(len(issues)) + " 件の指摘"}')
sys.exit(1 if issues else 0)
