#!/bin/bash

URL_BASE="file://$HOME/Documents/schedule-studio-r135-work/phone-staff.html"

echo "============================="
echo "R138 hash router テスト（STAFF版）"
echo "============================="
echo ""
echo "6 つの URL を順番に Chrome で開きます。"
echo "各タブで「想定される画面」が出るか確認してください。"
echo ""
echo "⚠ 注意：Chrome のキャッシュで古い HTML が出る可能性があるので、"
echo "   最初の 1 タブが開いたら Cmd+Shift+R でハードリロードしてください。"
echo ""

for hash in today calendar rehearsal info hotel pass; do
  url="${URL_BASE}#${hash}"
  echo "→ #${hash}"
  open "${url}"
  sleep 1
done

echo ""
echo "============================="
echo "各タブで確認する画面（期待値）"
echo "============================="
echo "  #today     → DAY SCHEDULE 画面（サブタブ DAY SCHEDULE active、下タブ DAY SCHEDULE active）"
echo "  #calendar  → TOUR CALENDAR 画面（下タブ CALENDAR active）"
echo "  #rehearsal → REHEARSAL（全体リハ）画面（下タブ REHEARSAL active）"
echo "  #info      → INFO 画面（下タブ INFO active）"
echo "  #hotel     → HOTEL 画面（下タブ HOTEL active）"
echo "  #pass      → PASS（パスワード認証）画面（下タブ PASS active）"
echo ""
echo "💡 もし開いたタブで違う画面が出ていたら、Cmd+Shift+R でハードリロードしてみてください"
