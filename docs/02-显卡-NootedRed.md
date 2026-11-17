# 02 显卡：卡顿、花屏、GPU hang

核显 Vega（Cezanne，1002:1638），驱动 NootedRed 0.9.0‑pre‑release.15（[steve12311/NootedRed](https://github.com/steve12311/NootedRed)），启动参数 `-NRedDisplayFix -NRedVideoFix`。

## 现象

- 打开 Chromium / Electron 类软件（浏览器、Claude 桌面版）后十几秒内全屏冻住或花屏。
- 严重时 WindowServer 无响应，被看门狗强制重启。
- 内核日志里反复出现 `GPU hang`，最多一天 695 次。

## 排查命令

```bash
# 显卡卡死记录（zsh 脚本里 log 是内建命令，要写全路径）
/usr/bin/log show --last 1h --style compact --predicate 'process == "kernel" AND eventMessage BEGINSWITH "GPU hang"'
# NootedRed 各项修复的状态（最有用）
ioreg -l -w0 | grep -oE '"NRed[A-Za-z]*" = [0-9]+' | sort -u
```

正常时能看到 `NRedSubmitGuardApplied` 等 Applied 项；如果出现 `...DynamicRejected = 1` 且没有 Applied，说明修复没装上。

## 原因（三层）

1. **SIP 全开，NootedRed 的用户态补丁打不上。** 改成 `csr-active-config = 430A0000` 后明显好转，不能设回 `00000000`。
2. **MonitorControl（DDC 调显示器亮度/音量的软件）会触发显卡卡死。** 它一启动，显示器就"重新配置"，约 30 秒后显卡卡死。卸载，不要装。
3. **根本原因：NootedRed 自带的参考数据只认特定系统版本。**
   - 驱动给 AMD Metal 驱动打补丁前，要核对目标代码和自带参考数据完全一致。
   - 当时的数据按 Sequoia 15.8.1（24H32）生成；15.8.3（24H241）里这些函数的逻辑没变，但系统缓存把数据区挪了 8～16 字节，引用地址对不上。
   - 结果 SRD、LegacyBlend、ComputeScratch、SubmitGuard 四项修复**一个都没装上**。

## 修法：重新生成参考数据（Sequoia 时期做过）

1. 下载对应版本的 NootedRed 源码和同版本 RELEASE kext。
2. **先确认"代码没变、只是引用地址变了"**：把参考数据里记录的外部引用位置遮住，再和本机系统缓存里的函数逐字节比较（`tools/nootedred/maskcmp.py`）。全部 `diff after masking refs: 0` 才能继续；否则说明苹果真的改了代码，只能等作者更新。
3. 更新 `tools/fixtures/sequoia-compat.json`：uuid 改成本机缓存的 UUID，变化了的函数的 sha256 改成本机的值。
4. 重新生成数据：
   ```bash
   python3 tools/build_sequoia_surface.py --major 24 --cache /System/Volumes/Preboot/Cryptexes/OS/System/Library/dyld
   ```
5. 离线验证：把驱动里的解析代码在用户态编译，对着本机缓存跑一遍；旧数据应 REJECTED，新数据应 OK。
6. 把新数据写进官方 RELEASE 二进制（`tools/nootedred/binpatch.py`，只替换 `__TEXT,__const` 里的数组，这次 273 字节，不改代码），或者用 Xcode 从源码完整编译。
7. 替换 EFI 里的 NootedRed.kext，重启，用上面的 ioreg 命令确认。

需要先装命令行工具（`xcode-select --install`）。

## Tahoe 26.7.2 上不需要改

本机 Tahoe 26.7.2 的系统缓存 UUID 和 NootedRed pre‑release.15 的参考缓存**完全相同**，用驱动自带的 `tools/test_cache_resolver_reference.py` 离线测试全部 PASS。官方二进制直接可用，修复全部 Applied，0 次卡死。

**所以：不要升级到 26.7.3 或更新的版本**，除非确认 NootedRed 已经支持（屏蔽更新的方法见 [07](07-维护与救急.md)）。

## 应用层的临时规避（驱动没修好时）

- Chromium / Electron 软件关闭硬件加速。
- 没有开关的 Electron 应用可以这样启动：`open -a /Applications/某应用.app --args --disable-gpu --disable-gpu-compositing`

## 显示器与显存

- 4K 显示器走 HDMI 时最高 30Hz（接口 / 线材限制）。选"看起来像 1080p"的 HiDPI 模式时，实际仍输出 4K 30Hz；改成真 2560×1440 可以到 60Hz，但在 4K 屏上发虚。要 4K 60Hz 需要换 DP 或 USB‑C 转 DP。
- 核显显存（UMA Frame Buffer）BIOS 里设的是 3GB，对 4K 桌面足够；加大只会占用系统内存，不会让 NootedRed 更流畅。
