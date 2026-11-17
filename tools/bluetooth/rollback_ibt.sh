#!/bin/bash
# 从备份恢复 IntelBluetoothFirmware / IntelBTPatcher（只恢复这两个 kext）
# 用法：sudo bash rollback_ibt.sh <备份目录，如 /Library/EFI-backups/efi-时间戳> <EFI分区，如 disk0s1>
set -euo pipefail
[ "$(id -u)" = 0 ] || { echo "请用 sudo 运行"; exit 1; }
BK=${1:?备份目录}; DEV=${2:?EFI 分区}
diskutil mount "$DEV" >/dev/null
MP=$(diskutil info "$DEV" | awk -F': *' '/Mount Point/{print $2}')
for k in IntelBluetoothFirmware IntelBTPatcher; do
  [ -d "$BK/EFI/OC/Kexts/$k.kext" ] || { echo "备份里没有 $k"; exit 1; }
  rm -rf "$MP/EFI/OC/Kexts/$k.kext"
  ditto --norsrc --noextattr --noqtn "$BK/EFI/OC/Kexts/$k.kext" "$MP/EFI/OC/Kexts/$k.kext"
  echo "$k -> $(/usr/libexec/PlistBuddy -c 'Print :CFBundleVersion' "$MP/EFI/OC/Kexts/$k.kext/Contents/Info.plist")"
done
sync; diskutil unmount "$DEV" >/dev/null; echo "已回滚，重启生效。"
