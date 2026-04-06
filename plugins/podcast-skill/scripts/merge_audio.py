#!/usr/bin/env python3
"""Merge podcast audio segments into a single MP3 file using pydub."""

import argparse
import sys
from pathlib import Path

from pydub import AudioSegment


def merge_segments(segments_dir: str, output_path: str, crossfade_ms: int = 0) -> None:
    """Concatenate MP3 segments from a directory into a single output file.

    Segments are sorted by filename — use zero-padded naming (001_alex.mp3, 002_sarah.mp3).
    """
    segments_path = Path(segments_dir)
    output = Path(output_path)

    mp3_files = sorted(segments_path.glob("*.mp3"))

    if not mp3_files:
        print(f"Error: No MP3 files found in {segments_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(mp3_files)} segments to merge:")
    for f in mp3_files:
        print(f"  - {f.name}")

    combined = AudioSegment.from_mp3(str(mp3_files[0]))

    for mp3_file in mp3_files[1:]:
        segment = AudioSegment.from_mp3(str(mp3_file))
        if crossfade_ms > 0:
            combined = combined.append(segment, crossfade=crossfade_ms)
        else:
            combined = combined + segment

    output.parent.mkdir(parents=True, exist_ok=True)
    combined.export(str(output), format="mp3")

    duration_sec = len(combined) / 1000
    print(f"Merged podcast saved to: {output}")
    print(f"Total duration: {duration_sec:.1f}s ({duration_sec/60:.1f} min)")


def main():
    parser = argparse.ArgumentParser(description="Merge podcast audio segments into one MP3")
    parser.add_argument("--segments-dir", required=True, help="Directory containing MP3 segments")
    parser.add_argument("--output", required=True, help="Output MP3 file path")
    parser.add_argument("--crossfade-ms", type=int, default=0, help="Crossfade duration in ms (default: 0)")
    args = parser.parse_args()

    merge_segments(args.segments_dir, args.output, args.crossfade_ms)


if __name__ == "__main__":
    main()
