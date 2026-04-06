# Contributing to aws-ses-mailer-skill

Thank you for your interest in contributing! This guide will help you get started.

## Reporting Bugs

1. Check [existing issues](https://github.com/andasv/aws-ses-mailer-skill/issues) to avoid duplicates
2. Use the **Bug Report** issue template
3. Include:
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment (OS, AWS CLI version, Python version)
   - Error messages (redact any sensitive information)

## Suggesting Features

1. Check [existing issues](https://github.com/andasv/aws-ses-mailer-skill/issues) for similar requests
2. Use the **Feature Request** issue template
3. Describe the use case and why it would benefit the community

## Pull Requests

### Before You Start

- Open an issue first to discuss significant changes
- For small fixes (typos, docs), a PR without an issue is fine

### Development Setup

```bash
git clone https://github.com/andasv/aws-ses-mailer-skill.git
cd aws-ses-mailer-skill
```

### Code Style

- **Bash scripts**: Must pass [ShellCheck](https://www.shellcheck.net/) without warnings
- **Python scripts**: Follow [PEP 8](https://peps.python.org/pep-0008/). Must pass `python3 -m py_compile`
- Keep scripts POSIX-compatible where possible
- Use `set -euo pipefail` in all bash scripts

### Testing

Before submitting:

1. Run ShellCheck on shell scripts:
   ```bash
   shellcheck scripts/*.sh
   ```

2. Verify Python syntax:
   ```bash
   python3 -m py_compile scripts/send_ses_raw.py
   ```

3. Test with `--dry-run` to verify output format:
   ```bash
   SES_FROM_ADDRESS="test@example.com" SES_AWS_REGION="us-east-1" \
     scripts/send_ses_email.sh --to "test@test.com" --subject "Test" --body "Test" --dry-run
   ```

### Submitting

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Ensure all checks pass
5. Commit with a clear message
6. Push and open a Pull Request using the PR template

### What We Look For

- Changes work with all three skill flavors (Claude Cowork, OpenClaw, generic)
- Scripts handle errors gracefully
- New flags are documented in both SKILL.md files
- No hardcoded credentials or sensitive data
- Backward compatibility with existing usage

## Code of Conduct

Be respectful and constructive. We're all here to build something useful together.
