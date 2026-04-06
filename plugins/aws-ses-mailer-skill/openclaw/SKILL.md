---
name: aws-ses-mailer
description: Send emails via AWS SES using the AWS CLI. Supports plain text, HTML, CC/BCC, reply-to, display name, file attachments, and dry-run mode. Use when the user asks to send an email, compose a message, or mail something to someone.
metadata:
  openclaw:
    emoji: "📧"
    requires:
      bins: ["aws", "python3"]
    install: []
    env:
      SES_FROM_ADDRESS:
        required: true
        description: "Verified SES sender email address"
      SES_AWS_REGION:
        required: true
        description: "AWS region where SES is configured (e.g. eu-west-1)"
      AWS_PROFILE:
        required: false
        description: "AWS CLI profile name. If not set, falls back to IAM instance role credentials."
    credentials:
      - type: aws
        description: "AWS credentials with SES permissions. Provided via IAM instance role or AWS_PROFILE."
        permissions:
          - "ses:SendEmail"
          - "ses:SendRawEmail"
          - "ses:GetIdentityVerificationAttributes"
---

# AWS SES Mailer

Send emails via Amazon Simple Email Service (SES) using the AWS CLI. Supports plain text, HTML body, CC/BCC, reply-to headers, sender display name, and file attachments.

## When to Use

Use this skill when the user asks to:
- Send an email or message to someone
- Compose and deliver an email
- Mail a file or document to an address
- Test email delivery
- Check if an email identity is verified in SES

## Prerequisites

- **AWS CLI** installed and available in `$PATH`
- **Python 3** installed and available in `$PATH`
- **AWS SES** configured with a verified sender identity (email or domain)
- **AWS credentials** available via IAM instance role or `AWS_PROFILE` environment variable

## Configuration

Add to `~/.openclaw/openclaw.json` under `skills.entries`:

```json
{
  "skills": {
    "entries": {
      "aws-ses-mailer": {
        "env": {
          "SES_FROM_ADDRESS": "sender@example.com",
          "SES_AWS_REGION": "eu-west-1",
          "AWS_PROFILE": "my-profile"
        }
      }
    }
  }
}
```

| Variable | Required | Description |
|----------|----------|-------------|
| `SES_FROM_ADDRESS` | Yes | Verified SES sender email address |
| `SES_AWS_REGION` | Yes | AWS region where SES is configured |
| `AWS_PROFILE` | No | AWS CLI profile name (if not using IAM role) |

## Usage

### Send a plain text email

```bash
send_ses_email.sh --to "recipient@example.com" --subject "Hello" --body "This is a test email."
```

### Send an HTML email

```bash
send_ses_email.sh --to "recipient@example.com" --subject "Newsletter" --html "<h1>Hello</h1><p>This is HTML content.</p>"
```

### Send with both text and HTML

```bash
send_ses_email.sh --to "recipient@example.com" --subject "Dual format" --body "Plain text fallback" --html "<h1>Rich content</h1>"
```

### Send with CC, BCC, and display name

```bash
send_ses_email.sh \
  --to "alice@example.com,bob@example.com" \
  --cc "manager@example.com" \
  --bcc "archive@example.com" \
  --subject "Weekly Update" \
  --body "Here is the weekly update." \
  --from-name "Weekly Bot" \
  --reply-to "noreply@example.com"
```

### Send with file attachment

```bash
send_ses_raw.py \
  --to "recipient@example.com" \
  --subject "Report attached" \
  --body "See attached." \
  --attach-file "/path/to/report.pdf"
```

### Send with inline base64 attachment

```bash
send_ses_raw.py \
  --to "recipient@example.com" \
  --subject "Report attached" \
  --body "See attached." \
  --attach "report.pdf:application/pdf:$(base64 < report.pdf)"
```

### Send with multiple attachments

```bash
send_ses_raw.py \
  --to "recipient@example.com" \
  --subject "Documents" \
  --html "<p>Please review the attached documents.</p>" \
  --attach-file "/tmp/report.pdf" \
  --attach-file "/tmp/data.csv" \
  --from-name "Document Service"
```

### Dry run (preview without sending)

```bash
send_ses_email.sh --to "test@example.com" --subject "Test" --body "Testing" --dry-run
```

### Check if a sender identity is verified

```bash
check_ses_identity.sh --email "sender@example.com"
```

## Script Reference

### send_ses_email.sh

| Option | Required | Description |
|--------|----------|-------------|
| `--to <address>` | Yes | Recipient email (comma-separated for multiple) |
| `--subject <subject>` | Yes | Email subject |
| `--body <text>` | * | Plain text body |
| `--html <html>` | * | HTML body |
| `--cc <address>` | No | CC recipients (comma-separated) |
| `--bcc <address>` | No | BCC recipients (comma-separated) |
| `--reply-to <address>` | No | Reply-To address |
| `--from-name <name>` | No | Display name for sender |
| `--dry-run` | No | Print payload without sending |

\* At least one of `--body` or `--html` is required.

### send_ses_raw.py

All options from `send_ses_email.sh` plus:

| Option | Required | Description |
|--------|----------|-------------|
| `--attach-file <path>` | No | Attach a local file (auto-detects MIME type, repeatable) |
| `--attach <spec>` | No | Inline attachment as `filename:mimetype:base64data` (repeatable) |

### check_ses_identity.sh

| Option | Required | Description |
|--------|----------|-------------|
| `--email <address>` | Yes | Email address to check |

## Important Notes

- The `SES_FROM_ADDRESS` is injected via environment variable. Do NOT read `openclaw.json` directly.
- If `AWS_PROFILE` is set, it will be used. Otherwise, the script falls back to the instance IAM role.
- SES must be out of sandbox mode to send to unverified recipients, or both sender and recipient must be verified.
- Attachments via `--attach-file` auto-detect MIME type from file extension.
- Inline attachments (`--attach`) must use base64-encoded content without line breaks.
- Use `--dry-run` to inspect the email payload before sending.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Email address is not verified" | Verify the From address in SES console or run `check_ses_identity.sh` |
| "AccessDenied" | Ensure IAM role/profile has `ses:SendEmail` and `ses:SendRawEmail` permissions |
| "MessageRejected" | SES may be in sandbox mode — request production access |
| Attachment not received | For inline: ensure base64 has no line breaks (`base64 -w0`). For file: check path exists |
