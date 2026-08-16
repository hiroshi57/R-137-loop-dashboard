# エージェントループ・ポータル調査（1次情報 / 2次情報）

> 調査日: 2026-08-10
> 目的: 現在ダッシュボードが取り込んでいる FF / EL 以外のループ・ポータルを洗い出し、
>       取り込み候補（独自コンテンツを持つもの）と、参照のみで足りるもの（ミラー・解説）を切り分ける。
> 判定基準: **独自ループを保有しているか**（＝取り込む価値があるか）／ミラー・再配信か／解説記事か。

---

## 結論サマリ

| 区分 | 件数 | 扱い |
|---|---|---|
| **A. 独自ループを持つポータル**（取り込み候補） | **4** | DI/FF/EL に続く取り込み対象 |
| B. FF のミラー・再配信 | 4 | 取り込み不要（FF と重複） |
| C. 1次情報（公式ドキュメント・発案者の原典） | 5 | 出典として引用 |
| D. 2次情報（解説・キュレーション記事） | 9 | 背景理解・用語整理に利用 |

**要点**: 「ループのポータルは2つだけ」ではなく、**独自コンテンツを持つものが少なくとも4つ**存在する。
一方で、検索上位に出る `ailooplibrary.com` や複数の GitHub リポジトリは **FF（Forward Future）の同一コンテンツの再配信**であり、
重複取り込みの価値はない（＝見かけの数ほどには独立ソースは多くない）。

---

## A. 独自ループを持つポータル（取り込み候補）

| # | 名称 / URL | 規模 | 特徴 | 取り込み優先度 |
|---|---|---|---|---|
| A-1 | **loops!**<br>https://loops.elorm.xyz/ | 13本（本体は40+と称する） | **取り込み済み（EL）**。steps / exitCondition / guardrails / kickoff が構造化。フック型（event）を含む | ✅ 導入済み |
| A-2 | **Loop Library (Forward Future)**<br>https://signals.forwardfuture.com/loop-library/ | 70本 | **取り込み済み（FF）**。MIT。Matthew Berman 発 | ✅ 導入済み |
| A-3 | **Awesome Agent Loops**<br>https://github.com/serenakeyitan/awesome-agent-loops | **18本** | **独自**。X の実践者由来の実運用プロンプト集。`/loop`・`/goal`・`/schedule` の**Claude Code コマンド別**に整理。各ループに出典 X ポストあり（13アカウント）。CC BY 4.0 | ★ 高（構造が我々の4タイプ分類と直結） |
| A-4 | **Agent Loop Hub**<br>https://agentloophub.com | **27本** | **独自**。1ループ7フィールド（goal / cron trigger / verify / exit / token cost 等）。DISCOVER→ACT→VERIFY→PERSIST→EXIT の5段構造。**日本語UIあり**。3ランタイム対応（Claude Code / Codex / OpenClaw）。オープンソース | ★ 高（**トークンコスト**と**cron**を持つ点が独自） |

> A-3 と A-4 を取り込むと、ダッシュボードは **DI 1,126 + FF 70 + EL 13 + 18 + 27 = 1,254本** になる。

### 補足: 周辺ツール（ループ本体ではないが関連）
- **loopable** — https://github.com/serenakeyitan/loopable
  会話中にループを提案する Claude/Codex 用フック。awesome-agent-loops の「司書」役。MIT
- **first-tree** — https://first-tree.ai/ 「Agent orchestration for engineers」
- **superpowers** — https://github.com/obra/superpowers エージェント・スキルのフレームワーク

---

## B. FF のミラー・再配信（取り込み不要）

いずれも **Forward Future の Loop Library と同一コンテンツ**。独自ループなし。

| URL | 実体 |
|---|---|
| https://ailooplibrary.com/ | FF の68ループを **MCP 経由の読み取り専用**で再提供するサイト（"68 LOOPS INDEXED"）。UI は独自だが中身は FF |
| https://github.com/Forward-Future/loopy | **FF の本体リポジトリ**（`loop-library/site/` にサイト実体）。1次情報として価値あり |
| https://github.com/Tks2k4/loop-library | 上記のフォーク（説明文が完全一致） |
| https://keysersoose.github.io/loop-library/ | 同じくミラー公開 |

> 注意: `ailooplibrary.com` は「68 loops」と表示するが、FF 本体は現在70本。**再配信側が古い**可能性がある（＝1次情報の FF を直接見るべき理由）。

---

## C. 1次情報（原典・公式）

| 種別 | 出典 | 内容 |
|---|---|---|
| 公式ドキュメント | https://code.claude.com/docs/en/goal | `/goal` = 条件を満たすまで実行 |
| 公式ドキュメント | https://code.claude.com/docs/en/scheduled-tasks | `/loop`（間隔実行）・`/schedule`（クラウドcron） |
| 公式ブログ | https://claude.com/ja/blog/getting-started-with-loops | Claude Code チームによる**4ループタイプ**の定義（取り込み済み） |
| 発案者の言 | Boris Cherny（Claude Code 作者）<br>https://x.com/0xMovez/status/2064047579499770218 | 「もうプロンプトは書かない。**ループを作る**。私の仕事はループを作ることだ」 |
| 原典記事 | https://ghuntley.com/ralph/ | "Ralph Wiggum as a software engineer" — Ralph ループの原典（EL の ralph-story-executor の元ネタ） |
| 論文（PDF） | Loop Design: A Field Playbook for Agentic Systems | 5つの動作・自律レベル・自己採点バイアス（取り込み済み） |

---

## D. 2次情報（解説・キュレーション）

背景理解や用語整理に有用。ループ本体の取り込み元としては不要。

| URL | 位置づけ |
|---|---|
| https://github.com/rudy2steiner/awesome-agent-loops | **loop engineering のキュレーション**（同名だが A-3 とは別内容）。概念・原典・パターン・テンプレ・ランタイム・検証・状態管理・コスト管理で分類。本調査の起点として有用 |
| https://addyosmani.com/blog/loop-engineering/ | Addy Osmani による解説 |
| https://linas.substack.com/p/loop-engineering-complete-guide | 完全ガイド |
| https://www.mindstudio.ai/blog/what-is-loop-engineering-ai-coding-agents | 入門 |
| https://explainx.ai/blog/loop-engineering-coding-agents-claude-code-guide-2026 | 実践ガイド |
| https://lushbinary.com/blog/loop-engineering-ai-coding-agents-guide/ | 同上 |
| https://wmedia.es/en/tips/claude-code-schedule-vs-loop-vs-cron | `/schedule` vs `/loop` vs cron の比較 |
| https://www.verdent.ai/guides/claude-code-loop-command | `/loop` コマンド解説 |
| https://www.explainx.ai/blog/matthew-berman-loop-library-forward-future-ai-agents-2026 | FF Loop Library の紹介記事 |

---

## 次アクション案

1. **A-3 Awesome Agent Loops（18本）を取り込む**
   - `/loop`・`/goal`・`/schedule` の区分が、既に実装済みの**4ループタイプ分類と直接対応**する
     （`/loop`→時間型、`/goal`→ゴール型、`/schedule`→能動型）
   - ライセンス **CC BY 4.0** → 帰属表示を付ければ商用可。`THIRD_PARTY_LICENSES.txt` に追記が必要
2. **A-4 Agent Loop Hub（27本）を取り込む**
   - **トークンコスト**という他にない軸を持つ。ダッシュボードに「コスト」列を追加できる
   - DISCOVER/ACT/VERIFY/PERSIST/EXIT は論文の5動作とほぼ一致 → 既存の可視化と噛み合う
   - ライセンス（"100% open source content"の具体条項）を要確認
3. **ミラー系（B）は取り込まない**。ただし FF 本体リポジトリ（loopy）は更新追跡先として記録
4. 取り込み時は既存同様、**日本語訳＋4タイプ分類＋ループ＝グラフ表現**を付与して統一する

---

## 調査メモ（再現手順）

- 検索: DuckDuckGo HTML 版でクエリを変えて横断（`agent loop library` / `awesome agent loops` 等）
- 各候補は HTTP ステータスと `<title>`、本文テキストを取得して実体を判定
- 「同一コンテンツか」は README の説明文一致・ループ本数・サイト構造で判定

---

# 追補（2026-08-14）: 敵対的反証と全件精査の結果

初版の「独自ポータルは4つ」「これ以上ない」という結論は**誤りだった**。
敵対的反証を行い、4つの主張のうち3つが崩れた。以下は再調査後の確定版。

## 反証で判明した初版の誤り

| 初版の主張 | 反証結果 |
|---|---|
| EL は13本 | ❌ **実際は40本**。一覧ページのHTMLだけを見て、sitemap.xml と照合していなかった（27本の取りこぼし） |
| これ以上ポータルはない | ❌ DuckDuckGo が0件を返したのは**レート制限による失敗**。GitHub API で再検索したところ未確認リポジトリが多数 |
| 取り込み対象は出尽くした | ❌ **Awesome Loop Engineering**（956 resources / 22ループ契約 / HuggingFaceデータセット）を発見 |
| 他ソースの件数は正確 | ✅ ALH 27・FF 85 は正しかった（唯一支持された） |

**根本原因**: 証拠の不在（検索0件）を不在の証拠として扱った。単一のキュレーションリストに依存した。
生成（調査）と評価（結論）を同じ文脈で行い、独立した検証手続きを持たなかった。
＝ 我々がダッシュボードに実装した「自己採点バイアス」そのものを、調査者自身が犯していた。

## 確定版：取り込み済み7ソース 1,354本

| ソース | 本数 | ライセンス | 特徴 |
|---|---|---|---|
| DI | 1,126 | 自社 | 13サービス×10業種の日本語ループ |
| FF Forward Future | 85 | MIT | 2026-07-07更新で70→85に追従済み |
| EL loops! | 40 | — | 取りこぼし27本を回収済み |
| LE Loop Engineering Prompts | 36 | MIT | 教材プロンプト＋**Ralph原典**(21,476★) |
| ALH Agent Loop Hub | 27 | MIT | 7フィールド仕様・トークンコスト |
| ALE Awesome Loop Engineering | 22 | MIT/CC BY 4.0 | **ループ契約**（役割分担・ゲート・予算・禁止操作） |
| AW Awesome Agent Loops | 18 | CC BY 4.0 | X実践者由来の `/loop`・`/goal`・`/schedule` |

4タイプ分布（外部6ソース228本）: time 93 / goal 80 / proactive 54 / turn 1

## 非取込と判断したもの（理由付き）

| 対象 | 規模 | 非取込の理由 |
|---|---|---|
| ailooplibrary.com | 68 | FF の再配信。しかも85本に追従できておらず**古い** |
| Forward-Future/loopy 他ミラー3件 | — | FF と同一コンテンツ |
| webfuse-com/awesome-autoresearch | 2,434★ | **102リンクを全件精査**。いずれも自律研究エージェントの「実装」であり、コピペ可能なループカタログではない |
| ChaoYue0307 の956 resources | 956 | 論文・記事へのリンク集。ループ本体は examples/22本のみで、それは ALE として取込済み |
| ランタイム類（OpenClaw / superpowers / fractal 等） | — | ループの実行基盤であって配布元ではない |

## 再発防止（常設化）

- `check_coverage.py` — 一次情報（sitemap / catalog.json / HuggingFace API / GitHub）と
  取込済みカタログを機械照合。取りこぼしがあれば非ゼロ終了
- `audit_quality.py` — 全ソース横断で、翻訳漏れ・4タイプ分類・カテゴリ日本語・
  slug重複・通し番号・出典URL・本文の有無を検査

```bash
python check_coverage.py && python audit_quality.py
```

いずれも現在オールグリーン。**「網羅した」と主張する代わりに、網羅を検証する手続きを持つ**方針に変更した。
