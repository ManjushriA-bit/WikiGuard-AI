import ast
import json
import re
from datetime import datetime


def clean_text(value):
    if value is None:
        return ""
    try:
        if value != value:
            return ""
    except Exception:
        pass
    return str(value).strip()


def parse_any(value):
    """Best-effort parser for Wikimedia JSON/Python-like structured fields."""
    if value is None:
        return {}
    if isinstance(value, (dict, list)):
        return value
    text = clean_text(value)
    if not text:
        return {}
    for parser in (json.loads, ast.literal_eval):
        try:
            return parser(text)
        except Exception:
            continue
    return {}


def flatten_pairs(obj, prefix=""):
    pairs = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            label = f"{prefix}.{key}" if prefix else str(key)
            if isinstance(value, (dict, list)):
                pairs.extend(flatten_pairs(value, label))
            else:
                value = clean_text(value)
                if value:
                    pairs.append((label, value))
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            pairs.extend(flatten_pairs(value, f"{prefix}[{i}]"))
    return pairs


def normalize(value):
    text = clean_text(value).lower()
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("&nbsp;", " ")
    text = re.sub(r"[‘’]", "'", text)
    text = re.sub(r"[“”]", '"', text)
    text = re.sub(r"\s+", " ", text).strip()

    for fmt in ("%d %B %Y", "%d %b %Y", "%B %d, %Y",
                "%b %d, %Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass

    aliases = {
        "usa": "united states",
        "u.s.a.": "united states",
        "u.s.": "united states",
        "uk": "united kingdom",
    }
    return aliases.get(text, text)


def same_fact(a, b):
    left, right = normalize(a), normalize(b)
    if not left or not right:
        return False
    if left == right:
        return True
    return len(left) >= 8 and len(right) >= 8 and (
        left in right or right in left
    )


def extract_date_candidates(text):
    patterns = [
        r"\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b",
        r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b",
        r"\b\d{4}-\d{2}-\d{2}\b",
    ]
    found = []
    for pattern in patterns:
        found.extend(re.findall(pattern, text, flags=re.I))
    return list(dict.fromkeys(found))


def evidence_window(text, value, window=180):
    text = clean_text(text)
    value = clean_text(value)
    if not text or not value:
        return ""

    position = text.lower().find(value.lower())

    if position < 0:
        target = normalize(value)
        for candidate in extract_date_candidates(text):
            if normalize(candidate) == target:
                position = text.lower().find(candidate.lower())
                value = candidate
                break

    if position < 0:
        return ""

    start = max(0, position - window)
    end = min(len(text), position + len(value) + window)
    return text[start:end].replace("\n", " ").strip()


def build_article_text(row):
    columns = ["abstract", "description", "sections"]
    return " ".join(clean_text(row.get(column, "")) for column in columns)


def compare_article(row, max_facts=80):
    structured = parse_any(row.get("infoboxes", ""))
    pairs = flatten_pairs(structured)
    article_text = build_article_text(row)
    results = []

    for label, structured_value in pairs[:max_facts]:
        if len(structured_value) < 2:
            continue

        evidence = evidence_window(article_text, structured_value)

        if evidence:
            results.append({
                "fact": label,
                "structured": structured_value,
                "article_value": structured_value,
                "status": "CONSISTENT",
                "evidence": evidence,
            })
            continue

        is_date_field = any(
            word in label.lower()
            for word in ["date", "born", "birth", "founded", "established"]
        )

        if is_date_field:
            for candidate in extract_date_candidates(article_text):
                if normalize(candidate) != normalize(structured_value):
                    results.append({
                        "fact": label,
                        "structured": structured_value,
                        "article_value": candidate,
                        "status": "POSSIBLE MISMATCH",
                        "evidence": evidence_window(article_text, candidate),
                    })
                    break

    return results


def summarize_results(results):
    summary = {
        "facts_analyzed": len(results),
        "consistent": sum(r["status"] == "CONSISTENT" for r in results),
        "possible_mismatch": sum(
            r["status"] == "POSSIBLE MISMATCH" for r in results
        ),
        "not_found": 0,
    }
    return summary
