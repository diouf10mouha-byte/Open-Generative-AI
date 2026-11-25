"""Build voice.wav + timeline.json from the ElevenLabs line MP3s (noe/lineN.mp3)."""
import json, os, subprocess
D = os.path.dirname(os.path.abspath(__file__))
LINES = [
 "Contre le Barça de Guardiola, quand tu récupérais le ballon… tu avais six secondes. Pas une de plus.",
 "Normalement, quand une équipe perd le ballon, elle recule. Elle se replace. Elle attend.",
 "Le Barça ? Il fait l'inverse. Il attaque. Tout de suite.",
 "Trois joueurs foncent sur le porteur. Les autres ferment toutes les passes courtes.",
 "Pourquoi si vite ? Parce que celui qui vient de récupérer le ballon a la tête baissée. Il regarde le ballon… pas le jeu.",
 "Résultat : le Barça récupère le ballon à trente mètres du but adverse. Et là, c'est souvent fini.",
 "Et si au bout de six secondes, ça ne marche pas ? Pas de panique : tout le monde recule et se replace.",
 "C'est comme ça que des équipes entières passaient des matchs à courir… sans jamais toucher le ballon.",
 "Aujourd'hui, ça s'appelle le contre-pressing. Klopp, Arteta… presque tous les grands coachs l'utilisent.",
 "Abonne-toi. La prochaine fois, je t'explique le faux neuf.",
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
