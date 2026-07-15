const GH_REPO = 'hiroshi57/loop-dashboard';
const GH_BRANCH = 'main';
const LOG_PATH = 'data/analytics.jsonl';

/**
 * 記録済みの利用状況ログを集計して返す。
 * ダッシュボード側（解析ビュー）から読み込まれる想定。
 */
module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');

  try {
    const lines = await fetchLogLines();
    const summary = summarize(lines);
    res.status(200).json(summary);
  } catch (err) {
    res.status(200).json({ error: String(err), pageViews: 0, loopViews: {}, loopCopies: {}, painSelects: {} });
  }
};

async function fetchLogLines() {
  const apiUrl = `https://raw.githubusercontent.com/${GH_REPO}/${GH_BRANCH}/${LOG_PATH}`;
  const res = await fetch(apiUrl, { cache: 'no-store' });
  if (!res.ok) return [];
  const text = await res.text();
  return text.split('\n').filter(Boolean);
}

function summarize(lines) {
  let pageViews = 0;
  const loopViews = {};
  const loopCopies = {};
  const painSelects = {};
  let earliestAt = null;
  let latestAt = null;

  for (const line of lines) {
    let entry;
    try { entry = JSON.parse(line); } catch { continue; }

    if (entry.trackedAt) {
      if (!earliestAt || entry.trackedAt < earliestAt) earliestAt = entry.trackedAt;
      if (!latestAt || entry.trackedAt > latestAt) latestAt = entry.trackedAt;
    }

    switch (entry.event) {
      case 'page_view':
        pageViews += 1;
        break;
      case 'loop_view':
        if (entry.loopId) loopViews[entry.loopId] = (loopViews[entry.loopId] || 0) + 1;
        break;
      case 'loop_copy':
        if (entry.loopId) loopCopies[entry.loopId] = (loopCopies[entry.loopId] || 0) + 1;
        break;
      case 'pain_select':
        if (entry.painId) painSelects[entry.painId] = (painSelects[entry.painId] || 0) + 1;
        break;
      default:
        break;
    }
  }

  return {
    generatedAt: new Date().toISOString(),
    range: { from: earliestAt, to: latestAt },
    totalEvents: lines.length,
    pageViews,
    loopViews,
    loopCopies,
    painSelects,
  };
}
