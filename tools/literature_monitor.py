#!/usr/bin/env python3
"""
literature_monitor.py
Wind turbine blade degradation research - new literature monitor

Uses OpenAlex API (free, no key required) to check for new papers
matching predefined search queries. Deduplicates against known references
and generates a Markdown report.

Usage:
    python3 literature_monitor.py              # check last 30 days
    python3 literature_monitor.py --days 90    # check last 90 days
    python3 literature_monitor.py --dry-run    # preview queries without saving
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote

import requests

# --- Configuration ---

TOOLS_DIR = Path(__file__).parent
KNOWN_REFS_PATH = TOOLS_DIR / "known_references.json"
REPORTS_DIR = TOOLS_DIR / "literature_reports"
STATE_PATH = TOOLS_DIR / "monitor_state.json"

# OpenAlex API (free, polite pool with email)
OPENALEX_BASE = "https://api.openalex.org/works"
MAILTO = "runa.kosei@gmail.com"  # for polite pool (faster rate limit)

# Search query groups - each targets a specific research domain
SEARCH_QUERIES = [
    {
        "name": "Blade damage detection (YOLO/deep learning)",
        "query": "wind turbine blade damage detection YOLO",
        "relevance": "Paper 1 - new detection architectures",
    },
    {
        "name": "Blade erosion detection",
        "query": "wind turbine blade erosion detection deep learning",
        "relevance": "Paper 1 - erosion-specific methods",
    },
    {
        "name": "Drone inspection wind turbine",
        "query": "drone inspection wind turbine blade automated",
        "relevance": "Paper 1 - inspection methodology",
    },
    {
        "name": "SCADA condition monitoring",
        "query": "SCADA condition monitoring wind turbine",
        "relevance": "Paper 2 - SCADA-based approaches",
    },
    {
        "name": "Fatigue load estimation wind",
        "query": "fatigue load estimation wind turbine SCADA",
        "relevance": "Paper 2 - DEL/fatigue methods",
    },
    {
        "name": "Digital twin wind turbine",
        "query": "digital twin wind turbine blade 3D",
        "relevance": "Paper 3 - integration & digital twin",
    },
    {
        "name": "Blade degradation prediction",
        "query": "wind turbine blade degradation prediction model",
        "relevance": "Paper 3 - core research direction",
    },
    {
        "name": "Public blade dataset",
        "query": "wind turbine blade dataset public open access",
        "relevance": "All papers - new data sources",
    },
    {
        "name": "Small object detection SAHI",
        "query": "small object detection slicing inference wind",
        "relevance": "Paper 1 - SAHI methodology updates",
    },
    {
        "name": "O&M optimization wind turbine",
        "query": "operation maintenance optimization wind turbine predictive",
        "relevance": "Paper 3 - O&M decision support",
    },
]

# Maximum results per query
MAX_PER_QUERY = 25

# Relevance filter: at least one of these must appear in title or abstract
# to be included in the report (case-insensitive)
RELEVANCE_KEYWORDS = [
    "wind turbine",
    "wind energy",
    "blade erosion",
    "blade damage",
    "blade defect",
    "blade inspection",
    "blade degradation",
    "leading edge",
    "rotor blade",
    "SCADA",
    "fatigue load",
    "wind farm",
    "OpenFAST",
]

# Exclude patterns: papers matching these are filtered out
EXCLUDE_PATTERNS = [
    "reply on rc",
    "comment on",
    "author response",
    "corrigendum",
    "erratum",
]


def load_known_references():
    """Load the list of already-known paper DOIs and titles."""
    if not KNOWN_REFS_PATH.exists():
        print(f"Warning: {KNOWN_REFS_PATH} not found. No dedup will be performed.")
        return set(), set()

    with open(KNOWN_REFS_PATH, "r", encoding="utf-8") as f:
        refs = json.load(f)

    known_dois = set()
    known_titles = set()
    for ref in refs:
        if ref.get("doi"):
            # Normalize DOI to lowercase
            known_dois.add(ref["doi"].lower().strip())
        if ref.get("title"):
            known_titles.add(ref["title"].lower().strip())

    return known_dois, known_titles


def load_state():
    """Load the last-run state."""
    if STATE_PATH.exists():
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(state):
    """Save the current run state."""
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def query_openalex(search_text, from_date, to_date):
    """
    Query OpenAlex API for works matching the search text.
    Returns a list of work objects.
    """
    params = {
        "search": search_text,
        "filter": f"from_publication_date:{from_date},to_publication_date:{to_date}",
        "sort": "relevance_score:desc",
        "per_page": MAX_PER_QUERY,
        "mailto": MAILTO,
    }

    try:
        resp = requests.get(OPENALEX_BASE, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("results", [])
    except requests.RequestException as e:
        print(f"  API error: {e}")
        return []


def extract_paper_info(work):
    """Extract relevant fields from an OpenAlex work object."""
    # Get DOI
    doi = work.get("doi", "") or ""
    if doi.startswith("https://doi.org/"):
        doi = doi[len("https://doi.org/"):]

    # Get authors
    authorships = work.get("authorships", [])
    authors = []
    for a in authorships[:5]:  # first 5 authors
        author = a.get("author", {})
        name = author.get("display_name", "Unknown")
        authors.append(name)
    if len(authorships) > 5:
        authors.append("et al.")

    # Get year
    year = work.get("publication_year")

    # Get title
    title = work.get("title", "No title")

    # Get source (journal/conference)
    source = ""
    primary_location = work.get("primary_location", {}) or {}
    source_obj = primary_location.get("source", {}) or {}
    source = source_obj.get("display_name", "")

    # Get cited_by_count
    cited_by = work.get("cited_by_count", 0)

    # Get open access status
    oa = work.get("open_access", {}) or {}
    is_oa = oa.get("is_oa", False)
    oa_url = oa.get("oa_url", "")

    # Get abstract (inverted index -> reconstructed)
    abstract = reconstruct_abstract(work.get("abstract_inverted_index"))

    return {
        "title": title,
        "authors": authors,
        "year": year,
        "doi": doi,
        "source": source,
        "cited_by_count": cited_by,
        "is_open_access": is_oa,
        "oa_url": oa_url,
        "abstract_snippet": abstract[:300] + "..." if len(abstract) > 300 else abstract,
        "openalex_id": work.get("id", ""),
    }


def reconstruct_abstract(inverted_index):
    """Reconstruct abstract text from OpenAlex inverted index format."""
    if not inverted_index:
        return ""
    word_positions = []
    for word, positions in inverted_index.items():
        for pos in positions:
            word_positions.append((pos, word))
    word_positions.sort(key=lambda x: x[0])
    return " ".join(w for _, w in word_positions)


def is_duplicate(paper, known_dois, known_titles, seen_dois):
    """Check if paper is already known or seen in this run."""
    doi = paper["doi"].lower().strip() if paper["doi"] else ""
    title = paper["title"].lower().strip() if paper["title"] else ""

    # Check DOI match
    if doi and (doi in known_dois or doi in seen_dois):
        return True

    # Check title similarity (exact match after lowering)
    if title and title in known_titles:
        return True

    return False


def is_relevant(paper):
    """Check if paper passes the relevance filter."""
    title = (paper.get("title") or "").lower()
    abstract = (paper.get("abstract_snippet") or "").lower()
    text = title + " " + abstract

    # Exclude editorial/review responses
    for pattern in EXCLUDE_PATTERNS:
        if pattern in title:
            return False

    # Require at least one relevance keyword
    for kw in RELEVANCE_KEYWORDS:
        if kw.lower() in text:
            return True

    return False


def generate_report(new_papers_by_query, from_date, to_date, run_time):
    """Generate a Markdown report of new papers found."""
    total_new = sum(len(papers) for papers in new_papers_by_query.values())

    lines = []
    lines.append(f"# Literature Monitor Report")
    lines.append(f"")
    lines.append(f"- **Run date**: {run_time}")
    lines.append(f"- **Search period**: {from_date} to {to_date}")
    lines.append(f"- **New papers found**: {total_new}")
    lines.append(f"- **Queries executed**: {len(SEARCH_QUERIES)}")
    lines.append(f"")

    if total_new == 0:
        lines.append("No new papers found in this period.")
        lines.append("")
        return "\n".join(lines)

    lines.append("---")
    lines.append("")

    for query_info in SEARCH_QUERIES:
        name = query_info["name"]
        relevance = query_info["relevance"]
        papers = new_papers_by_query.get(name, [])

        if not papers:
            continue

        lines.append(f"## {name}")
        lines.append(f"*Relevance: {relevance}*")
        lines.append(f"")

        for i, p in enumerate(papers, 1):
            authors_str = ", ".join(p["authors"])
            lines.append(f"### {i}. {p['title']}")
            lines.append(f"")
            lines.append(f"- **Authors**: {authors_str}")
            lines.append(f"- **Year**: {p['year']}")
            if p["doi"]:
                lines.append(f"- **DOI**: [{p['doi']}](https://doi.org/{p['doi']})")
            lines.append(f"- **Source**: {p['source']}")
            lines.append(f"- **Cited by**: {p['cited_by_count']}")
            if p["is_open_access"] and p["oa_url"]:
                lines.append(f"- **Open Access**: [Link]({p['oa_url']})")
            if p["abstract_snippet"]:
                lines.append(f"- **Abstract**: {p['abstract_snippet']}")
            lines.append(f"")

    lines.append("---")
    lines.append(f"*Generated by literature_monitor.py*")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Check for new literature in blade degradation research"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days to look back (default: 30)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview queries without saving report",
    )
    args = parser.parse_args()

    run_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    to_date = datetime.now().strftime("%Y-%m-%d")
    from_date = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")

    print(f"=== Literature Monitor ===")
    print(f"Search period: {from_date} to {to_date}")
    print(f"")

    # Load known references for dedup
    known_dois, known_titles = load_known_references()
    print(f"Known references loaded: {len(known_dois)} DOIs, {len(known_titles)} titles")
    print()

    # Track DOIs seen across all queries in this run
    seen_dois = set()
    new_papers_by_query = {}
    total_api_results = 0
    total_new = 0

    for qi, query_info in enumerate(SEARCH_QUERIES, 1):
        name = query_info["name"]
        query = query_info["query"]
        print(f"[{qi}/{len(SEARCH_QUERIES)}] {name}")
        print(f"  Query: {query}")

        works = query_openalex(query, from_date, to_date)
        total_api_results += len(works)
        print(f"  API results: {len(works)}")

        new_papers = []
        filtered_out = 0
        for w in works:
            paper = extract_paper_info(w)
            if is_duplicate(paper, known_dois, known_titles, seen_dois):
                continue
            if not is_relevant(paper):
                filtered_out += 1
                continue
            new_papers.append(paper)
            if paper["doi"]:
                seen_dois.add(paper["doi"].lower().strip())

        new_papers_by_query[name] = new_papers
        total_new += len(new_papers)
        print(f"  New (relevant, not known): {len(new_papers)} (filtered out: {filtered_out})")
        print()

        # Be polite to the API
        if qi < len(SEARCH_QUERIES):
            time.sleep(0.5)

    print(f"=== Summary ===")
    print(f"Total API results: {total_api_results}")
    print(f"Total new papers: {total_new}")
    print()

    if args.dry_run:
        print("[DRY RUN] Skipping report save.")
        if total_new > 0:
            print("\nPreview of new papers:")
            for name, papers in new_papers_by_query.items():
                for p in papers:
                    print(f"  - [{p['year']}] {p['title'][:80]}")
        return

    # Generate and save report
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report = generate_report(new_papers_by_query, from_date, to_date, run_time)

    report_filename = f"{datetime.now().strftime('%Y-%m')}.md"
    report_path = REPORTS_DIR / report_filename

    # If report already exists this month, append
    if report_path.exists():
        with open(report_path, "r", encoding="utf-8") as f:
            existing = f.read()
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(existing)
            f.write("\n\n" + "=" * 60 + "\n\n")
            f.write(report)
        print(f"Report appended to: {report_path}")
    else:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Report saved to: {report_path}")

    # Update state
    state = load_state()
    state["last_run"] = run_time
    state["last_from_date"] = from_date
    state["last_to_date"] = to_date
    state["last_new_count"] = total_new
    save_state(state)
    print(f"State updated: {STATE_PATH}")


if __name__ == "__main__":
    main()
