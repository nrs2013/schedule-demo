#!/bin/bash
set -e

cd ~/Documents/schedule-studio-r135-work

echo "=== 1/4 git add ==="
git add phone-staff.html

echo ""
echo "=== 2/4 git commit ==="
git commit -m "R140: NEW POST モーダルを画面中央表示に修正（iPhone Safari の UI / 下タブとの干渉を回避）"

echo ""
echo "=== 3/4 git push ==="
git push origin main

echo ""
echo "=== 4/4 GitHub 側の検証 ==="
sleep 3
git fetch origin
echo ""
echo "▼ 最新コミット:"
git log origin/main --oneline -3
echo ""
echo "▼ モーダルが中央配置になってるか（1 件なら成功）"
echo -n "  align-items: center: "
git show origin/main:phone-staff.html | grep -c 'align-items: center; justify-content: center;.*\n.*padding: 20px 12px' || git show origin/main:phone-staff.html | grep -c "R139: 投稿モーダル（画面中央表示" || true

echo ""
echo "============================="
echo "🎉 R140 push 完了"
echo "============================="
echo "本番 URL: https://nrs2013.github.io/schedule-studio/phone-staff.html"
echo ""
echo "⚠ スマホ Safari は前回のキャッシュがまだ残ってる可能性が高いので、"
echo "  プライベートブラウズで新規タブを開いて URL を入れるのが確実です。"
