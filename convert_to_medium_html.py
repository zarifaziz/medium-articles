import markdown
import re

with open("prompt-optimization-frameworks-vs-agents.md", "r") as f:
    md_content = f.read()

# Remove [IMAGE: ...] placeholders - we'll add images later in Medium
md_content = re.sub(r'\[IMAGE:.*?\]', '', md_content)

# Remove --- horizontal rules (Medium doesn't use them the same way)
md_content = re.sub(r'^---$', '', md_content, flags=re.MULTILINE)

# Convert markdown to HTML
html = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])

# Wrap in a basic HTML page
full_html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Article</title>
<style>
body {{ font-family: Georgia, serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.8; }}
h1 {{ font-size: 2em; }}
h2 {{ font-size: 1.5em; margin-top: 2em; }}
h3 {{ font-size: 1.2em; margin-top: 1.5em; }}
pre {{ background: #f5f5f5; padding: 16px; overflow-x: auto; border-radius: 4px; }}
code {{ background: #f5f5f5; padding: 2px 6px; border-radius: 3px; }}
table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
th {{ background: #f5f5f5; }}
blockquote {{ border-left: 3px solid #ccc; margin-left: 0; padding-left: 1em; color: #666; }}
</style>
</head><body>
{html}
</body></html>"""

with open("article_for_medium.html", "w") as f:
    f.write(full_html)

print("Done! HTML written to article_for_medium.html")
