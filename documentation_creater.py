import os
import re
import argparse
from markdown import markdown


# ---------------------------------------------------------------------------
# HTML Templates
# ---------------------------------------------------------------------------

HTML_HEADER = """<!DOCTYPE html>
<html lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="styles.css">
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


# ---------------------------------------------------------------------------
# Heading & TOC Utilities
# ---------------------------------------------------------------------------

def extract_headings(md_text):
    """
    Scan Markdown text and return a list of all headings with metadata.

    For each heading found, this function:
      - Determines the heading level (1-6).
      - Extracts a custom anchor ID if present in the form {#some-id}.
      - Generates a fallback ID like 'section-1-2' if no custom ID is given.
      - Computes a hierarchical numbering string (e.g. '1.2.3').

    Returns:
        List of tuples: (numbering, title, level, section_id)
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
    Convert a TOC list (from extract_headings) into a nested HTML structure.

    Produces a <div class='toc'> block with a hierarchical <ul> tree.
    Handles skipped heading levels gracefully.

    Returns:
        HTML string for the table of contents, or empty string if toc is empty.
    """
    if not toc:
        return ""

    html = "<div class='toc'>\n<h2>جدول المحتويات</h2>\n<ul>\n"
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

    html += "</div>\n"
    return html


def add_ids_to_headings(html, toc):
    """
    Inject id attributes into HTML heading tags based on the TOC section IDs.

    Matches each <hN>...</hN> tag in order and replaces it with
    <hN id="section_id">title</hN>, enabling anchor navigation from the TOC.

    Args:
        html (str): Rendered HTML content.
        toc (list): TOC list from extract_headings().

    Returns:
        HTML string with id attributes added to headings.
    """
    heading_index = 0

    def replace_heading(match):
        nonlocal heading_index
        if heading_index >= len(toc):
            return match.group(0)
        _, _, level, section_id = toc[heading_index]
        title = re.sub(r'\s*\{#.*?\}\s*$', '', match.group(3)).strip()
        heading_index += 1
        return f'<h{level} id="{section_id}">{title}</h{level}>'

    return re.sub(r'(<h([1-6])>(.*?)</h\2>)', replace_heading, html)


# ---------------------------------------------------------------------------
# Markdown Transformation Utilities
# ---------------------------------------------------------------------------

def remove_inline_links(md_text):
    """
    Strip internal anchor links of the form [text](#anchor), keeping only the text.

    Example:
        [النافذة الرئيسية](#main-interface)  ->  النافذة الرئيسية

    External links (http/https) are left untouched.
    """
    return re.sub(r'\[([^\]]+)\]\(#[^)]*\)', r'\1', md_text)


def demote_headings(md_text):
    """
    Reduce every heading level by one '#' symbol.

    ## becomes #, ### becomes ##, #### becomes ###, etc.
    Headings already at level 1 (#) are left unchanged.
    """
    def replace_heading(match):
        hashes = match.group(1)
        rest = match.group(2)
        if len(hashes) > 1:
            return f'{"#" * (len(hashes) - 1)} {rest}'
        return match.group(0)

    return re.sub(r'^(#{1,6})\s+(.*)', replace_heading, md_text, flags=re.MULTILINE)


def modify_external_links(html):
    """
    Make all external links (http/https) open in a new browser tab securely.

    Adds target="_blank" and rel="noopener noreferrer" to qualifying <a> tags.
    Internal anchor links are left unchanged.
    """
    def replace_link(match):
        href, text = match.group(1), match.group(2)
        if href.startswith("http://") or href.startswith("https://"):
            return f'<a href="{href}" target="_blank" rel="noopener noreferrer">{text}</a>'
        return match.group(0)

    return re.sub(r'<a href="([^"]+)">(.*?)</a>', replace_link, html)


# ---------------------------------------------------------------------------
# Section Extraction
# ---------------------------------------------------------------------------

def extract_section(md_text, heading_pattern):
    """
    Generic helper to extract a ## section block from Markdown text.

    Starts collecting lines when a line matches heading_pattern,
    and stops when the next ## heading (different from the start) is found.

    Args:
        md_text (str): Full Markdown content.
        heading_pattern (re.Pattern): Compiled regex matching the target ## heading line.

    Returns:
        Extracted section as a string, or None if the heading was not found.
    """
    lines = md_text.splitlines(keepends=True)
    next_h2 = re.compile(r'^##\s+')
    in_section = False
    section_lines = []

    for line in lines:
        if not in_section:
            if heading_pattern.match(line.rstrip()):
                in_section = True
                section_lines.append(line)
        else:
            if next_h2.match(line) and not heading_pattern.match(line.rstrip()):
                break
            section_lines.append(line)

    return ''.join(section_lines) if section_lines else None


def build_section_md(md_text, heading_pattern):
    """
    Extract a section, remove internal anchor links, and demote all headings by one level.

    This is the shared pipeline used before writing Shortcuts or Marks to
    their own standalone Markdown files.

    Args:
        md_text (str): Full Markdown content of UserGuide.md.
        heading_pattern (re.Pattern): Compiled regex matching the target ## heading.

    Returns:
        Processed Markdown string, or None if the section was not found.
    """
    section = extract_section(md_text, heading_pattern)
    if section is None:
        return None
    section = remove_inline_links(section)
    section = demote_headings(section)
    return section


# Precompiled heading patterns for each extracted section
SHORTCUTS_HEADING = re.compile(r'^##\s+اختصارات لوحة المفاتيح(\s*\{#[^}]*\})?\s*$')
MARKS_HEADING     = re.compile(r'^##\s+علامات الوقف(\s*\{#[^}]*\})?\s*$')


# ---------------------------------------------------------------------------
# HTML Assembly
# ---------------------------------------------------------------------------

def build_html(md_text, title, include_toc=True, add_heading_ids=True):
    """
    Convert Markdown text to a complete, styled HTML document string.

    Args:
        md_text (str): Markdown content to convert.
        title (str): Value for the HTML <title> tag.
        include_toc (bool): If True, prepend a table of contents. Default: True.
        add_heading_ids (bool): If True, inject id attributes into headings. Default: True.

    Returns:
        Full HTML document as a string.
    """
    toc = extract_headings(md_text) if (include_toc or add_heading_ids) else []
    body = markdown(md_text, extensions=['extra', 'tables', 'fenced_code'])

    if add_heading_ids:
        body = add_ids_to_headings(body, toc)

    body = modify_external_links(body)

    if include_toc:
        body = generate_toc_html(toc) + body

    body = f"<article>\n{body}\n</article>"
    return HTML_HEADER.format(title=title) + body + HTML_FOOTER


def write_file(path, content):
    """
    Write a string to a file, creating parent directories as needed.

    Args:
        path (str): Full file path to write to.
        content (str): Text content to write.
    """
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


# ---------------------------------------------------------------------------
# Per-document Conversion Logic
# ---------------------------------------------------------------------------

def process_whats_new(md_text, output_folder, version):
    """
    Convert WhatsNew.md to HTML.

    Output: WhatsNew.html — no TOC, no heading IDs.
    Title:  'ما الجديد في البيان الإصدار {version}؟'
    """
    title = f"ما الجديد في البيان الإصدار {version}؟"
    html = build_html(md_text, title, include_toc=False, add_heading_ids=False)
    out = os.path.join(output_folder, "WhatsNew.html")
    write_file(out, html)
    print(f"✅ Converted: WhatsNew.md -> {out}")


def process_user_guide(md_text, output_folder, version, include_toc,
                        gen_shortcuts, gen_marks):
    """
    Convert UserGuide.md to HTML, and optionally generate Shortcuts and Marks files.

    Args:
        md_text (str): Content of UserGuide.md.
        output_folder (str): Destination folder for all output files.
        version (str): Version string used in page titles.
        include_toc (bool): Whether to include a TOC in UserGuide.html.
        gen_shortcuts (bool): Whether to generate Shortcuts.md and Shortcuts.html.
        gen_marks (bool): Whether to generate Marks.md and Marks.html.
    """
    # --- UserGuide.html ---
    title = f"دليل استخدام البيان الإصدار {version}"
    html = build_html(md_text, title, include_toc=include_toc)
    out = os.path.join(output_folder, "UserGuide.html")
    write_file(out, html)
    print(f"✅ Converted: UserGuide.md -> {out}")

    # --- Shortcuts.md + Shortcuts.html ---
    if gen_shortcuts:
        shortcuts_md = build_section_md(md_text, SHORTCUTS_HEADING)
        if shortcuts_md:
            md_path = os.path.join(output_folder, "Shortcuts.md")
            write_file(md_path, shortcuts_md)
            print(f"✅ Created: {md_path}")

            shortcuts_title = f"دليل اختصارات البيان الإصدار {version}"
            shortcuts_html = build_html(shortcuts_md, shortcuts_title, include_toc=include_toc)
            html_path = os.path.join(output_folder, "Shortcuts.html")
            write_file(html_path, shortcuts_html)
            print(f"✅ Created: {html_path}")
        else:
            print("⚠ Shortcuts section not found in UserGuide.md")

    # --- Marks.md + Marks.html ---
    if gen_marks:
        marks_md = build_section_md(md_text, MARKS_HEADING)
        if marks_md:
            md_path = os.path.join(output_folder, "Marks.md")
            write_file(md_path, marks_md)
            print(f"✅ Created: {md_path}")

            marks_title = f"علامات الوقف في البيان الإصدار {version}"
            marks_html = build_html(marks_md, marks_title, include_toc=False, add_heading_ids=False)
            html_path = os.path.join(output_folder, "Marks.html")
            write_file(html_path, marks_html)
            print(f"✅ Created: {html_path}")
        else:
            print("⚠ Marks section not found in UserGuide.md")


def process_generic(md_text, input_file, output_folder, include_toc):
    """
    Convert any unrecognized Markdown file to HTML with TOC and heading IDs.

    The output filename mirrors the input filename with an .html extension.
    The page title is set to the filename (without extension).
    """
    filename = os.path.basename(input_file)
    title = os.path.splitext(filename)[0]
    html = build_html(md_text, title, include_toc=include_toc)
    out = os.path.join(output_folder, os.path.splitext(filename)[0] + ".html")
    write_file(out, html)
    print(f"✅ Converted: {input_file} -> {out}")


# ---------------------------------------------------------------------------
# File Dispatcher
# ---------------------------------------------------------------------------

def convert_file(input_file, output_folder, version, include_toc,
                 gen_shortcuts, gen_marks):
    """
    Read a Markdown file and dispatch it to the appropriate processing function.

    Routes based on filename:
      - WhatsNew.md  -> process_whats_new()
      - UserGuide.md -> process_user_guide()
      - anything else -> process_generic()

    Args:
        input_file (str): Path to the source .md file.
        output_folder (str): Directory to write all output files into.
        version (str): Version number string for HTML titles.
        include_toc (bool): Whether to generate a table of contents.
        gen_shortcuts (bool): Whether to generate the Shortcuts files.
        gen_marks (bool): Whether to generate the Marks files.
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        md_text = f.read()

    filename = os.path.basename(input_file)

    if "WhatsNew.md" in filename:
        process_whats_new(md_text, output_folder, version)
    elif "UserGuide.md" in filename:
        process_user_guide(md_text, output_folder, version, include_toc,
                           gen_shortcuts, gen_marks)
    else:
        process_generic(md_text, input_file, output_folder, include_toc)


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

def main():
    """
    Parse CLI arguments and process all .md files in the input folder.

    Parameters
    ----------
    -i / --input
        Path to the folder containing Markdown source files.
        Default: the directory where this script lives.

    -o / --output
        Path to the folder where all output files will be saved.
        Default: same as --input.

    -v / --version
        Version number string embedded in HTML page titles.
        Default: '5.0.1'
        Example: -v 5.0.1

    --no-toc
        Disable table of contents for all documents that normally include one
        (UserGuide, Shortcuts, and generic files).

    --no-shortcuts
        Skip generating Shortcuts.md and Shortcuts.html from UserGuide.md.

    --no-marks
        Skip generating Marks.md and Marks.html from UserGuide.md.

    --only ITEM [ITEM ...]
        Generate only the specified output files; everything else is skipped.
        Accepted values (case-insensitive):
            userguide   -> UserGuide.html
            whatsnew    -> WhatsNew.html
            shortcuts   -> Shortcuts.md + Shortcuts.html
            marks       -> Marks.md + Marks.html
        Example: --only shortcuts marks
        Note: --only takes precedence over --no-shortcuts and --no-marks.

    Usage examples
    --------------
    # Convert everything with defaults:
        python md_to_html.py

    # Custom input/output folders and version:
        python md_to_html.py -i ./docs -o ./dist -v 5.0.1

    # Skip shortcuts and marks:
        python md_to_html.py --no-shortcuts --no-marks

    # Generate only shortcuts and marks (skip UserGuide.html and WhatsNew.html):
        python md_to_html.py --only shortcuts marks

    # Generate only UserGuide.html without a TOC:
        python md_to_html.py --only userguide --no-toc
    """
    parser = argparse.ArgumentParser(
        description="Convert Markdown documentation to HTML with Arabic TOC and custom IDs.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-i", "--input",
                        help="Input folder containing Markdown files. Default: script directory.")
    parser.add_argument("-o", "--output",
                        help="Output folder for generated files. Default: same as input.")
    parser.add_argument("-v", "--version", default="5.0.1",
                        help="Version number for page titles. Default: 5.0.1")
    parser.add_argument("--no-toc", action="store_true",
                        help="Disable table of contents in all output HTML files.")
    parser.add_argument("--no-shortcuts", action="store_true",
                        help="Skip generating Shortcuts.md and Shortcuts.html.")
    parser.add_argument("--no-marks", action="store_true",
                        help="Skip generating Marks.md and Marks.html.")
    parser.add_argument("--only", nargs="+", metavar="ITEM",
                        help=(
                            "Generate only the listed outputs. "
                            "Accepted: userguide, whatsnew, shortcuts, marks. "
                            "Example: --only shortcuts marks"
                        ))
    args = parser.parse_args()

    # Resolve input/output folders
    current_dir   = os.path.dirname(os.path.abspath(__file__))
    input_folder  = args.input  if args.input  else current_dir
    output_folder = args.output if args.output else input_folder

    if not os.path.isdir(input_folder):
        print(f"⚠ Input folder not found: {input_folder}")
        return

    md_files = [os.path.join(input_folder, f)
                for f in os.listdir(input_folder) if f.endswith(".md")]
    if not md_files:
        print("⚠ No Markdown files found in the input folder!")
        return

    # Resolve which outputs to produce (--only overrides individual --no-* flags)
    if args.only:
        only          = {item.lower() for item in args.only}
        run_userguide = "userguide"  in only
        run_whatsnew  = "whatsnew"   in only
        gen_shortcuts = "shortcuts"  in only
        gen_marks     = "marks"      in only
    else:
        run_userguide = True
        run_whatsnew  = True
        gen_shortcuts = not args.no_shortcuts
        gen_marks     = not args.no_marks

    include_toc = not args.no_toc

    for file in md_files:
        filename = os.path.basename(file)

        # Skip files not selected by --only
        if "WhatsNew.md" in filename and not run_whatsnew:
            continue
        if "UserGuide.md" in filename and not run_userguide and not gen_shortcuts and not gen_marks:
            continue

        convert_file(file, output_folder, args.version, include_toc,
                     gen_shortcuts, gen_marks)


if __name__ == "__main__":
    main()