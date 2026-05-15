#!/bin/bash
set -e

cd ~/Documents/schedule-studio-r135-work

echo "=== 1/5 git add ==="
git add phone-staff.html phone-artist.html

echo ""
echo "=== 2/5 git commit ==="
git commit -m "R139: INFO の NEW POST 機能（PASS認証連動 / 題名任意 / 投稿者名端末記憶 / 投稿後の削除編集不可）＋入り時間欄の幅修正（box-sizing/min-width）＋NEW POST ボタン色をオレンジに強調"

echo ""
echo "=== 3/5 git push ==="
git push origin main

echo ""
echo "=== 4/5 GitHub 側の最新を取得 ==="
sleep 3
git fetch origin
echo ""
echo "▼ GitHub origin/main 最新コミット 3 件:"
git log origin/main --oneline -3

echo ""
echo "=== 5/5 GitHub 上の中身検証 ==="

echo ""
echo "▼ R139 マーカー"
echo -n "  phone-staff.html (12 件以上で成功):  "
git show origin/main:phone-staff.html | grep -c 'R139' || true
echo -n "  phone-artist.html (6 件以上で成功): "
git show origin/main:phone-artist.html | grep -c 'R139' || true

echo ""
echo "▼ NEW POST 投稿フォーム（staff のみ）"
echo -n "  info-input-title（題名フィールド、1）: "
git show origin/main:phone-staff.html | grep -c 'id="info-input-title"' || true

echo ""
echo "▼ 入り時間欄の box-sizing 修正（両ファイル 1 以上）"
echo -n "  phone-staff.html:  "
git show origin/main:phone-staff.html | grep -c 'min-width:0; box-sizing:border-box' || true
echo -n "  phone-artist.html: "
git show origin/main:phone-artist.html | grep -c 'min-width:0; box-sizing:border-box' || true

echo ""
echo "============================="
echo "🎉 Phase H + 微修正 push 完了"
echo "============================="
echo ""
echo "次はスマホ実機テスト："
echo "  https://nrs2013.github.io/schedule-studio/phone-staff.html"
echo ""
echo "  ※ スマホ実機ではブラウザのキャッシュを強制更新するため、"
echo "    Safari なら 設定 → Safari → 履歴と Web サイトデータを消去"
echo "    または別のシークレットタブで開くのが確実"
echo ""
echo "（GitHub Pages が反映されるまで 1〜2 分かかります）"
