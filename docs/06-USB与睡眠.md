# 06 USB 与睡眠

## USB 控制器

| 控制器 | 说明 |
|---|---|
| XHC2（pcidebug 4:0:4） | 蓝牙（USB2 3 号口）、一个 USB3 Hub、一个 USB2 Hub |
| XHC0 | 前后面板常用的 USB 口（键盘鼠标） |

目前**没有使用任何 USB 映射**。在 Tahoe 上，自制的 XHC2 映射会让整个控制器消失，详见 [05 蓝牙](05-蓝牙.md#坑-2usb-映射让整个控制器消失)。

## USB 键盘"自动掉线"

### 现象
USB 键盘隔一会儿就断开再重连。

### 原因
`pmset` 里 `sleep = 1`，电脑空闲 1 分钟就睡眠、随即又被唤醒。每次睡眠 / 唤醒，USB 端口都会断电重连。日志里依次出现 `port is powering off` → `upstream hub is terminating` → 重新 enumerated，半小时内发生了 9 次，每次都紧跟 `PMRD: System Wake`。

```bash
pmset -g
/usr/bin/log show --last 1h --style compact --predicate 'eventMessage CONTAINS "System Wake" OR eventMessage CONTAINS "powering off"'
```

### 处理
这台机器的睡眠本身没调通（睡下去马上醒），直接关掉睡眠，保留显示器熄屏：

```bash
pmset -g > ~/pmset-before.txt   # 先备份
sudo pmset -a sleep 0 disksleep 0 powernap 0 standby 0 womp 0 hibernatemode 0 proximitywake 0 tcpkeepalive 0
```

要用睡眠，得另外排查唤醒源（`pmset -g log | grep -i wake`）。

> 另一种掉线发生在 Sequoia 显卡卡死期间（`hardware connection lost`），属于显卡问题的连带，显卡修好后没再出现。
