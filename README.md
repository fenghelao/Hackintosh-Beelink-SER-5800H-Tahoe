# Beelink SER（Ryzen 7 5800H）黑苹果：macOS Tahoe 26.7.2 安装与踩坑记录

AZW / Beelink SER 迷你主机（Ryzen 7 5800H + Vega 核显）安装 macOS 的完整过程记录：从 Sonoma 装起、经过 Sequoia、最终稳定在 **macOS Tahoe 26.7.2**。重点是**每个问题是怎么查出来、怎么修好的**，方便同配置或同类 AMD 核显机器参考。

> ⚠️ 这里只放文档、脱敏后的 `config.plist`、ACPI 和自己写的脚本。第三方 kext 请到各自项目下载（版本和链接见下表）。**config.plist 里的 SMBIOS 已清空，必须自己用 GenSMBIOS 生成后再用。**

## 硬件

| 部件 | 型号 | macOS 下状态 |
|---|---|---|
| 主机 | AZW / Beelink SER，BIOS 5800H501 | — |
| CPU | AMD Ryzen 7 5800H（8 核 16 线程） | ✅ AMD Vanilla 补丁 + AMDRyzenCPUPowerManagement |
| 核显 | Radeon Vega（Cezanne，1002:1638） | ✅ NootedRed（Metal 3）；4K HDMI 输出只有 30Hz |
| 内存 | 32GB | ✅ |
| 硬盘 | KINGSTON OM8SEP4512N（512GB NVMe，无缓存） | ✅ 写入较慢 |
| 声卡 | Realtek ALC897 | ✅ AppleALC（layout‑id 77）+ SimpleHDA（Tahoe 必需） |
| 有线 | Realtek RTL8168 | ✅ RealtekRTL8111 |
| Wi‑Fi | Intel AX200（8086:2723） | ✅ itlwm + HeliPort（5GHz 需改 2 字节，见文档） |
| 蓝牙 | Intel AX200（USB 8087:0029） | ⚠️ 可用。IntelBluetoothFirmware **lshbluesky 2.5.3** 后 BLE 键盘掉线能 5 秒内自动重连，但偶尔仍会掉线（排查中） |
| 睡眠 | — | ❌ 睡下去马上醒，已关闭睡眠 |

## 最终可用配置（Tahoe 26.7.2 / 25G332）

- OpenCore 1.0.8 RELEASE，机型 iMac20,1
- SIP：`csr-active-config = 430A0000`（NootedRed 用户态补丁需要）
- 启动参数：`keepsyms=1 revcpu=1 revpatch=auto,sbvmm -NRedDisplayFix -NRedVideoFix`
- NVRAM：`bluetoothExternalDongleFailed = 00`，`bluetoothInternalControllerInfo = 14 字节 00`

| kext | 版本 | 来源 |
|---|---|---|
| Lilu | 1.7.2 | [acidanthera/Lilu](https://github.com/acidanthera/Lilu) |
| VirtualSMC | 1.3.8 | [acidanthera/VirtualSMC](https://github.com/acidanthera/VirtualSMC) |
| ForgedInvariant | 1.5.0 | [ChefKissInc/ForgedInvariant](https://github.com/ChefKissInc/ForgedInvariant) |
| AMDRyzenCPUPowerManagement / SMCAMDProcessor | 0.7.2 / 1.0.1 | [trulyspinach/SMCAMDProcessor](https://github.com/trulyspinach/SMCAMDProcessor) |
| NootedRed | 0.9.0‑pre‑release.15 | [steve12311/NootedRed](https://github.com/steve12311/NootedRed)（ChefKissInc/NootedRed 分支） |
| NVMeFix | 1.1.3 | [acidanthera/NVMeFix](https://github.com/acidanthera/NVMeFix) |
| RestrictEvents | 1.1.6 | [acidanthera/RestrictEvents](https://github.com/acidanthera/RestrictEvents) |
| AppleALC | 1.9.8 | [acidanthera/AppleALC](https://github.com/acidanthera/AppleALC) |
| SimpleHDA | 1.0.0 | [laobamac/SimpleHDA](https://github.com/laobamac/SimpleHDA) |
| RealtekRTL8111 | 2.4.3 | [Mieze/RTL8111_driver_for_OS_X](https://github.com/Mieze/RTL8111_driver_for_OS_X) |
| itlwm | 2.3.0（改 2 字节） | [OpenIntelWireless/itlwm](https://github.com/OpenIntelWireless/itlwm) + [HeliPort](https://github.com/OpenIntelWireless/HeliPort) |
| IntelBluetoothFirmware / IntelBTPatcher | **2.5.3** | [lshbluesky/IntelBluetoothFirmware](https://github.com/lshbluesky/IntelBluetoothFirmware/releases) |
| BlueToolFixup | 2.7.2 | [acidanthera/BrcmPatchRAM](https://github.com/acidanthera/BrcmPatchRAM) |

## 文档目录

1. [安装流程与版本选择](docs/01-安装流程与版本选择.md) —— 为什么先装 Sonoma、Sequoia 24.6 内核为什么卡死、怎么升到 Tahoe 26.7.2
2. [显卡：卡顿、花屏、GPU hang](docs/02-显卡-NootedRed.md) —— SIP、MonitorControl、NootedRed 参考数据不匹配与重新生成
3. [声卡](docs/03-声卡.md) —— Tahoe 去掉 AppleHDA 之后怎么办
4. [Wi‑Fi](docs/04-WiFi.md) —— itlwm + HeliPort、5GHz 握手卡在 2/4 的 AKM 补丁
5. [蓝牙与 BLE 键盘掉线](docs/05-蓝牙.md) —— ghost 控制器、USB 映射的坑、打字中掉线的完整排查
6. [USB、睡眠、键盘掉线](docs/06-USB与睡眠.md)
7. [维护：屏蔽系统更新、改 EFI 的流程、救急](docs/07-维护与救急.md)

## 最重要的几条经验

1. **系统小版本也会让 NootedRed 失效**：它的补丁依赖系统缓存的参考数据，系统一更新就可能对不上。升级前先查驱动是否支持目标版本，并屏蔽自动更新。
2. **静态校验通过 ≠ 能用**：`ocvalidate` 只检查配置格式。一份 USB 映射在 Sequoia 正常，到 Tahoe 直接让整个 XHC2 控制器消失。
3. **先确认是从哪个 EFI 启动的**：`nvram 4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102:boot-path` 带 `USB(...)` 就是 U 盘，带 `NVMe(...)` 才是内置盘。
4. **改 EFI 的固定流程**：完整备份 → 在副本上改 → `ocvalidate` → 复制 → 逐文件比对哈希。
5. **蓝牙问题先看 bluetoothd 日志里的断开原因码**（708/762 = 700 + HCI 错误码），能快速分清是射频超时、建连失败还是加密问题。

## 参考过的同类项目

- [pexcn/hackintosh-beelink-ser5-max-5800h](https://github.com/pexcn/hackintosh-beelink-ser5-max-5800h)（Sonoma）
- [cgartlab/Beelink-SER5-Max-Hackintosh](https://github.com/cgartlab/Beelink-SER5-Max-Hackintosh)（Ventura）
- [Kingtous/thinkbook14p-Gen2-ACH-hackintosh](https://github.com/Kingtous/thinkbook14p-Gen2-ACH-hackintosh)（5800H 笔记本，Tahoe）
- [AMD-OSX/AMD_Vanilla](https://github.com/AMD-OSX/AMD_Vanilla)、[Dortania OpenCore Install Guide](https://dortania.github.io/OpenCore-Install-Guide/)

## 免责声明

仅供学习参考。每台机器的 BIOS、USB 布局、硬盘都可能不同，照搬配置可能无法启动。操作前请完整备份。

---

## English summary

Hackintosh notes for the **AZW / Beelink SER mini PC (AMD Ryzen 7 5800H, Vega 1002:1638)** running **macOS Tahoe 26.7.2 (25G332)** with OpenCore 1.0.8.

- iGPU via **NootedRed 0.9.0‑pre‑release.15** (`-NRedDisplayFix -NRedVideoFix`, SIP `430A0000`). GPU hangs on 15.8.3 were caused by NootedRed's reference data not matching the dyld cache; the docs explain how it was regenerated. On 26.7.2 the stock data matches.
- Audio (ALC897): **AppleALC layout 77 + SimpleHDA** (Tahoe removed AppleHDA); needs `keepsyms=1` and `DisableLinkeditJettison`.
- Wi‑Fi (AX200): itlwm 2.3.0 + HeliPort. A 2‑byte patch (`wpa.i_akms` 0xf → 0x3) fixes networks that advertise both PSK and PSK‑SHA256.
- Bluetooth (AX200, 8087:0029): BLE keyboard kept dropping while typing (bluetoothd reason 708 = HCI 0x08 timeout, then repeated 762 = HCI 0x3E). Wi‑Fi, pairing and the keyboard itself were ruled out; upgrading **IntelBluetoothFirmware/IntelBTPatcher to the lshbluesky fork v2.5.3** made reconnection recover within ~5 s (2.5.0 failed for minutes), but occasional 708 timeouts while typing remain — still under investigation (AX200 RF/antenna on this box not yet ruled out). A custom USBMap that worked on Sequoia made the whole XHC2 controller disappear on Tahoe — no USB map is used.
- Sleep is disabled (wakes immediately).

The SMBIOS in `EFI-config/OC/config.plist` is blanked — generate your own. Third‑party kexts are not redistributed; see the table above for versions and sources.
