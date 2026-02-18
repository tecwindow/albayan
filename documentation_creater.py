import os
import re
import argparse
from markdown import markdown

HTML_HEADER = """<!DOCTYPE html>
<html lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel='stylesheet' type='text/css' media='screen' href='styles.css'>
    <style>
        html {{

        }}
    </style>
</head>
<body>
"""

HTML_FOOTER = """
</body>
</html>
"""


def extract_headings(md_text):
    """
    Extract all markdown headings and generate hierarchical numbering with custom IDs.
    
    This function scans the Markdown content and identifies all heading lines (#, ##, ###, etc.).
    It generates section numbers (like 1.2.3) and assigns either custom IDs (if provided in the Markdown)
    or automatically generated IDs (e.g., section-1-2). 
    It returns a list of tuples containing (numbering, title, level, section_id).
    """
    toc = []
    counters = []
    for line in md_text.splitlines():
        match = re.match(r'^(#{1,6})\s+(.*)', line)
        if match:
            level = len(match.group(1))
            content = match.group(2).strip()
            id_match = re.search(r'\{#([^}]+)\}', content)
            custom_id = id_match.group(1) if id_match else None
            title = re.sub(r'\s*\{#.*?\}\s*$', '', content).strip()
            while len(counters) < level:
                counters.append(0)
            while len(counters) > level:
                counters.pop()
            counters[-1] += 1
            numbering = '.'.join(str(c) for c in counters)
            section_id = custom_id if custom_id else "section-" + "-".join(str(c) for c in counters)
            toc.append((numbering, title, level, section_id))
    return toc


def generate_toc_html(toc):
    """
    Generate a single hierarchical TOC with one main <ul>,
    handling skipped levels and consecutive headings.
    """
    if not toc:
        return ""

    html = "<div class='toc'>\n<h2>جدول المحتويات</h2>\n"
    html += "<ul>\n"
    
    prev_level = 0
    
    for num, title, level, section_id in toc:
        if level > prev_level:

            for _ in range(level - prev_level - 1):
                html += "<li><ul>\n"
            if prev_level > 0:
                html += "<ul>\n"
        elif level < prev_level:
            for _ in range(prev_level - level):
                html += "</li>\n</ul>\n"
            html += "</li>\n"
        else:
            if prev_level > 0:
                html += "</li>\n"
        
        html += f'<li><a href="#{section_id}">{num}. {title}</a>'
        prev_level = level
    
    for _ in range(prev_level):
        html += "</li>\n</ul>\n"
    
    html += "</ul>\n</div>\n"
    return html

def add_ids_to_headings(html, toc):
    """
    Add id attributes to HTML headings corresponding to their section IDs in the TOC.
    
    This ensures that clicking a TOC entry scrolls to the correct heading.
    """
    pattern = r'(<h([1-6])>(.*?)</h\2>)'
    heading_index = 0

    def replace_heading(match):
        nonlocal heading_index
        if heading_index >= len(toc):
            return match.group(0)
        _, _, level, section_id = toc[heading_index]
        title = re.sub(r'\s*\{#.*?\}\s*$', '', match.group(3)).strip()
        heading_index += 1
        return f'<h{level} id="{section_id}">{title}</h{level}>'

    return re.sub(pattern, replace_heading, html)


def modify_external_links(html):
    """
    Modify all external links to open in a new tab with security attributes.
    
    Adds target="_blank" and rel="noopener noreferrer" to links that begin with http or https.
    """
    def replace_link(match):
        href = match.group(1)
        text = match.group(2)
        if href.startswith("http://") or href.startswith("https://"):
            return f'<a href="{href}" target="_blank" rel="noopener noreferrer">{text}</a>'
        else:
            return match.group(0)
    return re.sub(r'<a href="([^"]+)">(.*?)</a>', replace_link, html)


def convert_file(input_file, output_folder, version, include_toc=True):
    """
    Convert a single Markdown file to an HTML document with optional TOC and Arabic titles.
    
    Arguments:
        input_file (str): Path to the source Markdown file.
        output_folder (str): Path to the output folder for saving the HTML file.
        version (str): The version number to include in titles.
        include_toc (bool): Whether to include the Table of Contents (default: True).
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        md_text = f.read()

    filename = os.path.basename(input_file)

    if "WhatsNew.md" in filename:
        title = f"ما الجديد في البيان الإصدار {version}؟"
        html_body = markdown(md_text, extensions=['extra', 'tables', 'fenced_code'])
        html_body = modify_external_links(html_body)

    elif "UserGuide.md" in filename:
        title = f"دليل استخدام البيان الإصدار {version}"
        toc = extract_headings(md_text)
        toc_html = generate_toc_html(toc) if include_toc else ""
        html_body = markdown(md_text, extensions=['extra', 'tables', 'fenced_code'])
        html_body = add_ids_to_headings(html_body, toc)
        html_body = modify_external_links(html_body)
        html_body = toc_html + html_body if include_toc else html_body

    else:
        title = os.path.splitext(filename)[0]
        toc = extract_headings(md_text)
        toc_html = generate_toc_html(toc) if include_toc else ""
        html_body = markdown(md_text, extensions=['extra', 'tables', 'fenced_code'])
        html_body = add_ids_to_headings(html_body, toc)
        html_body = modify_external_links(html_body)
        html_body = toc_html + html_body if include_toc else html_body

    html_body = f"<article>\n{html_body}\n</article>"
    full_html = HTML_HEADER.format(title=title) + html_body + HTML_FOOTER

    output_file = os.path.join(output_folder, os.path.splitext(filename)[0] + ".html")
    os.makedirs(output_folder, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_html)

    print(f"✅ Converted: {input_file} → {output_file}")


def main():
    """
    Main entry point of the script.
    
    The script can:
        - Automatically search for Markdown files in the same directory if no input folder is given.
        - Output generated HTML files to the same directory unless a custom output is specified.
        - Optionally disable the Table of Contents or specify a custom version number.
    """
    parser = argparse.ArgumentParser(description="Convert Markdown to HTML with Arabic TOC and custom IDs.")
    parser.add_argument("-i", "--input", help="Input folder containing Markdown files. Default: current folder.")
    parser.add_argument("-o", "--output", help="Output folder for generated HTML files. Default: same as input.")
    parser.add_argument("-v", "--version", default="5.0.0", help="Version number (default: 4.0.2).")
    parser.add_argument("--no-toc", action="store_true", help="Disable Table of Contents generation.")
    args = parser.parse_args()

    # Determine input and output folders
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_folder = args.input if args.input else current_dir
    output_folder = args.output if args.output else input_folder

    if not os.path.isdir(input_folder):
        print(f"⚠ Input folder not found: {input_folder}")
        return

    md_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith(".md")]
    if not md_files:
        print("⚠ No Markdown files found in the input folder!")
        return

    for file in md_files:
        convert_file(file, output_folder, args.version, include_toc=not args.no_toc)


if __name__ == "__main__":
    main()
