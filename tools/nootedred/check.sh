#!/bin/zsh
# 重启后运行：查看 NootedRed 用户态修复是否生效
echo "系统: $(sw_vers -productVersion) ($(sw_vers -buildVersion))  启动参数: $(nvram boot-args | cut -f2-)"
P=$(ioreg -l -w0 | grep -oE '"NRed[A-Za-z]*" = [0-9]+' | sort -u)
show() { v=$(echo "$P" | grep "\"$1\"" | awk '{print $3}'); echo "  $1 = ${v:-（无）}"; }
echo "应为 1（表示修复已匹配/已安装）:"
for k in NRedImmediateSyncDynamicMatched NRedImmediateSyncDynamicApplied NRedSubmitGuardApplied NRedSubmitGuardWindowServerApplied; do show $k; done
echo "应为（无）（表示没有被拒绝）:"
for k in NRedSubmitGuardDynamicRejected NRedImmediateSyncDynamicRejected NRedSubmitGuardRejected NRedImmediateSyncRejected NRedSubmitGuardRollbackFailed NRedImmediateSyncLastError; do show $k; done
echo "全部 NRed 状态:"; echo "$P" | sed 's/^/  /'
echo "本次开机以来 GPU 卡死次数: $(/usr/bin/log show --last boot --style compact --predicate 'process == "kernel" AND eventMessage BEGINSWITH "GPU hang"' 2>/dev/null | grep -c 'GPU hang')"
