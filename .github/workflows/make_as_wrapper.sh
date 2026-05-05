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
  exec /usr/bin/aarch64-linux-gnu-as.real "$@"
else
  exec /usr/bin/as.real "$@"
fi
EOF
chmod +x "$WRAPPER"

# 备份真正的汇编器，再覆盖
sudo cp /usr/bin/as /usr/bin/as.real
sudo cp /usr/bin/aarch64-linux-gnu-as /usr/bin/aarch64-linux-gnu-as.real
sudo cp "$WRAPPER" /usr/bin/as
sudo cp "$WRAPPER" /usr/bin/aarch64-linux-gnu-as

echo "=== wrapper content ==="
cat "$WRAPPER"
echo "=== wrapper test (aarch64 path) ==="
/usr/bin/aarch64-linux-gnu-as.real --version | head -1
echo "=== wrapper test (host path) ==="
/usr/bin/as.real --version | head -1
echo "=== done ==="