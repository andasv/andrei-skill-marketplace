"""Eltern-Portal MCP Server — access school data via Model Context Protocol."""

from fastmcp import FastMCP

from .auth import get_base_url, get_session, reset_session
from .parsers.elternbriefe import get_elternbrief as _get_elternbrief
from .parsers.elternbriefe import list_elternbriefe as _list_elternbriefe
from .parsers.schwarzes_brett import get_schwarzes_brett as _get_schwarzes_brett
from .parsers.termine import get_termine as _get_termine
from .parsers.vertretungsplan import get_vertretungsplan as _get_vertretungsplan

mcp = FastMCP("elternportal")


def _with_session(fn, *args, **kwargs):
    """Execute fn with an authenticated session, retrying once on auth failure."""
    try:
        session = get_session()
        return fn(session, get_base_url(), *args, **kwargs)
    except Exception as e:
        if "login" in str(e).lower() or "csrf" in str(e).lower() or "form-signin" in str(e).lower():
            reset_session()
            session = get_session()
            return fn(session, get_base_url(), *args, **kwargs)
        raise


@mcp.tool()
def check_login() -> dict:
    """Verify that Eltern-Portal credentials are valid and login succeeds."""
    try:
        get_session()
        return {"status": "ok", "message": "Login successful", "url": get_base_url()}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
def get_vertretungsplan() -> dict:
    """Fetch the current substitution plan (Vertretungsplan) with structured data.

    Returns class name, last updated timestamp, and a list of days with
    substitution entries including period, teachers, subjects, room, and info.
    """
    return _with_session(_get_vertretungsplan)


@mcp.tool()
def list_elternbriefe() -> dict:
    """List all parent letters (Elternbriefe) with metadata.

    Returns entry number, title, date, classes, confirmation status, and
    whether a PDF file is available for download.
    """
    return _with_session(_list_elternbriefe)


@mcp.tool()
def get_elternbrief(number: int | None = None, title: str | None = None) -> dict:
    """Fetch a specific parent letter by number or title search.

    Provide either `number` (exact match, e.g. 134) or `title` (case-insensitive
    substring search). Returns the full content as markdown, converted from PDF
    if applicable.
    """
    return _with_session(_get_elternbrief, number=number, title=title)


@mcp.tool()
def get_schwarzes_brett() -> dict:
    """Fetch the bulletin board (Schwarzes Brett) announcements.

    Returns a list of announcements with title and content text.
    """
    return _with_session(_get_schwarzes_brett)


@mcp.tool()
def get_termine() -> dict:
    """Fetch upcoming school events and calendar entries (Termine).

    Returns a list of events with date, title, and description.
    """
    return _with_session(_get_termine)
