# Les dessous du foot

Vidéos TikTok / Shorts de 1 min à 1 min 30 : la tactique du foot expliquée sur un tableau à la craie.

## Vidéos

| Dossier | Sujet | Durée |
|---|---|---|
| `videos/6-secondes/` | La règle des 6 secondes du Barça de Guardiola (contre-pressing) — version finale : `tactique-6-secondes-v3.mp4` | 50 s |
| `videos/inter-barca-2025/` | Inter 4-3 Barça, demi-finale retour de Ligue des champions 2025 : contexte, score cumulé en direct, Yamal, ce qui a manqué — `inter-barca-2025.mp4` | 1 min 26 |

La vidéo finie est dans chaque dossier (`*.mp4`).

## Comment c'est fabriqué

1. **Script** : les phrases sont listées dans `timeline.py`.
2. **Voix off** : voix « Noé – Content Creator » d'ElevenLabs (`voice_id` `7pDdnNI6PhXmAp0pXFZm`, modèle `eleven_v4`), une phrase par fichier dans `noe/line0.mp3`, `line1.mp3`…
3. **Sons** : ambiance de stade, clameur, sifflet et frappe de balle générés par ElevenLabs, dans `sfx/`.
4. **Animation** : `index.html` dessine le tableau, les pions et les flèches (rough.js) image par image. Chaque scène correspond à une phrase du script, et les éléments apparaissent sur des mots précis grâce à la fonction `W(scène, 'mot')`.
5. **Plans réalistes** : images et plan de stade générés par ElevenLabs (Seedream 5 Lite, LTX v2 fast), originaux dans `broll/src/`, recadrés en vertical dans `broll/`. Ils s'affichent avec un zoom lent (liste `BROLL` dans `index.html`).
6. **Rendu** : `render.js` capture les images avec Playwright, `audio2.py` mixe la voix, la foule (qui baisse quand la voix parle) et les bruitages, puis ffmpeg assemble le MP4 en 1080×1920.

## Refaire une vidéo

Prérequis : Node 18+, Python 3, ffmpeg, Playwright avec Chromium.

```bash
cd videos/6-secondes
npm install
mkdir -p broll/stadium && ffmpeg -i broll/src/stadium.mp4 -vf "fps=30,crop=ih*9/16:ih,scale=1080:1920" -q:v 4 broll/stadium/%04d.jpg
python3 timeline.py        # voice.wav + timeline.json à partir de noe/*.mp3
node render.js 2,12,21     # quelques images d'aperçu (still_*.png)
node render.js             # la vidéo complète
```

## Nouvelle vidéo

1. Copier `videos/6-secondes` vers `videos/<sujet>`.
2. Écrire les nouvelles phrases dans `timeline.py` et générer une voix par phrase avec ElevenLabs dans `noe/`.
3. Adapter les scènes de `index.html` (fonction `build()`) : titres, pions, flèches, mots déclencheurs.
4. Lancer `python3 timeline.py` puis `node render.js`.
