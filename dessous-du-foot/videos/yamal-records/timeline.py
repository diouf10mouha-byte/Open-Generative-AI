"""Build voice.wav + timeline.json from the ElevenLabs line MP3s (noe/lineN.mp3)."""
import json, os, subprocess
D = os.path.dirname(os.path.abspath(__file__))
LINES = [
 "Avant ses dix-huit ans, Lamine Yamal a fait des choses que Messi n'a jamais faites à son âge.",
 "Quinze ans et neuf mois : premier match en Liga avec le Barça.",
 "Seize ans : plus jeune buteur de toute l'histoire de la Liga.",
 "Seize ans et cinquante-sept jours : plus jeune buteur de l'histoire de l'équipe d'Espagne.",
 "À l'Euro 2024 : plus jeune joueur, plus jeune buteur de l'histoire du tournoi… et champion d'Europe le lendemain de ses dix-sept ans.",
 "Dix-sept ans : un but de génie en demi-finale de Ligue des champions contre l'Inter.",
 "Et en 2025, il termine deuxième du Ballon d'Or. À dix-huit ans.",
 "Et Messi à dix-sept ans ? Il venait tout juste de jouer son premier match officiel avec le Barça.",
 "Mais attention : son corps commence à protester. Une pubalgie l'a privé de plusieurs matchs en 2025.",
 "Bref : à ce rythme, on n'aura plus besoin de l'appeler le nouveau Messi.",
 "Abonne-toi pour d'autres stats de foot qui retournent le cerveau.",
]
GAP, LEAD = 0.25, 0.15
def dur(f):
    return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f]).decode())
# trim leading/trailing silence of each line to keep the pace tight
t, tl, inputs, filt = LEAD, [], [], []
for i, text in enumerate(LINES):
    src = os.path.join(D, "noe", f"line{i}.mp3"); out = os.path.join(D, "noe", f"trim{i}.wav")
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",src,"-af",
        "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse",
        "-ar","44100","-ac","1",out], check=True)
    d = dur(out); tl.append({"text": text, "start": round(t,3), "end": round(t+d,3)})
    inputs += ["-i", out]; ms = int(t*1000); filt.append(f"[{i}:a]adelay={ms}|{ms}[a{i}]"); t += d + GAP
total = t + 0.8
filt.append("".join(f"[a{i}]" for i in range(len(LINES))) + f"amix=inputs={len(LINES)}:normalize=0,apad,atrim=0:{total:.2f}[out]")
subprocess.run(["ffmpeg","-y","-loglevel","error",*inputs,"-filter_complex",";".join(filt),"-map","[out]","-ac","2",os.path.join(D,"voice.wav")], check=True)
json.dump({"total": round(total,2), "lines": tl}, open(os.path.join(D,"timeline.json"),"w"), ensure_ascii=False, indent=1)
print("total", round(total,2)); [print(l["start"], l["end"], l["text"][:50]) for l in tl]
