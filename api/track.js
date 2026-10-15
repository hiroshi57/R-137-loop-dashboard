const GH_REPO = 'hiroshi57/loop-dashboard';
const GH_BRANCH = 'main';
const LOG_PATH = 'data/analytics.jsonl';

const ALLOWED_EVENTS = new Set([
  'page_view', 'loop_view', 'loop_copy', 'pain_select',
  'loop_download',  // SKILL.md / Markdown / JSON として持ち出した
  'loop_run',       // ループを実際に回した結果（成功・停止理由を記録する）
]);

// loop_run の停止理由。記事の「どの条件で止まったかを残す」に対応する
const STOP_REASONS = new Set(['success', 'max_turns', 'budget', 'no_progress', 'abort', 'manual']);
const SOURCES = new Set(['DI', 'FF', 'EL', 'LE', 'ALH', 'ALE', 'AW', 'custom']);

/**
 * ダッシュボードの利用状況（どのループが見られているか）を記録する。
 * Vercel はサーバーレスでファイル書き込みができないため、
 * GitHub Contents API 経由で data/analytics.jsonl に追記する
 * （chatwork-x-automation の /api/aff-click と同じ設計）。
 */
module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.status(204).end();
    return;
  }
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'method not allowed' });
    return;
  }

  const body = req.body || {};
  const event = body.event;
  const loopId = typeof body.loopId === 'string' ? body.loopId.slice(0, 100) : undefined;
  const painId = typeof body.painId === 'string' ? body.painId.slice(0, 100) : undefined;

  if (!ALLOWED_EVENTS.has(event)) {
    res.status(400).json({ error: 'invalid event' });
    return;
  }

  // ソース種別（DI/FF/EL/…）。どのソースのループが使われているかの判断に使う
  const src = SOURCES.has(body.src) ? body.src : undefined;
  // 持ち出し形式（skill / md / json）
  const fmt = typeof body.fmt === 'string' ? body.fmt.slice(0, 20) : undefined;
  // 実行結果（loop_run のときだけ）
  const stopReason = STOP_REASONS.has(body.stopReason) ? body.stopReason : undefined;
  const turns = Number.isFinite(body.turns) ? Math.min(Math.max(0, body.turns | 0), 9999) : undefined;
  const note = typeof body.note === 'string' ? body.note.slice(0, 200) : undefined;

  if (event === 'loop_run' && !stopReason) {
    res.status(400).json({ error: 'loop_run requires stopReason' });
    return;
  }

  const entry = {
    event,
    loopId,
    painId,
    src,
    fmt,
    stopReason,
    turns,
    note,
    trackedAt: new Date().toISOString(),
  };

  // Vercel のサーバーレス関数はレスポンス送信後の非同期処理継続を保証しないため、
  // 記録の完了を待ってからレスポンスを返す（fire-and-forget だと記録が消える）。
  try {
    await appendLog(entry);
    res.status(204).end();
  } catch (err) {
    res.status(200).json({ ok: false, error: String(err) });
  }
};

async function appendLog(entry) {
  const token = process.env.GH_PAT;
  if (!token) return;

  const line = JSON.stringify(entry);
  const apiUrl = `https://api.github.com/repos/${GH_REPO}/contents/${LOG_PATH}`;
  const headers = {
    Authorization: `token ${token}`,
    Accept: 'application/vnd.github+json',
  };

  const getRes = await fetch(`${apiUrl}?ref=${GH_BRANCH}`, { headers });
  let sha;
  let existingContent = '';
  if (getRes.ok) {
    const data = await getRes.json();
    sha = data.sha;
    existingContent = Buffer.from(data.content, 'base64').toString('utf-8');
  }

  const newContent = existingContent + (existingContent.endsWith('\n') || !existingContent ? '' : '\n') + line + '\n';

  const putRes = await fetch(apiUrl, {
    method: 'PUT',
    headers: { ...headers, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: `chore: record ${entry.event} [skip ci]`,
      content: Buffer.from(newContent, 'utf-8').toString('base64'),
      sha,
      branch: GH_BRANCH,
    }),
  });

  if (!putRes.ok) {
    throw new Error(`GitHub Contents API PUT failed: ${putRes.status}`);
  }
}
