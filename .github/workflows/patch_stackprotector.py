with open('Makefile', 'r') as f:
    lines = f.readlines()
out = []
i = 0
while i < len(lines):
    line = lines[i]
    if 'Cannot use CONFIG_CC_STACKPROTECTOR' in line and 'exit 1' in line:
        out.append('# PATCHED: ' + line)
    elif 'Cannot use CONFIG_CC_STACKPROTECTOR' in line:
        out.append('# PATCHED: ' + line)
        if i + 1 < len(lines) and 'exit 1' in lines[i + 1]:
            i += 1
            out.append('# PATCHED: ' + lines[i])
    else:
        out.append(line)
    i += 1
with open('Makefile', 'w') as f:
    f.writelines(out)
patched = [l for l in out if 'PATCHED' in l]
print(str(len(patched)) + ' line(s) patched')
for l in patched:
    print(l.rstrip())