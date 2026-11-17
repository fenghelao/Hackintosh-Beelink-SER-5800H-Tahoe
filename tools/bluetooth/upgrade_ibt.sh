#!/bin/bash
# 升级 EFI 里的 IntelBluetoothFirmware / IntelBTPatcher（只替换这两个 kext，不改 config.plist）
# 用法：sudo bash upgrade_ibt.sh <解压后的新版目录> <EFI分区设备，如 disk0s1>
# 新版下载：https://github.com/lshbluesky/IntelBluetoothFirmware/releases （下载后先和 GitHub 上的 sha256 核对）
set -euo pipefail
[ "$(id -u)" = 0 ] || { echo "请用 sudo 运行"; exit 1; }
NEW=${1:?新版 kext 所在目录}; DEV=${2:?EFI 分区，例如 disk0s1}
PB=/usr/libexec/PlistBuddy; TS=$(date +%Y%m%d-%H%M%S)
for k in IntelBluetoothFirmware IntelBTPatcher; do [ -d "$NEW/$k.kext" ] || { echo "缺少 $NEW/$k.kext"; exit 1; }; done

diskutil mount "$DEV" >/dev/null
MP=$(diskutil info "$DEV" | awk -F': *' '/Mount Point/{print $2}'); OC=$MP/EFI/OC
[ -f "$OC/config.plist" ] || { echo "$MP 下没有 EFI/OC/config.plist"; exit 1; }

# 核对 config 里的 ExecutablePath 与新包一致
i=0
while $PB -c "Print :Kernel:Add:$i:BundlePath" "$OC/config.plist" >/dev/null 2>&1; do
  bp=$($PB -c "Print :Kernel:Add:$i:BundlePath" "$OC/config.plist")
  case "$bp" in IntelBluetoothFirmware.kext|IntelBTPatcher.kext)
    ex=$($PB -c "Print :Kernel:Add:$i:ExecutablePath" "$OC/config.plist")
    [ "$ex" = "Contents/MacOS/${bp%.kext}" ] || { echo "$bp 的 ExecutablePath 不一致，中止"; exit 1; }
    echo "config #$i $bp Enabled=$($PB -c "Print :Kernel:Add:$i:Enabled" "$OC/config.plist")";;
  esac; i=$((i+1))
done

# 完整备份并逐文件校验
BK=/Library/EFI-backups/efi-$TS; mkdir -p "$BK"; ditto "$MP/EFI" "$BK/EFI"
diff <(cd "$MP/EFI" && find . -type f -exec shasum -a 256 {} + | sort) <(cd "$BK/EFI" && find . -type f -exec shasum -a 256 {} + | sort) >/dev/null \
  || { echo "备份校验失败，EFI 未改动"; exit 1; }
echo "EFI 已备份到 $BK"

for k in IntelBluetoothFirmware IntelBTPatcher; do
  old=$($PB -c 'Print :CFBundleVersion' "$OC/Kexts/$k.kext/Contents/Info.plist" 2>/dev/null || echo 无)
  rm -rf "$OC/Kexts/$k.kext"
  ditto --norsrc --noextattr --noqtn "$NEW/$k.kext" "$OC/Kexts/$k.kext"
  diff -rq "$NEW/$k.kext" "$OC/Kexts/$k.kext" >/dev/null || { echo "$k 复制校验失败，请用 $BK 回滚"; exit 1; }
  echo "$k: $old -> $($PB -c 'Print :CFBundleVersion' "$OC/Kexts/$k.kext/Contents/Info.plist")"
done
sync; diskutil unmount "$DEV" >/dev/null
echo "完成，重启生效。回滚：sudo bash rollback_ibt.sh $BK $DEV"
