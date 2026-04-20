"""Video frame and audio extraction using ffmpeg."""

import asyncio
import os
from pathlib import Path

import ffmpeg

from banshield.utils.helpers import generate_scan_id


class VideoProcessor:
    """Extracts frames and audio from video files for analysis."""

    async def extract_frames(
        self, video_path: str, output_dir: str, fps: float = 1.0
    ) -> list[str]:
        """Extract frames at the specified FPS and return their paths."""
        output_pattern = os.path.join(output_dir, "frame_%04d.jpg")

        def _run() -> None:
            try:
                (
                    ffmpeg.input(video_path)
                    .filter("fps", fps=fps)
                    .output(output_pattern, start_number=1)
                    .run(quiet=True, overwrite_output=True)
                )
            except ffmpeg.Error as exc:
                stderr = exc.stderr.decode("utf-8") if exc.stderr else "unknown"
                raise RuntimeError(
                    f"ffmpeg failed to extract frames from {video_path}: {stderr}"
                ) from exc

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _run)

        frame_files = sorted(
            f for f in os.listdir(output_dir) if f.startswith("frame_") and f.endswith(".jpg")
        )
        return [os.path.join(output_dir, f) for f in frame_files]

    async def extract_audio(self, video_path: str, output_dir: str) -> str:
        """Extract audio track as 16kHz mono WAV and return its path."""
        output_path = os.path.join(output_dir, "audio.wav")

        def _run() -> None:
            try:
                (
                    ffmpeg.input(video_path)
                    .output(output_path, ar=16000, ac=1)
                    .run(quiet=True, overwrite_output=True)
                )
            except ffmpeg.Error as exc:
                stderr = exc.stderr.decode("utf-8") if exc.stderr else "unknown"
                raise RuntimeError(
                    f"ffmpeg failed to extract audio from {video_path}: {stderr}"
                ) from exc

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _run)

        return output_path

    async def process(self, video_path: str) -> dict:
        """Extract frames and audio into a processing directory."""
        scan_id = generate_scan_id()
        output_dir = os.path.join("data", "processing", scan_id)
        os.makedirs(output_dir, exist_ok=True)

        frames, audio_path = await asyncio.gather(
            self.extract_frames(video_path, output_dir),
            self.extract_audio(video_path, output_dir),
        )

        return {
            "scan_id": scan_id,
            "frames": frames,
            "audio_path": audio_path,
            "frame_count": len(frames),
        }
