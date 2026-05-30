import re, os, subprocess, shutil

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

# ── Fix: NT36672C 栈帧超限 ───────────────────────────────────────────────────
nt36_path = 'drivers/input/touchscreen/mediatek/NT36672C/nt36xxx_mp_ctrlram.c'
try:
    with open(nt36_path, 'r', errors='replace') as f:
        src = f.read()

    new_src = src

    for func_name in ['nvt_selftest_open', 'nvt_tp_selftest_store']:
        p1 = r'\bstatic\b(\s+(?:(?:int|void|ssize_t|long)\s+))(' + re.escape(func_name) + r'\s*\()'
        r1 = r'static noinline\1\2'
        candidate = re.sub(p1, r1, new_src)
        if candidate != new_src:
            new_src = candidate
            print('patched ' + nt36_path + ': noinline (static) -> ' + func_name)
            continue
        p2 = r'\b((?:int|void|ssize_t|long)\s+)(' + re.escape(func_name) + r'\s*\()'
        r2 = r'noinline \1\2'
        candidate = re.sub(p2, r2, new_src)
        if candidate != new_src:
            new_src = candidate
            print('patched ' + nt36_path + ': noinline (non-static) -> ' + func_name)
            continue
        print('WARN: could not add noinline to ' + func_name)

    pragma_guard = '#pragma clang diagnostic ignored "-Wframe-larger-than="'
    if pragma_guard not in new_src:
        new_src = re.sub(
            r'(#include\s)',
            '#pragma clang diagnostic ignored "-Wframe-larger-than="\n\\1',
            new_src,
            count=1
        )
        print('patched ' + nt36_path + ': added clang pragma')

    if new_src != src:
        with open(nt36_path, 'w') as f:
            f.write(new_src)
except Exception as e:
    print('skip ' + nt36_path + ': ' + str(e))

# ── Fix: imgsensor_ca_invoke_command 链接期缺失符号 ──────────────────────────
seninf_candidates = [
    'drivers/misc/mediatek/imgsensor/src/common/v1_1/seninf.c',
    'drivers/misc/mediatek/imgsensor/src/mt6853/common/v1_1/seninf.c',
    'drivers/misc/mediatek/imgsensor/src/mt6853/seninf.c',
]

seninf_paths = [p for p in seninf_candidates if os.path.exists(p)]

if not seninf_paths:
    for root, dirs, files in os.walk('drivers/misc/mediatek/imgsensor'):
        dirs[:] = [d for d in dirs if d != '.git']
        if 'seninf.c' in files:
            seninf_paths.append(os.path.join(root, 'seninf.c'))

if seninf_paths:
    for seninf_path in seninf_paths:
        try:
            with open(seninf_path, 'r', errors='replace') as f:
                lines = f.readlines()

            if any('AUTO-PATCHED-IFDEF' in l for l in lines):
                print('skip ' + seninf_path + ': 已打过补丁')
                continue

            new_lines = []
            i = 0
            patched_count = 0

            while i < len(lines):
                line = lines[i]

                if 'imgsensor_ca_invoke_command' in line:
                    block = line
                    j = i + 1
                    while ';' not in block and j < len(lines):
                        block += lines[j]
                        j += 1
                    new_lines.append('#ifdef CONFIG_IMGSENSOR_CA /* AUTO-PATCHED-IFDEF */\n')
                    new_lines.append(block)
                    new_lines.append('#endif /* CONFIG_IMGSENSOR_CA */\n')
                    patched_count += 1
                    i = j
                    continue

                new_lines.append(line)
                i += 1

            if patched_count > 0:
                with open(seninf_path, 'w') as f:
                    f.writelines(new_lines)
                print('patched ' + seninf_path + ': 共包住 ' + str(patched_count) + ' 处')
            else:
                count = src.count('imgsensor_ca_invoke_command')
                print('WARN ' + seninf_path + ': 未找到任何引用，该符号出现 ' + str(count) + ' 次')

        except Exception as e:
            print('skip ' + seninf_path + ': ' + str(e))
else:
    print('ERROR: 找不到 seninf.c，补丁未注入')

# ── 集成 KernelSU-Next ───────────────────────────────────────────────────────
print('\n>>> 开始集成 KernelSU-Next')

ksu_dst = 'drivers/kernelsu'
defconfig = 'arch/arm64/configs/camellia_defconfig'

try:
    # 1. clone KernelSU-Next 到 drivers/kernelsu
    if not os.path.exists(ksu_dst):
        print('正在 clone KernelSU-Next...')
        subprocess.run([
            'git', 'clone',
            'https://github.com/KernelSU-Next/KernelSU-Next.git',
            '--depth=1',
            ksu_dst
        ], check=True)
        print('clone 完成')
    else:
        print('skip clone: ' + ksu_dst + ' 已存在，尝试更新')
        subprocess.run(['git', '-C', ksu_dst, 'pull', '--depth=1'],
                       check=False)

    # 2. 确认 KSU kernel 子目录存在
    ksu_kernel_dir = os.path.join(ksu_dst, 'kernel')
    if not os.path.isdir(ksu_kernel_dir):
        raise FileNotFoundError('KSU kernel 子目录不存在: ' + ksu_kernel_dir)
    print('KSU kernel 子目录确认: ' + ksu_kernel_dir)

    # 3. 在 drivers/Makefile 里加入编译入口
    drivers_mk = 'drivers/Makefile'
    with open(drivers_mk, 'r', errors='replace') as f:
        mk_src = f.read()
    if 'kernelsu' not in mk_src:
        with open(drivers_mk, 'a') as f:
            f.write('\n# KernelSU-Next\nobj-$(CONFIG_KSU) += kernelsu/kernel/\n')
        print('patched drivers/Makefile: 加入 KSU 编译入口')
    else:
        print('skip drivers/Makefile: KSU 入口已存在')

    # 4. 在 defconfig 里开启 CONFIG_KSU 和依赖项
    with open(defconfig, 'r', errors='replace') as f:
        def_src = f.read()

    configs_to_add = []

    # CONFIG_KSU 主开关
    if 'CONFIG_KSU=' not in def_src:
        configs_to_add.append('CONFIG_KSU=y')
    else:
        # 确保是 y 不是 n
        def_src = re.sub(r'CONFIG_KSU=n', 'CONFIG_KSU=y', def_src)
        print('CONFIG_KSU 已存在，确认为 y')

    # KPROBES 相关（KSU hook 依赖）
    for cfg in [
        'CONFIG_KPROBES',
        'CONFIG_HAVE_KPROBES',
        'CONFIG_KPROBE_EVENTS',
        'CONFIG_KALLSYMS',
        'CONFIG_KALLSYMS_ALL',
    ]:
        if cfg + '=y' not in def_src and cfg + '=' not in def_src:
            configs_to_add.append(cfg + '=y')

    if configs_to_add:
        with open(defconfig, 'a') as f:
            f.write('\n# KernelSU-Next\n')
            for cfg in configs_to_add:
                f.write(cfg + '\n')
        print('patched defconfig: 加入 ' + str(configs_to_add))
    else:
        print('skip defconfig: 所有 KSU 配置已存在')

    # 5. 如果内核不支持 kprobes，改用手动 hook 模式
    # 检查 defconfig 里是否明确禁用了 KPROBES
    with open(defconfig, 'r', errors='replace') as f:
        def_src_check = f.read()
    if '# CONFIG_KPROBES is not set' in def_src_check:
        print('WARN: KPROBES 被禁用，KSU 将使用手动 hook 模式')
        print('      需要手动在 fs/exec.c / fs/open.c / fs/read_write.c 添加 KSU hook 调用')
        print('      参考: https://kernelsu.org/guide/how-to-integrate-for-non-gki.html')

    print('>>> KernelSU-Next 集成完成')

except subprocess.CalledProcessError as e:
    print('ERROR: git 操作失败: ' + str(e))
except Exception as e:
    print('ERROR: KernelSU-Next 集成失败: ' + str(e))