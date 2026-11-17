# EFI 配置（已脱敏）

- `OC/config.plist`：本机 macOS Tahoe 26.7.2 当前在用的 OpenCore 1.0.8 配置。
- `OC/ACPI/`：SSDT‑CPUR‑5800H、SSDT‑EC、SSDT‑HPET、SSDT‑PLUG、SSDT‑USB‑Reset、SSDT‑USBX、SSDT‑XOSI。

## 使用前必须做

1. **生成自己的 SMBIOS**：`PlatformInfo → Generic` 里的 `SystemSerialNumber`、`MLB`、`ROM`、`SystemUUID` 已清空。用 [GenSMBIOS](https://github.com/corpnewt/GenSMBIOS) 按 **iMac20,1** 生成，ROM 填你的网卡 MAC（去掉冒号）。**不要用别人的序列号。**
2. **按 README 里的版本表下载 kext**，放进 `OC/Kexts/`。名字和 `Kernel → Add` 里的 BundlePath 要一致。
3. `Drivers/` 需要 `OpenRuntime.efi`、`HfsPlus.efi`、`ResetNvramEntry.efi`；`OpenCore.efi` 和 `BOOTx64.efi` 用 OpenCore 1.0.8 RELEASE。
4. 用 OpenCore 1.0.8 的 `ocvalidate` 校验后再用。

## 关键设置

| 位置 | 值 | 原因 |
|---|---|---|
| `NVRAM → 7C436110‑… → csr-active-config` | `430A0000` | NootedRed 用户态补丁需要 |
| `boot-args` | `keepsyms=1 revcpu=1 revpatch=auto,sbvmm -NRedDisplayFix -NRedVideoFix` | `keepsyms=1` 给 SimpleHDA；`-NRedDisplayFix` `-NRedVideoFix` 打开 NootedRed 显示和视频修复 |
| `Kernel → Quirks → DisableLinkeditJettison` | true | SimpleHDA 需要 |
| `Kernel → Patch` | AMD Vanilla（覆盖到 Darwin 25.99.99），核心数 8 | Ryzen 7 5800H |
| `SimpleHDA` | `MinKernel = 25.0.0` | 只在 Tahoe 加载 |
| `USBMap*.kext` | 关闭 | 在 Tahoe 上会让 XHC2 消失（见 docs/05） |
| `AirportItlwm*`、`SMCRadeonSensors`、`AppleMCEReporterDisabler` | 关闭 | 用 itlwm + HeliPort |
| `NVRAM → bluetoothExternalDongleFailed / bluetoothInternalControllerInfo` | 00 / 14 字节 00 | 蓝牙控制器识别 |
| `Misc → Boot` | RELEASE、无 `-v` | 稳定后关掉调试 |

> 这是**本机**的配置。BIOS 版本、USB 布局、硬盘不同的机器可能无法直接启动。
