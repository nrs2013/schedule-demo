#!/bin/bash
set -e

cd ~/Documents/schedule-studio-r135-work

echo "=== 1/5 git add ==="
git add phone-staff.html phone-artist.html

echo ""
echo "=== 2/5 git commit ==="
git commit -m "R135: phone-staff/artist の静的リハカード残骸を完全撤去（DAY SCHEDULE/INFO タブ漏れの修正）"

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
echo "▼ 静的残骸チェック（両方 0 件なら成功）"
echo -n "  phone-staff.html:  "
git show origin/main:phone-staff.html | grep -c '<div class="rh-card" data-rh=' || true
echo -n "  phone-artist.html: "
git show origin/main:phone-artist.html | grep -c '<div class="rh-card" data-rh=' || true

echo ""
echo "▼ R135 マーカー確認（両方 1 件なら成功）"
echo -n "  phone-staff.html:  "
git show origin/main:phone-staff.html | grep -c 'R135: 静的デモ完全撤去' || true
echo -n "  phone-artist.html: "
git show origin/main:phone-artist.html | grep -c 'R135: 静的デモ完全撤去' || true

echo ""
echo "============================="
echo "🎉 Phase E 完了"
echo "============================="
echo "本番 URL: https://nrs2013.github.io/schedule-studio/"
echo "（GitHub Pages が反映されるまで 1〜2 分かかります）"
