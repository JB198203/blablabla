# Campagne Instagram — KASHING

> Je ne peux pas créer ni piloter le compte Instagram moi-même : la création exige une vérification
> par téléphone ou par email, et les règles de Meta interdisent les comptes créés ou gérés par des bots.
> Je produis les clips, les visuels, les légendes et le planning. Tu publies, ou tu programmes
> les posts avec Meta Business Suite (gratuit).

## Positionnement

- **KASHING** est l'artiste : Frenchcore, Hardbass, World fusion. C'est lui qu'on fait connaître.
  On ne montre pas son visage pour l'instant, mais on n'en fait pas un sujet : pas de « mystère »,
  pas de masque, pas d'histoire perso. On parle de la musique, c'est tout. L'image, c'est le logo.
- **Kash Studio** (ghost production) n'apparaît ni sur le site ni dans le fil Instagram : un compte
  artiste qui vend des tracks à d'autres brouille le message.

## Profil

- **Handle** : `@kashingguudenoff` (https://www.instagram.com/kashingguudenoff/)
- **Nom affiché** : `KASHING | Frenchcore` (ce champ est pris en compte par la recherche Instagram)
- **Type de compte** : Professionnel, catégorie « Artiste »
- **Photo de profil** : le logo KASHING sur fond noir (`assets/instagram_profile.jpg`, 1080x1080)
- **Bio** :

```
Frenchcore · Hardbass · World fusion
Feel the drop. 🔊
🎧 Full tracks ↓
```

En anglais : on vise un public international. Ne pas écrire l'URL dans la bio (elle n'y est pas cliquable).

- **Lien** (champ « Liens ») : https://kashing.vercel.app
- **Stories à la une** : `Tracks` · `Live` · `Studio vibes` · `Dates`

## Charte (identique au site et aux clips)

| Élément | Valeur |
|---|---|
| Fond | noir bleuté `#05060a` |
| Accents | cyan `#22e8ff`, magenta `#ff2bd6` |
| Nom | KASHING en chrome, police Tourney (italique, graisse 900) |
| Infos | JetBrains Mono (titre, handle) |
| Emblème | le logo KASHING (triangle d'acier, disque doré, scanner rouge K2000), présent dans **chaque** visuel |

Règles : pas de visage de KASHING, au plus une phrase à l'écran, le logo toujours au même endroit
(en haut ou au centre) pour qu'on le reconnaisse en scrollant. Les photos d'ambiance (foule, scène)
sont bienvenues ; si elles sont générées par IA, étiquette « Info IA ».

## Deux canaux, deux rôles

| | YouTube | Instagram |
|---|---|---|
| Rôle | Catalogue : là où on écoute en entier, là où un morceau peut décoller | Dynamisme : faire parler de soi, ramener vers YouTube |
| Format | Clip 16:9 du morceau entier (`--format youtube`) + Shorts | Reels 9:16 de 20 s |
| Rythme | 1 clip complet par semaine, pas plus | 3 à 4 Reels par semaine |

Les Reels 9:16 servent aussi de **YouTube Shorts**, sans retouche. Les Shorts sont ce qui fait
découvrir une chaîne ; le clip complet est là où l'auditeur reste. Chaque Short renvoie au clip
complet du même morceau (« vidéo liée » dans YouTube Studio).

### Le piège : être classé « contenu produit en masse »

Depuis juillet 2025, YouTube précise qu'une chaîne remplie de vidéos génériques, répétitives et
interchangeables n'est pas monétisable. L'IA n'est pas interdite en soi : c'est l'impression de
production à la chaîne qui est sanctionnée, et la chaîne est évaluée dans son ensemble. Avec
4 000 morceaux, la tentation de tout publier en image fixe mène exactement là.

Ce qui fait la différence :
- **Peu et choisi.** 5 ou 6 morceaux soignés plutôt que 200. On ajoute ensuite au rythme d'un par
  semaine, en suivant ce qui marche.
- **Un vrai visuel animé**, qui réagit au son (c'est ce que fait le générateur), plutôt qu'une image fixe.
- **De la personnalité dans les textes** : une description écrite par toi pour chaque morceau
  (d'où il vient, ce qu'il raconte), et pas un modèle copié-collé.
- **Le logo comme fil conducteur** : une identité reconnaissable donne de la cohérence à la chaîne.
- **Transparence** : une ligne dans la description de la chaîne, « musique créée avec Suno, écrite et
  dirigée par Kashing ». La case « contenu altéré ou synthétique » de YouTube vise surtout les contenus
  réalistes (visages, voix de vraies personnes) ; dans le doute, la cocher ne pénalise pas la vidéo.

### Les 4 premiers clips YouTube

*Sugar Spike Blues* (version longue), *Ten Tabs Open Syndrome*, *Here We Are*, *Ukulele Gone Bad*.
Les clips d'accroche viraux (hooks) sont faits par Kashing lui-même.

### Sur l'objectif « décoller à la Orelsan »

Un morceau viral, ça ne se planifie pas. Ce qui se planifie, c'est d'avoir assez de bons morceaux
en ligne, bien présentés, au moment où l'un d'eux part, pour que les nouveaux venus trouvent
une chaîne qui donne envie de rester. C'est le rôle des 4 clips de départ.

## Genres : Frenchcore, Hardbass, World fusion

Le catalogue couvre tous les styles, mais KASHING s'en tient à trois familles :
**Frenchcore, Hardbass, World fusion** (le kick Frenchcore/Hardbass mélangé à une musique
d'ailleurs : baile funk, samba, flamenco, musiques des Balkans…). Les morceaux qui n'ont pas
ce kick ne sortent pas sur les comptes KASHING. Ils restent disponibles via le catalogue Kash Studio.

- Instagram et YouTube : uniquement ces trois genres.
- Site : ces trois genres d'abord ; les autres morceaux déjà en ligne passent dans une section
  « Off the map » en fin de playlist (`"focus": false` dans `tracks.js`).
- Hashtags de base : `#frenchcore` `#hardbass` `#worldfusion` selon le morceau, plus `#kashing` partout.

## Fil rouge discret : « ça sonne comme dans ma tête »

Plusieurs tracks parlent du TDAH (*Executive Dysfunction*, *Dopamine Chase*, *Squirrel!*,
*Ten Tabs Open Syndrome*, *Masking Tape*, *Sugar Spike Blues*). On ne l'annonce jamais :
pas de « musique pour TDAH », pas d'explication. Les titres et les légendes suffisent pour
que ceux qui le vivent se reconnaissent.

- Légendes en clins d'œil : « 10 onglets ouverts, 1 seul kick. », « J'étais venu pour quoi déjà ? Squirrel! »,
  « Dopamine trouvée à 200 BPM. »
- Si quelqu'un pose la question en commentaire : réponse courte et sincère, en privé ou en story,
  jamais un post « campagne de sensibilisation ».
- Pas de noms de médicaments dans les posts publics. Dans un contexte rave, une blague sur un
  stimulant peut être lue comme une incitation et faire signaler le compte. Elle peut rester dans le
  morceau, mais pas dans la légende.
- Les Reels de cette série gardent la même direction visuelle que les autres. C'est le son et
  les titres qui portent le sujet, pas l'image.

## Campagne « FEEL THE DROP » — 6 semaines

### Semaine 1 : teasing (aucune track entière)
| Jour | Format | Contenu |
|---|---|---|
| L | 3 posts en mosaïque | Le logo découpé sur 3 posts côte à côte, qui forment une seule image dans la grille |
| Me | Reel 7 s | Écran noir, un kick, le scanner rouge s'allume dans le logo. Texte : « Feel the drop. » |
| V | Reel 10 s | La foule dans le noir, le logo apparaît sur le premier kick. Texte : « Soon. » |
| Stories | quotidien | Sondage « Frenchcore ou Hardbass ? », compte à rebours vers le lancement |

### Semaines 2 et 3 : lancement
- **4 Reels visualizer par semaine** (lun, mer, ven, dim, entre 18 h et 20 h), chacun sur le drop d'une track.
- Ordre : les 3 tracks les plus fortes d'abord. Garde-les pour l'ouverture, pas pour la fin.
- Chaque Reel renvoie au site (« track complète en bio »).

### Semaines 4 et 5 : engagement
- **« Pick the next drop »** : en story, 2 extraits de 10 s, le public vote pour le prochain Reel.
- **Défi kick** : un Reel où le kick est isolé, puis « fais ton edit et identifie @kashingguudenoff ».
  On repartage les meilleures réponses.
- Contacter 5 à 10 **pages de repost Frenchcore et Uptempo** en leur envoyant le meilleur clip.
  C'est le levier de portée le plus rentable sur cette niche.

### Semaine 6 : clips IA
- Sortie des 2 ou 3 clips IA (voir plus bas) sur les tracks qui ont le mieux marché en semaines 2 à 5.

### Ensuite
- 3 Reels par semaine. Les 30 tracks donnent environ 10 semaines de contenu sans répétition,
  puis on refait des Reels sur d'autres passages des tracks qui ont marché.

## Ce qu'on mesure

- **Partages et enregistrements** par Reel, pas les likes. C'est ce qui pousse un Reel dans l'algorithme.
- **Taux de visionnage complet** : si les gens décrochent avant le drop, il faut commencer le clip plus tard.
- Au bout de 2 semaines, on garde les 3 tracks qui partagent le plus et on fait plus de contenu sur elles.
- Optionnel : sponsoriser à 5 €/jour le Reel qui a le mieux marché sans pub au bout de 48 h.
  Ne jamais acheter de followers.

## Direction des clips

### Format A — Visualizer automatique (pour toutes les tracks)
Généré avec `tools/make_clip.py` : 1080x1920, 20 s, démarre sur le drop.
- La première seconde doit déjà frapper : on commence **sur** le drop, pas avant.
- Titre et handle restent au-dessus de la zone couverte par la légende Instagram.
- Couverture du Reel : l'image `.jpg` exportée avec `--cover`.
- Si la détection du drop se trompe (master très compressé) : `--start 62.5`.

### Format B — Clips IA (2 ou 3 tracks phares)
Outils : Runway, Kling, Luma ou Sora (abonnement de ton côté). Je ne peux pas générer
la vidéo moi-même, j'écris les prompts et le découpage.

**Fiche visuelle, à coller en tête de chaque prompt pour que le logo reste identique d'un plan à l'autre :**
```
The KASHING emblem: a brushed steel triangle with riveted corners, a gold disc with two small
horns in its center, a dark horizontal slot across the disc where a red light sweeps left and right.
Dark rave atmosphere, haze, cyan and magenta lasers. No identifiable faces in close-up.
```
Ajouter `assets/kashing_logo.png` comme image de référence pour les outils qui l'acceptent.

**Clip 1 — « Rave en entrepôt »** (15 à 20 s, sur le drop)
1. `dark concrete warehouse, thick haze, cyan and magenta laser beams fanning from the ceiling, slow push-in, cinematic, 35mm`
2. `[emblem] hanging above the stage, the red light in its slot sweeping on each beat, laser reflections on the steel`
3. `wide shot of a crowd from behind, hands raised, strobe light, lasers sweeping`
4. `extreme close-up, gloved hand slamming a fader on a DJ mixer, sparks of light`

**Clip 2 — « Autoroute de nuit »**
1. `night drive on a French highway, orange tunnel lights strobing across the windshield`
2. `POV through windshield, tunnel lights turning into cyan and magenta laser streaks, speed`
3. `[emblem] appears at the end of the tunnel, red light igniting`

**Clip 3 — « La forge »**
1. `molten gold pouring in slow motion on black background, forming a horned disc`
2. `a steel triangle cut by sparks, the gold disc set in its center`
3. `[emblem] floating in haze, red light sweeping, laser beams behind`

**Montage** (CapCut ou Premiere) : à 200 BPM, un temps dure 0,3 s. On coupe tous les 4 temps (1,2 s)
et sur chaque kick fort pendant le drop. Les plans IA sont mis à l'échelle de la track,
jamais l'inverse. On termine sur le logo, scanner allumé, avec « KASHING » dessous.

**Obligation** : Instagram demande d'activer l'étiquette « IA » pour les contenus réalistes générés
par IA. On l'active systématiquement : c'est une règle de la plateforme, et la découverte après coup
coûte plus cher que la transparence.

## Légendes types

**Reel visualizer**
```
SUGAR SPIKE BLUES
Feel the drop. 🔊
Full track: link in bio.
#frenchcore #frenchcoremusic #uptempo #hardcoremusic #rave #kashing
```

**Teasing**
```
Feel the drop.
Soon.
#frenchcore #hardcore #rave
```

## Hashtags (5 à 8 par post, à faire tourner)

- Niche : `#frenchcore` `#frenchcoremusic` `#uptempo` `#terrorcore` `#hardcoremusic` `#hardcore`
- Ambiance : `#rave` `#raveculture` `#lasershow` `#techno`
- Marque : `#kashing` (sur tous les posts)

## Automatisation

- [`Jakeschincariol/instagram-agent-skill`](https://github.com/Jakeschincariol/instagram-agent-skill) :
  des skills Claude pour écrire les accroches et les légendes. Il écrit, tu publies : c'est l'option raisonnable.
- Les agents qui **publient tout seuls** en contournant les détections d'Instagram violent ses règles et
  exposent le compte à un ban. Je les déconseille.
- Pour programmer les posts sans risque : Meta Business Suite.
