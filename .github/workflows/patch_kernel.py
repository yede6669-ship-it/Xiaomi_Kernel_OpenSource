import re, os

def safe_remove_werror(text):
    lines = text.split('\n')
    result = []
    for line in lines:
        tokens = line.split(' ')
        new_tokens = []
        for token in tokens:
            if '$(' in token:
                new_tokens.append(token)
            elif re.match(r'^-Werror(=[^\s]*)?$', token):
                pass
            else:
                new_tokens.append(token)
        result.append(' '.join(new_tokens))
    return '\n'.join(result)

makefiles = []
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d != '.git']
    for fname in files:
        if fname in ('Makefile', 'Kbuild') or fname.endswith('.mk'):
            makefiles.append(os.path.join(root, fname))

changed = 0
for path in makefiles:
    try:
        with open(path, 'r', errors='replace') as f:
            original = f.read()
        new = safe_remove_werror(original)
        if new != original:
            with open(path, 'w') as f:
                f.write(new)
            changed += 1
    except Exception as e:
        print('skip ' + path + ': ' + str(e))
print(str(changed) + ' file(s) modified')

# ── Fix 1: xiaomi_touch.c 无参数函数声明补 void ──────────────────────────────
touch_path = 'drivers/input/touchscreen/mediatek/xiaomi/xiaomi_touch.c'
try:
    with open(touch_path, 'r', errors='replace') as f:
        src = f.read()
    # 只针对函数定义行（后面紧跟换行+{），避免误改函数指针/调用
    src = re.sub(
        r'\b(struct\s+\w+\s*\*?\s*\w+)\(\)(\s*\n\s*\{)',
        r'\1(void)\2',
        src
    )
    with open(touch_path, 'w') as f:
        f.write(src)
    print('patched ' + touch_path)
except Exception as e:
    print('skip ' + touch_path + ': ' + str(e))

# ── Fix 2: kernel/cfi.c void* 算术赋值给 uint64_t ────────────────────────────
cfi_path = 'kernel/cfi.c'
try:
    with open(cfi_path, 'r', errors='replace') as f:
        src = f.read()
    old = '        func_addr = ptr + (imm26 << 2) - signextend;'
    new = '        func_addr = (uint64_t)(uintptr_t)ptr + (imm26 << 2) - signextend;'
    if old in src:
        src = src.replace(old, new, 1)
        with open(cfi_path, 'w') as f:
            f.write(src)
        print('patched ' + cfi_path)
    else:
        print('skip ' + cfi_path + ': pattern not found (already patched?)')
except Exception as e:
    print('skip ' + cfi_path + ': ' + str(e))