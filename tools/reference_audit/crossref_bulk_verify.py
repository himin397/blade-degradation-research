#!/usr/bin/env python3
"""Bulk verify all reference DOIs in Paper 1/2/3 against Crossref API.

Each entry contains the DOI and the manuscript-recorded fields. The script
fetches Crossref metadata, extracts canonical fields, and prints a comparison.
"""

import json
import subprocess
import sys
import time
from typing import Dict, List, Optional, Tuple

# Manuscript-recorded references (DOI + ground truth fields)
# Sources: paper1 §9 References, paper2 § References, paper3 § References

REFERENCES: List[Dict] = [
    # Paper 1
    {"paper": "P1", "ref": "1",  "doi": "10.3390/en12040676",
     "first_author": "Shihavuddin", "year": 2019, "container": "Energies",
     "volume": "12", "issue": "4", "page": "676",
     "title_keywords": ["wind turbine", "surface damage", "drone"]},
    {"paper": "P1", "ref": "2",  "doi": "10.3390/machines11100953",
     "first_author": "Gohar", "year": 2023, "container": "Machines",
     "volume": "11", "issue": "10", "page": "953",
     "title_keywords": ["slice-aided", "wind turbine"]},
    {"paper": "P1", "ref": "3",  "doi": "10.5194/wes-10-227-2025",
     "first_author": "Malik", "year": 2025, "container": "Wind Energy Science",
     "volume": "10", "page": "227",
     "title_keywords": ["wind turbine power loss", "blade erosion"]},
    {"paper": "P1", "ref": "7",  "doi": "10.3390/machines10050327",
     "first_author": "Konovalenko", "year": 2022, "container": "Machines",
     "volume": "10", "issue": "5", "page": "327",
     "title_keywords": ["U-Net", "metal surface"]},
    {"paper": "P1", "ref": "8",  "doi": "10.1016/j.solener.2019.02.067",
     "first_author": "Deitsch", "year": 2019, "container": "Solar Energy",
     "volume": "185", "page": "455",
     "title_keywords": ["photovoltaic", "electroluminescence"]},
    {"paper": "P1", "ref": "9",  "doi": "10.1111/mice.12263",
     "first_author": "Cha", "year": 2017, "container": "Computer-Aided Civil and Infrastructure Engineering",
     "volume": "32", "issue": "5", "page": "361",
     "title_keywords": ["crack damage", "convolutional neural"]},
    {"paper": "P1", "ref": "10", "doi": "10.1109/ACCESS.2024.3371493",
     "first_author": "Memari", "year": 2024, "container": "IEEE Access",
     "title_keywords": ["wind turbine blade inspection", "drone"]},
    {"paper": "P1", "ref": "11", "doi": "10.1109/ACCESS.2025.3569799",
     "first_author": "Masita", "year": 2025, "container": "IEEE Access",
     "title_keywords": ["deep learning", "blade", "review"]},
    {"paper": "P1", "ref": "12", "doi": "10.1038/s41598-025-03639-8",
     "first_author": "Zhao", "year": 2025, "container": "Scientific Reports",
     "volume": "15", "page": "18667",
     "title_keywords": ["YOLO-Wind", "blade"]},
    {"paper": "P1", "ref": "13", "doi": "10.3390/app16031333",
     "first_author": "Shi", "year": 2026, "container": "Applied Sciences",
     "title_keywords": ["DMR-YOLO", "blade"]},
    {"paper": "P1", "ref": "14", "doi": "10.3390/app14198763",
     "first_author": "Zou", "year": 2024, "container": "Applied Sciences",
     "volume": "14", "issue": "19", "page": "8763",
     "title_keywords": ["DCW-YOLO", "blade"]},
    {"paper": "P1", "ref": "15", "doi": "10.1038/s41598-025-89864-7",
     "first_author": "Zou", "year": 2025, "container": "Scientific Reports",
     "volume": "15", "page": "5833",
     "title_keywords": ["AUD-YOLO", "blade"]},
    {"paper": "P1", "ref": "16", "doi": "10.1109/ICIP46576.2022.9897990",
     "first_author": "Akyon", "year": 2022, "container": "ICIP",
     "title_keywords": ["slicing aided", "small object"]},

    # Paper 2 (DOIs explicit in citation)
    {"paper": "P2", "ref": "8",  "doi": "10.5194/wes-10-227-2025",  # dup of P1-3
     "first_author": "Malik", "year": 2025, "container": "Wind Energy Science",
     "title_keywords": ["wind turbine power loss"]},
    {"paper": "P2", "ref": "11", "doi": "10.11581/DTU:00000033",
     "first_author": "Colone", "year": 2018, "container": "Technical University of Denmark",
     "title_keywords": ["wind farm", "structural reliability", "predictive maintenance"]},
    {"paper": "P2", "ref": "16", "doi": "10.1016/j.egypro.2017.10.333",
     "first_author": "Robertson", "year": 2017, "container": "Energy Procedia",
     "volume": "137", "page": "38",
     "title_keywords": ["OC5", "DeepCwind"]},
    {"paper": "P2", "ref": "18", "doi": "10.2172/578635",
     "first_author": "Mandell", "year": 1997, "container": "Sandia",
     "title_keywords": ["composite", "fatigue"]},
    {"paper": "P2", "ref": "20", "doi": "10.1016/j.renene.2017.01.065",
     "first_author": "Vera-Tudela", "year": 2017, "container": "Renewable Energy",
     "volume": "107", "page": "352",
     "title_keywords": ["fatigue load prediction", "wind farm"]},

    # Paper 2 (DOIs not in citation but verified earlier)
    {"paper": "P2", "ref": "4",  "doi": "10.1049/iet-rpg.2016.0248",
     "first_author": "Tautz-Weinert", "year": 2017, "container": "IET Renewable Power Generation",
     "volume": "11", "issue": "4", "page": "382",
     "title_keywords": ["SCADA", "wind turbine condition monitoring", "review"]},
    {"paper": "P2", "ref": "9",  "doi": "10.5194/wes-7-53-2022",
     "first_author": "Abbas", "year": 2022, "container": "Wind Energy Science",
     "volume": "7", "issue": "1", "page": "53",
     "title_keywords": ["reference open-source controller", "floating offshore"]},
    {"paper": "P2", "ref": "12", "doi": "10.1002/we.1797",
     "first_author": "Dimitrov", "year": 2015, "container": "Wind Energy",
     "volume": "18", "issue": "11", "page": "1917",
     "title_keywords": ["wind shear", "turbulence"]},
    {"paper": "P2", "ref": "21", "doi": "10.1016/j.renene.2017.02.069",
     "first_author": "Herp", "year": 2018, "container": "Renewable Energy",
     "volume": "116", "page": "164",
     "title_keywords": ["bayesian", "bearing failure"]},

    # Paper 3 (DOIs unique to Paper 3)
    {"paper": "P3", "ref": "9",  "doi": "10.1177/0309524X221124031",
     "first_author": "Pandit", "year": 2023, "container": "Wind Engineering",
     "volume": "47", "issue": "2", "page": "422",
     "title_keywords": ["SCADA", "data-driven", "review"]},
    {"paper": "P3", "ref": "10", "doi": "10.3390/en7042595",
     "first_author": "Tchakoua", "year": 2014, "container": "Energies",
     "volume": "7", "issue": "4", "page": "2595",
     "title_keywords": ["wind turbine", "condition monitoring", "review"]},
    {"paper": "P3", "ref": "12", "doi": "10.1016/j.renene.2020.07.145",
     "first_author": "García Márquez", "year": 2020, "container": "Renewable Energy",
     "volume": "161", "page": "998",
     "title_keywords": ["non-destructive testing", "blade"]},
    {"paper": "P3", "ref": "13", "doi": "10.1016/j.renene.2018.10.047",
     "first_author": "Stetco", "year": 2019, "container": "Renewable Energy",
     "volume": "133", "page": "620",
     "title_keywords": ["machine learning", "condition monitoring"]},
    {"paper": "P3", "ref": "14", "doi": "10.1016/j.renene.2017.06.089",
     "first_author": "Dao", "year": 2018, "container": "Renewable Energy",
     "volume": "116", "page": "107",
     "title_keywords": ["cointegration", "SCADA"]},
    {"paper": "P3", "ref": "15", "doi": "10.1016/j.engappai.2024.109970",
     "first_author": "Gohar", "year": 2025, "container": "Engineering Applications of Artificial Intelligence",
     "volume": "144", "page": "109970",
     "title_keywords": ["surface defect detection", "aerial"]},
    {"paper": "P3", "ref": "16", "doi": "10.1016/j.aei.2023.102292",
     "first_author": "Liu", "year": 2024, "container": "Advanced Engineering Informatics",
     "volume": "59", "page": "102292",
     "title_keywords": ["defect detection", "attention"]},
    {"paper": "P3", "ref": "17", "doi": "10.1016/j.renene.2012.11.030",
     "first_author": "Yang", "year": 2013, "container": "Renewable Energy",
     "volume": "53", "page": "365",
     "title_keywords": ["SCADA data analysis", "condition monitoring"]},
    {"paper": "P3", "ref": "18", "doi": "10.1016/j.egyr.2024.06.041",
     "first_author": "Castellani", "year": 2024, "container": "Energy Reports",
     "volume": "12", "page": "750",
     "title_keywords": ["gearbox", "vibration"]},
    {"paper": "P3", "ref": "19", "doi": "10.3390/en13123132",
     "first_author": "Maldonado-Correa", "year": 2020, "container": "Energies",
     "volume": "13", "issue": "12", "page": "3132",
     "title_keywords": ["SCADA", "condition monitoring", "literature review"]},
    {"paper": "P3", "ref": "20", "doi": "10.1186/s42162-024-00373-9",
     "first_author": "Kandemir", "year": 2024, "container": "Energy Informatics",
     "volume": "7", "page": "68",
     "title_keywords": ["digital twin", "wind energy"]},
    {"paper": "P3", "ref": "21", "doi": "10.1088/1742-6596/1618/2/022030",
     "first_author": "Branlard", "year": 2020, "container": "Journal of Physics",
     "volume": "1618", "page": "022030",
     "title_keywords": ["digital twin", "OpenFAST", "fatigue"]},
    {"paper": "P3", "ref": "22", "doi": "10.1016/j.renene.2024.122332",
     "first_author": "Hu", "year": 2025, "container": "Renewable Energy",
     "volume": "241", "page": "122332",
     "title_keywords": ["digital twin", "drone"]},
    {"paper": "P3", "ref": "23", "doi": "10.1016/j.ress.2010.07.007",
     "first_author": "Nielsen", "year": 2011, "container": "Reliability Engineering",
     "volume": "96", "issue": "1", "page": "218",
     "title_keywords": ["risk-based", "operation", "offshore"]},
    {"paper": "P3", "ref": "24", "doi": "10.1016/j.egypro.2017.10.349",
     "first_author": "Florian", "year": 2017, "container": "Energy Procedia",
     "volume": "137", "page": "261",
     "title_keywords": ["risk-based planning", "offshore"]},
    {"paper": "P3", "ref": "25", "doi": "10.1016/j.ress.2020.107062",
     "first_author": "Yeter", "year": 2020, "container": "Reliability Engineering",
     "volume": "202", "page": "107062",
     "title_keywords": ["risk-based maintenance", "offshore"]},
]


USER_AGENT = "BladeResearchAudit/1.0 (mailto:research@example.com)"


def fetch_crossref(doi: str, max_retries: int = 4) -> Optional[Dict]:
    url = f"https://api.crossref.org/works/{doi}"
    backoff = 2.0
    last_error = "unknown"
    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                [
                    "curl", "-fsSL", "--max-time", "20",
                    "-H", f"User-Agent: {USER_AGENT}",
                    "-H", "Accept: application/json",
                    url,
                ],
                capture_output=True,
                timeout=25,
            )
        except subprocess.TimeoutExpired:
            last_error = "curl timeout"
            time.sleep(backoff)
            backoff *= 2
            continue
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout.decode("utf-8"))
            except json.JSONDecodeError as e:
                return {"_error": f"json decode error: {e}"}
            return data.get("message")
        stderr = result.stderr.decode("utf-8", errors="replace").strip()
        last_error = f"curl rc={result.returncode}: {stderr[:200]}"
        # Retry on rate limit (HTTP 429) or transient failures
        if "429" in stderr or "503" in stderr or result.returncode in (28, 56):
            time.sleep(backoff)
            backoff *= 2
            continue
        return {"_error": last_error}
    return {"_error": f"max retries exhausted: {last_error}"}


def normalize(s: Optional[str]) -> str:
    if s is None:
        return ""
    return "".join(ch for ch in s.lower() if ch.isalnum() or ch.isspace()).strip()


def get_first_author_family(msg: Dict) -> str:
    authors = msg.get("author") or []
    if not authors:
        return ""
    return authors[0].get("family") or ""


def get_year(msg: Dict) -> Optional[int]:
    for key in ("published-print", "published-online", "issued", "created"):
        date = msg.get(key) or {}
        parts = date.get("date-parts") or []
        if parts and parts[0]:
            return parts[0][0]
    return None


def compare_entry(entry: Dict, msg: Optional[Dict]) -> Tuple[str, List[str]]:
    if msg is None or msg.get("_error"):
        err = msg.get("_error") if msg else "no response"
        return "ERROR", [f"crossref fetch failed: {err}"]

    issues: List[str] = []

    # First author
    expected_au = normalize(entry.get("first_author"))
    actual_au = normalize(get_first_author_family(msg))
    if expected_au and expected_au not in actual_au and actual_au not in expected_au:
        issues.append(f"author MISMATCH: manuscript='{entry['first_author']}' crossref='{get_first_author_family(msg)}'")

    # Year
    expected_year = entry.get("year")
    actual_year = get_year(msg)
    if expected_year is not None and actual_year is not None and expected_year != actual_year:
        # Allow off-by-one for online-vs-print scenarios
        if abs(expected_year - actual_year) > 1:
            issues.append(f"year MISMATCH: manuscript={expected_year} crossref={actual_year}")
        else:
            issues.append(f"year ±1y: manuscript={expected_year} crossref={actual_year}")

    # Container
    expected_container = normalize(entry.get("container", ""))
    container_titles = msg.get("container-title") or []
    actual_container = normalize(container_titles[0] if container_titles else "")
    if expected_container and expected_container not in actual_container and actual_container not in expected_container:
        issues.append(f"container MISMATCH: manuscript='{entry.get('container')}' crossref='{container_titles[0] if container_titles else None}'")

    # Volume
    if entry.get("volume"):
        actual_volume = msg.get("volume") or ""
        if entry["volume"] != actual_volume:
            issues.append(f"volume MISMATCH: manuscript={entry['volume']} crossref={actual_volume}")

    # Issue
    if entry.get("issue"):
        actual_issue = msg.get("issue") or ""
        if entry["issue"] != actual_issue:
            issues.append(f"issue MISMATCH: manuscript={entry['issue']} crossref={actual_issue}")

    # Page (only check first page)
    if entry.get("page"):
        actual_page = msg.get("page") or ""
        # Crossref returns "352-360" or just "676" or "022030"
        first_page = actual_page.split("-")[0].strip()
        if entry["page"].lstrip("0") != first_page.lstrip("0"):
            issues.append(f"page MISMATCH: manuscript={entry['page']} crossref={actual_page}")

    # Title keywords
    title_list = msg.get("title") or []
    actual_title_norm = normalize(title_list[0] if title_list else "")
    missing_keywords = []
    for kw in entry.get("title_keywords", []) or []:
        if normalize(kw) not in actual_title_norm:
            missing_keywords.append(kw)
    if missing_keywords:
        issues.append(f"title keywords missing: {missing_keywords} actual='{title_list[0] if title_list else None}'")

    if issues:
        return "ISSUE", issues
    return "OK", []


def main() -> int:
    results = []
    print(f"Verifying {len(REFERENCES)} references against Crossref API...\n")
    for i, entry in enumerate(REFERENCES):
        msg = fetch_crossref(entry["doi"])
        status, issues = compare_entry(entry, msg)
        results.append((entry, status, issues, msg))
        marker = "✅" if status == "OK" else ("⚠️" if status == "ISSUE" else "❌")
        print(f"{marker} [{entry['paper']}-{entry['ref']}] {entry['doi']} ({entry['first_author']} {entry['year']}) — {status}")
        for line in issues:
            print(f"     {line}")
        time.sleep(0.6)  # be polite to Crossref API (avoid 429)

    # Summary
    total = len(results)
    ok = sum(1 for _, s, _, _ in results if s == "OK")
    issue = sum(1 for _, s, _, _ in results if s == "ISSUE")
    err = sum(1 for _, s, _, _ in results if s == "ERROR")
    print()
    print(f"=== Summary === total={total}  OK={ok}  ISSUE={issue}  ERROR={err}")
    if issue or err:
        print("\nNon-OK entries:")
        for entry, status, issues, _ in results:
            if status != "OK":
                print(f"  [{status}] {entry['paper']}-{entry['ref']} {entry['doi']} {entry['first_author']} {entry['year']}")
                for line in issues:
                    print(f"      - {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
