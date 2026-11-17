# NootedRed 相关工具

| 文件 | 用途 |
|---|---|
| `check.sh` | 重启后检查 NootedRed 各项用户态修复是否 Applied、有无 Rejected，以及本次开机 GPU hang 次数 |
| `maskcmp.py` | 把参考数据里的外部引用位置遮住，和本机 dyld 缓存里的函数逐字节比较，确认"代码没变、只是地址变了" |
| `binpatch.py` | 把重新生成的参考数据原位写入官方 RELEASE 二进制（只改 `__TEXT,__const` 常量） |

`maskcmp.py` 依赖 NootedRed 源码 `tools/` 目录里的 `metal_cache.py`：
```bash
python3 maskcmp.py <NootedRed源码目录> <NootedRed源码目录>/tools
python3 binpatch.py 旧UserSequoiaSurfaceData.hpp 新UserSequoiaSurfaceData.hpp NootedRed原版二进制 输出二进制
```
这些是针对 Sequoia 15.8.3（24H241）做的；Tahoe 26.7.2 上官方数据已经匹配，不需要。详细步骤见 docs/02-显卡-NootedRed.md。
