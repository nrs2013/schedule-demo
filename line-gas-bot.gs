/**
 * SCHEDULE STUDIO ↔ LINE Bot 連携 (Google Apps Script)
 *
 * 機能:
 *  1. LINE 公式アカウント Bot が LINE グループに招待されたら、groupId を自動保存
 *  2. SCHEDULE STUDIO (pc-edit.html) から HTTP POST で「このグループに送って」と
 *     リクエストすると、LINE Push API でメッセージ送信
 *  3. グループ一覧を取得（pc-edit.html がドロップダウンで選べるように）
 *
 * セットアップ手順:
 *  ① LINE 公式アカウント管理画面で Messaging API を有効化
 *  ② LINE Developers でチャネルアクセストークン (long-lived) を発行
 *  ③ そのトークンを下の CHANNEL_ACCESS_TOKEN に貼る
 *  ④ このスクリプトを「ウェブアプリ」としてデプロイ (アクセス権: 全員)
 *  ⑤ デプロイで得た URL を LINE Webhook URL に登録 (LINE Developers)
 *  ⑥ 同じ URL を pc-edit.html の INFO タブ「LINE 連携 設定」に貼る
 *  ⑦ のむさんが自分の LINE で「○○公演スタッフ」グループを作り、
 *     SCHEDULE STUDIO Bot を招待 → groupId が自動保存される
 *  ⑧ pc-edit.html の各 CONCERT に「グループ ID」を紐付ければ
 *     公演切替で送信先グループも自動切替
 */

// ★ ここに LINE Developers で取得した Channel Access Token を貼る ★
const CHANNEL_ACCESS_TOKEN = 'PASTE_YOUR_CHANNEL_ACCESS_TOKEN_HERE';

// ────────────────────────────────────────────────────────────
// エントリポイント
// ────────────────────────────────────────────────────────────
function doPost(e) {
  let body;
  try {
    body = JSON.parse(e.postData.contents);
  } catch (err) {
    return _json({ ok: false, error: 'invalid JSON' });
  }

  // LINE Webhook (events 配列が来る)
  if (body.events) {
    return handleLineWebhook(body);
  }

  // SCHEDULE STUDIO からのアクション
  switch (body.action) {
    case 'push':
      return handlePush(body);
    case 'pushMenu':
      return handlePushMenu(body);
    case 'listGroups':
      return handleListGroups();
    case 'getGroupName':
      return handleGetGroupName(body);
    case 'ping':
      return _json({ ok: true, msg: 'pong' });
    default:
      return _json({ ok: false, error: 'unknown action: ' + body.action });
  }
}

function doGet(e) {
  // 動作確認用
  return _json({ ok: true, msg: 'SCHEDULE STUDIO LINE Bot is running' });
}

// ────────────────────────────────────────────────────────────
// LINE Webhook 受信
// ────────────────────────────────────────────────────────────
function handleLineWebhook(body) {
  const props = PropertiesService.getScriptProperties();

  (body.events || []).forEach(function (event) {
    // グループに招待された
    if (event.type === 'join' && event.source && event.source.type === 'group') {
      const groupId = event.source.groupId;
      let groupName = '';
      try {
        const res = UrlFetchApp.fetch(
          'https://api.line.me/v2/bot/group/' + groupId + '/summary',
          {
            method: 'get',
            headers: { Authorization: 'Bearer ' + CHANNEL_ACCESS_TOKEN },
            muteHttpExceptions: true
          }
        );
        const data = JSON.parse(res.getContentText());
        groupName = data.groupName || '';
      } catch (e) {}

      const groups = JSON.parse(props.getProperty('groups') || '[]');
      if (!groups.find(function (g) { return g.id === groupId; })) {
        groups.push({
          id: groupId,
          name: groupName,
          joinedAt: Date.now()
        });
        props.setProperty('groups', JSON.stringify(groups));
      }

      // 招待挨拶 + メニューカード自動送信
      try {
        pushToGroup(
          groupId,
          'SCHEDULE STUDIO Bot が参加しました。\n' +
            'グループ名: ' + (groupName || '(未設定)') + '\n\n' +
            '下のメニューカードを長押し →「アナウンス」で固定すると、\n' +
            'グループ画面の上部に常時表示されて便利です。\n\n' +
            '※もう一度出したい時は、このグループに「メニュー」と入力してください。'
        );
      } catch (e) {}
      // 続けてメニュー Flex も送る
      try {
        pushFlexToGroup(groupId, 'SCHEDULE STUDIO メニュー', buildMenuFlex());
      } catch (e) {}
    }

    // グループから外れた
    if (event.type === 'leave' && event.source && event.source.type === 'group') {
      const groupId = event.source.groupId;
      const groups = JSON.parse(props.getProperty('groups') || '[]');
      const filtered = groups.filter(function (g) { return g.id !== groupId; });
      props.setProperty('groups', JSON.stringify(filtered));
    }

    // メンバー参加 (グループ名が後から変わる場合の追従)
    if (event.type === 'memberJoined' && event.source && event.source.type === 'group') {
      _refreshGroupName(event.source.groupId);
    }

    // テキストメッセージ受信 → 「メニュー」キーワードで Flex 返信
    if (event.type === 'message' && event.message && event.message.type === 'text') {
      const raw = (event.message.text || '').trim();
      const norm = raw.toLowerCase()
        .replace(/ﾒﾆｭｰ/g, 'メニュー');
      if (
        norm === 'メニュー' ||
        norm === 'めにゅー' ||
        norm === 'menu' ||
        norm === 'menyu'
      ) {
        const target =
          (event.source && (event.source.groupId || event.source.roomId || event.source.userId)) || null;
        if (target) {
          try {
            pushFlexToGroup(target, 'SCHEDULE STUDIO メニュー', buildMenuFlex());
          } catch (e) {}
        }
      }
    }
  });

  return _json({ ok: true });
}

// ────────────────────────────────────────────────────────────
// メニュー Flex Message（6ボタン）
// ────────────────────────────────────────────────────────────
function buildMenuFlex() {
  const base = 'https://nrs2013.github.io/schedule-studio/phone-staff.html';
  const btn = function (label, hash, bg) {
    return {
      type: 'button',
      style: 'primary',
      color: bg,
      height: 'md',
      action: { type: 'uri', label: label, uri: base + '#' + hash }
    };
  };
  return {
    type: 'bubble',
    size: 'mega',
    header: {
      type: 'box',
      layout: 'vertical',
      backgroundColor: '#00B900',
      paddingAll: '16px',
      contents: [
        { type: 'text', text: 'SCHEDULE STUDIO', color: '#FFFFFF', weight: 'bold', size: 'lg' },
        { type: 'text', text: '知りたい情報をタップしてください', color: '#FFFFFF', size: 'sm', margin: 'xs' }
      ]
    },
    body: {
      type: 'box',
      layout: 'vertical',
      spacing: 'md',
      paddingAll: '14px',
      contents: [
        btn('TODAY',     'today',     '#D85A30'),
        btn('CALENDAR',  'calendar',  '#185FA5'),
        btn('REHEARSAL', 'rehearsal', '#534AB7'),
        btn('INFO',      'info',      '#0F6E56'),
        btn('HOTEL',     'hotel',     '#854F0B'),
        btn('PASS',      'pass',      '#993556'),
        {
          type: 'text',
          text: 'このカードを長押し →「アナウンス」で上部に固定できます',
          size: 'xs',
          color: '#888888',
          wrap: true,
          margin: 'md',
          align: 'center'
        }
      ]
    }
  };
}

function pushFlexToGroup(groupId, altText, contents) {
  const url = 'https://api.line.me/v2/bot/message/push';
  const payload = {
    to: groupId,
    messages: [{ type: 'flex', altText: altText, contents: contents }]
  };
  return UrlFetchApp.fetch(url, {
    method: 'post',
    contentType: 'application/json',
    headers: { Authorization: 'Bearer ' + CHANNEL_ACCESS_TOKEN },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  });
}

function _refreshGroupName(groupId) {
  try {
    const res = UrlFetchApp.fetch(
      'https://api.line.me/v2/bot/group/' + groupId + '/summary',
      {
        method: 'get',
        headers: { Authorization: 'Bearer ' + CHANNEL_ACCESS_TOKEN },
        muteHttpExceptions: true
      }
    );
    const data = JSON.parse(res.getContentText());
    if (!data || !data.groupName) return;
    const props = PropertiesService.getScriptProperties();
    const groups = JSON.parse(props.getProperty('groups') || '[]');
    let updated = false;
    groups.forEach(function (g) {
      if (g.id === groupId && g.name !== data.groupName) {
        g.name = data.groupName;
        updated = true;
      }
    });
    if (updated) props.setProperty('groups', JSON.stringify(groups));
  } catch (e) {}
}

// ────────────────────────────────────────────────────────────
// SCHEDULE STUDIO → LINE Push 送信
// ────────────────────────────────────────────────────────────
function handlePush(body) {
  const to = body.to;
  const text = body.text || '';
  if (!to || !text) {
    return _json({ ok: false, error: 'missing to or text' });
  }
  try {
    const res = pushToGroup(to, text);
    return _json({ ok: true, lineStatus: res.getResponseCode() });
  } catch (e) {
    /* R398: 内部例外メッセージ (スタックトレース等) の外部漏洩を防止。
       詳細は GAS 実行ログ側で確認 */
    console.error('[GAS Error]', e);
    return _json({ ok: false, error: 'internal error' });
  }
}

function pushToGroup(groupId, text) {
  const url = 'https://api.line.me/v2/bot/message/push';
  const payload = {
    to: groupId,
    messages: [{ type: 'text', text: text }]
  };
  return UrlFetchApp.fetch(url, {
    method: 'post',
    contentType: 'application/json',
    headers: { Authorization: 'Bearer ' + CHANNEL_ACCESS_TOKEN },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  });
}

// ────────────────────────────────────────────────────────────
// メニューカード（Flex Message）を SCHEDULE STUDIO から手動送信
// ────────────────────────────────────────────────────────────
function handlePushMenu(body) {
  const to = body.to;
  if (!to) return _json({ ok: false, error: 'missing to' });
  try {
    const res = pushFlexToGroup(to, 'SCHEDULE STUDIO メニュー', buildMenuFlex());
    return _json({ ok: true, lineStatus: res.getResponseCode() });
  } catch (e) {
    /* R398: 内部例外メッセージ (スタックトレース等) の外部漏洩を防止。
       詳細は GAS 実行ログ側で確認 */
    console.error('[GAS Error]', e);
    return _json({ ok: false, error: 'internal error' });
  }
}

// ────────────────────────────────────────────────────────────
// グループ一覧の取得
// ────────────────────────────────────────────────────────────
function handleListGroups() {
  const props = PropertiesService.getScriptProperties();
  const groups = JSON.parse(props.getProperty('groups') || '[]');
  return _json({ ok: true, groups: groups });
}

function handleGetGroupName(body) {
  const groupId = body.groupId;
  if (!groupId) return _json({ ok: false, error: 'missing groupId' });
  try {
    const res = UrlFetchApp.fetch(
      'https://api.line.me/v2/bot/group/' + groupId + '/summary',
      {
        method: 'get',
        headers: { Authorization: 'Bearer ' + CHANNEL_ACCESS_TOKEN },
        muteHttpExceptions: true
      }
    );
    const data = JSON.parse(res.getContentText());
    return _json({ ok: true, groupName: data.groupName || '', memberCount: data.memberCount });
  } catch (e) {
    /* R398: 内部例外メッセージ (スタックトレース等) の外部漏洩を防止。
       詳細は GAS 実行ログ側で確認 */
    console.error('[GAS Error]', e);
    return _json({ ok: false, error: 'internal error' });
  }
}

// ────────────────────────────────────────────────────────────
// 共通ヘルパー
// ────────────────────────────────────────────────────────────
function _json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

// ────────────────────────────────────────────────────────────
// 動作確認用 (GAS エディタから直接実行)
// ────────────────────────────────────────────────────────────
function testListGroups() {
  const props = PropertiesService.getScriptProperties();
  console.log(props.getProperty('groups'));
}

function testPush() {
  // ★ ここに保存された groupId を貼ってテスト送信
  const groupId = 'PASTE_GROUP_ID_HERE';
  const res = pushToGroup(groupId, 'これは SCHEDULE STUDIO からのテスト送信です。');
  console.log('status:', res.getResponseCode());
  console.log('body:', res.getContentText());
}
