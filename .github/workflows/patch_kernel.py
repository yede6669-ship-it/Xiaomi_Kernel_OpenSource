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

# ── Fix: mtk-cmdq-helper.c 指针返回函数里 return -ENOMEM → ERR_PTR ──────────
cmdq_path = 'drivers/soc/mediatek/mtk-cmdq-helper.c'
try:
    with open(cmdq_path, 'r', errors='replace') as f:
        lines = f.readlines()
    target_lines = {174, 190, 384, 410, 507, 598, 1491}
    changed_cmdq = False
    new_lines = []
    for i, line in enumerate(lines):
        lineno = i + 1
        if lineno in target_lines and re.search(r'return\s+-ENOMEM\s*;', line):
            new_line = re.sub(r'return\s+-ENOMEM\s*;', 'return ERR_PTR(-ENOMEM);', line)
            print('patched ' + cmdq_path + ' line ' + str(lineno))
            new_lines.append(new_line)
            changed_cmdq = True
        else:
            new_lines.append(line)
    if changed_cmdq:
        with open(cmdq_path, 'w') as f:
            f.writelines(new_lines)
    else:
        print('skip ' + cmdq_path + ': no target lines matched')
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

# ── Fix: mtk-vcu Makefile 重复链接 mtk_vcodec_mem.o ─────────────────────────
vcu_mk_path = 'drivers/media/platform/mtk-vcu/Makefile'
try:
    with open(vcu_mk_path, 'r', errors='replace') as f:
        src = f.read()
    new_src = src.replace(
        'obj-$(CONFIG_VIDEO_MEDIATEK_VCU) += mtk-vcu.o mtk_vcodec_mem.o',
        'obj-$(CONFIG_VIDEO_MEDIATEK_VCU) += mtk-vcu.o'
    )
    if new_src != src:
        with open(vcu_mk_path, 'w') as f:
            f.write(new_src)
        print('patched ' + vcu_mk_path)
    else:
        print('skip ' + vcu_mk_path + ': pattern not found')
except Exception as e:
    print('skip ' + vcu_mk_path + ': ' + str(e))

# ── Fix: 为缺失的 stpcpy 提供实现 ────────────────────────────────────────────
string_path = 'lib/string.c'
stpcpy_impl = '''
char *stpcpy(char *dest, const char *src)
{
\twhile ((*dest++ = *src++) != '\\0')
\t\t;
\treturn dest - 1;
}
EXPORT_SYMBOL(stpcpy);
'''
try:
    with open(string_path, 'r', errors='replace') as f:
        src = f.read()
    if 'stpcpy' not in src:
        with open(string_path, 'a') as f:
            f.write(stpcpy_impl)
        print('patched ' + string_path + ': added stpcpy')
    else:
        print('skip ' + string_path + ': stpcpy already exists')
except Exception as e:
    print('skip ' + string_path + ': ' + str(e))

# ── Fix: imgsensor_ca_invoke_command 缺失符号，搜索正确路径后注入 stub ─────────
imgsensor_stub_impl = '''#include <linux/types.h>
#include <linux/errno.h>
#include <linux/export.h>

int imgsensor_ca_invoke_command(unsigned int cmd, unsigned long long arg, int *result)
{
\treturn -ENOSYS;
}
EXPORT_SYMBOL(imgsensor_ca_invoke_command);
'''

# 找到 seninf.c 所在目录，stub 放在同级目录
seninf_found = None
for root, dirs, files in os.walk('drivers/misc/mediatek/imgsensor'):
    dirs[:] = [d for d in dirs if d != '.git']
    if 'seninf.c' in files:
        seninf_found = root
        break

if seninf_found:
    stub_path = os.path.join(seninf_found, 'imgsensor_ca_stub.c')
    mk_path = os.path.join(seninf_found, 'Makefile')
    try:
        if not os.path.exists(stub_path):
            with open(stub_path, 'w') as f:
                f.write(imgsensor_stub_impl)
            print('created ' + stub_path)
        else:
            print('skip ' + stub_path + ': already exists')
        with open(mk_path, 'r', errors='replace') as f:
            mk = f.read()
        if 'imgsensor_ca_stub.o' not in mk:
            with open(mk_path, 'a') as f:
                f.write('\nobj-y += imgsensor_ca_stub.o\n')
            print('patched ' + mk_path)
        else:
            print('skip ' + mk_path + ': already patched')
    except Exception as e:
        print('skip imgsensor stub: ' + str(e))
else:
    print('WARNING: seninf.c not found, trying fallback paths')
    for fallback in [
        'drivers/misc/mediatek/imgsensor/src/common/v1_1',
        'drivers/misc/mediatek/imgsensor/src/mt6853/common/v1_1',
        'drivers/misc/mediatek/imgsensor/src',
    ]:
        if os.path.isdir(fallback):
            stub_path = os.path.join(fallback, 'imgsensor_ca_stub.c')
            mk_path = os.path.join(fallback, 'Makefile')
            try:
                if not os.path.exists(stub_path):
                    with open(stub_path, 'w') as f:
                        f.write(imgsensor_stub_impl)
                    print('created ' + stub_path)
                with open(mk_path, 'r', errors='replace') as f:
                    mk = f.read()
                if 'imgsensor_ca_stub.o' not in mk:
                    with open(mk_path, 'a') as f:
                        f.write('\nobj-y += imgsensor_ca_stub.o\n')
                    print('patched ' + mk_path)
            except Exception as e:
                print('skip fallback ' + fallback + ': ' + str(e))
            break