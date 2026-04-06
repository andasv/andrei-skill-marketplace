# aws-ses-mailer

Send emails via Amazon SES from AI coding agents. Works with **Claude Cowork** and any agentic assistant that supports MCP.

Uses the official [AWS API MCP Server](https://github.com/awslabs/mcp) (`awslabs.aws-api-mcp-server`) to execute AWS CLI commands — no custom scripts or local credentials management needed.

## Features

- Plain text and HTML email bodies (or both)
- Multiple recipients with TO, CC, and BCC
- Reply-To header support
- Sender display name (e.g. "Acme Corp \<sender@example.com\>")
- File attachments via raw MIME messages
- Dry-run mode for testing without sending
- SES identity verification check

## Prerequisites

- [AWS API MCP Server](https://github.com/awslabs/mcp) configured with SES permissions
- An AWS account with SES configured and a verified sender identity

### MCP Server Setup

Add to your MCP config (e.g. `.mcp.json`):

```json
{
  "mcpServers": {
    "awslabs.aws-api-mcp-server": {
      "command": "uvx",
      "args": ["awslabs.aws-api-mcp-server@latest"],
      "env": {
        "AWS_REGION": "eu-west-1",
        "AWS_API_MCP_PROFILE_NAME": "ses-mailer"
      }
    }
  }
}
```

### Required IAM Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ses:SendEmail",
        "ses:SendRawEmail",
        "ses:GetIdentityVerificationAttributes"
      ],
      "Resource": "*"
    }
  ]
}
```

## Usage

Once installed, the skill is auto-discovered. Ask Claude to send an email:

> "Send an email to alice@example.com with subject 'Hello' and body 'Hi there!'"

> "Email the report to bob@example.com with CC to manager@example.com"

> "Do a dry run of sending a newsletter to the team"

## License

This project is licensed under the [MIT License](LICENSE).

**Important:** Please read the [DISCLAIMER](DISCLAIMER) file for additional terms regarding liability, AWS costs, email compliance, and data handling.
