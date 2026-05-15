#!/bin/bash
set -e

cd ~/Documents/schedule-studio-r135-work

echo "=== 1/5 git add ==="
git add phone-staff.html phone-artist.html

echo ""
echo "=== 2/5 git commit ==="
git commit -m "R137: スマホ版構造改修（DAY SCHEDULE+入り時間サブタブ統合 / 下タブに CALENDAR 新設・ARRIVAL 廃止・INFO/HOTEL 入替 / SCHEDULE戻るボタン廃止）"

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
echo "▼ R137 マーカー数（両方 6 件なら成功）"
echo -n "  phone-staff.html:  "
git show origin/main:phone-staff.html | grep -c 'R137' || true
echo -n "  phone-artist.html: "
git show origin/main:phone-artist.html | grep -c 'R137' || true

echo ""
echo "▼ screen-schedule に active 付与（両方 1 件なら成功）"
echo -n "  phone-staff.html:  "
git show origin/main:phone-staff.html | grep -c '<div class="screen active" id="screen-schedule">' || true
echo -n "  phone-artist.html: "
git show origin/main:phone-artist.html | grep -c '<div class="screen active" id="screen-schedule">' || true

echo ""
echo "▼ 下タブの CALENDAR 新設（両方 1 件なら成功）"
echo -n "  phone-staff.html:  "
git show origin/main:phone-staff.html | grep -c "show('tour-calendar').*CALENDAR" || true
echo -n "  phone-artist.html: "
git show origin/main:phone-artist.html | grep -c "show('tour-calendar').*CALENDAR" || true

echo ""
echo "▼ TOUR CALENDAR 画面内ボタン廃止（両方 0 件なら成功）"
echo -n "  phone-staff.html:  "
git show origin/main:phone-staff.html | grep -c 'class="tour-cal-btn"' || true
echo -n "  phone-artist.html: "
git show origin/main:phone-artist.html | grep -c 'class="tour-cal-btn"' || true

echo ""
echo "============================="
echo "🎉 Phase G 完了"
echo "============================="
echo "本番 URL: https://nrs2013.github.io/schedule-studio/"
echo "（GitHub Pages が反映されるまで 1〜2 分かかります）"
