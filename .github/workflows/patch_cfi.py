import re

path = 'kernel/cfi.c'
try:
    with open(path, 'r', errors='replace') as f:
        src = f.read()
    # 把 void* 赋值给 uint64_t 的地方加强制转换
    src = re.sub(
        r'(uint64_t\s+\w+\s*=\s*)((?!.*\(uint64_t\)).*?)(;)',
        lambda m: m.group(1) + '(uint64_t)(uintptr_t)' + m.group(2).strip() + m.group(3)
        if 'void *' in m.group(2) or re.search(r'\b\w+\b\s*$', m.group(2))
        else m.group(0),
        src
    )
    with open(path, 'w') as f:
        f.write(src)
    print('patched ' + path)
except Exception as e:
    print('skip ' + path + ': ' + str(e))