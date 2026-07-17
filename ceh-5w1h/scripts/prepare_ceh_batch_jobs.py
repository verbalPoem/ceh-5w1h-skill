#!/usr/bin/env python3
"""Prepare line-based text as stateless, one-record CEH extraction jobs."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path


def iter_records(path: Path):
    with path.open("r", encoding="utf-8-sig", newline=None) as handle:
        logical_index = 0
        for source_line, raw in enumerate(handle, start=1):
            text = raw.strip()
            if not text:
                continue
            logical_index += 1
            yield {
                "Id": f"{path.stem}_L{logical_index:04d}",
                "Text": text,
                "Source_File": path.name,
                "Source_Line": source_line,
            }


def write_jsonl(path: Path, records: list[dict[str, object]], session_id: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for position, record in enumerate(records, start=1):
            job = dict(record)
            job["Session_Id"] = session_id
            job["Session_Position"] = position
            handle.write(json.dumps(job, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create one-record CEH jobs grouped into session shards")
    parser.add_argument("input", type=Path, help="a line-based .txt file or a folder containing .txt files")
    parser.add_argument("output_dir", type=Path, help="new folder for JSONL session shards")
    parser.add_argument("--records-per-session", type=int, default=100, help="context reset boundary; default 100")
    args = parser.parse_args()

    if args.records_per_session < 1 or args.records_per_session > 100:
        parser.error("--records-per-session must be between 1 and 100")
    if not args.input.exists():
        parser.error(f"input not found: {args.input}")

    sources = [args.input] if args.input.is_file() else sorted(args.input.glob("*.txt"))
    if not sources:
        parser.error("no .txt source files found")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, object] = {
        "format": "ceh-one-record-jobs-v1",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "records_per_session": args.records_per_session,
        "source": str(args.input),
        "sessions": [],
    }

    total_records = 0
    for source in sources:
        records = list(iter_records(source))
        for start in range(0, len(records), args.records_per_session):
            chunk = records[start : start + args.records_per_session]
            session_number = start // args.records_per_session + 1
            session_id = f"{source.stem}_S{session_number:03d}"
            output_name = f"{session_id}.jsonl"
            write_jsonl(args.output_dir / output_name, chunk, session_id)
            manifest["sessions"].append(
                {
                    "Session_Id": session_id,
                    "Source_File": source.name,
                    "Output_File": output_name,
                    "Records": len(chunk),
                    "First_Id": chunk[0]["Id"],
                    "Last_Id": chunk[-1]["Id"],
                }
            )
            total_records += len(chunk)

    manifest["total_sources"] = len(sources)
    manifest["total_sessions"] = len(manifest["sessions"])
    manifest["total_records"] = total_records
    manifest_path = args.output_dir / "manifest.json"
    with manifest_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    print(
        f"PREPARED: {total_records} record(s), {len(manifest['sessions'])} session shard(s), "
        f"max {args.records_per_session} records per session"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
