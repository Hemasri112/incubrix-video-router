from pathlib import Path
from typing import List, Dict


def seconds_to_srt_time(seconds: float) -> str:
    """Convert seconds to SRT timestamp format."""

    milliseconds = int(round(seconds * 1000))

    hours = milliseconds // 3_600_000
    milliseconds %= 3_600_000

    minutes = milliseconds // 60_000
    milliseconds %= 60_000

    seconds_part = milliseconds // 1000
    milliseconds %= 1000

    return (
        f"{hours:02d}:"
        f"{minutes:02d}:"
        f"{seconds_part:02d},"
        f"{milliseconds:03d}"
    )


def create_srt(
    captions: List[Dict],
    output_path: str,
) -> Path:
    """
    Create an SRT subtitle file.

    Each caption should contain:
        - start
        - end
        - text
    """

    if not captions:
        raise ValueError("At least one caption is required.")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w", encoding="utf-8") as file:
        for index, caption in enumerate(captions, start=1):
            start = float(caption["start"])
            end = float(caption["end"])
            text = str(caption["text"]).strip()

            if end <= start:
                raise ValueError(
                    f"Caption {index} has invalid timing."
                )

            if not text:
                raise ValueError(
                    f"Caption {index} has empty text."
                )

            file.write(f"{index}\n")
            file.write(
                f"{seconds_to_srt_time(start)} --> "
                f"{seconds_to_srt_time(end)}\n"
            )
            file.write(f"{text}\n\n")

    return output