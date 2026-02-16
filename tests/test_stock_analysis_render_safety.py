from pages.analysis_tabs.fundamental import _resolve_peg_display
from pages.stock_analysis import _sanitize_html_text


def test_sanitize_html_text_escapes_and_keeps_linebreaks() -> None:
    value = "More for you <<tag>>\nline2 <b>raw</b>"
    rendered = _sanitize_html_text(value, multiline=True)
    assert "&lt;&lt;tag&gt;&gt;" in rendered
    assert "line2 &lt;b&gt;raw&lt;/b&gt;" in rendered
    assert "<br>" in rendered


def test_resolve_peg_display_uses_derived_when_reported_missing() -> None:
    value, source = _resolve_peg_display(
        {"peg_ratio": None, "rev_growth": 0.25},
        {"trailing_pe": 40.0},
    )
    assert value == "1.60"
    assert "derived" in source
