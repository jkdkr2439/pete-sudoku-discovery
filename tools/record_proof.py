from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "_vendor"))

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
SIZE = (1440, 1000)


def api(url, method="GET"):
    request = Request(url, method=method)
    with urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode())


def font(size, bold=False):
    name = "segoeuib.ttf" if bold else "segoeui.ttf"
    return ImageFont.truetype(str(Path(r"C:\Windows\Fonts") / name), size)


def card(title, lines, accent):
    image = Image.new("RGB", SIZE, "#f5f1e8")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 32, SIZE[1]), fill=accent)
    draw.text((92, 105), "PETE / FALSIFIABLE RUN RECORD", font=font(20, True), fill=accent)
    draw.text((92, 165), title, font=font(54, True), fill="#172237")
    y = 280
    for line in lines:
        draw.rounded_rectangle((92, y, 1340, y + 78), 18, fill="#fffdf8", outline="#d7d4ca", width=2)
        draw.text((122, y + 20), line, font=font(25), fill="#465065")
        y += 98
    return image


def capture(url, target, profile, sequence):
    cmd = [
        str(EDGE), "--headless=new", "--disable-gpu", "--hide-scrollbars",
        f"--window-size={SIZE[0]},{SIZE[1]}", f"--user-data-dir={profile}",
        "--virtual-time-budget=1400", f"--screenshot={target}",
        f"{url}?proof_frame={sequence}",
    ]
    completed = subprocess.run(cmd, capture_output=True, timeout=30)
    if completed.returncode or not target.exists():
        raise RuntimeError(completed.stderr.decode(errors="replace"))
    with Image.open(target) as image:
        return image.convert("RGB").resize(SIZE)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8792")
    parser.add_argument("--output", default="artifacts/proof/PETE_9X9_EMPTY_TO_SOLVED_20260914.mp4")
    args = parser.parse_args()
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    work = ROOT / "runtime" / "video-proof"
    profile = ROOT / "runtime" / "edge-proof-profile"
    shutil.rmtree(work, ignore_errors=True)
    shutil.rmtree(profile, ignore_errors=True)
    work.mkdir(parents=True)
    profile.mkdir(parents=True)

    initial = api(args.url + "/api/state")
    if initial["running"] or initial["fieldmap"]["samples"] or initial["fieldmap"]["clauses"] or initial["journal"]["events"]:
        raise RuntimeError("PROOF_REQUIRES_EMPTY_RUNTIME")

    frames = []
    frames.extend([card("EMPTY START", [
        "Sudoku world: 9 x 9", "Training corpus: 0",
        "Pretrained or fixed learned weights: 0",
        "Fieldmap samples: 0   |   clauses: 0   |   journal: GENESIS",
    ], "#ef735f")] * 6)
    frames.extend([card("HARD BOUNDARY", [
        "Sudoku constraints exist only inside the external substrate.",
        "Cognition cannot import substrate authority.",
        "Sandbox has no validator callback.",
        "Every physical reaction is written to a hash-chained journal.",
    ], "#53b89d")] * 6)

    initial_frame = capture(args.url, work / "frame-000.png", profile, 0)
    frames.extend([initial_frame] * 8)
    api(args.url + "/api/start-once", "POST")
    states = []
    sequence = 1
    deadline = time.time() + 120
    while time.time() < deadline:
        state = api(args.url + "/api/state")
        states.append({
            "phase": state["phase"], "samples": state["fieldmap"]["samples"],
            "reaction_events": state["fieldmap"]["reaction_events"],
            "reaction_shapes": state["fieldmap"]["reaction_shapes"],
            "clauses": len(state["fieldmap"]["clauses"]),
            "structure_hash": state["fieldmap"]["structure_hash"],
        })
        frames.append(capture(args.url, work / f"frame-{sequence:03d}.png", profile, sequence))
        sequence += 1
        if not state["running"] and state["phase"] in {"SOLVED", "FAILED", "COUNTEREXAMPLE", "GAP_UNRESOLVED"}:
            break
    final = api(args.url + "/api/state")
    if final["phase"] != "SOLVED":
        raise RuntimeError(f"PROOF_RUN_DID_NOT_SOLVE: {final['phase']} {final['error']}")
    frames.extend([frames[-1]] * 10)
    frames.extend([card("AUTHORITATIVE RESULT: SOLVED", [
        f"Physical samples: {final['fieldmap']['samples']}",
        f"Structural reactions: {final['fieldmap']['reaction_events']} events / {final['fieldmap']['reaction_shapes']} shapes",
        f"Collapsed relations: {len(final['fieldmap']['clauses'])}",
        f"Held-out accuracy: {100 * final['metrics']['verification']['accuracy']:.1f}%",
    ], "#8874ca")] * 8)

    writer = imageio_ffmpeg.write_frames(
        str(output), SIZE, fps=2, codec="libx264", pix_fmt_in="rgb24",
        pix_fmt_out="yuv420p", output_params=["-crf", "19", "-movflags", "+faststart"],
    )
    writer.send(None)
    for frame in frames:
        writer.send(frame.tobytes())
    writer.close()

    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    manifest = {
        "schema": "pete.sudoku-discovery.video-proof.v1",
        "source_commit": commit, "video": str(output.relative_to(ROOT)),
        "frame_rate": 2, "frame_count": len(frames),
        "initial": {
            "shape": initial["substrate"]["shape"],
            "fieldmap_samples": initial["fieldmap"]["samples"],
            "fieldmap_clauses": len(initial["fieldmap"]["clauses"]),
            "journal_events": initial["journal"]["events"],
            "structure_hash": initial["fieldmap"]["structure_hash"],
        },
        "timeline": states,
        "final": {
            "phase": final["phase"], "samples": final["fieldmap"]["samples"],
            "clauses": final["fieldmap"]["clauses"],
            "reactions": {
                "events": final["fieldmap"]["reaction_events"],
                "shapes": final["fieldmap"]["reaction_shapes"],
                "structure_hash": final["fieldmap"]["structure_hash"],
            },
            "verification": final["metrics"]["verification"],
            "sandbox_attempts": final["sandbox"]["attempts"],
            "journal": final["journal"],
        },
    }
    manifest_path = output.with_suffix(".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    shutil.rmtree(work, ignore_errors=True)
    shutil.rmtree(profile, ignore_errors=True)
    print(json.dumps({"video": str(output), "manifest": str(manifest_path), "frames": len(frames), "result": final["phase"]}))


if __name__ == "__main__":
    main()
