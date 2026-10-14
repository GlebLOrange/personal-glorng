from app.services.og_html import render_og_html


def test_render_og_html_quote_escapes_attributes() -> None:
    html = render_og_html(
        title='Title "quoted"',
        description="Desc <tag>",
        canonical_url='https://example.com/x?a="b"',
        og_type="article",
        image_url="https://example.com/img.png",
    )
    assert 'content="Title &quot;quoted&quot;"' in html
    assert 'content="Desc &lt;tag&gt;"' in html
    assert 'href="https://example.com/x?a=&quot;b&quot;"' in html
    assert 'content="article"' in html
