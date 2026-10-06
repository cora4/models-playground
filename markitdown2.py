import json
import sys

from bs4 import BeautifulSoup, NavigableString, Tag, Comment

def render_list_item_content(li):
    """Render the non-list content of an <li> without destroying
    block-level whitespace such as fenced code blocks.
    """
    parts = []

    for child in li.children:
        if isinstance(child, Tag):
            if child.name in ("ul", "ol"):
                continue

            if child.name == "pre":
                code = child.find("code")

                if code:
                    content = code.get_text()
                    language = ""

                    for class_name in code.get("class", []):
                        if class_name.startswith("language-"):
                            language = class_name[len("language-"):]
                            break

                    parts.append(
                        f"```{language}\n"
                        f"{content.rstrip(chr(10))}\n"
                        f"```"
                    )
                else:
                    parts.append(
                        "```\n"
                        + child.get_text().rstrip("\n")
                        + "\n```"
                    )

            elif child.name == "p":
                parts.append(
                    inline_markdown(child).strip()
                )

            else:
                parts.append(
                    inline_markdown(child)
                )

        elif isinstance(child, NavigableString):
            value = str(child)

            if value.strip():
                parts.append(value.strip())

    return "\n\n".join(
        part for part in parts if part
    )

def clean_stream_markers(soup):
    """Remove streaming/commit marker comments."""
    for comment in soup.find_all(
        string=lambda text: isinstance(text, Comment)
    ):
        text = str(comment).strip()

        if (
            text.startswith("?marker ")
            or text.startswith("?start ")
            or text.startswith("?end")
        ):
            comment.extract()


def inline_markdown(element):
    """
    Convert inline HTML inside an element to Markdown.

    This recursively preserves inline formatting such as:
        <strong>...</strong>
        <em>...</em>
        <a href="...">...</a>
        <code>...</code>
        <br>
    """
    if isinstance(element, NavigableString):
        return str(element)

    if not isinstance(element, Tag):
        return ""

    tag = element.name.lower()

    if tag in ("strong", "b"):
        content = "".join(
            inline_markdown(child)
            for child in element.children
        )
        return f"**{content}**"

    if tag in ("em", "i"):
        content = "".join(
            inline_markdown(child)
            for child in element.children
        )
        return f"_{content}_"

    if tag == "a":
        content = "".join(
            inline_markdown(child)
            for child in element.children
        )

        href = element.get("href")

        if href:
            return f"[{content}]({href})"

        return content

#    if tag == "code":
#        return f"`{element.get_text()}`"

#    if tag == "br":
#        return "<br>"

    if tag == "code":
        content = element.get_text()
        # Markdown inline-code fences must be longer than any
        # consecutive run of backticks in the content.
        max_backticks = 0
        current = 0
        for char in content:
            if char == "`":
                current += 1
                max_backticks = max(max_backticks, current)
            else:
                current = 0
        delimiter = "`" * max(1, max_backticks + 1)
        # CommonMark convention: add spaces when the content
        # starts/ends with a backtick so the delimiters are clear.
        if (
            content.startswith("`")
            or content.endswith("`")
        ):
            return f"{delimiter} {content} {delimiter}"
        return f"{delimiter}{content}{delimiter}"

    return "".join(
        inline_markdown(child)
        for child in element.children
    )


def convert_math(soup):
    """Convert rendered MathML/KaTeX to Markdown LaTeX."""
    for x in soup.select("span[data-assistant-math-rendered]"):
        annotation = x.find(
            "annotation",
            attrs={"encoding": "application/x-tex"}
        )

        if not annotation:
            continue

        latex = annotation.get_text(strip=True)
        kind = x.get("data-assistant-math-rendered")

        if kind == "display":
            replacement = f"\n$$\n{latex}\n$$\n"
        else:
            replacement = f"${latex}$"

        x.replace_with(replacement)

def strip_param(url):
    return url.removesuffix("?utm_source=chatgpt.com").removesuffix("&utm_source=chatgpt.com")

def convert_assistant_links(soup):
    """
    Convert assistant source-reference buttons to Markdown links.

    Handles:
        button[data-assistant-sources-payload]
    """
    for container in soup.select("[data-assistant-grouped-webpages]"):
        button = container.select_one(
            "button[data-assistant-sources-payload]"
        )

        if not button:
            continue

        payload = button.get("data-assistant-sources-payload")

        if not payload:
            continue

        try:
            sources = json.loads(payload)
        except (json.JSONDecodeError, TypeError):
            continue

        links = []

        for source in sources:
            url = strip_param(source.get("url"))
            title = (
                source.get("title")
                or source.get("attribution")	
                or url
            )

            if url:
                links.append(f"[{title}]({url})")

        if links:
            container.replace_with("\n".join(links))

def convert_tables(soup):
    """Convert HTML tables to Markdown tables."""
    for container in soup.select(
        "[data-assistant-markdown-table]"
    ):
        table = container.find("table")

        if not table:
            continue

        rows = []

        for tr in table.find_all("tr"):
            cells = tr.find_all(
                ["th", "td"],
                recursive=False,
            )

            if not cells:
                continue

            row = []

            for cell in cells:
                text = inline_markdown(cell).strip()

                # Escape pipes because | has special meaning
                # inside Markdown tables.
                text = text.replace("|", r"\|")

                row.append(text)

            rows.append(row)

        if not rows:
            continue

        header = rows[0]
        column_count = len(header)

        # Preserve column alignment from the HTML header cells.
        header_cells = table.find("tr").find_all(
            ["th", "td"],
            recursive=False,
        )

        alignments = []
        for cell in header_cells:
            style = cell.get("style", "")
            alignments.append(
                "left" if "text-align: left" in style
                else "right" if "text-align: right" in style
                else "center" if "text-align: center" in style
                else None
            )

        alignment_markers = {
            "left": ":---",
            "center": ":---:",
            "right": "---:",
        }

        markdown = [
            "| " + " | ".join(header) + " |",
            "| " + " | ".join(
                alignment_markers.get(alignment, "---")
                for alignment in alignments
            ) + " |",
        ]

        for row in rows[1:]:
            row = row + [""] * (
                column_count - len(row)
            )

            markdown.append(
                "| "
                + " | ".join(row[:column_count])
                + " |"
            )

        container.replace_with(
            "\n"
            + "\n".join(markdown)
            + "\n\n"
        )

def render_list(list_element, depth=0):
    """
    Recursively render <ul>/<ol> while preserving list type.

    Unordered lists use:
        * at depth 0
        + at depth 1
        - at depth 2

    Ordered lists use:
        1.
        2.
        3.

    Nested list types are preserved independently.
    """
    ordered = list_element.name == "ol"
    lines = []

    direct_items = list_element.find_all(
        "li",
        recursive=False,
    )

    for index, li in enumerate(direct_items, 1):
        if ordered:
            marker = f"{index}."
        else:
            marker = ["*", "+", "-"][depth % 3]

        indentation = "  " * depth

        text = render_list_item_content(li)

        text_lines = text.splitlines()

        if not text_lines:
            lines.append(
                f"{indentation}{marker}"
            )
        else:
            # First line.
            lines.append(
                f"{indentation}{marker} {text_lines[0]}"
            )

            # Every subsequent line belongs to this list item.
            continuation_indent = indentation + "  "

            for line in text_lines[1:]:
                if line:
                    lines.append(
                        continuation_indent + line
                    )
                else:
                    lines.append("")

        # Nested lists.
        nested_lists = li.find_all(
            ["ul", "ol"],
            recursive=False,
        )

        for nested in nested_lists:
            lines.extend(
                render_list(
                    nested,
                    depth=depth + 1,
                )
            )

    return lines

def convert_lists(soup):
    """
    Convert top-level <ul>/<ol> elements recursively.

    Only top-level lists are processed here. Nested lists are
    handled by render_list(), preventing them from being flattened.
    """
    top_level_lists = [
        element
        for element in soup.find_all(["ul", "ol"])
        if element.find_parent(["ul", "ol"]) is None
    ]

    for list_element in top_level_lists:
        markdown = render_list(
            list_element,
            depth=0,
        )

        # Keep the generated Markdown as an explicit text node.
        list_element.replace_with(
            NavigableString(
                "\n"
                + "\n".join(markdown)
                + "\n"
            )
        )


def convert_blockquotes(soup):
    """Convert <blockquote>...</blockquote> to Markdown."""
    for blockquote in soup.find_all("blockquote"):
        text = inline_markdown(blockquote).strip()

        lines = [
            " ".join(line.split())
            for line in text.splitlines()
            if line.strip()
        ]

        markdown = "\n".join(
            "> " + line
            for line in lines
        )

        blockquote.replace_with(
            "\n"
            + markdown
            + "\n"
        )


def convert_headings(soup):
    """Convert HTML headings to Markdown headings."""
    for level in range(1, 7):
        for heading in soup.find_all(
            f"h{level}"
        ):
            text = inline_markdown(
                heading
            ).strip()

            heading.replace_with(
                "\n"
                + ("#" * level)
                + " "
                + text
                + "\n"
            )


def convert_code_blocks(soup):
    """
    Convert <pre><code>...</code></pre> to fenced Markdown.

    Preserves:
        - code content
        - newlines
        - indentation
        - language information from classes such as
          language-python

    Example:

        <pre>
            <code class="language-python">
            print("hello")
            </code>
        </pre>

    becomes:

        ```python
        print("hello")
        ```
    """
    for pre in soup.find_all("pre"):
        code = pre.find("code")

        if not code:
            content = pre.get_text()

            max_backticks = 0
            current = 0

            for char in content:
                if char == "`":
                    current += 1
                    max_backticks = max(
                        max_backticks,
                        current,
                    )
                else:
                    current = 0

            fence = "`" * max(
                3,
                max_backticks + 1,
            )

            markdown = (
                f"\n{fence}\n"
                f"{content.rstrip(chr(10))}\n"
                f"{fence}\n"
            )

            pre.replace_with(markdown)
            continue

        content = code.get_text()

        language = ""

        for class_name in code.get("class", []):
            if class_name.startswith("language-"):
                language = class_name[
                    len("language-"):
                ]
                break

        # Find the longest consecutive run of backticks
        # anywhere inside the code content.
        max_backticks = 0
        current = 0

        for char in content:
            if char == "`":
                current += 1
                max_backticks = max(
                    max_backticks,
                    current,
                )
            else:
                current = 0

        # Markdown fenced code blocks require at least 3 backticks,
        # and the fence must be longer than any backtick run inside
        # the content.
        fence = "`" * max(
            3,
            max_backticks + 1,
        )

        markdown = (
            f"\n{fence}{language}\n"
            f"{content.rstrip(chr(10))}\n"
            f"{fence}\n"
        )

        # Replace the entire <pre>, not merely <code>.
        pre.replace_with(markdown)

def convert_horizontal_rules(soup):
    """Convert <hr> to Markdown horizontal rules."""
    for hr in soup.find_all("hr"):
        hr.replace_with("\n---\n")


def clean_output(text):
    """
    Clean excessive blank lines while preserving Markdown
    structure and indentation.
    """
    lines = text.splitlines()

    output = []
    blank = False

    for line in lines:
        # Only remove trailing whitespace.
        line = line.rstrip()

        if not line:
            if not blank:
                output.append("")
            blank = True
        else:
            output.append(line)
            blank = False

    return "\n".join(output).strip()

def convert_paragraphs(soup):
    """Convert HTML paragraphs into separated Markdown paragraphs."""
    for paragraph in soup.find_all("p"):
        if paragraph.find_parent(
            ["li", "blockquote", "table", "pre"]
        ):
            continue

        content = inline_markdown(paragraph).strip()

        paragraph.replace_with(
            "\n\n" + content + "\n\n"
        )

def main():
    html = sys.stdin.read()

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    # ------------------------------------------------------------
    # Conversion order matters.
    # ------------------------------------------------------------

    # Remove internal streaming markers first.
    clean_stream_markers(soup)

    # Math must be converted before structures containing it.
    convert_math(soup)

    # Convert assistant source/reference UI.
    convert_assistant_links(soup)

    # Tables before generic text extraction.
    convert_tables(soup)

    # Lists recursively preserve <ul>/<ol> hierarchy and type.
    convert_lists(soup)

    # Code blocks must be converted before generic inline <code>.
    convert_code_blocks(soup)

    # Other block-level structures.
    convert_blockquotes(soup)
    convert_headings(soup)
    convert_horizontal_rules(soup)

    convert_paragraphs(soup)

    # Everything remaining is ordinary text or already-generated
    # Markdown strings.
    result = soup.get_text()

    print(clean_output(result))


if __name__ == "__main__":
    main()
