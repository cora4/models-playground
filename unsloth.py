#!/usr/bin/env python3

import argparse
import json
import re
import time
import uuid


THINKING_RE = re.compile(
    r"^\s*<thinking>\s*\n?(.*?)\n?\s*</thinking>\s*(?:\n\n|\n)?",
    re.DOTALL,
)


def uid():
    return str(uuid.uuid4())


def now_ms():
    return 0
#    return time.time_ns() // 1_000_000


def as_text(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def parse_tool_calls(value):
    """
    Normalise unsloth tool_calls into a Python list.
    """
    if not value:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            pass

    return []


def split_thinking(content):
    """
    Extract all <thinking>...</thinking> blocks from the beginning of
    an assistant message.

    Returns:
        reasoningContent: concatenation of all thinking blocks
        content: everything remaining after the thinking blocks
    """
    if not isinstance(content, str):
        return None, content

    pos = 0
    reasoning_parts = []

    while True:
        # Allow whitespace/newlines before the next thinking block.
        while pos < len(content) and content[pos].isspace():
            pos += 1

        if not content.startswith("<thinking>", pos):
            break

        start = pos + len("<thinking>")
        end = content.find("</thinking>", start)

        if end == -1:
            # Malformed/unclosed thinking block: leave the rest untouched.
            break

        reasoning_parts.append(content[start:end])

        pos = end + len("</thinking>")

    if not reasoning_parts:
        return None, content

    reasoning_content = "\n\n## TOOL_CALL\n\n".join(
        part.strip() for part in reasoning_parts
    )

    remaining = content[pos:].strip()

    return reasoning_content, remaining


def first_user_message(messages):
    return next(
        (m for m in messages if m.get("role") == "user"),
        messages[0] if messages else {},
    )


def build_messages(unsloth_messages, format_name):
    """
    Convert the unsloth flat message list into the linked message-node
    structure used by both target formats.
    """
    conv_id = uid()
    root_id = uid()

    root_timestamp = now_ms()

    root = {
        "children": [],
        "content": "",
        "convId": conv_id,
        "id": root_id,
        "parent": None,
        "role": "system",
        "timestamp": root_timestamp,
        "type": "root",
    }

    nodes = [root]
    parent_id = root_id

    for src in unsloth_messages:
        role = src.get("role")

        if role not in ("user", "assistant", "tool", "system"):
            continue

        node_id = uid()
        source_content = src.get("content", "")

        node = {
            "convId": conv_id,
            "type": "text",
            "timestamp": now_ms(),
            "role": role,
            "content": "",
            "id": node_id,
            "parent": parent_id
        }

        if role == "assistant":
            reasoning, content = split_thinking(source_content)

            node["content"] = content
            node["model"] = "gpt-5.6-luna"

            # IMPORTANT:
            # reasoningContent and content belong to THIS SAME node/ID.
            if reasoning is not None:
                node["reasoningContent"] = reasoning

            calls = parse_tool_calls(
                src.get("tool_calls", src.get("toolCalls"))
            )

            if calls:
                node["toolCalls"] = json.dumps(
                    calls,
                    ensure_ascii=False,
                    separators=(",", ":"),
                )

            for key in (
                "model",
                "completionId"
            ):
                if key in src:
                    node[key] = src[key]

        elif role == "tool":
            node["content"] = as_text(source_content)

            # Tool result is the CONTENT of the tool message.
            #
            # For --format jsonl (time):
            #   content remains the raw result, e.g.
            #   {"result":"2026-08-01T11:00:51+01:00","timezone":"UTC"}
            #
            # For --format json (facts):
            #   content remains the search-result text, e.g.
            #   Title: Unsloth (software) - Wikipedia
            #   URL: https://...
            #
            # Thus no parsing/reconstruction is needed here.
            if "tool_call_id" in src:
                node["toolCallId"] = src["tool_call_id"]
            elif "toolCallId" in src:
                node["toolCallId"] = src["toolCallId"]

        else:
            node["content"] = as_text(source_content)

        if "extra" in src:
            node["extra"] = src["extra"]

        # Parent -> child.
        nodes[-1]["children"] = [node_id]

        nodes.append(node)
        parent_id = node_id

        # Prevent identical timestamps in very fast conversions.
        time.sleep(0.001)

    return conv_id, nodes, parent_id


def convert_time(unsloth):
    source_messages = unsloth["messages"]

    if not isinstance(source_messages, list):
        raise ValueError("`messages` must be a list")

    conv_id, nodes, leaf_id = build_messages(
        source_messages,
        "time",
    )

    first_user = first_user_message(source_messages)

    metadata = {
        "type":"session",
        "harness":"llama.app",
        "currNode": leaf_id,
        "id": conv_id,
        "lastModified": nodes[-1]["timestamp"],
        "name": as_text(first_user.get("content")),
        "reasoningEffort": "low",
    }

    return [
        metadata,
        *(
            {
                "message": node,
                "type": "message",
            }
            for node in nodes
        ),
    ]


def convert_facts(unsloth):
    source_messages = unsloth["messages"]

    if not isinstance(source_messages, list):
        raise ValueError("`messages` must be a list")

    conv_id, nodes, leaf_id = build_messages(
        source_messages,
        "facts",
    )

    first_user = first_user_message(source_messages)

    conv = {
        "id": conv_id,
        "name": as_text(first_user.get("content")),
        "lastModified": nodes[-1]["timestamp"],
        "currNode": leaf_id,
        "thinkingEnabled": True,
        "mcpServerOverrides": [],
    }

    return [
        {
            "conv": conv,
            "messages": nodes,
        }
    ]


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "input",
        help="Unsloth JSON file",
    )

    parser.add_argument(
        "--format",
        required=True,
        choices=["jsonl", "json"],
        help="Output format",
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Output file. Defaults to stdout.",
    )

    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output.",
    )

    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        unsloth = json.load(f)

    if args.format == "jsonl":
        result = convert_time(unsloth)

        # JSONL
        output = "\n".join(
            json.dumps(
                obj,
                ensure_ascii=False,
                separators=(",", ":"),
                indent=2 if args.pretty else None,
            )
            for obj in result
        ) + "\n"

    if args.format == "json":
        result = convert_facts(unsloth)

        # Normal JSON array
        output = json.dumps(
            result,
            ensure_ascii=False,
            separators=(",", ":"),
            indent=2 if args.pretty else None,
        ) + "\n"

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
    else:
        print(output, end="")


if __name__ == "__main__":
    main()
