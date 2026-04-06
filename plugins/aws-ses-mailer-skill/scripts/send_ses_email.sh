#!/usr/bin/env bash
set -euo pipefail

# Send email via AWS SES CLI (plain text and/or HTML)
# Environment: SES_FROM_ADDRESS, SES_AWS_REGION, AWS_PROFILE (optional)

usage() {
  cat <<'USAGE'
Usage: send_ses_email.sh --to <address> --subject <subject> [options]

Required:
  --to <address>        Recipient email (comma-separated for multiple)
  --subject <subject>   Email subject line

Content (at least one required):
  --body <text>         Plain text body
  --html <html>         HTML body

Optional:
  --cc <address>        CC recipients (comma-separated)
  --bcc <address>       BCC recipients (comma-separated)
  --reply-to <address>  Reply-To address
  --from-name <name>    Display name for sender (e.g. "Acme Corp")
  --dry-run             Print the request payload without sending
USAGE
  exit 1
}

TO=""
SUBJECT=""
BODY=""
HTML=""
CC=""
BCC=""
REPLY_TO=""
FROM_NAME=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --to) TO="$2"; shift 2 ;;
    --subject) SUBJECT="$2"; shift 2 ;;
    --body) BODY="$2"; shift 2 ;;
    --html) HTML="$2"; shift 2 ;;
    --cc) CC="$2"; shift 2 ;;
    --bcc) BCC="$2"; shift 2 ;;
    --reply-to) REPLY_TO="$2"; shift 2 ;;
    --from-name) FROM_NAME="$2"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    *) echo "Unknown option: $1"; usage ;;
  esac
done

if [[ -z "$TO" || -z "$SUBJECT" ]]; then
  echo "Error: --to and --subject are required."
  usage
fi

if [[ -z "$BODY" && -z "$HTML" ]]; then
  echo "Error: at least one of --body or --html is required."
  usage
fi

if [[ -z "${SES_FROM_ADDRESS:-}" ]]; then
  echo "Error: SES_FROM_ADDRESS environment variable is not set."
  exit 1
fi

if [[ -z "${SES_AWS_REGION:-}" ]]; then
  echo "Error: SES_AWS_REGION environment variable is not set."
  exit 1
fi

AWS_ARGS=(--region "$SES_AWS_REGION")
if [[ -n "${AWS_PROFILE:-}" ]]; then
  AWS_ARGS+=(--profile "$AWS_PROFILE")
fi

# Build sender address
SENDER="$SES_FROM_ADDRESS"
if [[ -n "$FROM_NAME" ]]; then
  SENDER="$FROM_NAME <$SES_FROM_ADDRESS>"
fi

# Helper: convert comma-separated emails to JSON array
emails_to_json_array() {
  local input="$1"
  python3 -c "
import json, sys
emails = [e.strip() for e in sys.argv[1].split(',') if e.strip()]
print(json.dumps(emails))
" "$input"
}

# Build destination JSON
TO_JSON=$(emails_to_json_array "$TO")
DEST="{\"ToAddresses\":$TO_JSON"
if [[ -n "$CC" ]]; then
  CC_JSON=$(emails_to_json_array "$CC")
  DEST+=",\"CcAddresses\":$CC_JSON"
fi
if [[ -n "$BCC" ]]; then
  BCC_JSON=$(emails_to_json_array "$BCC")
  DEST+=",\"BccAddresses\":$BCC_JSON"
fi
DEST+="}"

# Build the message JSON
json_encode() {
  printf '%s' "$1" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))'
}

MESSAGE="{\"Subject\":{\"Data\":$(json_encode "$SUBJECT")}"

BODY_PART="{"
if [[ -n "$BODY" ]]; then
  BODY_PART+="\"Text\":{\"Data\":$(json_encode "$BODY")}"
fi
if [[ -n "$HTML" ]]; then
  if [[ -n "$BODY" ]]; then
    BODY_PART+=","
  fi
  BODY_PART+="\"Html\":{\"Data\":$(json_encode "$HTML")}"
fi
BODY_PART+="}"

MESSAGE+=",\"Body\":$BODY_PART}"

# Build optional args
OPTIONAL_ARGS=()
if [[ -n "$REPLY_TO" ]]; then
  REPLY_TO_JSON=$(emails_to_json_array "$REPLY_TO")
  OPTIONAL_ARGS+=(--reply-to-addresses "$REPLY_TO_JSON")
fi

if [[ "$DRY_RUN" == true ]]; then
  echo "=== DRY RUN ==="
  echo "From: $SENDER"
  echo "Destination: $DEST"
  echo "Message: $MESSAGE"
  if [[ -n "$REPLY_TO" ]]; then
    echo "Reply-To: $REPLY_TO"
  fi
  echo "Region: $SES_AWS_REGION"
  echo "=== No email was sent ==="
  exit 0
fi

RESULT=$(aws ses send-email \
  "${AWS_ARGS[@]}" \
  --from "$SENDER" \
  --destination "$DEST" \
  --message "$MESSAGE" \
  ${OPTIONAL_ARGS[@]+"${OPTIONAL_ARGS[@]}"} \
  --output json 2>&1)

if [[ $? -eq 0 ]]; then
  MESSAGE_ID=$(echo "$RESULT" | python3 -c 'import sys,json; print(json.load(sys.stdin)["MessageId"])' 2>/dev/null || echo "unknown")
  echo "Email sent successfully."
  echo "MessageId: $MESSAGE_ID"
else
  echo "Failed to send email."
  echo "$RESULT"
  exit 1
fi
