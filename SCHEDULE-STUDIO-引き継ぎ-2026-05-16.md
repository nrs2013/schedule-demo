# SCHEDULE STUDIO 引き継ぎ書（2026-05-16 / R236 まで）

> 次のセッションの Claude へ：このファイルを **最初に必ず全部読んでから** のむさんに対応してください。
> 過去セッションで「PC ⇔ スマホ同期が壊れる」事故が複数発生。慎重に。

---

## 0. 即読みサマリ（最重要 3 行）

- **本番 URL**：https://nrs2013.github.io/schedule-studio/
- **最新コミット**：R236（`1e01d51`）/ main にあり
- **PC ⇔ スマホ Firebase 同期は R235 で R187 時代のフラット構造に戻した**。tek/main 二系統は完全撤去済み

---

## 1. のむさんから受けた絶対ルール（厳守）

### 1-1. Claude が完結する作業範囲
- ファイル編集（Edit / Write）、commit、push まで **Claude が直接実行**
- 動作確認用のターミナル操作は **のむさんに依頼しない**（git lock 解除など特殊例外あり）

### 1-2. のむさんに依頼してよい唯一のこと
- スマホでの最終動作確認（プライベートブラウズで本番 URL を見る）のみ
- 1 回の作業で何度もスマホ確認を依頼しない

### 1-3. 質問・確認の出し方
- 質問は **箇条書きで簡潔に**。長い解説禁止
- 結論 → 必要なら根拠の順。1 メッセージ 200 字以内目安
- 専門用語禁止
- **舞台用語禁止**（過去に「舞台用語使うな」と明示された）
- コードは絶対みせない

### 1-4. のむさんの返事を待つ時間の使い方
- 返事がない時間は **他の安全に進められるタスクを並列で進める**
- 進めた内容は次のメッセージで「裏で X 完了しました」と簡潔に報告
- 手を止めて待つのは NG

### 1-5. リスクの高い改修の判断
- UI 大改修・複数機能の再導入 → **箇条書きで選択肢を提示**、判断を仰ぐ
- 単純なバグ修正・コードロジック修正 → Claude の判断で **そのまま push**
- 失敗したらバックアップから戻す。バックアップは大改修前に必ず作成

### 1-6. Subagent の活用
- バグの原因が分からない・複雑なコード調査が必要なときは **必ず Subagent（Agent ツール）を使う**
- 単独で推測しない → Subagent に並列調査させて結論を出す
- 「徹底的に調べて」と言われたら Subagent 一択

### 1-7. AskUserQuestion の活用
- 複数の方向性がある質問は **AskUserQuestion ツール** で選択肢を見せる
- ただし、稀にツールがエラーで止まることがある。その時はテキストで選択肢を提示

### 1-8. `ssp` エイリアス
- のむさんのターミナルに `ssp` エイリアスが登録済み（`~/.zshrc`）
- 中身：`cd ~/Documents/schedule-studio-r135-work && rm -f .git/HEAD.lock .git/index.lock 2>/dev/null; git push origin main`
- Claude が commit したら **「ターミナルで ssp 実行してください」** だけ伝えれば push 完了
- git lock 問題で commit 自体が詰まることがある。その時はのむさんに `rm -f .git/*.lock && git commit ...` を依頼

---

## 2. ファイル構成（ワークスペース）

```
~/Documents/schedule-studio-r135-work/
├── pc-edit.html                # PC 編集版（メインアプリ、~10000 行）
├── phone-staff.html            # スマホ STAFF 版（~4100 行）
├── phone-artist.html           # スマホ ARTIST 版（~4000 行）
├── pc-hotel.html               # PC HOTEL 編集版
├── index.html                  # 入口メニュー
├── line-gas-bot.gs             # GAS スクリプト雛形（Channel Token 含む実体）
├── LINE連携セットアップ手順.md
├── R146-R155-作業ログ.md
├── R146-R176-作業ログ.md
├── R186-R187-動作確認チェックリスト.md
├── SCHEDULE-STUDIO-引き継ぎ-2026-05-15.md    # 前回引き継ぎ
├── SCHEDULE-STUDIO-引き継ぎ-2026-05-16.md    # ★このファイル
├── *-rNNN-backup.html          # バックアップ群
│   ├── phone-staff-r187-backup.html  # 同期が動いていた時代のお手本
│   └── phone-artist-r187-backup.html
└── push-and-verify-rNNN.sh     # 過去 push 用シェル
```

---

## 3. リポジトリ情報

- **GitHub**：`https://github.com/nrs2013/schedule-studio`
- **本番**：GitHub Pages（main ブランチ）
- **ローカル**：`~/Documents/schedule-studio-r135-work/`
- **push 方法**：のむさんが `ssp` 実行（前述）
- **lock 問題**：`.git/*.lock` が残るときは Claude では消せない。のむさんに `rm -f ~/Documents/schedule-studio-r135-work/.git/*.lock` を依頼

---

## 4. 今セッション（2026-05-16）でやったこと

### 4-1. LINE 関連の追加修正（R186〜R191）
- **R186**: GAS Bot に Flex Message メニュー追加。グループ招待時に自動送信＋「メニュー」キーワードで再送
- **R187**: pc-edit に「📋 メニューカード送信」ボタン追加
- **R188-R191**: スマホ版の R137（入り時間 ⇔ DAY SCHEDULE サブタブ統合）復元、カレンダーの endDate 対応、venue band（会場帯）実装

### 4-2. スマホ UI 統一（R215〜R217 + R210）
- 全カードを共通トークン（背景 `#1a1a1a`、ボーダー `0.5px solid #2c2c2c`、角丸 `8px`）に統一
- アクセント色を **オレンジ `#e89a4a` → クリームベージュ `#c8a878`** に全置換（R216）
- 文字サイズを 17/14/12/11 px の 4 段階に圧縮
- DAY SCHEDULE のカードをコンパクトに（時間 22→17px、ラベル 18→14px）
- `+追加`ボタンを固定幅 max-width:72px に
- タクシー行を 3 列 grid に（空列のガタつき解消）

### 4-3. スマホ機能追加
- 入り時間：認証不要で誰でも編集可（R195）
- 入り時間の編集シート（時間ピッカー対応）（R206）
- INFO の NEW POST 投稿機能（R202 + R207 で認証撤去）
- ホテルのタクシー配車・宿泊メンバー編集（要 PASS 認証）（R211）
- リハカウントダウンを DAY SCHEDULE のリハ終了時刻と連動（R213）
- 認証を sessionStorage 永続化（R231）

### 4-4. カレンダーバグ修正
- 連続イベント（本番 2 日連続など）を **先頭日に span 倍幅の 1 本の pill** として描画（R205）
- bar-end の `min-height: 12px` で空テキスト時の潰れ解消（R203）
- venue band の bar-start を `overflow:visible` + `has-band-start` クラスで前面表示（R197-R198）
- 長いラベルでカレンダーセルが横に広がる問題を `min-width: 0` で解消（R196）
- in-tour ハイライトを削除（PC 準拠）（R197）

### 4-5. PC 側機能修正
- Excel 取込：非表示シート除外（R221）、自動推奨撤去（R219）、独自モーダルでシート選択（R220）
- M# 列が空欄なら空欄表示（連番自動付与を撤去）（R222 + R223）
- タイトル空欄なら空欄表示（「（タイトル未定）」自動付与撤去）（R225）
- ドラッグ並び替えをハンドル（.drag）のみに限定（R224 + R226）

### 4-6. **R230 の失敗とロールバック（最重要）**

#### 経緯
- R230 でテクリハ／リハーサルのリセットボタンを分離するため、`rehearsalByDate[date][songId]` を `{ tek: {rhNo,tags,memo}, main: {rhNo,tags,memo} }` の **二系統構造** に拡張
- PC・スマホ両方で active mode（テクリハ/全体リハ）に応じて tek or main を読み書き
- **結果：PC が tek に書いた値はスマホの main では見えず、「同期されない」と認識された**

#### 修正試行（R232, R234）→ 失敗
- R232：reorder lock、自分の write 値以外を reject などの複雑なガード追加 → 同期が更に詰まる
- R234：「片側空ならフォールバック」→ 解消しきれず

#### **R235 で完全撤去（現状）**
- `rehearsalByDate[date][songId]` を R187 時代のフラット構造 `{ rhNo, tags, memo }` に戻す
- 起動時マイグレーション関数 `_r235MigrateRehFlat` で既存の `{tek, main}` データを main 優先で平坦化
- pc-edit, phone-staff, phone-artist の 3 ファイル全部に同じマイグレーション関数あり

#### R236：R232 の lock 系も完全撤去
- reorder lock 3 秒 → 撤去
- focusout 抑止フラグ → 撤去
- `__reloadSetlists` の lock チェック → 撤去
- drift 検知 interval の lock チェック → 撤去
- → R187 時代の素直な同期に戻った

---

## 5. 現状の既知の課題

### 5-1. 「リンクが詰まる」現象
- のむさんから「完全にはリンクしません。ちょっとリンクする場面もあります」と報告
- R236 で R232 の lock 系を全撤去した直後の状態
- **次セッションで真っ先に確認すべき**：PC で何か変更→スマホで即座に反映されるか
- もし詰まる感じが残っているなら、Firebase 接続の根本確認が必要

### 5-2. テクリハ／リハーサルのリセット分離
- 現状は **諦めている**（フラット構造なので区別不可）
- R235 のリセットボタンは「リハ計画（rhNo/tags/memo）を全曲分クリア、曲リストは残す」
- もし将来テクリハ／リハ別に持ちたければ、別キー（例：`tekRehearsalByDate`）として localStorage に保存する設計を検討
- 二系統構造（tek/main 統合）は同期問題を起こすので **絶対採用しない**

### 5-3. スマホでドラッグ並び替え対応していない
- PC のみ対応。スマホで曲順入れ替えしたい要望は出てない
- 必要になれば実装

### 5-4. LINE グループのリッチメニュー
- LINE 仕様で **グループにリッチメニューは出せない**（公式制限）
- 代替：「メニュー」とテキストすると Flex Message でメニューカードが出る方式
- ピン留めしてもらえばグループ画面上部に常時表示可能

---

## 6. 次にやるべきこと（優先度順）

### 6-1. 同期問題の最終確認
- [ ] PC で曲を追加 → スマホで即座に見えるか
- [ ] PC でタグ ON/OFF → スマホで即座に反映されるか
- [ ] スマホで入り時間追加 → PC で即座に見えるか
- [ ] 並び替え → 数秒後に戻らないか

### 6-2. 動作確認（のむさんにスマホで）
- [ ] 全タブの統一感（A 案 シック・ブラック × クリーム）
- [ ] 入り時間タブで時間が左・セクション名が右
- [ ] INFO で NEW POST 投稿できる
- [ ] HOTEL タブでタクシー・宿泊メンバー編集できる（PASS 認証後）
- [ ] CALENDAR で venue band（横浜アリーナなど）が連続日に1本のバーで表示
- [ ] DAY SCHEDULE のカードがコンパクト

### 6-3. ペンディング機能
- リッチメニュー的な体験をグループでも → ピン留め運用で対応済み（PC側からも送信可）

---

## 7. 同期構造（重要：絶対に壊さないこと）

### 7-1. localStorage キー（共通）
- `schedule-studio:setlists:v1`：曲リスト（全 setlist の配列）
- `schedule-studio:activeSetlistId`：現在アクティブな setlist の ID
- `schedule-studio:rehearsalByDate:v1`：日付別のリハ計画 `{date: {songId: {rhNo, tags, memo}}}`
- `schedule-studio:dayEvents:v1`：日付別 DAY SCHEDULE
- `schedule-studio:arrivalSectionsByDate:v1`：入り時間
- `schedule-studio:hotels:v1`：ホテル
- `schedule-studio:calEvents:v1`：カレンダーイベント
- `schedule-studio:venueGroups:v1`：会場バンド
- `schedule-studio:infoHistory:v1`：INFO 投稿履歴
- `schedule-studio:concerts:v1`：公演リスト
- `schedule-studio:active-concert-id`：現在の公演 ID
- `schedule-studio:line-gas-url`：LINE GAS URL

### 7-2. 同期の仕組み
- pc-edit.html / phone-staff.html / phone-artist.html それぞれが Firebase Realtime DB に接続
- L100 周辺の IIFE で `localStorage.setItem` を hook（フック）して、`schedule-studio:` で始まるキーを自動で Firebase に書き込む
- 他端末からの child_changed イベントで localStorage を更新し、`__reloadXxx` 関数で in-memory を更新 → 再描画
- **絶対に Firebase 直接書き込み（`.set()`）を hook と二重で行わない**（R232 で失敗した）

### 7-3. データ構造（フラット）
- `rehearsalByDate[date][songId] = { rhNo: null, tags: [], memo: '' }`
- **二系統（tek/main）構造は採用しない**（R230 の失敗を繰り返さない）

---

## 8. のむさんの環境

- **GitHub ユーザー名**：`nrs2013`
- **Mac**：MacBook Air-18
- **ターミナル**：zsh
- **ssp エイリアス**：登録済み（`~/.zshrc`）
- **Email**：nomura0913@gmail.com
- **Cowork mode**：Claude desktop で動作中

---

## 9. 申し送り（次セッションの Claude へ最初のメッセージ案）

新セッションでのむさんが「続きやろう」と言ったら：

1. このファイル（`SCHEDULE-STUDIO-引き継ぎ-2026-05-16.md`）を全部読む
2. 前回引き継ぎ書（`SCHEDULE-STUDIO-引き継ぎ-2026-05-15.md`）も合わせて読む
3. のむさんに「**前回 R236 まで完了してます。PC ⇔ スマホ同期を R187 時代のフラット構造に戻して、tek/main 二系統は完全撤去しました。今日は何やります？**」と短く確認
4. **最優先確認事項**：「同期は瞬時に効いてますか？まだ詰まりますか？」

---

## 10. リンク

- 本番 PC：https://nrs2013.github.io/schedule-studio/pc-edit.html
- 本番スマホ STAFF：https://nrs2013.github.io/schedule-studio/phone-staff.html
- 本番スマホ ARTIST：https://nrs2013.github.io/schedule-studio/phone-artist.html
- GitHub：https://github.com/nrs2013/schedule-studio
- GAS エディタ：https://script.google.com/d/1OhsCXbA6GyXcOmyCUBrAmD7DBoO7dYYnAp-rOOnoW7o3zqtPtESYA1KJ/edit

---

おわり。引き継ぎ書 作成者：Claude（2026-05-16 セッション、R236 完了時点）
