from __future__ import annotations

import subprocess
from pathlib import Path


def generate_reel(image_path: str, output_path: str, duration: int = 8) -> str:
    """
    Convert the generated infographic into a real MP4 Reel.

    Output:
      - 1080x1920
      - H.264
      - 30 FPS
      - 8 seconds by default
      - no audio
    """
    source = Path(image_path)
    output = Path(output_path)

    if not source.exists():
        raise FileNotFoundError(f"Infographic not found: {source}")

    output.parent.mkdir(parents=True, exist_ok=True)

    # Keep the existing 1080x1800 infographic centered inside a 1080x1920
    # Reel canvas. No image is posted directly to Instagram.
    vf = (
        "scale=1080:1800:force_original_aspect_ratio=decrease,"
        "pad=1080:1920:0:60:color=black,"
        "format=yuv420p"
    )

    command = [
        "ffmpeg",
        "-y",
        "-loop", "1",
        "-i", str(source),
        "-t", str(duration),
        "-vf", vf,
        "-r", "30",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-movflags", "+faststart",
        "-an",
        str(output),
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "FFmpeg failed to generate Reel:\n"
            + result.stderr[-4000:]
        )

    if not output.exists() or output.stat().st_size == 0:
        raise RuntimeError("Reel file was not created or is empty.")

    return str(output)
