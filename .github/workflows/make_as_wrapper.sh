#!/bin/bash
WRAPPER="$1/as"
cat > "$WRAPPER" << 'EOF'
#!/bin/bash
IS_AARCH64=0
for arg in "$@"; do
  if [ "$arg" = "-EL" ] || [ "$arg" = "-EB" ]; then
    IS_AARCH64=1
    break
  fi
done

if [ "$IS_AARCH64" = "1" ]; then
  exec /usr/bin/aarch64-linux-gnu-as "$@"
else
  exec /usr/bin/x86_64-linux-gnu-as "$@"
fi
EOF
chmod +x "$WRAPPER"
cp "$WRAPPER" "$1/aarch64-linux-gnu-as"

# 覆盖系统 as，防止 clang 绕过 PATH 直接调用 /usr/bin/as
sudo cp "$WRAPPER" /usr/bin/as
sudo cp "$WRAPPER" /usr/bin/aarch64-linux-gnu-as

echo "=== wrapper content ==="
cat "$WRAPPER"
echo "=== wrapper test ==="
"$WRAPPER" --version