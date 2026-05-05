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
  exec /usr/bin/as.real "$@"
fi
EOF
chmod +x "$WRAPPER"
cp "$WRAPPER" "$1/aarch64-linux-gnu-as"

# 备份系统原版 as
sudo cp /usr/bin/as /usr/bin/as.real
sudo cp "$WRAPPER" /usr/bin/as
sudo cp "$WRAPPER" /usr/bin/aarch64-linux-gnu-as

echo "=== wrapper content ==="
cat "$WRAPPER"
echo "=== wrapper test (aarch64 path) ==="
/usr/bin/aarch64-linux-gnu-as --version | head -1
echo "=== wrapper test (host path) ==="
/usr/bin/as.real --version | head -1
echo "=== done ==="