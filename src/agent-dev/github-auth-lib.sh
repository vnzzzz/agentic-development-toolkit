#!/usr/bin/env bash
set -Eeuo pipefail

AGENT_GITHUB_API_URL=${AGENT_GITHUB_API_URL:-https://api.github.com}
AGENT_GITHUB_API_VERSION=${AGENT_GITHUB_API_VERSION:-2026-03-10}
AGENT_GITHUB_REAL_GIT=${AGENT_GITHUB_REAL_GIT:-/usr/local/lib/agent-dev/real-bin/git}

agent_github_die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

agent_github_validate_profile_name() {
  local profile=${1:-}
  [[ $profile =~ ^[A-Za-z0-9._-]+$ ]] || agent_github_die "invalid GitHub App profile name: ${profile:-<empty>}"
}

agent_github_profile_dir() {
  local profile=$1
  agent_github_validate_profile_name "$profile"
  printf '%s/.config/agent-dev/github-apps/%s\n' "$HOME" "$profile"
}

agent_github_config_path() {
  local profile=$1
  printf '%s/config.json\n' "$(agent_github_profile_dir "$profile")"
}

agent_github_key_path() {
  local profile=$1
  printf '%s/private-key.pem\n' "$(agent_github_profile_dir "$profile")"
}

agent_github_load_profile() {
  local profile=$1
  local config_path
  config_path=$(agent_github_config_path "$profile")

  [[ -f $config_path ]] || agent_github_die "GitHub App profile is not configured: $profile (expected $config_path)"
  jq -e . "$config_path" >/dev/null 2>&1 || agent_github_die "invalid JSON config: $config_path"

  AGENT_GITHUB_APP_ID=$(jq -er '.app_id | tostring | select(test("^[0-9]+$"))' "$config_path") || \
    agent_github_die "config app_id must be numeric: $config_path"
  AGENT_GITHUB_KEY_PATH=$(agent_github_key_path "$profile")
}

agent_github_validate_private_key() {
  local key_path=$1
  local mode owner_uid

  [[ -f $key_path ]] || agent_github_die "GitHub App private key is missing: $key_path"
  mode=$(stat -c '%a' "$key_path")
  owner_uid=$(stat -c '%u' "$key_path")
  [[ $mode == 600 ]] || agent_github_die "private key must have mode 0600: $key_path (current: $mode)"
  [[ $owner_uid == "$(id -u)" ]] || agent_github_die "private key must be owned by the current user: $key_path"
  openssl pkey -in "$key_path" -check -noout >/dev/null 2>&1 || agent_github_die "private key is not a readable unencrypted PEM private key: $key_path"
}

agent_github_current_repo() {
  local remote path owner repo

  [[ -x $AGENT_GITHUB_REAL_GIT ]] || agent_github_die "real git binary is unavailable: $AGENT_GITHUB_REAL_GIT"
  remote=$($AGENT_GITHUB_REAL_GIT remote get-url origin 2>/dev/null) || agent_github_die "cannot resolve git remote 'origin'"

  case "$remote" in
    https://github.com/*)
      path=${remote#https://github.com/}
      ;;
    http://github.com/*)
      path=${remote#http://github.com/}
      ;;
    git@github.com:*)
      path=${remote#git@github.com:}
      ;;
    ssh://git@github.com/*)
      path=${remote#ssh://git@github.com/}
      ;;
    *)
      agent_github_die "origin must be a github.com repository URL: $remote"
      ;;
  esac

  path=${path%.git}
  owner=${path%%/*}
  repo=${path#*/}
  [[ -n $owner && -n $repo && $repo != "$path" && $repo != */* ]] || agent_github_die "cannot parse owner/repository from origin: $remote"

  AGENT_GITHUB_REPO_OWNER=$owner
  AGENT_GITHUB_REPO_NAME=$repo
  AGENT_GITHUB_REPO_FULL_NAME=$owner/$repo
}

agent_github_base64url() {
  openssl base64 -A | tr '+/' '-_' | tr -d '='
}

agent_github_jwt() {
  local app_id=$1 key_path=$2
  local now header payload encoded_header encoded_payload unsigned signature

  now=$(date +%s)
  header=$(jq -cn '{alg:"RS256",typ:"JWT"}')
  payload=$(jq -cn \
    --argjson iat "$((now - 60))" \
    --argjson exp "$((now + 540))" \
    --argjson iss "$app_id" \
    '{iat:$iat,exp:$exp,iss:$iss}')
  encoded_header=$(printf '%s' "$header" | agent_github_base64url)
  encoded_payload=$(printf '%s' "$payload" | agent_github_base64url)
  unsigned=$encoded_header.$encoded_payload
  signature=$(printf '%s' "$unsigned" | openssl dgst -sha256 -sign "$key_path" | agent_github_base64url)
  printf '%s.%s\n' "$unsigned" "$signature"
}

agent_github_installation_id() {
  local jwt=$1 owner=$2 repo=$3
  local response installation_id

  response=$(curl --fail-with-body --silent --show-error \
    -H 'Accept: application/vnd.github+json' \
    -H "Authorization: Bearer $jwt" \
    -H "X-GitHub-Api-Version: $AGENT_GITHUB_API_VERSION" \
    "$AGENT_GITHUB_API_URL/repos/$owner/$repo/installation") || \
    agent_github_die "GitHub App is not installed for $owner/$repo or the App JWT was rejected"
  installation_id=$(jq -er '.id' <<<"$response") || agent_github_die "GitHub installation response did not contain an id"
  printf '%s\n' "$installation_id"
}

agent_github_mint_token() {
  local profile=$1
  local jwt installation_id request response token

  agent_github_load_profile "$profile"
  agent_github_validate_private_key "$AGENT_GITHUB_KEY_PATH"
  agent_github_current_repo

  jwt=$(agent_github_jwt "$AGENT_GITHUB_APP_ID" "$AGENT_GITHUB_KEY_PATH")
  installation_id=$(agent_github_installation_id "$jwt" "$AGENT_GITHUB_REPO_OWNER" "$AGENT_GITHUB_REPO_NAME")
  request=$(jq -cn --arg repo "$AGENT_GITHUB_REPO_NAME" '{repositories:[$repo]}')
  response=$(curl --fail-with-body --silent --show-error \
    -X POST \
    -H 'Accept: application/vnd.github+json' \
    -H "Authorization: Bearer $jwt" \
    -H "X-GitHub-Api-Version: $AGENT_GITHUB_API_VERSION" \
    -H 'Content-Type: application/json' \
    --data "$request" \
    "$AGENT_GITHUB_API_URL/app/installations/$installation_id/access_tokens") || \
    agent_github_die "failed to mint a repository-scoped GitHub App installation token for $AGENT_GITHUB_REPO_FULL_NAME"
  token=$(jq -er '.token | strings | select(length > 0)' <<<"$response") || agent_github_die "GitHub token response did not contain a token"
  printf '%s\n' "$token"
}

agent_github_revoke_token() {
  local token=$1
  curl --fail --silent --show-error \
    -X DELETE \
    -H 'Accept: application/vnd.github+json' \
    -H "Authorization: Bearer $token" \
    -H "X-GitHub-Api-Version: $AGENT_GITHUB_API_VERSION" \
    "$AGENT_GITHUB_API_URL/installation/token" >/dev/null
}

agent_github_bot_identity() {
  local profile=$1 jwt app_response app_id app_slug user_response bot_id bot_login expected_login

  agent_github_load_profile "$profile"
  agent_github_validate_private_key "$AGENT_GITHUB_KEY_PATH"

  jwt=$(agent_github_jwt "$AGENT_GITHUB_APP_ID" "$AGENT_GITHUB_KEY_PATH")
  app_response=$(curl --fail-with-body --silent --show-error \
    -H 'Accept: application/vnd.github+json' \
    -H "Authorization: Bearer $jwt" \
    -H "X-GitHub-Api-Version: $AGENT_GITHUB_API_VERSION" \
    "$AGENT_GITHUB_API_URL/app") || \
    agent_github_die "cannot resolve metadata for authenticated GitHub App ID $AGENT_GITHUB_APP_ID"
  app_id=$(jq -er '.id | tostring | select(test("^[0-9]+$"))' <<<"$app_response") || \
    agent_github_die 'authenticated App response did not contain a numeric id'
  [[ $app_id == "$AGENT_GITHUB_APP_ID" ]] || \
    agent_github_die "authenticated App ID mismatch: configured $AGENT_GITHUB_APP_ID, returned $app_id"
  app_slug=$(jq -er '.slug | strings | select(test("^[A-Za-z0-9-]+$"))' <<<"$app_response") || \
    agent_github_die 'authenticated App response did not contain a valid slug'

  user_response=$(curl --fail-with-body --silent --show-error \
    -H 'Accept: application/vnd.github+json' \
    -H "X-GitHub-Api-Version: $AGENT_GITHUB_API_VERSION" \
    "$AGENT_GITHUB_API_URL/users/${app_slug}%5Bbot%5D") || \
    agent_github_die "cannot resolve GitHub App bot user for authenticated App slug: $app_slug"
  bot_id=$(jq -er '.id' <<<"$user_response") || agent_github_die "bot user response did not contain an id"
  bot_login=$(jq -er '.login' <<<"$user_response") || agent_github_die "bot user response did not contain a login"
  expected_login="${app_slug}[bot]"
  [[ $bot_login == "$expected_login" ]] || \
    agent_github_die "bot login mismatch for authenticated App: expected $expected_login, returned $bot_login"

  export AGENT_GITHUB_APP_SLUG=$app_slug
  export AGENT_GITHUB_BOT_ID=$bot_id
  export AGENT_GITHUB_BOT_LOGIN=$bot_login
  export AGENT_GITHUB_BOT_EMAIL=${bot_id}+${bot_login}@users.noreply.github.com
}
