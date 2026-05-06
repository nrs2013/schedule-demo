# SCHEDULE STUDIO ── 共同開発者オンボーディング

このドキュメントは、のむさん（コンサート演出家、GitHub `nrs2013`）が一人で育ててきた **SCHEDULE STUDIO** に、別の人が **Claude Cowork** を相棒にして加わるための引き継ぎノートです。

> 同じシリーズの **TELOP STUDIO 用オンボーディング** も併読してください。
> → `~/Projects/telop-studio/COLLABORATOR_ONBOARDING.md`
> 「のむさんとの作業ルール」「Cowork の使い方」「Mac 初期設定」など、**共通ルールはすべて TELOP 側に詳しく書いてあります**。
> こちらは **SCHEDULE 固有の話だけ** をまとめています。

---

## 0. まず最初に Claude（Cowork）に読ませてほしい順番

新しく Cowork を起動したら、最初の指示はこれだけで OK です：

```
~/Projects/schedule-studio/COLLABORATOR_ONBOARDING.md と
~/Projects/telop-studio/COLLABORATOR_ONBOARDING.md を読んで、
SCHEDULE STUDIO の作業に入る前にやるべきことを教えて。
```

これで Claude が、TELOP 側に書いてある共通ルールも合わせて読み込みます。

---

## 1. SCHEDULE STUDIO とは何か（一言でいうと）

**ツアー段取り（リハ・本番進行・入り時間・ホテル・タクシー）を 1 ページにまとめる Web アプリ。** のむさんが一人で組んで、スタッフは LINE 経由でスマホから見る。

| 立場 | 使う画面 |
|------|----------|
| **のむさん（演出）** | PC 編集版（`pc-edit.html`, `pc-hotel.html`） |
| **スタッフ全員** | スマホ閲覧版（`phone.html` ≒ `phone-vNN.html`） |

公開先は **GitHub Pages**：
- 入口: `https://nrs2013.github.io/schedule-studio/`
- 一覧: `index.html`（評価用モックの目次）
- スマホ実体: `phone.html`
- PC 実体: `pc-edit.html` / `pc-hotel.html`

**TELOP STUDIO とのいちばんの違い**: SCHEDULE STUDIO は **素の HTML ファイル群** で動いている。Vite も React も TypeScript もビルドステップも **無い**。`.html` を直接編集 → `git commit` → `git push` → 数十秒後に GitHub Pages へ反映、それだけ。

---

## 2. のむさんとの作業ルール（最重要、必ず読む）

詳細は **TELOP 版の §3「のむさんとの作業ルール」** に書いてあります。**全部当てはまります。** SCHEDULE 側でとくに効いてくるのを再掲します：

1. **エンジニア用語ではなく舞台用語で説明する**
   - ✗「state を localStorage に永続化します」
   - ◯「メモした内容を、画面を閉じても忘れないように Mac の中に保存します」
2. **ターミナルコマンドはコピペできる完成形で渡す**（`cd ~/Projects/schedule-studio && git add -A && git commit -m "..." && git push` のように1行で）
3. **「これでいい？」と必ず確認してから進む。** いきなり書き換えない。
4. **失敗したら戻す手段を一緒に渡す。** とくに HTML 1 ファイルに全部入っているので、壊したときの被害が大きい。`git stash` か `git revert` の手順を必ず添える。
5. **`.git/index.lock` が居座ったら `rm -f .git/index.lock` してから push する。** これも TELOP と同じ。

---

## 3. データ安全ルール（SCHEDULE 版の要点）

TELOP 側に詳しい `DATA_SAFETY_RULES.md` がありますが、SCHEDULE STUDIO **専用に効く要点だけ** ここに書きます：

### 3-1. 永続化はぜんぶ `localStorage`（サーバー DB は無い）

`pc-edit.html` の中で使われている保存キー一覧：

| キー | 保存している中身 |
|------|------------------|
| `schedule-studio:calEvents:v1` | カレンダー上のイベント（仕込み・テクリハ・リハ・SHOW・移動・休） |
| `schedule-studio:showTimes:v1` | 会場ごとの開場/開演時刻 |
| `schedule-studio:calMemos:v1` | 日付ごとの自由メモ |
| `schedule-studio:dayEvents:v1` | 日付別の DAY SCHEDULE イベント |
| `schedule-studio:arrivalSectionsByDate:v1` | 入り時間（日付別、セクション別） |
| `schedule-studio:hotels:v1` | ホテル＋部屋＋ルームメイト＋タクシー配車 |

**ルール:**
- 既存キーの **形（スキーマ）を変えない**。フィールドを足したいなら **後方互換で読み込めるように** する。
- どうしても形を変えたいときは **新しい `:v2` キーで並行運用** し、古い `:v1` は読み取り専用で残す。TELOP の DATA_SAFETY_RULES と同じ思想。
- 読み込みヘルパーは `loadJSON(key, defaultVal)` / `saveJSON(key, val)`。`pc-edit.html` の上の方にいるので、新しい保存先を作るときも必ずこの2つを通す。

### 3-2. PC とスマホは **localStorage 経由で同期**

スマホ側（`phone.html`）は、`pc-edit.html` が「同期リンクを発行」したときに作る **URL ハッシュ（Base64 で localStorage を丸ごと埋め込んだ長いリンク）** を開いて、自分の localStorage に流し込む。

つまり **同期の単位は「同期リンクを踏んだ瞬間のスナップショット」**。サーバーで自動同期している訳ではないので、

- のむさんが PC 側で何か変更したら → 「同期リンクを生成して LINE に貼る」までやってはじめてスタッフ側に伝わる
- スタッフが入り時間を入力 → スタッフ側 localStorage に貯まる、PC 側には自動では戻らない

ここを勘違いして「自動でリアルタイム同期するように Firebase と繋ぎましょう」みたいな大改造を提案しないこと。**のむさんはこの「手動で配る」運用を選んでいる。** やるなら必ず「これでいい？」を取る。

### 3-3. バージョン違いの phone-vNN.html は **消さない**

`phone-v30.html` 〜 `phone-v36.html` は **過去バージョンが固まったまま残してある**（モック評価用）。最新は `phone.html`。
- 安易に `git rm phone-v30.html` しない。
- 「古いから消そう」は **必ずのむさんに確認**。LINE で配ったリンクが過去バージョンを指していることがある。

---

## 4. ファイル構成（SCHEDULE STUDIO の全体図）

```
~/Projects/schedule-studio/
├── index.html              モック目次（"SCHEDULE STUDIO Mocks"）
├── pc-edit.html            ★PC編集版・本体（5000行超）
├── pc-hotel.html           PC編集版・HOTEL専用ビュー
├── phone.html              ★スマホ閲覧版・最新
├── phone-v30.html 〜 v36.html  過去バージョンの固定スナップショット
├── .git/                   GitHub: nrs2013/schedule-studio
└── (README なし、.github/workflows なし)
```

**触る順番のおすすめ:**

1. `index.html`（150行）── 全体の入り口、3 つのモックへリンクしているだけ。アプリの世界観の名刺。
2. `pc-edit.html` 上から 800 行くらいまで ── CSS（タブの見た目、配色、サイズ感）。R37/R51/R74/R77 などの **R番号は「のむさんが進めてきた版数」**。コミット履歴と対応している。
3. `pc-edit.html` の `<script>` 群 ── IIFE（即時実行関数）が複数並んでいる構造。マスター日付バー / カレンダー / DAY SCHEDULE / 入り時間 / HOTEL がそれぞれ別の IIFE。**1個の IIFE をまるごと読んでから次へ** が読みやすい。
4. `phone.html` ── PC 編集版のデータ受け側。受け取った localStorage を表示する。
5. `pc-hotel.html` ── HOTEL タブだけを切り出した PC 版。Excel 取込やタクシー配車の UI が中心。

---

## 5. SCHEDULE 用語集（のむさん語 ↔ コード）

| のむさん語 | アプリ／コード上の意味 |
|------------|------------------------|
| **マスター日付バー** | 画面上部の「2026.04.29」みたいな日付タブ群。`window.__masterDateState.current` が今選ばれている日付（`'YYYY-MM-DD'`）。すべてのタブがこれを基準に表示を切り替える |
| **REHEARSAL タブ / RH** | 当日のリハ進行表（M# / TITLE / TIME / RH# / TAGS / MEMO）。本番のセトリ順とは別に **リハ順** で並ぶ |
| **DAY SCHEDULE タブ** | 当日のステージ進行（時刻ベース）。リハ番号付きの曲を時系列に流し込む |
| **入り時間** | スタッフが「自分は何時に入ります」を申告するタブ。`arrivalSectionsByDate` に **日付別 → セクション別** で保存 |
| **HOTEL タブ** | ホテル名・部屋番号・ルームメイト・タクシー配車。`hotels` キーで全日まとめて保管 |
| **テクリハ** | テクニカルリハーサル。カレンダー上の `type:'tek'` |
| **rhNo** | その曲のリハ通し番号。リハ順で「1番目」「2番目」を意味する。**セトリ順とは別** |
| **rehearsalByDate** | 日付ごとに違うリハの並びを保存している中間オブジェクト |
| **セトリ順** | 本番のセトリ並び（M# 順） |
| **リハ順** | リハで通す並び（rhNo 順） |
| **R番号（R51, R77 など）** | のむさんと Claude の間で使ってる「版数」。コミットメッセージに必ず付く（例: `R77+R78: SCHEDULE自由入力共有 ＋ authed編集 ＋ iPad→Safari`） |

---

## 6. 標準ワークフロー（修正 → 公開）

```bash
# 1. 最新を取り込む
cd ~/Projects/schedule-studio
git pull

# 2. 編集（VS Code でも、Cowork から Claude に頼んでもよい）

# 3. ローカルで動作確認
#    - 何でもいい。Mac の Finder で .html をダブルクリックでも開ける。
#    - LINE 経由のスマホ確認は GitHub Pages にデプロイしないと辛い。

# 4. push（これで GitHub Pages に自動反映、数十秒〜1分）
rm -f .git/index.lock
git add -A
git commit -m "RXX: 何をしたか短く"
git push

# 5. 反映確認
#    https://nrs2013.github.io/schedule-studio/
```

**コミットメッセージの作法**: のむさんが付けてきた `RXX: ...` の通し番号を続けてください。直近を確認するには `git log --oneline -5`。

---

## 7. よくある宿題テンプレ（SCHEDULE で発生しやすい依頼）

| 依頼パターン | どこを触るか |
|-------------|-------------|
| 「タブの並び替えたい」「上部の見た目変えたい」 | `pc-edit.html` 上部 CSS（`.nav-`, `.mode-tabs`, `.pc-rh-` あたり）と `phone.html` の `.tab-bar` |
| 「日付バーで違う日を選んだら違うリハが出るようにしたい」 | `__masterDateState` を購読している IIFE。`rehearsalByDate` を介して切り替えるのが既存パターン |
| 「ホテル情報を Excel から取り込みたい」 | `pc-hotel.html`。SheetJS（XLSX.js）を CDN から読んでいるので、ライブラリ追加なしで触れる |
| 「同期リンク短くしたい・QR にしたい」 | `pc-edit.html` 5300行台の Base64 ハッシュ生成。**長くなる/壊れる** の典型パターンなので、必ず `phone.html` 側で読めるか同時に確認する |
| 「過去バージョンに戻したい」 | `git log --oneline -20` でコミット番号を出して、のむさんに「この時点に戻していい？」と確認 → `git revert <hash>` |

---

## 8. 過去にやらかしたパターン（学習用）

これも詳細は TELOP の `HANDOFF_TO_NEXT_CLAUDE.md` にいろいろ書いてあります。SCHEDULE で再発させやすいやつだけ：

1. **localStorage キーを勝手に rename した** → 全データ消失。**v1 のまま追記するか、新しく v2 を並行追加** する。
2. **IIFE の中で `let` し直して、別の IIFE が触れなくなる** → グローバル状態（`window.__masterDateState` など）はちゃんと `window.` 経由で公開しているか確認。
3. **`phone-vNN.html` を「整理」して消した** → LINE で配布済みのリンクが死ぬ。**消さない、触らない**。
4. **同期リンクのフォーマットを変えて、古いリンクが復元できなくなった** → 同期リンクは **後方互換** を死守。

---

## 9. 連絡（質問が出たら）

- まず **TELOP の `COLLABORATOR_ONBOARDING.md` と `HANDOFF_TO_NEXT_CLAUDE.md`** を読み返す（共通ルールはほぼこっちに書いてある）。
- それでも判断つかないことは **のむさんに「これでいい？」** を投げる。勝手に進めない。これがいちばん大事です。

それじゃ、よろしくお願いします 🎬
