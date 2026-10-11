# Prompts Suno — KASHING

Deux familles de morceaux, deux façons de prompter :

| | Morceaux d'artiste | Morceaux « club » |
|---|---|---|
| Pour | YouTube, Instagram, écoute | DJ, sets, gros systèmes son |
| Tempo | libre, il peut dériver (l'effet « dans ma tête ») | **fixe**, du début à la fin |
| Début / fin | comme tu veux | **intro et outro longues, kick seul** |
| Exemples actuels | *Sugar Spike Blues*, *Ten Tabs* | *Executive Dysfunction*, *Ukulele Gone Bad*, *Here We Bounce* (déjà proches) |

Les morceaux d'artiste ne changent pas : c'est ta signature. Les prompts ci-dessous servent
uniquement à produire **en plus** des morceaux que les DJ peuvent passer.

## Modèle « club » (à coller dans Style)

```
frenchcore, 200 bpm, steady tempo, constant bpm throughout, no tempo change,
distorted kick, DJ-friendly, long intro, long outro, club mix
```

Variantes de genre :
- Hardbass : `hardbass, 150 bpm, steady tempo, constant bpm, ...`
- Trance fusion : `frenchcore trance fusion, 190 bpm, uplifting lead, steady tempo, ...`

## Structure (à coller dans Lyrics, en mode instrumental ou wordless)

```
[Intro: kick only, 32 bars, DJ intro]
[Build-up]
[Drop]
[Breakdown: no kick, melody only]
[Build-up]
[Drop]
[Outro: kick only, 32 bars, DJ outro]
[End]
```

À éviter dans les morceaux club :
- `[Outro: abrupt cut]` et `kick starts immediately` : c'est ce qui rend tes morceaux actuels
  difficiles à mixer ;
- `[Speed Up]`, `[Slow Down]`, `tempo change` ;
- un breakdown de plus de 16 mesures (le DJ perd le fil).

## Ce que Suno respecte mal

Suno ne suit pas toujours le tempo ni la longueur demandés. Les balises augmentent les chances,
elles ne garantissent rien. D'où l'intérêt de générer plusieurs versions et de garder la meilleure.

Après génération, `python3 tools/dj_check.py fichier.mp3` mesure le tempo, l'intro, l'outro et le
volume. Garde les versions où :
- le tempo varie de 3 BPM au plus ;
- l'intro et l'outro font au moins 16 mesures ;
- le true peak reste sous −0,3 dB.

Le volume reste plus bas que les masters Frenchcore du commerce, et Suno ne permet pas de le régler.
Les DJ ajustent le gain, donc ce n'est pas bloquant pour faire tourner un morceau. Ça le devient
pour un label.

## Pour un DJ : quoi envoyer

- Le **WAV** (pas le MP3), nommé `KASHING - Titre (Club Mix).wav`.
- Le BPM et la tonalité dans le message.
- Un seul morceau à la fois, avec un lien d'écoute (SoundCloud privé ou YouTube non répertorié)
  et un lien de téléchargement direct. Pas de compte à créer pour l'écouter.
