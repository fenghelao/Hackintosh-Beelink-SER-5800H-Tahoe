# wifi：itlwm 命令行排查工具

通过 HeliPort 的 ClientKit 直接和 itlwm 驱动通信，列出扫描到的网络及其加密参数（akms 等），也可以绕过 HeliPort 直接连接，用来区分"密码错"和"AKM/PMF 不匹配"。

编译（需要 [HeliPort](https://github.com/OpenIntelWireless/HeliPort) 源码）：
```bash
clang -O1 -I<HeliPort源码>/ClientKit wifi.c <HeliPort源码>/ClientKit/Api.c -framework IOKit -framework CoreFoundation -o wifi
```

用法：
```bash
./wifi              # 当前状态 + 所有网络的 protos/akms/ciphers
./wifi 关键词        # 只看名字含关键词的网络
./wifi assoc 网络名 密码
./wifi disassoc 网络名
```
`akms=0x2` 是普通 WPA2‑PSK；`0xa` 表示同时广播 PSK 和 PSK‑SHA256，itlwm 2.3.0 原版会握手失败（见 docs/04-WiFi.md）。
