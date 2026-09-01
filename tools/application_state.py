#!/usr/bin/env python3
"""Safely create or update the private record for one job application.

This helper is intentionally stdlib-only.  It gives the apply workflow a
single idempotent operation for the otherwise easy-to-diverge tracker and
archive writes.  It only writes paths rooted in this checkout's ignored
``job_search_tracker.csv`` and ``documents/applications/`` locations.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parent.parent
TRACKER_FIELDS = [
    "date",
    "company",
    "sector",
    "role",
    "role_type",
    "channel",
    "status",
    "contact_person",
    "fit_rating",
    "notes",
    "cv_file",
    "cover_letter_file",
    "source",
    "location",
    "deadline",
    "archive_dir",
]


def canonical_url(value: str) -> str:
    """Normalize a public posting URL without changing its resource identity."""
    value = value.strip()
    if not value:
        return ""
    parts = urlsplit(value)
    query = [
        (key, item)
        for key, item in parse_qsl(parts.query, keep_blank_values=True)
        if not key.lower().startswith("utm_")
    ]
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), urlencode(sorted(query)), ""))


def normalized_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().casefold()


def safe_component(company: str, role: str) -> str:
    raw = f"{company}_{role}".casefold()
    component = re.sub(r"[^a-z0-9]+", "_", raw).strip("_")
    if not component:
        raise ValueError("company and role must contain at least one letter or number")
    return component


def archive_path(root: Path, company: str, role: str) -> Path:
    base = (root / "documents" / "applications").resolve()
    target = (base / safe_component(company, role)).resolve()
    if target.parent != base:
        raise ValueError("application archive path escaped the applications directory")
    return target


def read_tracker(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        return TRACKER_FIELDS.copy(), []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        if not headers:
            return TRACKER_FIELDS.copy(), []
        for field in TRACKER_FIELDS:
            if field not in headers:
                headers.append(field)
        return headers, [{field: row.get(field, "") for field in headers} for row in reader]


def write_tracker(path: Path, headers: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


@dataclass(frozen=True)
class ApplicationInput:
    company: str
    role: str
    location: str = ""
    source: str = ""
    deadline: str = ""
    sector: str = ""
    role_type: str = ""
    channel: str = ""
    fit_rating: str = ""
    status: str = ""
    cv_file: str = ""
    cover_letter_file: str = ""
    posting_text: str | None = None


def ensure_application(root: Path, item: ApplicationInput) -> dict[str, str | bool]:
    """Create/update exactly one private tracker row and its archive folder."""
    company = item.company.strip()
    role = item.role.strip()
    if not company or not role:
        raise ValueError("company and role are required")
    tracker = root / "job_search_tracker.csv"
    headers, rows = read_tracker(tracker)
    source = canonical_url(item.source)
    company_key, role_key = normalized_text(company), normalized_text(role)

    matches = [
        index
        for index, row in enumerate(rows)
        if (source and canonical_url(row.get("source", "")) == source)
        or (
            normalized_text(row.get("company", "")) == company_key
            and normalized_text(row.get("role", "")) == role_key
        )
    ]
    if len(matches) > 1:
        raise ValueError("tracker has duplicate rows for this canonical application; resolve them before continuing")

    archive = archive_path(root, company, role)
    archive.mkdir(parents=True, exist_ok=True)
    def artifact(value: str, directory: str) -> str:
        if not value:
            return ""
        candidate = (root / value).resolve()
        allowed = (root / directory).resolve()
        if candidate.parent != allowed:
            raise ValueError(f"{directory} artifact path escaped its intended output directory")
        return str(candidate.relative_to(root)).replace("\\", "/")

    record = {
        "date": date.today().isoformat(),
        "company": company,
        "sector": item.sector.strip(),
        "role": role,
        "role_type": item.role_type.strip(),
        "channel": item.channel.strip(),
        "status": item.status.strip() or "approved",
        "contact_person": "",
        "fit_rating": item.fit_rating.strip(),
        "notes": "",
        "cv_file": artifact(item.cv_file, "cv"),
        "cover_letter_file": artifact(item.cover_letter_file, "cover_letters"),
        "source": source,
        "location": item.location.strip(),
        "deadline": item.deadline.strip(),
        "archive_dir": str(archive.relative_to(root)).replace("\\", "/"),
    }
    created = not matches
    if matches:
        row = rows[matches[0]]
        for field, value in record.items():
            if value and not row.get(field, ""):
                row[field] = value
        if source:
            row["source"] = source
        if item.deadline.strip():
            row["deadline"] = item.deadline.strip()
        if item.status.strip():
            row["status"] = item.status.strip()
    else:
        rows.append(record)
    write_tracker(tracker, headers, rows)

    posting = archive / "job_posting.md"
    if item.posting_text is not None and not posting.exists():
        posting.write_text(item.posting_text.rstrip() + "\n", encoding="utf-8")
    return {
        "created": created,
        "tracker": str(tracker.relative_to(root)).replace("\\", "/"),
        "archive": str(archive.relative_to(root)).replace("\\", "/"),
        "posting_archived": posting.exists(),
        "deadline": item.deadline.strip(),
        "source": source,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create or update one private application record.")
    parser.add_argument("--company", required=True)
    parser.add_argument("--role", required=True)
    parser.add_argument("--location", default="")
    parser.add_argument("--source", default="")
    parser.add_argument("--deadline", default="")
    parser.add_argument("--sector", default="")
    parser.add_argument("--role-type", default="")
    parser.add_argument("--channel", default="")
    parser.add_argument("--fit-rating", default="")
    parser.add_argument("--status", default="")
    parser.add_argument("--cv-file", default="")
    parser.add_argument("--cover-letter-file", default="")
    parser.add_argument("--posting-file", type=Path)
    args = parser.parse_args()
    posting_text = args.posting_file.read_text(encoding="utf-8") if args.posting_file else None
    result = ensure_application(
        ROOT,
        ApplicationInput(
            company=args.company,
            role=args.role,
            location=args.location,
            source=args.source,
            deadline=args.deadline,
            sector=args.sector,
            role_type=args.role_type,
            channel=args.channel,
            fit_rating=args.fit_rating,
            status=args.status,
            cv_file=args.cv_file,
            cover_letter_file=args.cover_letter_file,
            posting_text=posting_text,
        ),
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
