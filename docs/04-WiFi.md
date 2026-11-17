# 04 Wi‑Fi（Intel AX200）

## 驱动选择

用 **itlwm 2.3.0 + [HeliPort](https://github.com/OpenIntelWireless/HeliPort)**，不是 AirportItlwm：

- 系统设置里它显示成"以太网"，选网络、输密码都要用 HeliPort（菜单栏图标），把 HeliPort 加入登录项。
- 代价：没有 AirDrop / Handoff / 隔空投送等 Apple 无线功能。

## 5GHz 网络握手卡在 2/4

### 现象
HeliPort 显示"已连接"，但没有 IP。`dmesg` 里 WPA 握手停在 msg 2/4。

```bash
sudo dmesg | grep itlwm | grep -E "msg [1-4]/4|Deauth|associated"
```

### 原因
这个路由器的 5GHz 网络**同时广播 PSK 和 PSK‑SHA256**（扫描结果 `akms=0xa`，其他网络都是 `0x2`）。itlwm 2.3.0 写死四种认证都支持并优先选 SHA256，但驱动不支持它要求的 802.11w 管理帧保护，握手永远停在第 2 步。

### 修法：改 2 个字节
把驱动里的 `wpa.i_akms` 从 `0xf` 改成 `0x3`（只留 PSK 和 802.1X）。在 itlwm 2.3.0 二进制里是两处 `movl $0xf, 0x18c(%rcx)`，文件偏移 **0x52ccc** 和 **0x53392**，各把立即数 `0x0f` 改成 `0x03`（指令起始位置 +6 处的 1 个字节）。对应源码 `itlwm/itlwm.cpp` 第 186 行和第 269 行。

> 偏移只适用于 itlwm 2.3.0 官方 RELEASE 二进制。改前先用 `otool -tV` 或反汇编确认这两处指令。另一个办法是在路由器里把该网络改成纯 WPA2‑PSK、关掉"管理帧保护"。

### 又一个坑：HeliPort 存了旧密码
打完补丁后仍然停在 msg 2/4，原因是 HeliPort 自动连接用的是**之前保存的错误密码**，现象和 AKM 问题一模一样。在 HeliPort 里对该网络"忘记此网络"再重新输入密码即可。

**经验**：握手停在 2/4 有两种可能——密码错，或 AKM / PMF 不匹配。先看扫描到的 akms 是否为 `0x2`，再用明确的密码直接测试，把两者分开。

结果：5GHz、160MHz、520Mbps，开机自动连接。

## 登录前自动连 Wi‑Fi（远程用）

itlwm 支持在 `itlwm.kext/Contents/Info.plist` 的 `IOKitPersonalities → itlwm → WiFiConfig` 里预置网络，驱动加载时自动连接，不需要登录用户、不依赖 HeliPort。注意这样密码是明文存在 EFI 里的，**不要把这个文件公开**。
