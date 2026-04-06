#!/usr/bin/env python3
"""Send raw email via AWS SES CLI with attachment support (inline base64 or local file)."""

import argparse
import base64
import email.encoders
import email.mime.base
import email.mime.multipart
import email.mime.text
import json
import mimetypes
import os
import subprocess
import sys


def parse_args():
    parser = argparse.ArgumentParser(description="Send email with attachments via AWS SES")
    parser.add_argument("--to", required=True, help="Recipient email (comma-separated for multiple)")
    parser.add_argument("--subject", required=True, help="Email subject")
    parser.add_argument("--body", default="", help="Plain text body")
    parser.add_argument("--html", default="", help="HTML body")
    parser.add_argument("--cc", default="", help="CC recipients (comma-separated)")
    parser.add_argument("--bcc", default="", help="BCC recipients (comma-separated)")
    parser.add_argument("--reply-to", default="", help="Reply-To address")
    parser.add_argument("--from-name", default="", help="Display name for sender")
    parser.add_argument(
        "--attach",
        action="append",
        default=[],
        help="Inline attachment as filename:mimetype:base64data (can be repeated)",
    )
    parser.add_argument(
        "--attach-file",
        action="append",
        default=[],
        help="Attach a local file by path (can be repeated). MIME type is auto-detected.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print the message without sending")
    return parser.parse_args()


def parse_emails(value):
    """Split comma-separated email string into a list."""
    if not value:
        return []
    return [e.strip() for e in value.split(",") if e.strip()]


def build_message(from_addr, to_addrs, subject, body, html, cc_addrs, bcc_addrs, reply_to, attachments):
    msg = email.mime.multipart.MIMEMultipart("mixed")
    msg["From"] = from_addr
    msg["To"] = ", ".join(to_addrs)
    msg["Subject"] = subject

    if cc_addrs:
        msg["Cc"] = ", ".join(cc_addrs)
    if reply_to:
        msg["Reply-To"] = reply_to

    # Body part (multipart/alternative if both text and html)
    if body and html:
        alt = email.mime.multipart.MIMEMultipart("alternative")
        alt.attach(email.mime.text.MIMEText(body, "plain", "utf-8"))
        alt.attach(email.mime.text.MIMEText(html, "html", "utf-8"))
        msg.attach(alt)
    elif html:
        msg.attach(email.mime.text.MIMEText(html, "html", "utf-8"))
    elif body:
        msg.attach(email.mime.text.MIMEText(body, "plain", "utf-8"))

    # Attachments
    for att in attachments:
        maintype, subtype = att["mimetype"].split("/", 1) if "/" in att["mimetype"] else ("application", "octet-stream")
        part = email.mime.base.MIMEBase(maintype, subtype)
        part.set_payload(att["data"])
        email.encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment", filename=att["filename"])
        msg.attach(part)

    return msg.as_string()


def load_inline_attachment(spec):
    """Parse filename:mimetype:base64data format."""
    parts = spec.split(":", 2)
    if len(parts) != 3:
        print(f"Error: attachment format must be filename:mimetype:base64data, got: {spec[:50]}...")
        sys.exit(1)
    filename, mimetype, b64data = parts
    try:
        raw_data = base64.b64decode(b64data)
    except Exception as e:
        print(f"Error: failed to decode base64 for {filename}: {e}")
        sys.exit(1)
    return {"filename": filename, "mimetype": mimetype, "data": raw_data}


def load_file_attachment(filepath):
    """Read a local file and auto-detect MIME type."""
    if not os.path.isfile(filepath):
        print(f"Error: file not found: {filepath}")
        sys.exit(1)
    mimetype, _ = mimetypes.guess_type(filepath)
    if not mimetype:
        mimetype = "application/octet-stream"
    filename = os.path.basename(filepath)
    with open(filepath, "rb") as f:
        raw_data = f.read()
    return {"filename": filename, "mimetype": mimetype, "data": raw_data}


def main():
    args = parse_args()

    from_addr = os.environ.get("SES_FROM_ADDRESS")
    if not from_addr:
        print("Error: SES_FROM_ADDRESS environment variable is not set.")
        sys.exit(1)

    region = os.environ.get("SES_AWS_REGION")
    if not region:
        print("Error: SES_AWS_REGION environment variable is not set.")
        sys.exit(1)

    # Build sender with display name
    sender = from_addr
    if args.from_name:
        sender = f"{args.from_name} <{from_addr}>"

    to_addrs = parse_emails(args.to)
    cc_addrs = parse_emails(args.cc)
    bcc_addrs = parse_emails(args.bcc)

    # Collect all attachments
    attachments = []
    for spec in args.attach:
        attachments.append(load_inline_attachment(spec))
    for filepath in args.attach_file:
        attachments.append(load_file_attachment(filepath))

    raw_message = build_message(
        sender, to_addrs, args.subject, args.body, args.html,
        cc_addrs, bcc_addrs, args.reply_to, attachments,
    )

    if args.dry_run:
        print("=== DRY RUN ===")
        print(raw_message)
        print("=== No email was sent ===")
        return

    # Encode as base64 for SES raw send
    raw_b64 = base64.b64encode(raw_message.encode("utf-8")).decode("ascii")

    aws_cmd = ["aws", "ses", "send-raw-email", "--region", region]

    profile = os.environ.get("AWS_PROFILE")
    if profile:
        aws_cmd.extend(["--profile", profile])

    aws_cmd.extend(["--source", from_addr])

    # Build destinations list (TO + CC + BCC)
    all_destinations = to_addrs + cc_addrs + bcc_addrs
    aws_cmd.extend(["--destinations"] + all_destinations)
    aws_cmd.extend(["--raw-message", json.dumps({"Data": raw_b64})])

    try:
        result = subprocess.run(aws_cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        message_id = data.get("MessageId", "unknown")
        print("Email sent successfully.")
        print(f"MessageId: {message_id}")
    except subprocess.CalledProcessError as e:
        print("Failed to send email.")
        print(e.stderr or e.stdout)
        sys.exit(1)


if __name__ == "__main__":
    main()
