# -*- coding: utf-8 -*-
"""ストック済みループ（1,354本）から候補を検索する。

インデックス全件を読み込ませるとコンテキストを浪費するため、
必ずこのスクリプト経由で必要な件数だけ取り出すこと。

使い方:
    python search_loops.py "CI 失敗 修正"                  # キーワード検索
    python search_loops.py "テスト" --type goal --top 5    # ループタイプで絞る
    python search_loops.py "" --src ALE --top 10           # ソースで絞る
    python search_loops.py "SEO" --detail                  # 完了条件まで表示

オプション:
    --type  turn|goal|time|proactive   4タイプで絞る
    --src   DI|FF|EL|LE|ALH|ALE|AW     出典で絞る
    --top   N                          件数（既定5）
    --detail                           使うタイミング・完了条件も出す
"""
import json, sys, os, re, argparse, unicodedata

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(HERE, 'loops_index.jsonl')

TYPE_JA = {'turn': 'ターン型', 'goal': 'ゴール型', 'time': '時間型', 'proactive': '能動型'}
SRC_JA = {'DI': 'DI(自社)', 'FF': 'ForwardFuture', 'EL': 'loops!', 'LE': 'LoopEng+Ralph',
          'ALH': 'AgentLoopHub', 'ALE': 'AwesomeLoopEng', 'AW': 'AwesomeAgentLoops'}


def norm(s):
    return unicodedata.normalize('NFKC', str(s or '')).lower()


def load():
    if not os.path.exists(INDEX):
        print(f'索引がありません: {INDEX}', file=sys.stderr)
        print('リポジトリ直下で python build_loop_index.py を実行してください。', file=sys.stderr)
        sys.exit(2)
    with open(INDEX, encoding='utf-8') as f:
        return [json.loads(l) for l in f if l.strip()]


def score(row, terms):
    """タイトル一致を最重視し、説明・用途・タグの順に重み付けする"""
    t, d = norm(row['title']), norm(row['desc'])
    w, tg = norm(row.get('when')), norm(' '.join(row.get('tags') or []))
    cat = norm(row.get('cat'))
    s = 0
    for q in terms:
        if not q:
            continue
        if q in t:   s += 10
        if q in cat: s += 4
        if q in tg:  s += 3
        if q in d:   s += 2
        if q in w:   s += 1
    return s


def main():
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument('query', nargs='?', default='')
    p.add_argument('--type', dest='ltype', default='')
    p.add_argument('--src', default='')
    p.add_argument('--top', type=int, default=5)
    p.add_argument('--detail', action='store_true')
    p.add_argument('-h', '--help', action='store_true')
    a = p.parse_args()
    if a.help:
        print(__doc__); return

    rows = load()
    if a.ltype:
        rows = [r for r in rows if r['type'] == a.ltype]
    if a.src:
        want = {s.strip().upper() for s in a.src.split(',')}
        rows = [r for r in rows if r['src'].upper() in want]

    terms = [norm(x) for x in re.split(r'[\s　,、]+', a.query) if x]
    if terms:
        scored = [(score(r, terms), r) for r in rows]
        scored = [(s, r) for s, r in scored if s > 0]
        scored.sort(key=lambda x: (-x[0], x[1]['src']))
        rows = [r for _, r in scored[:a.top]]
    else:
        rows = rows[:a.top]

    if not rows:
        print('該当なし。語を減らすか --type / --src の絞り込みを外してください。')
        return

    print(f'■ 候補 {len(rows)}件（全1,354本から）')
    for i, r in enumerate(rows, 1):
        print(f'\n[{i}] {r["title"]}')
        print(f'    出典: {SRC_JA.get(r["src"], r["src"])} / {r["id"]}')
        meta = [TYPE_JA.get(r['type'], r['type'])]
        if r.get('cat'):
            meta.append(r['cat'])
        if r.get('maxIter'):
            meta.append(f'最大{r["maxIter"]}回')
        print(f'    種別: {" ・ ".join(meta)}')
        print(f'    概要: {r["desc"]}')
        if a.detail:
            if r.get('when'):
                print(f'    使う時: {r["when"]}')
            if r.get('exit'):
                print(f'    完了条件: {r["exit"]}')
            if r.get('url'):
                print(f'    URL: {r["url"]}')


if __name__ == '__main__':
    main()
