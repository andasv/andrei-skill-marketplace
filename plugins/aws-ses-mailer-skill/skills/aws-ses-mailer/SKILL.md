---
name: aws-ses-mailer
description: Send emails via AWS SES using the AWS API MCP Server. Supports plain text, HTML, CC/BCC, reply-to, display name, file attachments, and dry-run mode. Use when the user asks to send an email, compose a message, or mail something to someone.
---

# AWS SES Mailer

Send emails via Amazon Simple Email Service (SES) using the AWS API MCP Server. Supports plain text, HTML body, CC/BCC, reply-to headers, sender display name, and file attachments.

## MCP Dependencies

This skill requires the following MCP server to be configured:

| MCP Server | Purpose | Required Tools |
|------------|---------|----------------|
| **AWS API** (`awslabs.aws-api-mcp-server`) | Execute AWS CLI commands for SES | `call_aws` |

The AWS API MCP server handles authentication via your configured AWS profile. No API keys need to be stored in the skill itself.

**Required IAM permissions:** `ses:SendEmail`, `ses:SendRawEmail`, `ses:GetIdentityVerificationAttributes`

## When to Use

Use this skill when the user asks to:
- Send an email or message to someone
- Compose and deliver an email
- Mail a file or document to an address
- Test email delivery (dry-run)
- Check if an email identity is verified in SES

## Configuration

The following must be configured in the AWS API MCP server environment or your AWS profile:

| Setting | Description |
|---------|-------------|
| AWS region | The region where SES is configured (e.g. `eu-west-1`) — set via `AWS_REGION` in MCP server config |
| AWS credentials | IAM user/role with SES permissions — set via `AWS_API_MCP_PROFILE_NAME` or default AWS credential chain |
| Verified sender | The From address must be verified in SES |

## Sending Emails

### 1. Plain Text or HTML Email

Use `call_aws` to run:

```
aws ses send-email \
  --from "sender@example.com" \
  --destination "ToAddresses=recipient@example.com" \
  --message "Subject={Data=Hello},Body={Text={Data=This is a test email.}}" \
  --region eu-west-1
```

**Common options:**
- `--from` — Verified SES sender email **(required)**
- `--destination` — Recipients: `ToAddresses=`, `CcAddresses=`, `BccAddresses=` (comma-separated within each)
- `--message` — Subject and Body. Use `Body={Text={Data=...}}` for plain text, `Body={Html={Data=...}}` for HTML, or both
- `--reply-to-addresses` — Reply-To address
- `--region` — AWS region where SES is configured

**With display name:**
```
aws ses send-email \
  --from "Acme Corp <sender@example.com>" \
  --destination "ToAddresses=alice@example.com,bob@example.com,CcAddresses=manager@example.com" \
  --message "Subject={Data=Weekly Update},Body={Text={Data=Here is the weekly update.}}" \
  --reply-to-addresses "noreply@example.com" \
  --region eu-west-1
```

### 2. Email with Attachments

For attachments, use `send-raw-email` with a MIME message. Build the raw message as a base64-encoded MIME structure:

```
aws ses send-raw-email \
  --raw-message "Data=$(base64 < mime_message.txt)" \
  --region eu-west-1
```

To construct the MIME message, create a file with proper MIME boundaries containing the text body and base64-encoded attachment. Alternatively, use Python's `email` module to build the MIME message programmatically via a Bash tool call.

### 3. Check SES Identity Verification

```
aws ses get-identity-verification-attributes \
  --identities "sender@example.com" \
  --region eu-west-1
```

### 4. Dry Run

To preview without sending, construct the full CLI command and present it to the user for review instead of executing it. Prefix the output with "DRY RUN — the following command would be executed:".

## Examples

### Send with CC, BCC, and display name
```
aws ses send-email \
  --from "Weekly Bot <sender@example.com>" \
  --destination "ToAddresses=alice@example.com,bob@example.com,CcAddresses=manager@example.com,BccAddresses=archive@example.com" \
  --message "Subject={Data=Weekly Update},Body={Text={Data=Here is the weekly update.}}" \
  --reply-to-addresses "noreply@example.com" \
  --region eu-west-1
```

### Send HTML email
```
aws ses send-email \
  --from "sender@example.com" \
  --destination "ToAddresses=recipient@example.com" \
  --message "Subject={Data=Invoice},Body={Html={Data=<h1>Invoice</h1><p>Please find details below.</p>}}" \
  --region eu-west-1
```

## Important Notes

- The sender address must be a verified identity in your SES account.
- SES must be out of sandbox mode to send to unverified recipients, or both sender and recipient must be verified.
- All commands are executed via `call_aws` from the AWS API MCP server — no local scripts required.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Email address is not verified" | Verify the From address in SES console or run `get-identity-verification-attributes` |
| "AccessDenied" | Ensure IAM role/profile has `ses:SendEmail` and `ses:SendRawEmail` permissions |
| "MessageRejected" | SES may be in sandbox mode — request production access |
