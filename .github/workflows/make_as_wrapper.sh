#!/bin/bash
WRAPPER="$1/as"
cat > "$WRAPPER" << 'EOF'
#!/bin/bash
for arg in "$@"; do
  if [ "$arg" = "-EL" ] || [ "$arg" = "-EB" ]; then
    exec /usr/bin/aarch64-linux-gnu-as "$@"
  fi
done
exec /usr/bin/as "$@"
EOF
chmod +x "$WRAPPER"
cp "$WRAPPER" "$1/aarch64-linux-gnu-as"
echo "=== wrapper content ==="
cat "$WRAPPER"
echo "=== wrapper test ==="
"$WRAPPER" --version