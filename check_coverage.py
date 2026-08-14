# -*- coding: utf-8 -*-
"""取りこぼし検知：各ソースの一次情報（sitemap/catalog）と取込済みカタログを突き合わせる。

EL を13本しか取り込めていなかった事故（実際は40本）の再発防止用。
「一覧ページのHTMLをスクレイプした件数」を信じず、必ず sitemap / catalog.json と照合する。

使い方: python _check_coverage.py
終了コード: 0=一致 / 1=取りこぼしあり
"""
import json, re, sys, urllib.request

sys.stdout.reconfigure(encoding='utf-8')
UA = {'User-Agent': 'Mozilla/5.0 (loop-dashboard coverage check)'}


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode('utf-8', 'replace')


def slugs_from_sitemap(url, pattern):
    try:
        return set(re.findall(pattern, fetch(url)))
    except Exception as e:
        return None


def local_slugs(path):
    d = json.load(open(path, encoding='utf-8'))
    return {l['slug'] for l in d['loops']}


CHECKS = [
    # (名前, ローカルカタログ, 一次情報URL, slug抽出パターン)
    ("FF  Forward Future", 'ff_catalog.json',
     'https://signals.forwardfuture.com/loop-library/catalog.json', None),
    ("EL  loops.elorm.xyz", 'el_catalog.json',
     'https://loops.elorm.xyz/sitemap.xml', r'/loops/([a-z0-9-]+)'),
    ("ALH Agent Loop Hub", 'alh_catalog.json',
     'https://agentloophub.com/sitemap.xml', r'/loops/([a-z0-9-]+)'),
]

fail = 0
for name, local, url, pat in CHECKS:
    have = local_slugs(local)
    if pat is None:
        # catalog.json 形式
        try:
            remote = {l['slug'] for l in json.loads(fetch(url))['loops']}
        except Exception as e:
            print(f"  ?  {name}: 一次情報を取得できず ({e})")
            continue
    else:
        remote = slugs_from_sitemap(url, pat)
        if remote is None:
            print(f"  ?  {name}: sitemap を取得できず")
            continue
    missing = sorted(remote - have)
    extra = sorted(have - remote)
    status = "OK " if not missing else "NG "
    if missing:
        fail = 1
    print(f"  {status}{name}: 一次情報 {len(remote)} / 取込済 {len(have)}")
    for s in missing:
        print(f"       + 取りこぼし: {s}")
    for s in extra:
        print(f"       - ローカルのみ(削除済みか?): {s}")

# LE は prompts/*.md のコードブロック数で照合（採用はキュレーション済みのため下限のみ確認）
try:
    n_remote = 0
    for f in ['goal-and-loop', 'loop-contracts', 'ralph-loops', 'automations',
              'subagents-maker-checker', 'verification-rubrics']:
        md = fetch('https://raw.githubusercontent.com/invincible04/awesome-loop-engineering/main/prompts/%s.md' % f)
        n_remote += len(re.findall(r'^```', md, re.M)) // 2
    n_local = len(local_slugs('le_catalog.json'))
    # LE は「実用的なブロックのみ採用」なので、極端に取りこぼしていないかだけ見る（6割以上）
    status = "OK " if n_local >= n_remote * 0.6 else "NG "
    if n_local < n_remote * 0.6:
        fail = 1
    print(f"  {status}LE  Loop Engineering Prompts: 一次情報 {n_remote}ブロック / 採用 {n_local}")
except Exception as e:
    print(f"  ?  LE: 取得できず ({e})")

# ALE は HuggingFace データセットの examples/*.json 数で照合
try:
    meta = json.loads(fetch('https://huggingface.co/api/datasets/cy0307/awesome-loop-engineering'))
    files = [f.get('rfilename', '') for f in meta.get('siblings', [])]
    n_remote = len([f for f in files if f.startswith('examples/') and f.endswith('.json')])
    n_local = len(local_slugs('ale_catalog.json'))
    status = "OK " if n_local >= n_remote else "NG "
    if n_local < n_remote:
        fail = 1
    print(f"  {status}ALE Awesome Loop Engineering: 一次情報 {n_remote} / 取込済 {n_local}")
except Exception as e:
    print(f"  ?  ALE: 取得できず ({e})")

# AW は GitHub README の見出し数で照合
try:
    md = fetch('https://raw.githubusercontent.com/serenakeyitan/awesome-agent-loops/main/README.md')
    n_remote = len(re.findall(r'^### ', md, re.M))
    n_local = len(local_slugs('aw_catalog.json'))
    status = "OK " if n_local >= n_remote else "NG "
    if n_local < n_remote:
        fail = 1
    print(f"  {status}AW  Awesome Agent Loops: 一次情報 {n_remote} / 取込済 {n_local}")
except Exception as e:
    print(f"  ?  AW: 取得できず ({e})")

print('=> ' + ('取りこぼしなし' if not fail else '取りこぼしあり（上記 + を取り込むこと）'))
sys.exit(fail)
