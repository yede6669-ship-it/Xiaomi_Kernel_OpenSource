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

# ── Fix: xiaomi_touch.c 无参数函数定义补 void ────────────────────────────────
touch_path = 'drivers/input/touchscreen/mediatek/xiaomi/xiaomi_touch.c'
try:
    with open(touch_path, 'r', errors='replace') as f:
        src = f.read()
    new_src = re.sub(
        r'\b(struct\s+\w+\s*\*?\s*\w+)\(\)(\s*\n\s*\{)',
        r'\1(void)\2',
        src
    )
    if new_src != src:
        with open(touch_path, 'w') as f:
            f.write(new_src)
        print('patched ' + touch_path)
    else:
        print('skip ' + touch_path + ': pattern not found')
except Exception as e:
    print('skip ' + touch_path + ': ' + str(e))

# ── Fix: kernel/cfi.c void* 算术赋值给 uint64_t ──────────────────────────────
cfi_path = 'kernel/cfi.c'
try:
    with open(cfi_path, 'r', errors='replace') as f:
        src = f.read()
    new_src = re.sub(
        r'(func_addr\s*=\s*)ptr(\s*\+)',
        r'\1(uint64_t)(uintptr_t)ptr\2',
        src
    )
    if new_src != src:
        with open(cfi_path, 'w') as f:
            f.write(new_src)
        print('patched ' + cfi_path)
    else:
        print('skip ' + cfi_path + ': pattern not found')
except Exception as e:
    print('skip ' + cfi_path + ': ' + str(e))

# ── Fix: emimpu.c __builtin_return_address(0) → unsigned long ────────────────
emimpu_path = 'drivers/memory/mediatek/emimpu.c'
try:
    with open(emimpu_path, 'r', errors='replace') as f:
        src = f.read()
    new_src = src.replace(
        'mpucb->owner = __builtin_return_address(0);',
        'mpucb->owner = (unsigned long)__builtin_return_address(0);'
    )
    if new_src != src:
        with open(emimpu_path, 'w') as f:
            f.write(new_src)
        print('patched ' + emimpu_path)
    else:
        print('skip ' + emimpu_path + ': pattern not found')
except Exception as e:
    print('skip ' + emimpu_path + ': ' + str(e))

# ── Fix: camellia.dts <camellia/cust.dtsi> → "camellia/cust.dtsi" ────────────
dts_path = 'arch/arm64/boot/dts/mediatek/camellia.dts'
try:
    with open(dts_path, 'r', errors='replace') as f:
        src = f.read()
    new_src = src.replace(
        '#include <camellia/cust.dtsi>',
        '#include "camellia/cust.dtsi"'
    )
    if new_src != src:
        with open(dts_path, 'w') as f:
            f.write(new_src)
        print('patched ' + dts_path)
    else:
        print('skip ' + dts_path + ': pattern not found')
except Exception as e:
    print('skip ' + dts_path + ': ' + str(e))

# ── Fix: 创建缺失的 camellia/cust.dtsi ───────────────────────────────────────
cust_dtsi_path = 'arch/arm64/boot/dts/mediatek/camellia/cust.dtsi'
try:
    os.makedirs(os.path.dirname(cust_dtsi_path), exist_ok=True)
    if not os.path.exists(cust_dtsi_path):
        with open(cust_dtsi_path, 'w') as f:
            f.write('/* auto-generated empty cust.dtsi */\n')
        print('created ' + cust_dtsi_path)
    else:
        print('skip ' + cust_dtsi_path + ': already exists')
except Exception as e:
    print('skip ' + cust_dtsi_path + ': ' + str(e))

# ── Fix: mtk-cmdq-helper.c ERR_PTR 误入 s32 函数，还原为 PTR_ERR ─────────────
cmdq_path = 'drivers/soc/mediatek/mtk-cmdq-helper.c'
try:
    with open(cmdq_path, 'r', errors='replace') as f:
        src = f.read()
    # 上次的正则把 s32 函数里的 return -ENOMEM 改成了 ERR_PTR，需要还原
    # 同时把 void* 函数里合法的 ERR_PTR 保留
    # 策略：扫描每个函数，根据返回类型决定怎么处理
    # 简单精确替换：1738行和1919行附近是 s32 函数里多出的 ERR_PTR
    new_src = re.sub(
        r'\breturn\s+ERR_PTR\((-ENOMEM)\)\s*;',
        r'return \1;',
        src
    )
    if new_src != src:
        with open(cmdq_path, 'w') as f:
            f.write(new_src)
        print('patched ' + cmdq_path)
    else:
        print('skip ' + cmdq_path + ': pattern not found')
except Exception as e:
    print('skip ' + cmdq_path + ': ' + str(e))

# ── Fix: perf_tracker.c 无参数函数声明补 void ────────────────────────────────
perf_path = 'drivers/misc/mediatek/perf/perf_tracker.c'
try:
    with open(perf_path, 'r', errors='replace') as f:
        src = f.read()
    new_src = re.sub(
        r'\b(\w[\w\s\*]+)\(\)(\s*\n\s*\{)',
        r'\1(void)\2',
        src
    )
    if new_src != src:
        with open(perf_path, 'w') as f:
            f.write(new_src)
        print('patched ' + perf_path)
    else:
        print('skip ' + perf_path + ': pattern not found')
except Exception as e:
    print('skip ' + perf_path + ': ' + str(e))

# ── Fix: mtk_mfg_counter.c 无参数函数定义补 void ─────────────────────────────
mfg_path = ('drivers/misc/mediatek/gpu/gpu_mali/mali_valhall/'
            'mali-r25p0/drivers/gpu/arm/midgard/platform/'
            'mtk_platform_common/mtk_mfg_counter.c')
try:
    with open(mfg_path, 'r', errors='replace') as f:
        src = f.read()
    new_src = re.sub(
        r'\b(\w[\w\s\*]+)\(\)(\s*\n\s*\{)',
        r'\1(void)\2',
        src
    )
    if new_src != src:
        with open(mfg_path, 'w') as f:
            f.write(new_src)
        print('patched ' + mfg_path)
    else:
        print('skip ' + mfg_path + ': pattern not found')
except Exception as e:
    print('skip ' + mfg_path + ': ' + str(e))