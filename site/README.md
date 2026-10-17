# Site KASHING

Site statique d'une page en anglais (HTML/CSS/JS, aucun build), consacré à l'artiste KASHING
uniquement : pas de section Kash Studio.

## Sections

- **Hero** : fixe, sans animation (pour ne rien consommer) : le logo KASHING devant la foule dans le noir (`hero-wide.webp` sur ordinateur, `hero-tall.webp` sur téléphone, tirées de `assets/ambiance/festival_01.jpg`), nom en police Tourney.
- **Music** : un lecteur avec playlist, forme d'onde cliquable, contrôles depuis l'écran de verrouillage du téléphone.
- **The Sound** : texte court et générique sur la musique (pas d'histoire perso).
- Pas de section contact : on passe par Instagram (DM).

## Ajouter des tracks

1. Déposer les MP3 dans `site/audio/`. L'ordre suit le nom de fichier : préfixer avec `01_`, `02_`…
2. Lancer `python3 tools/build_tracks.py`. Le script écrit `site/audio/tracks.js` avec le titre, le BPM
   (lu dans le tag du fichier ou estimé), la durée et la forme d'onde.
3. On peut corriger à la main `title`, `bpm` et `key` dans `tracks.js` : ces corrections sont
   conservées au prochain passage du script.
4. Versions Suno : `04_Squirrel.mp3` et `04_Squirrel_1.mp3` donnent un seul morceau avec un sélecteur
   V1 / V2 dans le lecteur. Changer de version garde la position, ce qui permet de comparer à l'oreille.

Prérequis : `ffmpeg` et Python 3 avec `numpy`.

## Clips Instagram

```sh
python3 tools/make_clip.py site/audio/07_Sugar_Spike_Blues.mp3 --cover                    # un Reel
python3 tools/make_clip.py site/audio/07_Sugar_Spike_Blues.mp3 --format youtube --cover   # clip YouTube
sh tools/make_all_clips.sh                                                                # tous les Reels
python3 tools/make_clip.py site/audio/07_Sugar_Spike_Blues.mp3 --bg assets/ambiance/festival_01.jpg  # Reel sur une photo
```

Avec `--bg`, le fond est une photo d'ambiance au format vertical : elle zoome lentement, respire et
tremble sur les kicks, et le logo se place dans le haut de l'image, qui doit être sombre. Pas de spectre
ni de lasers dessinés dans ce mode. Si la photo est générée par IA, active l'étiquette « Info IA » sur Instagram.

Le format `youtube` produit un clip 1920x1080 du morceau entier à 24 i/s (environ 9 min de calcul pour
4 min de musique), avec une miniature 1280x720.

Le script produit un Reel 1080x1920 de 20 s, calé sur le drop détecté (`--start` pour forcer le
départ, `--duration` pour changer la longueur), plus une couverture `.jpg`. Les fichiers sortent
dans `clips/`, qui n'est pas versionné.

## Lancer en local

```sh
npx serve site
```

Attention : `python3 -m http.server` ne gère pas les requêtes partielles (Range). Avec lui, cliquer
sur la forme d'onde ou changer de version repart du début. GitHub Pages, Netlify et Vercel n'ont pas ce problème.

En ouvrant directement `index.html` (file://), la musique joue, mais les lasers suivent un tempo
simulé au lieu d'analyser le son.

## À remplacer avant la mise en ligne

| Quoi | Où |
|---|---|
| ~~Email~~ fait : kashingguudenoff@gmail.com | `index.html` |
| ~~Lien Instagram~~ fait : @kashingguudenoff | `index.html` |

## Hébergement

Le dossier `site/` se déploie tel quel (GitHub Pages, Netlify, Vercel). 30 MP3 à environ 6 Mo
font environ 180 Mo : ça passe sur GitHub, sans marge énorme.
