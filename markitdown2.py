import json, sys, re
from bs4 import BeautifulSoup, NavigableString, Tag, Comment

def clean_stream_markers(soup):
    """Remove streaming/commit marker comments."""
    for comment in soup.find_all(
        string=lambda text: isinstance(text, Comment)
    ):
        if re.fullmatch(r"[/a-z-]*", str(comment).strip()):
            comment.extract()

        text = str(comment).strip()
        if (
            text.startswith("?marker ")
#            or text.startswith("?start ")
#            or text.startswith("?end")
        ):
            comment.extract()

def strip_param(url):
    return url.removesuffix("?utm_source=chatgpt.com").removesuffix("&utm_source=chatgpt.com")

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

#    if tag == "span":
#        content = "".join(
#            inline_markdown(child)
#            for child in element.children
#        )
        # Only treat a span as a heading when it contains an SVG.
#        if element.find("svg") and element.find("path") is not None:
#            return f"### {content}"

#        classes = element.get("class", [])
#        if "font-semibold" in classes:
#            return f"**{content}**"

#        return content

    if tag == "span":
        if (
            element.get("data-d-component") == "text"
            and (
                element.has_attr("data-d-default-strong")
                or (
                    element.has_attr("data-d-inline")
                    and "--x-color: var(--d-link-hover-color, var(--d-inherited-text-color, inherit));"
                    in element.get("style", "")
                )
            )
        ):
            content = "".join(
                inline_markdown(child)
                for child in element.children
            )
            classes = element.get("class", [])

            if "x1k4tb9n" in classes:
                return f"*{content}*"

#            if "x1s688f" in classes:
            return f"**{content}**"

    if tag == "a":
        content = "".join(
            inline_markdown(child)
            for child in element.children
        ).strip()

        href = strip_param(element.get("href"))

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
    for math in soup.select("math"):
        annotation = math.find(
            "annotation",
            attrs={"encoding": "application/x-tex"}
        )

        if not annotation:
            continue

        latex = annotation.get_text(strip=True)
        is_display = math.get("display") == "block"

        if is_display:
            replacement = f"\n$$\n{latex}\n$$\n"
        else:
            replacement = f"${latex}$"

        # Prefer replacing the entire KaTeX rendering.
        container = math.find_parent(
            "span", class_="katex"
        )

        # Support other rendered math containers, if present.
        if not container:
            container = math.find_parent(
                "div", attrs={"data-d-component": "math"}
            )

        if container:
            # Remove the rendered HTML to avoid duplicate math text.
#            katex_html = container.select_one(".katex-html")
#            if katex_html:
#                katex_html.decompose()

            container.replace_with(
                NavigableString(replacement)
            )

        else:
            math.replace_with(NavigableString(replacement))

def convert_assistant_links(soup):
    """
    Convert assistant source-reference buttons to Markdown links.

    Handles:
        button[data-assistant-sources-payload]
        button[data-grouped-citations]
    """
    for container in soup.select("[data-assistant-grouped-webpages]," "[data-assistant-reference-detail]"):
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
                title = f"*{title}*"

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
        'div[data-d-component="table"]'
#        "div:has(> div > table)"
#        "div > div:has(> table)"
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
                classes = cell.get("class", [])
                data_align = cell.get("data-d-align")

                if data_align in ("start", "center", "end"):
                    alignment = {
                        "start": "left",
                        "center": "center",
                        "end": "right",
                    }[data_align]
                elif "text-align: left" in style:
                    alignment = "left"
                elif "text-align: center" in style:
                    alignment = "center"
                elif "text-align: right" in style:
                    alignment = "right"
                elif "x1yc453h" in classes:
                    alignment = "left"  # text-align: start
                elif "x2b8uid" in classes:
                    alignment = "center"
                elif "xp4054r" in classes:
                    alignment = "right"  # text-align: end
                else:
                    alignment = None

                alignments.append(alignment)

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


def render_list_item_content(li):
    """Render an <li>'s text without including nested lists."""
    parts = []
    inline_parts = []

    def flush_inline():
        if inline_parts:
            content = "".join(inline_parts).strip()
            if content:
                parts.append(content)
            inline_parts.clear()

    def render_without_lists(node):
        if isinstance(node, NavigableString):
            return str(node)

        if not isinstance(node, Tag):
            return ""

        if node.name in ("ul", "ol"):
            return ""

        if node.name == "pre":
            return (
                "\n\n```\n"
                + node.get_text().rstrip("\n")
                + "\n```\n\n"
            )

        # Preserve inline formatting when the subtree has no lists.
        if not node.find(["ul", "ol"]):
            return inline_markdown(node)

        # A wrapper contains a nested list: render its children
        # individually, omitting the list but keeping surrounding text.
        return "".join(
            render_without_lists(child)
            for child in node.children
        )

    for child in li.children:
        rendered = render_without_lists(child)
        if rendered:
            inline_parts.append(rendered)

    flush_inline()
    return "\n\n".join(parts)


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
    item_index = int(list_element.get("start", 1)) - 1

    for child in list_element.find_all(recursive=False):
        if child.name == "li":
            item_index += 1

            marker = (
                f"{item_index}."
                if ordered
                else ["*", "+", "-"][depth % 3]
            )
            indentation = "  " * depth

            text = render_list_item_content(child)
            text_lines = text.splitlines()

            if text_lines:
                lines.append(f"{indentation}{marker} {text_lines[0]}")
                for line in text_lines[1:]:
                    lines.append(
                        f"{indentation}  {line}" if line else ""
                    )
            else:
                lines.append(f"{indentation}{marker}")

            # Find nested lists anywhere inside wrapper elements,
            # but do not descend into a nested list while searching.
            def direct_nested_lists(item):
                for node in item.children:
                    if not isinstance(node, Tag):
                        continue
                    if node.name in ("ul", "ol"):
                        yield node
                    else:
                        yield from direct_nested_lists(node)

            for nested in direct_nested_lists(child):
                lines.extend(render_list(nested, depth + 1))

        elif child.name in ("ul", "ol"):
            lines.extend(render_list(child, depth + 1))

        else:
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
    Convert HTML code blocks to fenced Markdown.

    Supports:
        - <pre><code>...</code></pre>
        - bare <pre>...</pre>
        - virtualized code editors using the structure:
            <div aria-label="Code Preview">
                <div tabindex="-1">
                    <div data-testid="one-copilot-code-identity">
                        <svg>...</svg>
                        <span>C++</span>
                    </div>

                    ...

                    <div data-virtualized-code-find-root="true">
                        <div data-line-index="0">...</div>
                        <div data-line-index="1">...</div>
                    </div>
                </div>
            </div>

    Preserves:
        - code content
        - newlines
        - indentation
        - language information
        - backticks inside code

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

    Handles:
      - HTML code components:
        <section data-conversation-component="html-code">...</section>
    """
    def get_fence(content):
        max_backticks = 0
        current = 0

        for char in content:
            if char == "`":
                current += 1
                max_backticks = max(
                    max_backticks,
                    current
                )
            else:
                current = 0

        return "`" * max(
            3,
            max_backticks + 1,
        )

    def to_markdown(content, language=""):
        fence = get_fence(content)

        return (
            f"\n{fence}{language}\n"
            f"{content.rstrip(chr(10))}\n"
            f"{fence}\n"
        )

    def get_language_from_classes(element):
        current = element

        while current is not None:
            for class_name in current.get("class", []):
                if class_name.startswith("language-"):
                    return class_name[len("language-"):]

            current = current.parent

        return ""

    def get_language_from_previous_span(pre):
        previous = pre.find_previous_sibling("span")

        if previous is not None:
            language = previous.get_text(strip=True)
            previous.decompose()
            if language:
                return language

        return ""

    # Handle HTML code components first.
    for section in reversed(
        soup.select(
'[data-conversation-component="html-code"], '
'[data-assistant-writing-block], '
'div > [data-code-block="true"]'
    )
    ):
         if section.parent is None:
             continue
     
         header = section.select_one(
             ':scope > div[data-markdown-copy="exclude"]'
         )
     
         language = ""
         if header is not None:
             label = header.select_one(
#                 ':scope > div.min-w-0.flex-1'
                 ':scope > div'
             )
             if label is not None:
                 language = label.get_text(strip=True).lower()
     
         code = section.select_one("pre > code")
         if code is None:
             continue
     
         content = code.get_text()
         section.replace_with(to_markdown(content, language))

    # Handle standard <pre> blocks.
    for pre in reversed(soup.find_all("pre")):
        if pre.parent is None:
            continue

        code = pre.find("code", recursive=False)

        if code is None:
            content = pre.get_text()
        else:
            content = code.get_text()

        language = (
            get_language_from_classes(code)
            if code is not None
            else ""
        )

        language = (
            language
            or get_language_from_previous_span(pre)
        )

        pre.replace_with(to_markdown(content, language))

    # ---------------------------------------------------------------
    # Virtualized code editors
    #
    # Both the language identity and the virtualized editor are
    # children of:
    #
    # <div aria-label="Code Preview">
    # ---------------------------------------------------------------
    for preview in soup.find_all(
        attrs={"aria-label": "Code Preview"}
    ):
        # The actual code-block container is the descendant
        # with tabindex="-1".
        container = preview.find(
            attrs={"tabindex": "-1"}
        )

        if container is None:
            continue

        root = container.find(
            attrs={
                "data-virtualized-code-find-root": True
            }
        )

        if root is None:
            continue

        line_elements = root.find_all(
            attrs={"data-line-index": True}
        )

        if not line_elements:
            continue

        lines = {}

        for element in line_elements:
            try:
                index = int(
                    element.get("data-line-index")
                )
            except (TypeError, ValueError):
                continue

            if index in lines:
                continue

            text = element.get_text()

            # BeautifulSoup converts &nbsp; to \xa0.
            text = text.replace("\xa0", " ")

            lines[index] = text

        if not lines:
            continue

        content = "\n".join(
            lines[index]
            for index in sorted(lines)
        )

        # The language and the virtualized editor are both
        # descendants of the tabindex="-1" container.
        language = ""

        identity = container.find(
            attrs={
                "data-testid": "one-copilot-code-identity"
            }
        )

        if identity is not None:
            span = identity.find("span")

            if span is not None:
                language = span.get_text(
                    strip=True
                ).lower()

        preview.replace_with(
            to_markdown(
                content,
                language,
            )
        )

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
#.removeprefix(" ")

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
