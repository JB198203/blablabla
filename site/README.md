# Site KASHING (+ Kash Studio)

Site statique d'une page (HTML/CSS/JS, aucun build). Direction visuelle : chrome & laser,
personnage masqué.

## Sections

- **Hero** : le masque chromé (`mask.svg`) et des lasers qui réagissent au son de la track en cours.
- **Musique** : un lecteur avec playlist, forme d'onde cliquable, contrôles depuis l'écran de verrouillage du téléphone.
- **Le masque** : le texte sur l'anonymat de l'artiste.
- **Kash Studio** : la ghost production (process, offres).
- **Contact** : booking ou brief.

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
python3 tools/make_clip.py site/audio/07_Sugar_Spike_Blues.mp3 --cover   # un clip
sh tools/make_all_clips.sh                                               # tous
```

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
| Email `contact@kashstudio.fr` | `index.html` (formulaire + footer) |
| Lien Instagram `@kashing` | `index.html` |
| Prix Kash Studio (« sur devis » pour l'instant) | section `#studio` |

## Hébergement

Le dossier `site/` se déploie tel quel (GitHub Pages, Netlify, Vercel). 30 MP3 à environ 6 Mo
font environ 180 Mo : ça passe sur GitHub, sans marge énorme.
