#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_NAME="DRYDefense.app"
SOURCE_APP="${SCRIPT_DIR}/${APP_NAME}"
PRIMARY_TARGET_DIR="/Applications"
FALLBACK_TARGET_DIR="${HOME}/Applications"

if [[ ! -d "${SOURCE_APP}" ]]; then
  echo "Expected ${APP_NAME} in the same folder as this installer."
  exit 1
fi

TARGET_DIR="${PRIMARY_TARGET_DIR}"
if [[ ! -w "${PRIMARY_TARGET_DIR}" ]]; then
  TARGET_DIR="${FALLBACK_TARGET_DIR}"
  mkdir -p "${TARGET_DIR}"
fi

TARGET_APP="${TARGET_DIR}/${APP_NAME}"

echo "Installing DRY Defense to ${TARGET_DIR}..."
rm -rf "${TARGET_APP}"
cp -R "${SOURCE_APP}" "${TARGET_APP}"

# Remove quarantine to avoid the most common Gatekeeper prompt for downloaded zips.
xattr -dr com.apple.quarantine "${TARGET_APP}" 2>/dev/null || true

echo "DRY Defense installed at: ${TARGET_APP}"
echo "If macOS still blocks launch, right-click the app, choose Open, then click Open again."
echo "Press Enter to finish."
read -r