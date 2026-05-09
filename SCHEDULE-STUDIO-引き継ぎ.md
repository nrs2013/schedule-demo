# SCHEDULE STUDIO — 引き継ぎ書

> 最終更新: 2026-05-07
> 対象: のむさん（コンサート演出家、GitHub `nrs2013`、コード未経験）

---

## 1. プロジェクト概要

ツアー段取り管理 Web アプリ。櫻坂46 5th Anniversary Live ツアー（仮）の演出進行を管理する。

- **本番URL**: https://nrs2013.github.io/schedule-studio/pc-edit.html
- **リポジトリ**: https://github.com/nrs2013/schedule-studio
- **ローカル**: `~/Documents/schedule-studio/`
- **メイン編集画面（PC）**: `pc-edit.html`（単一HTMLファイル、約8000行）
- **スマホ閲覧画面**: `phone.html`（LINE経由でスタッフが見る）
- **HOTEL タブ**: `pc-hotel.html`（PC編集版・Excel取込・タクシー配車）
- **入口**: `index.html`（モック一覧）

---

## 2. 技術スタック

- **単一HTML**（ビルドツール無し）。CSS / JS は `<style>` と `<script>` インライン
- **永続化**: localStorage（複数キー、prefix `schedule-studio:*:v1`）
- **デプロイ**: GitHub Pages（自動デプロイ、push後30〜60秒で反映）
- **キャッシュ無効化**: `<meta name="build-version" content="YYYYMMDD.HHMMSS">` で自動更新検知（ページ内の小さい`<script>`がサーバ最新を fetch して比較→違ってたら強制リロード）
- **Firebase 同期**: Phase 1 完了（プロジェクト作成・Realtime DB・firebaseConfig 取得）。Phase 2 以降のコード組込は未着手。

---

## 3. 現状の機能（カレンダー中心）

### CALENDAR タブ（メイン）

- **連続グリッド縦スクロール**: 25ヶ月（前12 +今+後12）を1つの 7列グリッドに流す。月境界に full-width header は挟まらず、シームレスに繋がる。
- **左レール（月名表示）**: グリッドは8列構成（38px rail + 7×1fr days）。月の最初の週の rail に月数字を upright で表示（年が変わる時のみ年付き）。**スクロール中は sticky で左上に貼りつく**。
- **D&D**: ピル（イベント）も会場帯（venue band）もマウスドラッグで移動・伸縮。掴んだ位置をキープ（Google Calendar 風）。
- **イベント種別（パレット順）**: 現地仕込み → 仕込み → テクリハ → リハ → 本番 → 移動 → OFF/休
- **会場名（VENUES）**: 別欄に追加 → ブロック化 → カレンダーに drop して会場帯（band）を貼る運用。日数入力欄は撤去（band を伸ばすだけ）。
- **lane 自動配置**: 重なるイベントは別 lane に縦並び。月内で同じイベントは常に同じ lane（横ズレしない）。
- **偶数月／奇数月**: セル背景の濃淡で月の境目を視認しやすく。
- **会場帯と pill の縦位置整列**: 同じ週で band を持つセルがあると、band 無しのセルにも空 placeholder を入れて events 位置を揃える（D86）。

### 詳細パネル（右）

- ヘッダー：エディトリアル雑誌マスト式（D82）
  - 左：TOUR ラベル + ツアー名（contenteditable, 多段）
  - 中央：縦線
  - 右：大日付（30px/light）+ DAY/会場 チップ
- 詳細：日付選択時のみ、本番日の DOOR/SHOW 時刻 + MEMO（自由メモ・日付別保存）
- メモ欄は flex column + grid 1fr で**カレンダー下端まで自動拡張**（VENUES が増えても自動で詰まる）
- **撤去済み**: 重複日付ヘッダー、会場プルダウン、+会場ボタン、保存ボタン、エクスポート/インポートボタン、共有ボタン、公演グループセクション、案内文

### 配色（D84）

ステージ照明フィルター式（Lee/Rosco）:

- 本番: Surprise Pink `rgba(255,88,140,0.55)`
- 現地仕込み: Bright Sun `rgba(245,168,40,0.55)`
- 仕込み: Pale Amber `rgba(255,212,68,0.42)`
- テクリハ: Sky Blue `rgba(58,160,224,0.55)`
- リハ: Apple Green `rgba(126,216,72,0.50)`
- 移動/休: Light Lavender `rgba(184,168,216,0.42)`
- 会場帯（venue band）: **未確定**（warm gold に仮戻し中、別案検討中）

### マスター日付バー連動

- ページ上部の DAY/会場 チップは、CALENDAR タブの D&D 結果から動的算出（getTourInfo）
- 千秋楽ラベルは撤去、すべて DAY 1 / DAY 2 / DAY 3 表記
- calApi の各 mutation で日付バーも自動再描画

### REHEARSAL / DAY SCHEDULE / HOTEL / INFO タブ

- 既存機能あり、現在は CALENDAR を中心に改修中
- HOTEL は Excel取込・タクシー配車管理あり
- リハ番号・タグ・メモは日付別管理（rhNo / tags / memo）

---

## 4. 重要なグローバル変数 / API

```js
// 状態
calEvents          // pill イベント配列（type/date/endDate/label/venue 等）
venueGroups        // 会場帯（band）配列（id/startDate/endDate/venue/name）
venueDefinitions   // パレットの VENUES ブロック配列
calMemos           // 日付別メモ {dateKey: text}
calState           // {year, month, selected}
masterDateState    // {current: Date} ← マスター日付バーの現在日

// API（IIFE 間連携用）
window.__calApi = {
  getVenueGroupByDateKey, addVenueGroup, updateVenueGroup, deleteVenueGroup,
  listVenueDefinitions, addVenueDefinition, deleteVenueDefinition,
  getEventsByDateKey, listAllEvents, inheritVenueForDateKey,
  pushEvent, updateEvent, deleteEvent
}
window.__masterDateState
window.__refreshMasterDateBar = syncAllDateDisplays
```

---

## 5. デプロイ手順（重要）

ローカルからの GitHub への push は、サンドボックス内の git lock の関係で `~/Documents/schedule-studio/` 直接だと失敗する。

**運用方法**: `/tmp/ss-d67/` に fresh clone を維持し、そこに `pc-edit.html` をコピー → コミット & push。

```bash
# 初回（クローン）
cd /tmp && rm -rf ss-d67
git clone https://nrs2013:GHP_TOKEN@github.com/nrs2013/schedule-studio.git ss-d67

# 毎回の push 手順
cp "/Users/nomurayuuki/Documents/schedule-studio/pc-edit.html" /tmp/ss-d67/pc-edit.html
cd /tmp/ss-d67
git pull origin main
git add pc-edit.html
git commit -m "DXX: 説明"
git push origin main
```

**PAT**: のむさん本人の GitHub Settings → Developer settings → Personal access tokens から発行・取得（クローンURL に `https://nrs2013:<PAT>@github.com/...` の形で直書き運用。引き継ぎ書には PAT 値そのものは記載しない — GitHub のシークレットスキャナーが push をブロックするため）

**build-version 更新**: push のたびに `<meta name="build-version">` を `date '+%Y%m%d.%H%M%S'` の値で更新（自動更新検知に必要）。

---

## 6. このセッションの履歴（D67〜D86）

### 整列 / D&D 系

- D67: lane 割当で月内一貫の縦位置（重なりは別lane）
- D68: move-pill で grab 位置を保持（連結バー中央を掴んでも先頭にならない）
- D75: クリック時の月ジャンプバグ修正（anchor を TODAY 固定）
- D86: venue band の有無で同週の events 位置がズレる問題を修正（is-empty placeholder）

### レイアウト改造

- D71: 25ヶ月縦スタック化＋スティッキー曜日行＋「今月へ」ボタン
- D73: 連続グリッド化（month section 廃止）＋カレンダー幅拡張
- D76: 左レール（月名縦書き sticky）
- D77: 左レールを「数字だけ大きく upright」に簡素化
- D78: セル縦幅 96→120px ＋ 会場帯と pill の間隔 2→7px
- D81: メモ欄を grid `auto 1fr` で自然サイズに、カレンダー下端と完全アライン

### UI 整理

- D69: TOUR期間ハイライト撤去＋マスター日付バーをカレンダー連動に
- D70: 詳細パネル整理＋現地仕込みブロック追加＋VENUES日数撤去
- D72: 公演グループセクション撤去（公演名はページ上部のみ）
- D74: 詳細パネル更にスリム化（保存ボタン等撤去）＋EVENTS順序入替
- D80: 凡例バー撤去（パレットと冗長）

### デザイン提案・実装

- D82: ヘッダーをエディトリアル雑誌マスト式に再構築（A案採用）
- D84: イベント色をステージ照明フィルター式に変更（B案採用）
- D85: 会場帯を黒抜きスタイルに（後にユーザー却下）
- D86: 黒抜き廃止、warm gold に仮戻し（次の Mock で別案検討中）

---

## 7. 次にやること（Pending）

### 即時：ユーザー確認待ち

- **会場帯の色**：B〜J 案の中からユーザーが選定中（直前の Mock を参照）
  - 候補: F=チャコール / G=ダスティローズ / H=モスグリーン / I=テラコッタ / J=マスキングテープ
  - 旧候補: B=白抜き / C=輪郭のみ / D=濃紺 / E=セルtint

### 中期：他タブ連動

- **DAY SCHEDULE**：本番日 / 仕込み日 / リハ日でテンプレート自動切替
- **REHEARSAL**：リハ日／テクリハ日のときだけ表示
- **HOTEL**：会場帯の venue を見てホテル候補を絞る
- **入り時間**：本番／リハ／仕込みでデフォルトを変える

### 長期：Phase 2 以降（Firebase 同期）

- Phase 2: pc-edit.html / phone.html に Firebase コード組込
- Phase 3: ローカル動作確認（PC ↔ スマホ同期テスト）
- Phase 4: GitHub に push してデプロイ

---

## 8. のむさんへの応対ルール

- **コード未経験**：必ず日本語で噛み砕いた説明、舞台用語OK
- **ターミナルコマンド**：必ずコピペできる完成形で渡す（変数や省略禁止）
- **進め方**：小さく区切ってデプロイ → 確認 → 次の改修。Phase 分けで「これでいい？」確認大事。
- **仕事内容**：演出家。音楽・照明・ステージング・特効・ダンス・レーザー・VJ・映像コンテンツ・電飾・美術・道具すべて担当。VJ ソフト Resolume Arena に詳しい。
- **趣向**：効率重視、スタイリッシュ志向、業務ツールっぽさは嫌う、毎日見ても疲れないトーン。
- **NG**：オレンジ系の発光・極太・派手は嫌い。中途半端なデザインも嫌い。

---

## 9. 直近のコミット（Git history）

```
5fe0001 D86: 会場帯の有無で同週セルが揃わない問題修正＋黒抜き廃止
c242349 D85: 会場帯を黒抜きスタイル（A案）に
52d86bc D84: イベントブロック色をステージ照明フィルター式（B案）に
a3acab8 D82: ヘッダーバーをエディトリアル雑誌マスト式（A案）に再構築
b19b2f7 D81: メモ欄高さをカレンダー下端に正確にアライン
9465c04 D79+D80: メモ欄を下端まで＋凡例バー撤去
bba6bb1 D78: セル縦幅拡張＋会場帯とピルの間隔調整
9586df1 D77: 左レールを「数字だけ縦上げ」スタイルに
717b421 D76: 左レール（月名縦書き）を本物のカレンダーに実装
9860a05 D75: 月ジャンプバグ修正＋偶数月/奇数月の色分け
1a13e21 D73: 連続グリッド化＋月ラベル埋込＋カレンダー幅拡張
e0b9e91 D71+D72: カレンダー縦スクロール連続月化＋千秋楽撤去＋公演グループセクション撤去
8fb8bb9 D70: 詳細パネル整理＋現地仕込み追加＋VENUES日数撤去
047f007 D69: TOUR期間ハイライト撤去＋マスター日付バーをカレンダーD&D連動に
b9b3724 D68: move-pill で掴んだセルを sourceDate として記録
895771c D67: 重なるイベントは lane 別に縦並び
```

---

## 10. 既知の課題 / 未確定事項

- 会場帯の色：未確定（Mock 提案中）
- アプリ全体カラーテーマ：今のオレンジ系で一旦保留（D83 で5案 mock 提示済み、実装は未）
- DAY SCHEDULE / REHEARSAL / HOTEL のカレンダー連動：未着手
- Firebase 同期：Phase 1 のみ完了、Phase 2 以降未着手
- スマホ画面（phone.html）：今回のセッションでは未触

---

## 11. 2026-05-09 セッション末尾申し送り（D157〜D178）

### 今回追加した主な機能・修正

| Rev | 内容 |
|---|---|
| D157 | **複数セトリ機能**（SET LIST A/B/C タブ + 切替 + 追加） |
| D158 | RH# 22バグ + M1/M8 ハイライト + M# データ保持 |
| D159 | ツアータイトル編集をトップだけに / TOP戻るボタン（鍵→「← TOP」テキスト） |
| D160 | RH# 1→11 バグ click+mouseup 対処 / SET LIST 行を独立化＋✕削除 / flex-wrap |
| D161 | SET LIST タブを緑系に変更＋テクリハと同じ行のセンター |
| D162 | REHEARSAL タブの全ボタン高さ・線太さ完全統一 / RH# **mousedown preventDefault** で 1→11 を根本対処 |
| D163 | SET LIST border 全タブ統一 |
| D164 | +行を追加 border opacity 統一 |
| D165〜D169 | **入り時間 PC版** を J案 → ホイール → J案1窓 と試行錯誤、最終的に **「1つの枠 + H/M ラベル付き透明 select」** に確定 |
| D170 | SET LIST 文字色を元のベージュに復帰 |
| D175 | SET LIST × ボタンと + セトリ追加 の **D157 で混入していた緑文字**（rgba(180,220,180,...)）を撤去 |
| D176〜D177 | TEST/REHEARSAL active/テクリハ active を順次 #d8a878 → #e89a4a などアンバーへ |
| D178 | 比較用 `pc-edit-old-d156.html` を別 URL でデプロイ |

### **超重要・未解決：「文字色が緑っぽく見える」問題**

**ユーザーの一貫した訴え**：
- D157（SET LIST A/B 追加）以降、**画面全体の白文字・グレー文字が緑寄りに見える**
- 「絶対に何かが同時に文字全体にかかった」と確信
- TEST タイトル、REHEARSAL active タブ文字、テクリハ文字 などピンポイントで指摘
- シークレットウィンドウで見ても変わらないと明言

**僕の調査結果（不十分）**：
- D156→D177 の git diff で CSS 全変更を grep
  - `filter` / `opacity` / `mix-blend-mode` / `backdrop-filter` / `mask` → 全体に効くものは無し
  - `body` / `html` / `*` / `:root` セレクタへの色追加 → 無し
  - CSS変数（`--xxx`）の追加 → 無し
  - `font-smoothing` / `text-shadow` 等 → 無し
  - inline `style="color: ..."` → 無し
- 唯一見つかった「緑文字の本当の元凶」：D157 で setlist-tab-x / setlist-add-btn の `color: rgba(180,220,180, ...)` （= G が最大値の **本物の緑**）→ D175 で撤去済み
- Chrome MCP で実機確認した結果：build-version は最新が反映、TEST color = #e89a4a で間違いなく修正後の値

**それでもユーザーは「変わってない」と言い続ける**

### 次セッションでまずやるべきこと（最優先）

1. **ユーザーの環境を1個ずつ確認**
   - Chrome 拡張機能（特に Dark Reader, Stylish, Stylus, ColorZilla 等の CSS 注入系）
   - Mac の Night Shift / True Tone の ON/OFF
   - モニターのカラープロファイル
   - ブラウザのテーマ拡張
2. **Chrome MCP で D156 と現在の computed color を全要素比較**
   - 比較用 D156 ファイル：`https://nrs2013.github.io/schedule-studio/pc-edit-old-d156.html`
   - 現在：`https://nrs2013.github.io/schedule-studio/pc-edit.html`
   - 全要素の computed color を JS で出力し、差分要素だけリスト化
3. **どうしても見つからなかったら**：pc-edit.html を D156 (`1245d5d`) に完全ロールバックし、SET LIST 機能だけを別の方法で局所的に再実装する

### 今回ユーザーが疲弊した経緯

- 同じ「緑」の問題で D170〜D177 と何度も色を変更したが、ユーザーから見て差が分からず
- D173 で全グレー色を一括置換 → ユーザーから「全然ダメ、全リバート希望」 → D174 で D170 に戻した
- D175〜D177 と段階的に色を振ったが「変わってない」「違う」が続いた
- 最終的にユーザーが「もう君頭まわってない」「引き継ぐ？」と提案 → 引き継ぎへ

**僕（前セッションClaude）の反省**：
- 修正幅が小さすぎ、視覚的に変化を見せられなかった
- 「色彩錯視」と決めつけて、ユーザーの観察を素直に信じきれなかった瞬間があった
- grep でしか調査せず、Chrome MCP の実機 computed color 比較を最初からやればよかった

### 触らなかった/触ってほしくないファイル（今セッション）

- `phone-staff.html` `phone-artist.html` は今回未触
- `pc-hotel.html` も未触

### 現在の build-version

- `pc-edit.html`: `20260509.640000`（D177 時点）
- `pc-edit-old-d156.html`: 比較用、デプロイ済み（GitHub Pages 反映に1〜2分）

### 残り pending（今回未着手）

- **DAY SCHEDULE（PC版）の時刻入力統一**（入り時間と同じ J案1窓型に）
- **スマホ版（STAFF/ARTIST）の時刻入力統一**（既にホイールピッカーは実装済み、UI 統一の話）
- **D128 Phase C/D**：CALENDAR の連結バー / 右パネル / TODAY を Notion 流に統一
- **D136 Phase D**：ロック画面で STAFF/ARTIST 振り分け
- **TODAY 自動更新**（1分ごと、開きっぱなし対策）
- **Firebase rules を認証付きに**（本番運用前必須）

---

以上。
