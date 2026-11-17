# 把官方 RELEASE 版 kext 里的 15.8.1 参考数据，原位替换成针对本机 15.8.3 (24H241) 重新生成的数据。
# 只改常量数据（长度、布局完全相同），不改任何代码。
import sys, re, struct, hashlib
orig_h, new_h, kin, kout = sys.argv[1:5]
def parse(path):
    t = open(path).read()
    out, ns = [], 'main'
    for m in re.finditer(r'namespace Submit \{|inline constexpr UInt8 (\w+)\[\] = \{(.*?)\};|inline constexpr UserCacheResolver::Reference (\w+)\[\] = \{(.*?)\};', t, re.S):
        if m[0].startswith('namespace'):
            ns = 'submit'; continue
        if m[1]:
            out.append((ns + '.' + m[1], bytes(int(x, 16) for x in re.findall(r'0x([0-9A-F]{2})', m[2]))))
        else:
            rows = [[int(v.strip().replace('ULL', ''), 0) for v in r.split(',')] for r in re.findall(r'\{([^{}]+)\}', m[4])]
            out.append((ns + '.' + m[3], b''.join(struct.pack('<IIQI4x', *r) for r in rows)))
    return out
old, new = parse(orig_h), parse(new_h)
assert [n for n, _ in old] == [n for n, _ in new], 'array list differs'
assert all(len(a[1]) == len(b[1]) for a, b in zip(old, new)), 'array size differs'
data = bytearray(open(kin, 'rb').read())
print('input kext sha256', hashlib.sha256(data).hexdigest()[:16], 'size', len(data))
def find_all(buf, pat):
    res, i = [], buf.find(pat)
    while i >= 0:
        res.append(i); i = buf.find(pat, i + 1)
    return res
changed = [(n, a, b) for (n, a), (_, b) in zip(old, new) if a != b]
# CacheUUID 只用于生成期溯源，官方二进制里没有这份数据（已被编译器丢弃），跳过
assert bytes(data).find(dict(old)['main.CacheUUID']) < 0
changed = [c for c in changed if c[0] != 'main.CacheUUID']
new = [x for x in new if x[0] != 'main.CacheUUID']
print('arrays total', len(old), 'changed', len(changed))
# 先全部定位，再统一写入，避免互相影响
plan, missing = [], []
for n, a, b in changed:
    locs = find_all(bytes(data), a)
    if not locs: missing.append(n)
    plan.append((n, locs, a, b))
    print('  %-34s size %5d  found at %s' % (n, len(a), [hex(x) for x in locs] or 'NOT FOUND'))
if missing:
    print('ABORT: not found:', missing); sys.exit(1)
snapshot = bytes(data)
for n, locs, a, b in plan:
    for off in locs:
        assert snapshot[off:off+len(a)] == a
        data[off:off+len(b)] = b
final = bytes(data)
# 校验：新头文件里的每个数组都必须能在成品里找到；任何被改动的旧数组都不能残留
absent = [n for n, b in new if final.find(b) < 0]
stale = [n for n, a, b in changed if final.find(a) >= 0]
print('new arrays absent from output:', absent)
print('stale old arrays remaining   :', stale)
print('bytes changed:', sum(x != y for x, y in zip(snapshot, final)), 'of', len(final))
if absent or stale: sys.exit(1)
open(kout, 'wb').write(final)
print('output kext sha256', hashlib.sha256(final).hexdigest()[:16])
