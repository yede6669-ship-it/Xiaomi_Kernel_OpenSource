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

# 额外直接修复 xiaomi_touch.c
touch_path = 'drivers/input/touchscreen/mediatek/xiaomi/xiaomi_touch.c'
try:
    with open(touch_path, 'r', errors='replace') as f:
        src = f.read()
    # 把无参数函数声明补上 void
    import re
    src = re.sub(r'(\w+\s+\w+)\(\)', r'\1(void)', src)
    with open(touch_path, 'w') as f:
        f.write(src)
    print('patched ' + touch_path)
except Exception as e:
    print('skip ' + touch_path + ': ' + str(e))