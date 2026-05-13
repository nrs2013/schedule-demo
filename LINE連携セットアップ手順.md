# LINE 連携セットアップ手順（のむさん用）

> SCHEDULE STUDIO から「公演ごとの LINE グループ」にプッシュ送信できるようにする手順。
> 一度だけやればよい。所要 30〜45 分。

---

## 完成後の運用イメージ

1. スタッフ全員：SCHEDULE STUDIO 公式アカウントを友だち追加（リッチメニューでアプリ操作）
2. のむさん：公演ごとに **LINE グループを作る**（例：「BACKS LIVE スタッフ」）
3. のむさん：そのグループに **SCHEDULE STUDIO Bot を招待**
4. アプリ：自動でグループ ID を保存
5. のむさん：pc-edit の各 CONCERT に「LINE グループ」を紐付ける
6. INFO タブから送信すると **その公演のグループだけに届く**

---

## 手順

### Step 1: LINE Messaging API を有効化（5 分）

1. ブラウザで `https://manager.line.biz/account/@242uoxqo/` を開く（SCHEDULE STUDIO 公式アカウントの管理画面）
2. 左メニュー：**設定** → **Messaging API**
3. 「Messaging API を利用する」ボタンをクリック
4. 開発者情報を入力（既にあればスキップ）
5. プロバイダーを選ぶ or 新規作成（プロバイダー名は何でも良い、例「nrs2013」）
6. 「OK」「同意」を進む → Messaging API 有効化完了

### Step 2: Channel Access Token を取得（5 分）

1. `https://developers.line.biz/console/` を開く（LINE Developers）
2. Step 1 で作ったプロバイダー → SCHEDULE STUDIO チャネル をクリック
3. タブ：**Messaging API 設定**
4. ページ下部「チャネルアクセストークン（長期）」セクションの「発行」ボタン
5. **表示されたトークンをコピー**（後で GAS に貼る）

> ⚠️ トークンは秘密。誰にも教えない。LINE Developers 以外には貼らない。

### Step 3: GAS スクリプトを公開（15 分）

1. ブラウザで `https://script.google.com` を開く（Google にログイン状態で）
2. **新しいプロジェクト** をクリック
3. 左の **コード.gs** ファイルを全選択して削除
4. このフォルダの `line-gas-bot.gs` の中身を全部コピーして貼り付け
5. 一番上の `CHANNEL_ACCESS_TOKEN = 'PASTE_YOUR_CHANNEL_ACCESS_TOKEN_HERE'` の引用符の中を、Step 2 でコピーしたトークンに置き換える
6. プロジェクト名を「SCHEDULE STUDIO LINE Bot」とか分かりやすい名前に
7. 右上の **デプロイ** → **新しいデプロイ**
8. 種類選択（歯車）→ **ウェブアプリ**
9. 説明：「v1」など何でも
10. アクセスできるユーザー：**全員**（重要！）
11. **デプロイ** ボタン
12. 認証ダイアログが出たら「アクセスを承認」→ Google アカウントを選択 → 「詳細」→「（プロジェクト名）に移動」→「許可」
13. 表示された **ウェブアプリ URL** をコピー（`https://script.google.com/macros/s/.../exec` の形）

### Step 4: LINE Webhook URL を設定（5 分）

1. LINE Developers の SCHEDULE STUDIO チャネル → **Messaging API 設定**
2. **Webhook URL** に Step 3 でコピーした GAS の URL を貼って「更新」
3. **Webhook の利用** を **ON** に
4. 「検証」ボタンで「成功」が出れば OK

### Step 5: 応答メッセージを OFF にする（重要・5 分）

1. 同じ Messaging API 設定ページ
2. **応答メッセージ** を **OFF**（友だち追加時の自動応答とかが邪魔になるため）
3. **あいさつメッセージ** はお好みで（OFF 推奨）
4. **Webhook** は **ON** のまま

### Step 6: SCHEDULE STUDIO 側に GAS URL を貼る（2 分）

1. PC で `pc-edit.html` を開いて INFO タブ
2. 「▶ LINE 連携 設定（初回のみ）」を開く
3. Step 3 でコピーした **GAS URL** を貼って「保存」
4. 「テスト送信」を押して動作確認（最初は登録グループがないからエラーかも → Step 7 へ）

### Step 7: 公演用 LINE グループを作る（5 分 / 公演ごと）

1. のむさんのスマホで LINE を開く
2. 公演用グループを新規作成（例：「BACKS LIVE スタッフ」）
3. メンバー：そのスタッフたち + **SCHEDULE STUDIO Bot を招待**
4. 招待された瞬間、Bot が「SCHEDULE STUDIO Bot が参加しました...」とメッセージを送る
5. pc-edit の INFO タブで「LINE プッシュ送信」ができるようになる

### Step 8: 公演とグループを紐付ける（R164 実装後）

> R164 で pc-edit に「現在の公演 → グループ選択」UI を追加する。実装後に手順追記。

---

## トラブルシューティング

- **Webhook 検証が失敗**：GAS のデプロイで「アクセスできるユーザー：全員」になってるか確認
- **Bot がグループに招待されない**：「グループ・複数人トークへの参加を許可」を LINE Developers で ON に（Messaging API 設定の下の方）
- **送信したのに届かない**：応答メッセージ OFF、Webhook ON を確認

---

## のむさんがやることサマリー

| Step | 何をする | 時間 |
|---|---|---|
| 1 | LINE 公式アカウント管理画面で Messaging API を有効化 | 5 分 |
| 2 | LINE Developers でトークン取得（コピーするだけ） | 5 分 |
| 3 | GAS にコードを貼って公開（Claude が用意したコードをコピペ） | 15 分 |
| 4 | LINE Webhook URL を設定 | 5 分 |
| 5 | 応答メッセージを OFF | 5 分 |
| 6 | GAS URL を SCHEDULE STUDIO に貼る | 2 分 |
| 7 | 公演用グループを作って Bot を招待 | 5 分 |

合計: 約 40 分（1 回だけ）

---

## ファイル

- `line-gas-bot.gs` ── GAS にコピペするコード（このフォルダ内）
- `LINE連携セットアップ手順.md` ── このファイル

困ったら Claude（このセッション）に「Step ○ で詰まった」と書き込んでください。
