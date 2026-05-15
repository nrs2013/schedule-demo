#!/bin/bash
set -e

cd ~/Documents/schedule-studio-r135-work

echo "=== 1/5 git add ==="
git add phone-staff.html phone-artist.html

echo ""
echo "=== 2/5 git commit ==="
git commit -m "R138: LINE リッチメニュー URL ハッシュルーティング実装（show ラップなし / 5秒 MutationObserver ガード / 下タブクリックで hash 解除）"

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
echo "=== 5/5 GitHub 上の中身検証（前任 R133 のアップロード失敗を絶対繰り返さない） ==="

echo ""
echo "▼ R138 マーカー（両方 3 件以上なら成功）"
echo -n "  phone-staff.html:  "
git show origin/main:phone-staff.html | grep -c 'R138\|r138HashRouter' || true
echo -n "  phone-artist.html: "
git show origin/main:phone-artist.html | grep -c 'R138\|r138HashRouter' || true

echo ""
echo "▼ r138HashRouter 関数定義（両方 1 件なら成功）"
echo -n "  phone-staff.html:  "
git show origin/main:phone-staff.html | grep -c 'function r138HashRouter' || true
echo -n "  phone-artist.html: "
git show origin/main:phone-artist.html | grep -c 'function r138HashRouter' || true

echo ""
echo "▼ HASH_TO_SCREEN マップ（両方 1 件なら成功）"
echo -n "  phone-staff.html:  "
git show origin/main:phone-staff.html | grep -c 'var HASH_TO_SCREEN' || true
echo -n "  phone-artist.html: "
git show origin/main:phone-artist.html | grep -c 'var HASH_TO_SCREEN' || true

echo ""
echo "▼ MutationObserver 設置（両方 1 件なら成功）"
echo -n "  phone-staff.html:  "
git show origin/main:phone-staff.html | grep -c 'new MutationObserver' || true
echo -n "  phone-artist.html: "
git show origin/main:phone-artist.html | grep -c 'new MutationObserver' || true

echo ""
echo "============================="
echo "🎉 Phase F の push 完了"
echo "============================="
echo ""
echo "次は本番 LINE 実機テスト："
echo "  1. LINE アプリで「SCHEDULE STUDIO」公式アカウントを開く"
echo "  2. リッチメニューの 6 ボタンを順番にタップ"
echo "  3. 各ボタンで該当画面に飛ぶか確認"
echo ""
echo "本番 URL: https://nrs2013.github.io/schedule-studio/"
echo "（GitHub Pages が反映されるまで 1〜2 分かかります）"
