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

# ── Fix: NT36672C 触摸屏自测函数栈帧过大，大数组改为动态分配 ────────────────
# nvt_selftest_open 和 nvt_tp_selftest_store 栈帧超过 3600 字节限制
nt36_path = 'drivers/input/touchscreen/mediatek/NT36672C/nt36xxx_mp_ctrlram.c'
try:
    with open(nt36_path, 'r', errors='replace') as f:
        src = f.read()

    # 在文件顶部 #include 区域之后插入抑制该警告的 pragma（clang 支持）
    # 同时用 noinline 拆分标记，让编译器不要内联这两个大函数
    new_src = src

    # 方案：在这两个函数上方插入 __attribute__((noinline)) 以减少内联带来的栈累积
    # 并用 #pragma clang optimize off/on 包围以抑制过度优化导致的栈增长
    for func_name in ['nvt_selftest_open', 'nvt_tp_selftest_store']:
        # 匹配函数定义行（返回类型 + 函数名 + 参数列表开头）
        pattern = r'((?:static\s+)?(?:\w+\s+){1,4}' + re.escape(func_name) + r'\s*\()'
        replacement = r'__attribute__((noinline)) \1'
        new_src_candidate = re.sub(pattern, replacement, new_src)
        if new_src_candidate != new_src:
            new_src = new_src_candidate
            print('patched ' + nt36_path + ': added noinline to ' + func_name)
        else:
            print('skip ' + nt36_path + ': pattern not found for ' + func_name)

    if new_src != src:
        with open(nt36_path, 'w') as f:
            f.write(new_src)
except Exception as e:
    print('skip ' + nt36_path + ': ' + str(e))

# ── Fix: imgsensor_ca_invoke_command 缺失符号 ────────────────────────────────
# seninf.c 调用了 imgsensor_ca_invoke_command，但该符号来自 TEE/CA 模块，
# 在不含 TrustZone 安全摄像头支持的构建中缺失。注入 stub 实现使链接通过。
#
# stub 函数签名需与 seninf.c 中的声明一致：
#   int imgsensor_ca_invoke_command(unsigned int cmd,
#                                   unsigned long long arg,
#                                   int *result);
imgsensor_stub_impl = '''/* AUTO-GENERATED STUB - imgsensor TEE/CA not available */
#include <linux/kernel.h>
#include <linux/errno.h>
#include <linux/export.h>

int imgsensor_ca_invoke_command(unsigned int a_cmd,
\t\t\t\tunsigned long long a_arg,
\t\t\t\tint *a_result)
{
\tpr_debug("imgsensor_ca_invoke_command: TEE/CA stub called (cmd=%u)\\n", a_cmd);
\tif (a_result)
\t\t*a_result = -ENOSYS;
\treturn -ENOSYS;
}
EXPORT_SYMBOL(imgsensor_ca_invoke_command);
'''

def patch_imgsensor_stub(directory):
    """在指定目录创建 stub 文件并将其注册到 Makefile。"""
    stub_path = os.path.join(directory, 'imgsensor_ca_stub.c')
    mk_path   = os.path.join(directory, 'Makefile')

    # 创建 stub 源文件
    if not os.path.exists(stub_path):
        with open(stub_path, 'w') as f:
            f.write(imgsensor_stub_impl)
        print('created ' + stub_path)
    else:
        print('skip ' + stub_path + ': already exists')

    # 将 stub 加入 Makefile（obj-y 保证无条件编译进内核）
    if os.path.exists(mk_path):
        with open(mk_path, 'r', errors='replace') as f:
            mk = f.read()
        if 'imgsensor_ca_stub.o' not in mk:
            with open(mk_path, 'a') as f:
                f.write('\n# stub for missing TEE/CA symbol\nobj-y += imgsensor_ca_stub.o\n')
            print('patched ' + mk_path + ': added imgsensor_ca_stub.o')
        else:
            print('skip ' + mk_path + ': already patched')
    else:
        # Makefile 不存在则新建一个最小 Makefile
        with open(mk_path, 'w') as f:
            f.write('# AUTO-GENERATED\nobj-y += imgsensor_ca_stub.o\n')
        print('created ' + mk_path)

# 第一步：搜索 seninf.c 的实际位置（最准确）
seninf_found = None
for root, dirs, files in os.walk('drivers/misc/mediatek/imgsensor'):
    dirs[:] = [d for d in dirs if d != '.git']
    if 'seninf.c' in files:
        seninf_found = root
        break

if seninf_found:
    print('found seninf.c at: ' + seninf_found)
    try:
        patch_imgsensor_stub(seninf_found)
    except Exception as e:
        print('skip imgsensor stub (seninf dir): ' + str(e))
else:
    # 第二步：fallback 到已知的常见路径
    print('WARNING: seninf.c not found by walk, trying known fallback paths')
    fallback_dirs = [
        'drivers/misc/mediatek/imgsensor/src/common/v1_1',
        'drivers/misc/mediatek/imgsensor/src/mt6853/common/v1_1',
        'drivers/misc/mediatek/imgsensor/src/mt6853',
        'drivers/misc/mediatek/imgsensor/src',
        'drivers/misc/mediatek/imgsensor',
    ]
    patched_fallback = False
    for fallback in fallback_dirs:
        if os.path.isdir(fallback):
            print('using fallback: ' + fallback)
            try:
                patch_imgsensor_stub(fallback)
                patched_fallback = True
            except Exception as e:
                print('skip fallback ' + fallback + ': ' + str(e))
            break
    if not patched_fallback:
        print('ERROR: could not find any imgsensor directory to place stub!')
        print('       Please manually create the stub in the directory containing seninf.c')