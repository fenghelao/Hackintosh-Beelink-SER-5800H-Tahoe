# 蓝牙驱动升级 / 回滚

| 文件 | 用途 |
|---|---|
| `upgrade_ibt.sh` | 完整备份 EFI 并逐文件校验后，只替换 `IntelBluetoothFirmware.kext` 和 `IntelBTPatcher.kext`；会先核对 config.plist 里的 ExecutablePath |
| `rollback_ibt.sh` | 从备份里只恢复这两个 kext |

```bash
# 1. 下载并核对（以 v2.5.3 为例）
curl -sSLO https://github.com/lshbluesky/IntelBluetoothFirmware/releases/download/v2.5.3/IntelBluetooth-2.5.3-RELEASE.zip
shasum -a 256 IntelBluetooth-2.5.3-RELEASE.zip   # 应为 8ae1cad6edf39f524bf5a106b88a2ddfd27744c12612f631b451d4017ff8b70b
mkdir ibt && ditto -x -k IntelBluetooth-2.5.3-RELEASE.zip ibt
# 2. 找到 EFI 分区（diskutil list），替换
sudo bash upgrade_ibt.sh ./ibt disk0s1
```
