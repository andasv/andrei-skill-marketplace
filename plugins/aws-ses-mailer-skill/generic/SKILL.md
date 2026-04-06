---
name: aws-ses-mailer
description: Send emails via AWS SES using the AWS CLI. Supports plain text, HTML, CC/BCC, reply-to, display name, file attachments, and dry-run mode. Use when the user asks to send an email, compose a message, or mail something to someone.
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

## Environment Variables

Set the following environment variables before using the scripts:

| Variable | Required | Description |
|----------|----------|-------------|
| `SES_FROM_ADDRESS` | Yes | Verified SES sender email address |
| `SES_AWS_REGION` | Yes | AWS region where SES is configured (e.g. `eu-west-1`) |
| `AWS_PROFILE` | No | AWS CLI profile name (falls back to IAM role if not set) |

## Available Scripts

All scripts are located in the `../scripts/` directory relative to this SKILL.md.

### 1. Send Plain Text or HTML Email

```bash
send_ses_email.sh --to "recipient@example.com" --subject "Hello" --body "This is a test email."
```

**Options:**
- `--to <address>` — Recipient email (comma-separated for multiple) **(required)**
- `--subject <subject>` — Email subject **(required)**
- `--body <text>` — Plain text body (at least one of --body or --html required)
- `--html <html>` — HTML body
- `--cc <address>` — CC recipients (comma-separated)
- `--bcc <address>` — BCC recipients (comma-separated)
- `--reply-to <address>` — Reply-To address
- `--from-name <name>` — Display name for sender (e.g. "Acme Corp")
- `--dry-run` — Print the request payload without sending

### 2. Send Email with Attachments

```bash
send_ses_raw.py --to "recipient@example.com" --subject "Report attached" --body "See attached." --attach-file "/path/to/report.pdf"
```

**Options:**
- `--to <address>` — Recipient email (comma-separated for multiple) **(required)**
- `--subject <subject>` — Email subject **(required)**
- `--body <text>` — Plain text body
- `--html <html>` — HTML body
- `--cc <address>` — CC recipients (comma-separated)
- `--bcc <address>` — BCC recipients (comma-separated)
- `--reply-to <address>` — Reply-To address
- `--from-name <name>` — Display name for sender
- `--attach-file <path>` — Attach a local file (auto-detects MIME type, can be repeated)
- `--attach <filename:mimetype:base64data>` — Inline base64 attachment (can be repeated)
- `--dry-run` — Print the raw MIME message without sending

### 3. Check SES Identity Verification

```bash
check_ses_identity.sh --email "sender@example.com"
```

## Examples

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

### Send HTML email with file attachment
```bash
send_ses_raw.py \
  --to "recipient@example.com" \
  --subject "Invoice" \
  --html "<h1>Invoice</h1><p>Please find attached.</p>" \
  --attach-file "/tmp/invoice.pdf" \
  --from-name "Billing Department"
```

### Dry run to preview without sending
```bash
send_ses_email.sh --to "test@example.com" --subject "Test" --body "Testing" --dry-run
```

## Important Notes

- The `SES_FROM_ADDRESS` must be a verified identity in your SES account.
- SES must be out of sandbox mode to send to unverified recipients, or both sender and recipient must be verified.
- Attachments via `--attach-file` auto-detect MIME type from file extension.
- Use `--dry-run` to inspect the email payload before sending.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Email address is not verified" | Verify the From address in SES console or run `check_ses_identity.sh` |
| "AccessDenied" | Ensure IAM role/profile has `ses:SendEmail` and `ses:SendRawEmail` permissions |
| "MessageRejected" | SES may be in sandbox mode — request production access |
| Attachment not received | Ensure file exists and is readable; check MIME type detection |
