#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "[1/3] Checking JS syntax..."
node --check lib/index.js
node --check lib/client.js
node --check lib/tools.js

echo "[2/3] Checking Python syntax & empty-library resilience..."
python3 -m py_compile scripts/core.py scripts/data_fetcher.py scripts/mcp_server.py
HOME="/tmp/nonexistent_reading_os_home" READING_OS_APPLE_BOOKS_DIR="/nonexistent_reading_os_dir" READING_OS_BOOKS_DIR="/nonexistent_reading_os_books" \
  python3 scripts/data_fetcher.py | node -e '
    const fs = require("fs");
    const data = JSON.parse(fs.readFileSync(0, "utf-8"));
    if (!data.system_info || data.system_info.status !== "not_found") {
      console.error("Expected not_found status, got:", data.system_info);
      process.exit(1);
    }
  '

echo "[3/3] Checking tilde expansion helper in lib/index.js..."
node -e '
  const os = require("os");
  const path = require("path");
  const fs = require("fs");
  const src = fs.readFileSync("lib/index.js", "utf-8");
  if (!src.includes("expandUserPath")) {
    console.error("expandUserPath helper missing in lib/index.js");
    process.exit(1);
  }
'

echo "All smoke tests passed."
