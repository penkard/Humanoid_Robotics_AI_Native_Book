"""Markdown-aware text chunker for RAG ingestion."""

import os
import re

# Part directory name to metadata mapping
PART_METADATA = {
    "Part-1-introduction": ("Introduction to Physical AI", 1),
    "Part-2-humanoid-robotics": ("Basics of Humanoid Robotics", 2),
    "Part-3-ros2": ("ROS 2 Fundamentals", 3),
    "Part-4-digital-twin": ("Digital Twin Simulation", 4),
    "Part-5-vla": ("Vision-Language-Action Systems", 5),
    "Part-6-capstone": ("Capstone", 6),
}

MAX_CHUNK_SIZE = 1000


def _extract_part_info(filepath: str) -> tuple[str, int]:
    """Extract part name and number from the file path."""
    for dir_name, (part_name, part_number) in PART_METADATA.items():
        if dir_name in filepath:
            return part_name, part_number
    return "Unknown", 0


def _extract_chapter_title(content: str) -> str:
    """Extract the chapter title from the first H1 heading or frontmatter."""
    # Try frontmatter title
    fm_match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
    if fm_match:
        return fm_match.group(1)
    # Try first H1
    h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if h1_match:
        return h1_match.group(1)
    return os.path.basename(filepath)


def _strip_frontmatter(content: str) -> str:
    """Remove YAML frontmatter from markdown content."""
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            return content[end + 3 :].strip()
    return content


def _split_long_chunk(text: str, max_size: int = MAX_CHUNK_SIZE) -> list[str]:
    """Split text that exceeds max_size into smaller pieces."""
    if len(text) <= max_size:
        return [text]

    chunks = []
    while text:
        if len(text) <= max_size:
            chunks.append(text)
            break
        # Find a good break point (paragraph, sentence, or space)
        break_at = text.rfind("\n\n", 0, max_size)
        if break_at == -1:
            break_at = text.rfind(". ", 0, max_size)
        if break_at == -1:
            break_at = text.rfind(" ", 0, max_size)
        if break_at == -1:
            break_at = max_size
        else:
            break_at += 1
        chunks.append(text[:break_at].strip())
        text = text[break_at:].strip()
    return chunks


def chunk_markdown(filepath: str) -> list[dict]:
    """Split a Markdown file into semantic chunks based on headings.

    Args:
        filepath: Path to the Markdown file.

    Returns:
        List of dicts with keys: text, source, part, part_number,
        chapter, section, chunk_index.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    part_name, part_number = _extract_part_info(filepath)
    chapter_title = _extract_chapter_title(content)
    body = _strip_frontmatter(content)

    # Split on H2 (##) and H3 (###) headings
    # Pattern captures the heading and its content
    sections: list[tuple[str, str]] = []
    pattern = re.compile(r"^(#{2,3})\s+(.+)$", re.MULTILINE)
    matches = list(pattern.finditer(body))

    if not matches:
        # No headings — treat entire body as one section
        sections.append(("Introduction", body.strip()))
    else:
        # Content before the first heading
        pre_content = body[: matches[0].start()].strip()
        if pre_content:
            sections.append(("Introduction", pre_content))

        for i, match in enumerate(matches):
            heading = match.group(2).strip()
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
            section_text = body[start:end].strip()
            if section_text:
                sections.append((heading, section_text))

    # Convert file path to relative source
    # Normalize to forward slashes and extract docs/... portion
    normalized = filepath.replace("\\", "/")
    docs_idx = normalized.find("docs/")
    source = normalized[docs_idx:] if docs_idx != -1 else os.path.basename(filepath)

    chunks = []
    for section_heading, section_text in sections:
        sub_chunks = _split_long_chunk(section_text)
        for idx, chunk_text in enumerate(sub_chunks):
            chunks.append(
                {
                    "text": chunk_text,
                    "source": source,
                    "part": part_name,
                    "part_number": part_number,
                    "chapter": chapter_title,
                    "section": section_heading,
                    "chunk_index": idx,
                }
            )

    return chunks
