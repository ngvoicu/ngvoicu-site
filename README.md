# ngvoicu-site

Personal site for **ngvoicu.dev** — Gabriel Voicu, software engineer.

Single static `index.html`, inline CSS/JS, no build step — same stack as the sibling
`kluris-site`, `specmint-site`, and `consensflow-site` repos in `~/Projects/ngvoicu/sites/`.

## Design

The page is laid out like a Kluris neuron about its author: a frontmatter block as the
hero, product cards with `related:` synapse links, and career history rendered as a
`git log`. Palette is Black Sea marine (Constanța); type is Archivo (expanded widths)
plus IBM Plex Mono.

Positioned as an AI-native consulting landing: the `lobe: consulting` section carries
the "Becoming an AI Native Company" talk/workshop offer and the Enhanced Forge Flow
diagram ported as-is (markup, CSS, and product logos) from the deck at
`~/Projects/others/ai-presentation-beginners/ai-native-scroll-prototype.html` — scoped
under `.eff` with its own palette vars; it breaks out of the text column and scrolls
horizontally on small screens. The work section ends with a worked-with strip (ZeeSpire
logo image + typographic wordmarks; no third-party logo artwork is bundled deliberately).

## Deploy

GitHub Pages with a custom domain (`CNAME` → ngvoicu.dev). Push `main` to deploy.
DNS: apex A records to GitHub Pages IPs (185.199.108–111.153) or ALIAS/ANAME to
`ngvoicu.github.io`, plus HTTPS enforced (required — .dev is HSTS-preloaded).

## Preview locally

```bash
python3 -m http.server 4173
# open http://localhost:4173
```
