"""Stadium mix: voice + looping crowd (ducked under the voice) + football SFX at the page's cues -> mix.wav."""
import json, os, subprocess

D = os.path.dirname(os.path.abspath(__file__))
tl = json.load(open(os.path.join(D, "timeline.json"), encoding="utf-8"))
cues = json.load(open(os.path.join(D, "cues.json"), encoding="utf-8"))
total = tl["total"]
GAIN = {"whistle": 0.6, "kick": 0.6, "roar": 0.75}

inputs = ["-i", os.path.join(D, "voice.wav"),
          "-stream_loop", "-1", "-i", os.path.join(D, "sfx", "crowd.mp3"),
          "-i", os.path.join(D, "music.mp3")]
filt = ["[0:a]aresample=44100,aformat=channel_layouts=stereo,asplit=2[v][sc]",
        f"[1:a]aresample=44100,aformat=channel_layouts=stereo,atrim=0:{total:.2f},volume=0.3,"
        f"afade=t=out:st={total - 1.2:.2f}:d=1.2[crowd]",
        "[crowd]anull[cd]",
        f"[2:a]aresample=44100,aformat=channel_layouts=stereo,atrim=0:{total:.2f},volume=0.22,afade=t=out:st={total - 2:.2f}:d=2[mu]",
        "[cd][mu]amix=inputs=2:normalize=0[bed]",
        "[bed][sc]sidechaincompress=threshold=0.03:ratio=6:attack=25:release=350[bd]"]
labels, n = [], 3
for c in cues:
    if c["fx"] not in GAIN: continue
    inputs += ["-i", os.path.join(D, "sfx", c["fx"] + ".mp3")]
    ms = max(0, int(c["t"] * 1000))
    filt.append(f"[{n}:a]aresample=44100,aformat=channel_layouts=stereo,volume={GAIN[c['fx']]},adelay={ms}|{ms}[s{n}]")
    labels.append(f"[s{n}]"); n += 1
filt.append(f"[v][bd]{''.join(labels)}amix=inputs={2 + len(labels)}:normalize=0,atrim=0:{total:.2f},alimiter=limit=0.95[out]")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filt),
                "-map", "[out]", "-ac", "2", os.path.join(D, "mix.wav")], check=True)
print("audio ok:", len(labels), "sfx")
