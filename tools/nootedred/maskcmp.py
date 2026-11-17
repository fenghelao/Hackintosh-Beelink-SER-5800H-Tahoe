# 用旧数据里记录的"外部引用字段"位置做掩码，比较 15.8.1 参考函数与本机 15.8.3 函数：
# 掩码后完全相同 => 代码逻辑没变，只是引用的外部地址变了。
import sys, re, json, hashlib, struct
src, tools = sys.argv[1], sys.argv[2]
sys.path.insert(0, tools)
from metal_cache import CacheReader, CACHE
text = open(src + '/NootedRed/UserSequoiaSurfaceData.hpp').read()
main, submit = text.split('namespace Submit {')
def arrays(t, prefix):
    out = {}
    for m in re.finditer(r'inline constexpr UInt8 (%s\d+)\[\] = \{(.*?)\};' % prefix, t, re.S):
        out[m[1]] = bytes(int(x, 16) for x in re.findall(r'0x([0-9A-F]{2})', m[2]))
    return out
def refs(t):
    out = {}
    for m in re.finditer(r'Reference (ResolverOriginalRefs\d+)\[\] = \{(.*?)\};', t, re.S):
        out[m[1]] = [tuple(int(x.strip().replace('ULL',''), 0) for x in r.split(',')) for r in re.findall(r'\{([^{}]+)\}', m[2])]
    return out
def images(t):
    m = re.search(r'ResolverImages\[\] = \{(.*?)\};', t, re.S)
    return re.findall(r'\{"([^"]+)"', m[1])
def funcs(t):
    m = re.search(r'ResolverFunctions\[\] = \{(.*?)\};', t, re.S)
    return [tuple(x.strip() for x in r.split(',')) for r in re.findall(r'\{([^{}]+)\}', m[1])]
uuid = open(str(CACHE) + '/dyld_shared_cache_x86_64h', 'rb').read(104)[88:104].hex()
c = CacheReader(CACHE, uuid)
for label, t in (('main', main), ('submit', submit)):
    A, R, I, F = arrays(t, 'ResolverOriginal'), refs(t), images(t), funcs(t)
    print('==', label, 'images:', [p.split('/')[-1] for p in I])
    for i, f in enumerate(F):
        img, rva = int(f[0]), int(f[1].rstrip('ULL'), 16)
        ref = A['ResolverOriginal%d' % i]
        rr = R.get('ResolverOriginalRefs%d' % i, [])
        local = c.read(c.image_base + rva, len(ref))
        a, b = bytearray(ref), bytearray(local)
        raw_diff = sum(x != y for x, y in zip(a, b))
        for off, im, trva, ind in rr:
            a[off:off+4] = b[off:off+4] = b'\0\0\0\0'
        masked_diff = [k for k, (x, y) in enumerate(zip(a, b)) if x != y]
        changed = []
        for off, im, trva, ind in rr:
            if ref[off:off+4] != local[off:off+4]:
                changed.append((off, I[im].split('/')[-1], hex(trva), ind,
                                struct.unpack('<i', local[off:off+4])[0] - struct.unpack('<i', ref[off:off+4])[0]))
        print('func%d rva %#x size %d refs %d | raw diff bytes %d | diff after masking refs: %d | changed refs: %d' %
              (i, rva, len(ref), len(rr), raw_diff, len(masked_diff), len(changed)))
        by = {}
        for off, name, trva, ind, delta in changed:
            by.setdefault((name, ind, delta), []).append(off)
        for k, v in sorted(by.items(), key=lambda kv: -len(kv[1]))[:8]:
            print('     ->', k[0], 'indirect=%d' % k[1], 'delta=%+d' % k[2], 'x%d' % len(v))
        if masked_diff:
            print('     UNEXPECTED offsets:', masked_diff[:20])
c.close()
