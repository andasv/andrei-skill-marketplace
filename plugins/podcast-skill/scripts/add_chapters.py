#!/usr/bin/env python3
"""Embed ID3 chapter markers (CTOC + CHAP frames) into a merged podcast MP3.

Chapter boundaries are given as turn indices that match the zero-padded segment
filenames produced by merge_audio.py. The script computes cumulative durations
from the per-turn segment files so chapter timestamps align perfectly with the
merged output, regardless of TTS-service timing quirks.
"""

import argparse
import json
import sys
from pathlib import Path

from mutagen.id3 import ID3, CHAP, CTOC, CTOCFlags, TIT2
from mutagen.id3._util import ID3NoHeaderError
from pydub import AudioSegment


def _fmt_hms(ms: int) -> str:
    s, ms = divmod(ms, 1000)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def segment_start_offsets_ms(segments_dir: Path) -> list[int]:
    """Return cumulative start offsets (ms) for each segment, in filename order.

    offsets[i] is the start time of turn i+1 (1-indexed) in the merged mp3.
    offsets[-1] + duration(last) == total duration.
    """
    segments = sorted(segments_dir.glob("*.mp3"))
    if not segments:
        raise SystemExit(f"No MP3 segments found in {segments_dir}")

    offsets: list[int] = []
    cursor_ms = 0
    for seg in segments:
        offsets.append(cursor_ms)
        cursor_ms += len(AudioSegment.from_mp3(str(seg)))
    # Append the final end-of-audio cursor so the last chapter can derive its end.
    offsets.append(cursor_ms)
    return offsets


def load_chapters(path: Path) -> list[dict]:
    raw = json.loads(path.read_text())
    if isinstance(raw, dict) and "chapters" in raw:
        chapters = raw["chapters"]
    elif isinstance(raw, list):
        chapters = raw
    else:
        raise SystemExit(f"{path}: expected {{\"chapters\": [...]}} or a top-level list")

    if not chapters:
        raise SystemExit(f"{path}: chapters list is empty")

    for i, ch in enumerate(chapters):
        if "title" not in ch or "start_turn" not in ch:
            raise SystemExit(f"{path}: chapter {i} missing required keys 'title' and 'start_turn'")
        if not isinstance(ch["start_turn"], int) or ch["start_turn"] < 1:
            raise SystemExit(f"{path}: chapter {i} start_turn must be a positive int (got {ch['start_turn']})")

    for i in range(1, len(chapters)):
        if chapters[i]["start_turn"] <= chapters[i - 1]["start_turn"]:
            raise SystemExit(
                f"{path}: chapters must be in strictly increasing start_turn order "
                f"(chapter {i} start_turn={chapters[i]['start_turn']} <= previous {chapters[i-1]['start_turn']})"
            )
    return chapters


def write_chapters(mp3_path: Path, chapters: list[dict], offsets_ms: list[int]) -> None:
    """Replace any existing CTOC/CHAP frames with the new chapter set."""
    turn_count = len(offsets_ms) - 1
    for ch in chapters:
        if ch["start_turn"] > turn_count:
            raise SystemExit(
                f"Chapter '{ch['title']}' start_turn={ch['start_turn']} exceeds segment count {turn_count}"
            )

    try:
        tags = ID3(mp3_path)
    except ID3NoHeaderError:
        tags = ID3()

    for key in list(tags.keys()):
        if key.startswith("CHAP") or key.startswith("CTOC"):
            del tags[key]

    total_ms = offsets_ms[-1]
    element_ids: list[str] = []

    for i, ch in enumerate(chapters):
        element_id = f"chp{i+1:02d}"
        element_ids.append(element_id)

        start_ms = offsets_ms[ch["start_turn"] - 1]
        next_turn_start = (
            offsets_ms[chapters[i + 1]["start_turn"] - 1]
            if i + 1 < len(chapters)
            else total_ms
        )
        end_ms = next_turn_start

        title = ch["title"].strip()

        tags.add(
            CHAP(
                element_id=element_id,
                start_time=start_ms,
                end_time=end_ms,
                start_offset=0xFFFFFFFF,
                end_offset=0xFFFFFFFF,
                sub_frames=[TIT2(encoding=3, text=[title])],
            )
        )

    tags.add(
        CTOC(
            element_id="toc",
            flags=CTOCFlags.TOP_LEVEL | CTOCFlags.ORDERED,
            child_element_ids=element_ids,
            sub_frames=[TIT2(encoding=3, text=["Chapters"])],
        )
    )

    tags.save(mp3_path, v2_version=3)

    print(f"Wrote {len(chapters)} chapters to {mp3_path}:")
    for i, ch in enumerate(chapters):
        start_ms = offsets_ms[ch["start_turn"] - 1]
        print(f"  {i+1:02d}  {_fmt_hms(start_ms)}  {ch['title'].strip()}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Embed ID3 chapter markers in a merged podcast MP3.")
    parser.add_argument("--segments-dir", required=True, help="Directory containing MP3 segments (same as merge_audio.py)")
    parser.add_argument("--output", required=True, help="Merged MP3 to annotate in place")
    parser.add_argument("--chapters-json", required=True, help="JSON file with chapter list")
    args = parser.parse_args()

    segments_dir = Path(args.segments_dir)
    mp3_path = Path(args.output)
    chapters_json = Path(args.chapters_json)

    if not mp3_path.is_file():
        sys.exit(f"MP3 not found: {mp3_path}")
    if not segments_dir.is_dir():
        sys.exit(f"Segments dir not found: {segments_dir}")
    if not chapters_json.is_file():
        sys.exit(f"Chapters JSON not found: {chapters_json}")

    chapters = load_chapters(chapters_json)

    if len(chapters) < 2:
        print(f"Skipping chapter write — need at least 2 chapters, got {len(chapters)}.")
        return

    offsets_ms = segment_start_offsets_ms(segments_dir)
    write_chapters(mp3_path, chapters, offsets_ms)


if __name__ == "__main__":
    main()
