#!/usr/bin/env bash
set -Eeuo pipefail

FEATURE_METADATA="${FEATURE_METADATA:-src/agent-dev/devcontainer-feature.json}"
FEATURE_REPOSITORY="${FEATURE_REPOSITORY:-ghcr.io/vnzzzz/agentic-development-toolkit/agent-dev}"
GHCR_USERNAME="${GHCR_USERNAME:-${GITHUB_ACTOR:-}}"
GHCR_TOKEN="${GHCR_TOKEN:-}"

for command_name in jq docker devcontainer; do
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    echo "error: required command not found: ${command_name}" >&2
    exit 1
  fi
done

if [[ -z "${GHCR_USERNAME}" || -z "${GHCR_TOKEN}" ]]; then
  echo "error: GHCR_USERNAME and GHCR_TOKEN are required" >&2
  exit 1
fi

version="$(jq -er '.version | select(type == "string" and length > 0)' "${FEATURE_METADATA}")"
feature_ref="${FEATURE_REPOSITORY}:${version}"

cleanup() {
  docker logout ghcr.io >/dev/null 2>&1 || true
}
trap cleanup EXIT

printf '%s' "${GHCR_TOKEN}" | docker login ghcr.io --username "${GHCR_USERNAME}" --password-stdin >/dev/null

set +e
lookup_output="$(devcontainer features info manifest "${feature_ref}" 2>&1)"
lookup_status=$?
set -e

if ((lookup_status == 0)); then
  echo "error: Feature version ${version} is already published: ${feature_ref}" >&2
  echo "Bump src/agent-dev/devcontainer-feature.json before releasing again." >&2
  exit 1
fi

if grep -Fq 'No manifest found!' <<<"${lookup_output}"; then
  echo "Feature version ${version} is not published yet: ${feature_ref}"
  exit 0
fi

echo "error: failed to verify whether ${feature_ref} is already published" >&2
printf '%s\n' "${lookup_output}" >&2
exit 1
