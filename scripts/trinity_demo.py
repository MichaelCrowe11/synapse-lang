"""Render an offline demonstration from actual installed-wheel execution traces."""
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "benchmarks" / "trinity-implementation"


def main():
    report = json.loads((OUT / "installed.json").read_text())
    assert report["status"] == "passed"
    python = report["combined_python"]
    code = """import json, random
from qubit_flow_lang.qubit_flow_interpreter import QubitFlowInterpreter
random.seed(73)
q = QubitFlowInterpreter()
frames = []
for source in ["qubit a\\nqubit b", "H[a]", "CNOT[a,b]", "measure a -> first", "measure b -> second"]:
    messages = q.execute(source)
    assert not any(m.startswith("Error:") for m in messages), messages
    frames.append({"source": source, "messages": messages,
                   "probabilities": (abs(q.state.amplitudes)**2).tolist(),
                   "measurements": dict(q.classical_bits)})
assert frames[-1]["measurements"]["first"] == frames[-1]["measurements"]["second"]
print(json.dumps(frames))
"""
    result = subprocess.run([python, "-I", "-c", code], check=True, capture_output=True, text=True)
    trace = json.loads(result.stdout)
    (OUT / "demo-trace.json").write_text(json.dumps(trace, indent=2) + "\n")
    font_path = "/System/Library/Fonts/Menlo.ttc"
    title = ImageFont.truetype(font_path, 38)
    body = ImageFont.truetype(font_path, 23)
    small = ImageFont.truetype(font_path, 18)
    images = OUT / "demo-frames"
    images.mkdir(exist_ok=True)

    def base(heading, subtitle):
        image = Image.new("RGB", (1280, 720), "#08131f")
        draw = ImageDraw.Draw(image)
        draw.text((55, 38), "CROWE LOGIC / TRINITY", font=small, fill="#52d7c1")
        draw.text((55, 87), heading, font=title, fill="white")
        draw.text((55, 150), subtitle, font=body, fill="#c0cede")
        draw.text((55, 668), "LOCAL SOFTWARE EVIDENCE | No hardware or production validation", font=small, fill="#91a4ba")
        return image, draw

    image, draw = base("Verified local foundation", "Build > install > execute > compare > retain evidence")
    for y, text in enumerate([
        "Canonical Qubit Flow source; build-time copying removed",
        "Shared joint state, Bell/GHZ and sequential collapse",
        "Supported Synapse bridge; honest parse-only Quantum Net CLI",
        "Fresh standalone + combined wheel checks",
        "40 injected faults detected / 40 clean controls: 0 alarms",
        "Remote matrix, hardware and staging rollout remain pending",
    ]):
        draw.text((70, 230 + y * 60), text, font=body, fill="white")
    image.save(images / "00.png")
    for i, frame in enumerate(trace, 1):
        image, draw = base(f"Execution step {i}: installed wheel", frame["source"].replace("\n", "; "))
        for j, probability in enumerate(frame["probabilities"]):
            x = 110 + j * 280
            height = round(probability * 310)
            draw.rectangle((x, 570-height, x+160, 570), fill="#52d7c1")
            draw.text((x, 590), f"|{j:02b}> {probability:.2f}", font=body, fill="white")
        draw.text((60, 205), "Measurements: " + str(frame["measurements"]), font=small, fill="#c0cede")
        image.save(images / f"{i:02}.png")
    image, draw = base("Independent fault detection", "Measured on 10 injected cases and 10 controls per category")
    for i, name in enumerate(("gate", "indexing", "noise", "uncertainty")):
        rows = [r for r in report["fault_campaign"]["cases"] if r["category"] == name]
        detected = sum(r["detected"] and r["defect_injected"] for r in rows)
        false = sum(r["detected"] and not r["defect_injected"] for r in rows)
        y = 240 + i * 85
        draw.text((70, y), name.upper(), font=body, fill="white")
        draw.rectangle((350, y, 350 + detected * 50, y+35), fill="#52d7c1")
        draw.text((880, y), f"{detected}/10 | FP {false}", font=body, fill="white")
    image.save(images / "06.png")
    image.save(OUT / "validation-chart.png")
    image, draw = base("Release gates remain closed", "The evidence supports private engineering work, not release")
    for i, text in enumerate([
        "1. Review source changes, compatibility breaks and licensing",
        "2. Run the configured remote OS/Python matrix",
        "3. Select candidate version and private registry",
        "4. Approve named hardware/data scope and budget",
        "5. Select staging product, flag, thresholds and rollback",
        "6. Review shadow evidence before publication or announcement",
    ]):
        draw.text((60, 225 + i * 60), text, font=body, fill="white")
    image.save(images / "07.png")
    movie = OUT / "trinity-demonstration.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "1/5", "-i",
                    str(images / "%02d.png"), "-c:v", "libx264", "-r", "30", "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart", str(movie)], check=True)
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                            "format=duration:stream=width,height,codec_name", "-of", "json", str(movie)],
                           check=True, capture_output=True, text=True)
    metadata = json.loads(probe.stdout)
    assert float(metadata["format"]["duration"]) == 40
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(movie), "-f", "null", "-"], check=True)
    (OUT / "video-verification.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(movie)


if __name__ == "__main__":
    main()
