#!/usr/bin/env bash
set -euo pipefail

# Check if an email identity is verified in AWS SES

usage() {
  echo "Usage: check_ses_identity.sh --email <address>"
  exit 1
}

EMAIL=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --email) EMAIL="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; usage ;;
  esac
done

if [[ -z "$EMAIL" ]]; then
  echo "Error: --email is required."
  usage
fi

if [[ -z "${SES_AWS_REGION:-}" ]]; then
  echo "Error: SES_AWS_REGION environment variable is not set."
  exit 1
fi

AWS_ARGS=(--region "$SES_AWS_REGION")
if [[ -n "${AWS_PROFILE:-}" ]]; then
  AWS_ARGS+=(--profile "$AWS_PROFILE")
fi

RESULT=$(aws ses get-identity-verification-attributes \
  "${AWS_ARGS[@]}" \
  --identities "$EMAIL" \
  --output json 2>&1)

if [[ $? -ne 0 ]]; then
  echo "Failed to check identity."
  echo "$RESULT"
  exit 1
fi

STATUS=$(echo "$RESULT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
attrs = data.get('VerificationAttributes', {}).get('$EMAIL', {})
status = attrs.get('VerificationStatus', 'NotFound')
print(status)
" 2>/dev/null || echo "Error")

case "$STATUS" in
  Success)
    echo "Identity '$EMAIL' is verified in SES (region: $SES_AWS_REGION)."
    ;;
  Pending)
    echo "Identity '$EMAIL' is pending verification. Check inbox for verification email."
    ;;
  NotFound)
    echo "Identity '$EMAIL' is not registered in SES (region: $SES_AWS_REGION)."
    echo "To verify, run: aws ses verify-email-identity --email-address $EMAIL --region $SES_AWS_REGION"
    ;;
  *)
    echo "Identity '$EMAIL' status: $STATUS"
    ;;
esac
