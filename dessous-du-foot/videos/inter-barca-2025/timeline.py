"""Build voice.wav + timeline.json from the ElevenLabs line MP3s (noe/lineN.mp3)."""
import json, os, subprocess
D = os.path.dirname(os.path.abspath(__file__))
LINES = [
 "6 mai 2025. San Siro. Le Barça est à quelques minutes de la finale de Ligue des champions… et tout s'écroule.",
 "Remontons une semaine plus tôt. À l'aller, à Barcelone, c'est un match fou : trois partout.",
 "L'Inter marque au bout de trente secondes. Lamine Yamal répond avec un but incroyable. Tout se jouera à Milan.",
 "L'enjeu est énorme : le Barça n'a plus joué de finale depuis 2015. Et Yamal, dix-sept ans, peut entrer dans la légende.",
 "Au retour, l'Inter frappe en premier. Lautaro, puis Çalhanoğlu sur penalty juste avant la pause. Deux à zéro.",
 "Mais ce Barça ne lâche rien. Eric García, puis Dani Olmo de la tête : deux partout, en six minutes.",
 "Et Yamal ? Il est partout. Il dribble, il frappe, il fait trembler San Siro… mais Yann Sommer arrête tout.",
 "Quatre-vingt-septième minute : Raphinha ! Trois à deux pour le Barça. La finale est là.",
 "Sauf qu'à la quatre-vingt-treizième, Acerbi, un défenseur de trente-sept ans, surgit dans la surface. Trois partout.",
 "Prolongation. Quatre-vingt-dix-neuvième minute : Frattesi. Quatre à trois. L'Inter est en finale.",
 "Alors, qu'est-ce qui a manqué au Barça ? D'abord, une défense très haute, prise dans le dos encore et encore.",
 "Ensuite, un Sommer monstrueux. Et enfin, l'expérience : savoir tenir un score pendant trois petites minutes.",
 "Sept buts à six sur les deux matchs. Une des demi-finales les plus folles de l'histoire.",
 "Et le pire ? En finale, l'Inter prendra cinq à zéro contre le PSG.",
 "Abonne-toi pour d'autres histoires de foot comme celle-là.",
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
