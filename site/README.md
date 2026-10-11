# Site KIKFORGE — ghost production Frenchcore

Site statique d'une page (HTML/CSS/JS, aucune dépendance ni build).

## Lancer en local

Ouvrir `index.html` dans un navigateur, ou :

```sh
python3 -m http.server -d site 8000
```

## Le contenu

- **Hero** : accroche + bouton « Tester le kick ». Il joue un kick frenchcore synthétisé en Web Audio à
  200 BPM (aucun fichier audio) et anime un oscilloscope.
- **Process** en 4 étapes, **Offres** (Exclusive / Sur mesure / Pack identité), **Catalogue**
  exclusif, **Garanties**, **FAQ**, **Formulaire de brief**.

## À remplacer avant la mise en ligne

| Quoi | Où |
|---|---|
| Nom `KIKFORGE` (provisoire) | `index.html` (logo, titre, footer) |
| Email `contact@kikforge.fr` | `index.html` (formulaire + footer) |
| Prix (290 € / 590 €) | section `#offres` |
| Tracks du catalogue (fictives) | section `#catalogue` |
| Lien Instagram | footer |

Le formulaire utilise `mailto:` (ouvre le client mail). Pour un vrai envoi, brancher Formspree,
Netlify Forms ou une fonction serverless.

## Hébergement

Dossier `site/` déployable tel quel sur GitHub Pages, Netlify ou Vercel.

## Références utilisées

- [Impeccable](https://github.com/pbakaus/impeccable) : règles anti-« AI slop » (pas de dégradés
  violets, pas de cartes imbriquées, accroches précises, un CTA principal par section).
- Site de [Dr. Peacock](https://www.dr-peacock.com) : sorties, tournée, store, Harderclass.
  Il ne fait rien de spécifique au ghost production, qui reste à inventer.
- [Awwwards — Sound & Audio](https://www.awwwards.com/websites/sound-audio/) : typo massive,
  fond sombre, interaction sonore.
