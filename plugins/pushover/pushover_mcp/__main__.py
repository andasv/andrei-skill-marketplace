"""Entry point for running the Pushover MCP server."""

from .server import mcp


def main():
    mcp.run()


if __name__ == "__main__":
    main()
