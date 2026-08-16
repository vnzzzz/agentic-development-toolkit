#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

mkdir -p "${TMP_DIR}/bin"
cat >"${TMP_DIR}/feature.json" <<'JSON'
{
  "version": "1.2.3"
}
JSON

cat >"${TMP_DIR}/bin/docker" <<'SH'
#!/usr/bin/env bash
set -Eeuo pipefail
case "${1:-}" in
  login|logout) exit 0 ;;
  *) exit 2 ;;
esac
SH

cat >"${TMP_DIR}/bin/devcontainer" <<'SH'
#!/usr/bin/env bash
set -Eeuo pipefail
case "${MOCK_DEVCONTAINER_RESULT:-}" in
  exists)
    printf '%s\n' '{"manifest":{}}'
    exit 0
    ;;
  missing)
    echo 'No manifest found! If this manifest requires authentication, please login.'
    exit 1
    ;;
  error)
    echo 'registry lookup failed'
    exit 1
    ;;
  *)
    exit 2
    ;;
esac
SH
chmod +x "${TMP_DIR}/bin/docker" "${TMP_DIR}/bin/devcontainer"

run_check() {
  env \
    PATH="${TMP_DIR}/bin:${PATH}" \
    GHCR_USERNAME=test-user \
    GHCR_TOKEN=test-token \
    FEATURE_METADATA="${TMP_DIR}/feature.json" \
    FEATURE_REPOSITORY=ghcr.io/example/toolkit/agent-dev \
    MOCK_DEVCONTAINER_RESULT="$1" \
    bash "${ROOT_DIR}/scripts/check-release-version.sh"
}

if run_check exists; then
  echo 'expected an already-published version to fail' >&2
  exit 1
fi

run_check missing

if run_check error; then
  echo 'expected an unexpected registry error to fail closed' >&2
  exit 1
fi

echo 'release version guard tests passed'
