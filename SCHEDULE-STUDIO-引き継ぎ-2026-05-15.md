# SCHEDULE STUDIO 引き継ぎ書（2026-05-15 / R185 まで完了）

> 次のセッションの Claude へ：このファイルを **最初に必ず全部読んでから** のむさんに対応してください。
> 過去セッションで「Bot」「リッチメニュー」など重要事項を Claude が忘れている事故が多発。

---

## 0. 即読みサマリ（最重要 3 行）

- **LINE 連携セットアップ全部完了**（GAS デプロイ済み、Webhook ON、Bot がグループ通知 OK、リッチメニュー hash routing 復活）
- **本番 URL**：https://nrs2013.github.io/schedule-studio/
- **最新コミット**：R185（`808754e`）/ main にあり

---

## 1. このセッション（2026-05-15）でやったこと

### 1-1. LINE 連携セットアップ実行（メイン作業）

|手順|状態|内容|
|---|---|---|
|GAS デプロイ|✅完了|v2、アクセス権「全員」（最初 v1 はGoogle アカウント限定で 401）|
|Channel Access Token|✅GAS内に保管|`line-gas-bot.gs` の `CHANNEL_ACCESS_TOKEN` 定数|
|Webhook URL 登録|✅完了|LINE Developers Webhook URL に GAS URL を登録|
|Webhook の利用|✅ON||
|応答メッセージ|✅OFF|LINE Official Account Manager|
|あいさつメッセージ|✅OFF|同上|
|グループトーク参加許可|✅ON|これが OFF だと Bot が招待瞬間に退会する重大設定|
|Bot 招待テスト|✅成功|「テスト」グループ作成 → Bot が groupId 自動保存 → 挨拶メッセージ送信|
|公演に紐付け|✅完了|pc-edit INFO タブで紐付けて、テスト送信で実際に LINE 「テスト」グループに届くこと確認|
|リッチメニュー画像|✅既存|6ボタン構成（TODAY/CALENDAR/REHEARSAL/INFO/HOTEL/PASS）すでにLINE側にアップ済|
|リッチメニュー hash routing|✅R185で復活|R138で実装→R147ロールバックで失われていた機能を再導入|

### 1-2. コード修正リスト（R184-R185）

|Rev|内容|ファイル|
|---|---|---|
|R184|`__r125TestLine` を新フォーマット対応に修正（旧：`{type:'test',subject,body}` → 新：`{action:'push',to:groupId,text}`）。現在の公演に紐付いた lineGroupId を読んで送信先を決める|pc-edit.html|
|R185|LINE リッチメニュー hash routing 軽量版を再導入。phone-staff/artist の末尾に追加。MutationObserver なし、起動時(120ms後)+hashchangeで `location.hash` → `show()` を呼ぶだけのシンプル版|phone-staff.html / phone-artist.html|

---

## 2. LINE 連携の完成構成（必ず把握すること）

### 2-1. アカウント情報

- **LINE 公式アカウント**：`SCHEDULE STUDIO`
- **ベーシック ID**：`@242uoxqo`（変更不可、プレミアム ID 取得は年 1200 円）
- **チャネル ID**：2010077319（LINE Developers）
- **管理者**：nomura0913@gmail.com（のむさん）

### 2-2. GAS（Google Apps Script）

- **プロジェクト ID**：`1OhsCXbA6GyXcOmyCUBrAmD7DBoO7dYYnAp-rOOnoW7o3zqtPtESYA1KJ`
- **Web App URL**：`https://script.google.com/macros/s/AKfycbxSI7VkxJAO59dG6zqXvYBGy0qAkNapfWwu3P7zEWKz7I5MHowvPPFQbp-TuSkunUyQrg/exec`
- **バージョン**：v2（v1 はアクセス権「Google アカウントを持つ全員」で 401 になるので使わない）
- **デプロイ ID**：`AKfycbxSI7VkxJAO59dG6zqXvYBGy0qAkNapfWwu3P7zEWKz7I5MHowvPPFQbp-TuSkunUyQrg`
- **アクセス権**：全員（Anyone）

### 2-3. Bot の挙動仕様

- **doPost** で `body.events` があれば LINE Webhook、`body.action` があれば SCHEDULE STUDIO のアクション
- アクション一覧：
  - `push`：`{action:'push', to:groupId, text}` でグループにメッセージ送信
  - `listGroups`：保存済み groupId と groupName のリスト返却
  - `getGroupName`：groupId からグループ名取得
  - `ping`：疎通確認
- **join イベント**：グループ招待時に groupId を ScriptProperties に保存、挨拶メッセージ送信
- **leave イベント**：保存済み groupId から削除
- **memberJoined**：グループ名リフレッシュ

### 2-4. SCHEDULE STUDIO 側との連携

- **localStorage キー**：
  - `schedule-studio:line-gas-url` → 上記 v2 URL
  - `schedule-studio:concerts:v1` → 各 concert に `lineGroupId` プロパティ
  - `schedule-studio:active-concert-id` → 現在の公演 ID
- **テスト送信**（R184）：`__r125TestLine()` が現在公演の groupId に向けて `action:'push'` で送る
- **CORS 回避**：`Content-Type: text/plain;charset=utf-8` で送る（`application/json` だと preflight で失敗）

### 2-5. リッチメニュー（6 ボタン構成）

LINE Official Account Manager → リッチメニューに既にアップロード済み。表示期間 2026/05/11 - 2030/12/31。

|位置|タイトル|URL|hash|
|---|---|---|---|
|左上|TODAY|`phone-staff.html#today`|schedule（DAY SCHEDULE）|
|中上|CALENDAR|`phone-staff.html#calendar`|tour-calendar|
|右上|REHEARSAL|`phone-staff.html#rehearsal`|rehearsal|
|左下|INFO|`phone-staff.html#info`|info|
|中下|HOTEL|`phone-staff.html#hotel`|hotel|
|右下|PASS|`phone-staff.html#pass`|pass|

**注意**：LINE リッチメニューは **個人トーク画面でのみ表示** される。**グループには表示されない**（LINE の仕様、回避不可）。

### 2-6. 運用フロー（覚えておくこと）

1. のむさん（or 現場マネージャー）が LINE で「SCHEDULE STUDIO」を友だち追加（URL or QR）
   - 友だち追加 URL：`https://line.me/R/ti/p/@242uoxqo`
   - 友だち追加が必要なのは **グループに Bot を招待する 1 人だけ**。他のスタッフは追加不要
2. その人が LINE でスタッフグループを作る（公演名を付ける）
3. グループ作成画面で「SCHEDULE STUDIO」を友だちから選んで追加 → Bot 自動参加挨拶
4. PC で pc-edit を開く → INFO タブ → 「グループ一覧を取得」または手動コピペで groupId を入力 → 保存
5. その公演を選んでる間、SCHEDULE STUDIO からのプッシュ通知はそのグループに届く

---

## 3. のむさんから受けた絶対ルール（厳守、これ違反するとセッション切られる）

### 3-1. Claude が完結する作業範囲
- ファイル編集（Edit / Write）、commit、**push まで Claude が直接実行**
- 動作確認用のターミナル操作は **のむさんに依頼しない**（git lock 解除など特殊例外あり）
- サンドボックスから git push は通常通る。`Operation not permitted` で lock 残るときだけのむさんに `rm -f .git/*.lock` 依頼

### 3-2. のむさんに依頼してよい唯一のこと
- スマホでの最終動作確認（プライベートブラウズで本番 URL を見る）のみ
- 1 回の作業で何度もスマホ確認を依頼しない

### 3-3. 質問・確認の出し方
- 質問は **箇条書きで簡潔に**。長い解説禁止
- 「確認して欲しいことは？」と聞かれたら、その時点での疑問・選択肢を **箇条書きで列挙**
- 結論 → 必要なら根拠の順。1 メッセージ 200 字以内目安
- 専門用語禁止。「Bot」も使うなら必ず「LINE 上の SCHEDULE STUDIO というアカウントの自動応答機能」と補足
- 舞台用語で噛み砕いて説明。コードは絶対みせない

### 3-4. のむさんの返事を待つ時間の使い方
- 返事がない時間は **他の安全に進められるタスクを並列で進める**
- 進めた内容は次のメッセージで「裏で X 完了しました」と簡潔に報告
- **手を止めて待つのは NG**

### 3-5. リスクの高い改修の判断
- UI 大改修・複数機能の再導入 → **箇条書きで選択肢を提示**、判断を仰ぐ
- 単純なバグ修正・コードロジック修正 → Claude の判断で **そのまま push**
- 失敗したらバックアップから戻す。バックアップは大改修前に必ず作成

### 3-6. Subagent の活用
- バグの原因が分からない・複雑なコード調査が必要なときは **必ず Subagent（Agent ツール）を使う**
- 単独で推測しない → Subagent に並列調査させて結論を出す
- 「徹底的に調べて」と言われたら Subagent 一択

### 3-7. AskUserQuestion の活用
- 複数の方向性がある質問は **AskUserQuestion ツール** で選択肢を見せる
- のむさんは「Other」で自由回答もできるが、選択肢があると圧倒的に楽

---

## 4. 次にやるべきこと（優先度順）

### 4-1. 動作確認（のむさんにスマホで）
- [ ] R185 反映後、LINE リッチメニューのボタンを押して、該当タブが開くか
  - TODAY → DAY SCHEDULE
  - CALENDAR → ツアーカレンダー
  - REHEARSAL → リハーサル
  - INFO → INFO
  - HOTEL → ホテル
  - PASS → 入場認証

### 4-2. 中期実装案（のむさん希望、Phase 分けで）
- **自動紐付け実装**（earlier の議論で「ボタン押すだけ」案 B 選んでた）
  - Bot がグループに招待された瞬間、LINE で「どの公演？」と公演ボタン付きメッセージを送る（Flex Message）
  - スタッフがボタンを 1 個タップ → groupId と公演 ID を自動紐付け
  - GAS 側の追加実装：handleLineWebhook の join イベントで Flex Message 送信、postback で紐付け処理
  - SCHEDULE STUDIO 側：concerts の lineGroupId を Firebase 経由で更新

### 4-3. ID 検索を有効化したいか確認
- 現状の `@242uoxqo` は未認証アカウントなので ID 検索でヒットしない可能性
- プレミアム ID（年 1200 円）取得すれば `@nrs-stage` みたいに変更可能
- 多分実用上は QR / URL 配布で十分なので、判断はのむさんに

---

## 5. ファイル構成（ワークスペース）

```
~/Documents/schedule-studio-r135-work/
├── pc-edit.html               # PC 編集版（メインアプリ、~9300 行）
├── phone-staff.html           # スマホ STAFF 版（~3900 行、R185 hash router 含む）
├── phone-artist.html          # スマホ ARTIST 版（~3850 行、R185 hash router 含む）
├── pc-hotel.html              # PC HOTEL 編集版
├── index.html                 # 入口メニュー
├── line-gas-bot.gs            # GAS スクリプト雛形（Channel Token 含む実体）
├── LINE連携セットアップ手順.md   # 初回セットアップ手順書
├── R146-R155-作業ログ.md       # 古い作業ログ
├── R146-R176-作業ログ.md       # R176 までの作業ログ
├── SCHEDULE-STUDIO-引き継ぎ-2026-05-15.md  # ★このファイル（最重要）
├── *-rNNN-backup.html         # バックアップ群
└── push-and-verify-rNNN.sh    # 過去 push 用シェル
```

## 6. リポジトリ情報

- **GitHub**：`https://github.com/nrs2013/schedule-studio`
- **本番**：GitHub Pages（main ブランチ）
- **ローカル**：`~/Documents/schedule-studio-r135-work/`
- **push 方法**：サンドボックス内 bash で `git push origin main` で通常通る
- **lock 問題**：`.git/*.lock` が残るときは Claude では消せない（macOS 仕様、サンドボックスから unlink できない）。のむさんに `rm -f ~/Documents/schedule-studio-r135-work/.git/*.lock` を依頼

---

## 7. トラブルシューティング集

|症状|原因|対処|
|---|---|---|
|LINE「検証」が 302 Found|GAS WebApp の仕様（POST 受信時に内部リダイレクト）|無視して OK。本番運用は問題なく動く（実例で確認済み）|
|LINE「検証」が 401 Unauthorized|GAS デプロイのアクセス権が「Google アカウントを持つ全員」になってる|「全員（Anyone）」に変更して再デプロイ。デプロイ ID 変わるので Webhook URL 再登録|
|Bot がグループ参加直後に退会|LINE Official Account Manager の「グループトーク参加許可」が無効|アカウント設定 → 機能の利用 → トークへの参加 → 「参加を許可する」に変更|
|テスト送信ボタンが LINE に届かない|R184 以前の旧フォーマット送信|R184 で修正済み（`__r125TestLine` 関数）|
|`Failed to fetch` で GAS 呼べない|CORS preflight|`Content-Type: text/plain;charset=utf-8` で送る|
|git の `.lock` ファイルで詰まる|サンドボックスからは unlink できない|のむさんに `rm -f .git/*.lock` 依頼|
|GitHub push が `fetch first` で reject|リモートに先行 commit|`git pull --rebase origin main && git push origin main`|
|スマホで矢印「›」が押せない|R138 hash router の残骸 or var/let の問題|R154 で完全修正済み|
|サブタブが消える|R138 hash router の影響|R147 ロールバック後の R168 起動時 show() で対処|
|drift 検知で入力が消える|R100/R157/R158 の interval が入力中も走る|R172 で `_r172IsEditing` ガード追加|
|Excel 取込後に新曲が消える|Firebase echo で旧データに巻き戻る|R173 で echo 抑止 + reload ガード|
|RH# 編集が保存されない|blur が bubble しない|R175 で `focusout` に変更|

---

## 8. SKILL.md 更新案

`/var/folders/.../skills/schedule-studio/SKILL.md` は read-only で Claude からは書けません。

のむさんが手動で更新する場合は、上記の **3. 絶対ルール** と **2. LINE 連携の完成構成** を SKILL.md の該当セクションに追記してください。場所：

```
/var/folders/kn/wfht75ks2zz89fhkkhjxrksw0000gn/T/claude-hostloop-plugins/cadd1cadf68c3420/skills/schedule-studio/SKILL.md
```

ただし、上記パスは temp フォルダなので、本来の skill ソースは Claude Plugin の管理画面から編集する必要があります。

---

## 9. 申し送り（次セッションの Claude へ最初のメッセージ案）

新セッションでのむさんが「続きやろう」と言ったら、最初に：

1. このファイル（`SCHEDULE-STUDIO-引き継ぎ-2026-05-15.md`）を全部読む
2. のむさんに「**前回 R185 まで完了してます。LINE 連携 + リッチメニュー hash routing が動いてる状態です。今日は何やります？**」と短く確認
3. やることリストは **4-1 動作確認** か **4-2 自動紐付け実装** が優先候補

---

おわり。引き継ぎ書 作成者：Claude（2026-05-15 セッション）
