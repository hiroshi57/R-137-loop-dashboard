# ループ在庫の更新手順

ストックは固定ではない。出典サイトは更新され続けるため、**取りこぼしを検知して取り込み直す**。
過去に EL を 13本しか取り込めていなかった（実際は40本）事故があり、その再発防止として
機械的な照合を常設している。

> 原則: **「網羅した」と主張しない。網羅を検証する手続きを持つ。**
> 検索が0件を返したことを「存在しない証拠」として扱わない（レート制限や取得失敗と区別できないため）。

---

## 1. 定期チェック（月1回を推奨）

```bash
python check_coverage.py
```

一次情報（sitemap.xml / catalog.json / HuggingFace API / GitHub README）と、
取り込み済みカタログを突き合わせる。取りこぼしがあれば非ゼロ終了する。

出力例:
```
  OK FF  Forward Future: 一次情報 85 / 取込済 85
  NG EL  loops.elorm.xyz: 一次情報 40 / 取込済 13
       + 取りこぼし: api-contract-until-match
```

`NG` が出たら 2 へ進む。

---

## 2. 取り込み（増加）

取りこぼしが出たソースについて、不足分を取得して既存カタログに**追加**する。
既存の日本語訳は保持し、上書きしない。

手順の骨子:

1. 一次情報（sitemap 等）から全 slug を取得する
2. 取り込み済みとの差分を取り、不足分だけ取得する
3. 日本語訳を付ける（title / description / 完了条件 / 手順 / ガードレール）
4. 既存カタログの `loops` に追加し、通し番号を振り直す
5. `categories` を再構築し、`loopCount` を更新する

**注意**: 一覧ページの HTML をスクレイプした件数を信じない。必ず sitemap / catalog.json と照合する。
サイトが「40+」と自称しているのに13件しか取れない、といった矛盾は必ず追及する。

---

## 3. 索引の再生成（必須）

カタログを更新したら、**必ず**索引を作り直す。これを忘れると提案に反映されない。

```bash
python build_loop_index.py
```

出力:
```
  loops: 1354 / size: 1087 KB
  by source: {'DI': 1126, 'FF': 85, ...}
```

---

## 4. 品質監査（改善・改修）

```bash
python audit_quality.py
```

全ソース横断で次を検査する。1件でも問題があれば非ゼロ終了する。

| 検査 | 内容 |
|---|---|
| 翻訳漏れ | `titleJa` / `descriptionJa` の欠落 |
| 4タイプ分類 | turn / goal / time / proactive のいずれかに収まるか |
| カテゴリ日本語 | `labelJa` の欠落 |
| slug 重複 | 同一 slug の重複 |
| 通し番号 | 連番・欠番 |
| 出典 URL | `url` の欠落 |
| 本文 | kickoff / steps / fields / gates のいずれかがあるか |

---

## 5. 反映

```bash
python _test.py                 # 68項目
git add -A && git commit        # feat: / fix: で始める
vercel --yes --prod --force --scope takizawahiroshi-gmailcoms-projects
git push origin main
```

---

## 取り込み判断の基準

新しいサイトを見つけたとき、**取り込むかどうか**は次で判断する。

| 判定 | 条件 | 例 |
|---|---|---|
| **取り込む** | コピーして使えるループ本体を持つ | loops.elorm.xyz、Agent Loop Hub |
| **取り込まない（再配信）** | 既存ソースと同一内容 | ailooplibrary.com（FFの再配信・しかも古い） |
| **取り込まない（実装）** | ループの実行基盤であって配布元でない | OpenClaw、superpowers、fractal |
| **取り込まない（リンク集）** | 解説記事・論文へのリンクのみ | awesome-autoresearch（102件すべて実装へのリンク） |

同一内容かは、README の説明文一致・ループ本数・サイト構造で判定する。

---

## 現在の在庫

| ソース | 本数 | ライセンス | 一次情報 |
|---|---|---|---|
| DI | 1,126 | 自社 | （自社データ） |
| FF Forward Future | 85 | MIT | `signals.forwardfuture.com/loop-library/catalog.json` |
| EL loops! | 40 | — | `loops.elorm.xyz/sitemap.xml` |
| LE LoopEng + Ralph | 36 | MIT | GitHub README |
| ALH Agent Loop Hub | 27 | MIT | `agentloophub.com/sitemap.xml` |
| ALE Awesome Loop Eng | 22 | MIT / CC BY 4.0 | HuggingFace datasets API |
| AW Awesome Agent Loops | 18 | CC BY 4.0 | GitHub README |

帰属表示は `THIRD_PARTY_LICENSES.txt` に記載。CC BY 4.0 のものは表示義務がある。
