"""Utility functions for plugin service."""
import markdown
from markupsafe import Markup


def render_markdown(content: str | None) -> Markup:
    """
    Render markdown to HTML safely.
    
    Args:
        content: Markdown content to render (or None)
        
    Returns:
        Markup object with rendered HTML (safe for Jinja2 templates)
    """
    if not content:
        return Markup("")
    
    html = markdown.markdown(
        content,
        extensions=['fenced_code', 'tables', 'nl2br'],
        output_format='html5'
    )
    return Markup(html)

