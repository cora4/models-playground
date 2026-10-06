import json
import sys

from bs4 import BeautifulSoup, NavigableString, Tag, Comment

def render_list_item_content(li):
    """Render the non-list content of an <li>.

    Inline content is kept together on the same line.
    Block-level content such as fenced code blocks is separated.
    """
    parts = []
    inline_parts = []

    def flush_inline():
        if inline_parts:
            content = "".join(inline_parts).strip()
            if content:
                parts.append(content)
            inline_parts.clear()

    for child in li.children:
        if isinstance(child, Tag):
            if child.name in ("ul", "ol"):
                continue

            if child.name == "pre":
                flush_inline()

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

            else:
                # <code>, <strong>, <em>, <span>, <p>, etc.
                inline_parts.append(inline_markdown(child))

        elif isinstance(child, NavigableString):
            # Preserve whitespace between inline elements, but ignore
            # indentation/newlines around block content.
            if child.strip():
                inline_parts.append(str(child))

    flush_inline()

    return "\n\n".join(parts)


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

    if tag == "span":
        content = "".join(
            inline_markdown(child)
            for child in element.children
        )
        # Only treat a span as a heading when it contains an SVG.
        if element.find("svg") and element.find("path") is not None:
            return f"### {content}"

        classes = element.get("class", [])
        if "font-semibold" in classes:
            return f"**{content}**"

        return content

    if tag == "a":
        content = "".join(
            inline_markdown(child)
            for child in element.children
        )

        href = element.get("href")

        if href:
            return f"[{content}]({href})"

        return content

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
        button[data-grouped-citations]
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
            inside_table = button.find_parent("table") is not None
            separator = "<br>" if inside_table else "\n"
            prefix = " " if inside_table else ""

            button.replace_with(
                prefix + separator.join(links)
            )

    # button[data-grouped-citations]
    for button in soup.select("button[data-grouped-citations]"):
        payload = button.get("data-grouped-citations")

        if not payload:
            continue

        try:
            sources = json.loads(payload)
        except (json.JSONDecodeError, TypeError):
            continue

        links = []

        for source in sources:
            url = strip_param(source.get("url"))

            if not url:
                continue

            # The first citation gets the descriptive text.
            # Subsequent citations use the domain/name.
            if not links:
                title = button.get("aria-label", "")

                # "Citation: openai — GPT-5 is here - OpenAI plus 1 more"
                if " — " in title:
                    title = title.split(" — ", 1)[1]
                    title = title.split(" plus ", 1)[0]
                else:
                    title = source.get("name") or url

            else:
                title = source.get("name") or url

            links.append(f"[{title}]({url})")

        if links:
            inside_table = button.find_parent("table") is not None
            separator = "<br>" if inside_table else "\n"
            prefix = " " if inside_table else ""

            button.replace_with(
                prefix + separator.join(links)
            )

def convert_tables(soup):
    """Convert HTML tables to Markdown tables."""
    for container in soup.select(
        "[data-assistant-markdown-table], "
        "c-gov-view-your-payments[c-govviewyourpaymentscontainer_govviewyourpaymentscontainer], "
#        "div:has(> div > table)"
        "div > div:has(> table)"
    ):
        for table in container.find_all("table"):
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

            # IMPORTANT: replace the table, not the container.
            table.replace_with(
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
    item_index = 0

    # Iterate over ALL direct children so that malformed-but-valid-in-
    # BeautifulSoup HTML such as <ul><li>...</li><a>...</a></ul>
    # doesn't lose the <a>.
    for child in list_element.find_all(recursive=False):

        if child.name == "li":
            item_index += 1

            if ordered:
                marker = f"{item_index}."
            else:
                marker = ["*", "+", "-"][depth % 3]

            indentation = "  " * depth

            text = render_list_item_content(child)
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

                # Subsequent lines belong to this list item.
                continuation_indent = indentation + "  "

                for line in text_lines[1:]:
                    if line:
                        lines.append(
                            continuation_indent + line
                        )
                    else:
                        lines.append("")

            # Nested lists.
            nested_lists = child.find_all(
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

        elif child.name in ("ul", "ol"):
            # Handle a directly nested list if one exists.
            lines.extend(
                render_list(
                    child,
                    depth=depth + 1,
                )
            )

        else:
            # Preserve things such as:
            # <a>...</a>
            text = inline_markdown(child).strip()

            if text:
                lines.append(text)

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
        line = line.rstrip().removeprefix(" ")

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
    for paragraph in soup.find_all(["p", "span"]):
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
