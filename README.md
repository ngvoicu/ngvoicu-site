# ngvoicu-site

Personal site for **ngvoicu.dev**: Gabriel Voicu, software engineer. The home page, his work, consulting, an About page,
the writing (articles, the Rust guide and the guide *Becoming an AI Native Company*) and the videos (an index, and a page for each video).

Static, hand-written HTML with inline CSS and a little vanilla JavaScript, no build step,
the same stack as the sibling `kluris-site`, `specmint-site` and `consensflow-site` repos.
Every page is its own folder with an `index.html`.

## Structure

| Path | Page |
|---|---|
| `/` | Home, in this order: the intro (the lead and his watercolour portrait, with the shore band along the bottom); Work (Enterprise work, his own company and Open source, in three columns); what colleagues say (three quotes); Consulting (the text beside the workshop painting, with a button to `/consulting/`); Writing (the six newest pieces, newest first, in one dated list: a date column, one title link per row, then an "All articles" link); Videos (built the same way: the three videos, newest first, each linking to its own page under `/videos/`, then an "All videos" link) |
| `/work/` | Work: Enterprise work (AI agents and application security, five items and "Earlier work"), ZeeSpire (Atlas, Burn The Burnout, InYourMind, and the talks and consulting), and the three open-source tools. Every item but "Earlier work" has a watercolour painting |
| `/consulting/` | Consulting: how I help, the Enhanced Forge Flow, and the talks and training I offer |
| `/about/` | About: his portrait, the timeline, teaching and mentoring (with a watercolour painting), what colleagues say (nine quotes) and skills |
| `/articles/` | Writing: the archive, grouped as guides, building with AI agents, and the Java and Spring archive. Articles only: no videos section |
| `/articles/<slug>/` | The 18 articles, one folder each, images in the article's own `images/` |
| `/articles/rust-for-java-developers/` | The Rust guide: 17 chapters with diagrams, 4 labs and a printable cheat sheet, in the article template |
| `/becoming-an-ai-native-company/` | The AI-native guide |
| `/videos/` | Videos: an index in the Writing page's rows (a date column, the title linking to the video's page, one line about it), in two groups, "My tools" (Kluris, Specmint) and "ConsensFlow, back when it was a plugin" (one video, with a note that it shows the plugin, not today's app), then "Java screencasts": six series from 2016 and 2017, each linking its article and its YouTube playlist, and a link to all the playlists. No embeds and no `VideoObject` on it |
| `/videos/kluris-shared-memory/` | Video page: Kluris, one shared memory for your AI agents (3:13, 16 July 2026) |
| `/videos/specmint-ai-coding-specs/` | Video page: Specmint, AI coding specs that survive the session (3:03, 14 July 2026) |
| `/videos/consensflow-second-opinion/` | Video page: ConsensFlow as the earlier Claude Code plugin and Pi extension (3:26, 21 July 2026), with its history note |
| `/404.html` | Not found (`noindex`, not in the sitemap) |
| `design/` | Source artwork and options, not linked, not indexed |

Assets: `fonts/` (the font files and their licences), `images/brand/` (the header's ink stamp, the footer's
full-name sign-off, the product logos and tiles, and the four social cards), `images/me/` (his portrait), `images/sea/`
(the shore), `images/consulting/`, `images/work/` and `images/about/` (the watercolour paintings), `videos/thumbs/`,
and at the root `favicon.ico`, `favicon-32.png`, `favicon-192.png`, `apple-touch-icon.png`, `sitemap.xml`,
`robots.txt`, `CNAME`, an empty `.nojekyll` and the IndexNow key file `c8042e3ed731c8d3cbcfb6f0514455d5.txt`
(see SEO, Deploy and Deploying).

## Design

White paper, a green-black ink and a bottle-green pen, with his handwritten "GV" ink stamp as the logo.

- **Light only.** `color-scheme: light` and no `prefers-color-scheme` rule anywhere: the site looks the same when
  the system is in dark mode. Tokens: page `#FFFFFF`, panel `#F1F7F4`, text `#1D2A28`, quiet `#52615D`,
  rule `#D5E0DC`, accent `#0B6B5D` (links, buttons, focus ring, the current menu item), and a sunny yellow
  `#F2C230` used only as decoration (the name's underline, quote strokes, selection).
- **Type.** Figtree for all text and JetBrains Mono for code, both OFL and self-hosted in `fonts/` as `woff2`
  split by Unicode range, so a face downloads only when a page uses its characters; `figtree-latin.woff2` is
  preloaded. Code has ligatures off, so `->` shows as typed. No third-party font or script requests.
- **Widths.** Text has no measure of its own: it fills the column it sits in. In a section (`.sec-grid`) the name hangs
  in a 12 rem left column from 64 em and the body fills the rest of the wrap (72 rem), up to the wrap's right edge, the
  same edge as the home page's quotes grid; paragraphs, intros and every list run to that edge. Only the
  home hero's lead keeps its own width (36 rem); buttons, logos and tiles keep their
  sizes. The lines are long (about 110 characters at 1440 px), so section bodies and article bodies are set with a line
  height of 1.7 instead of the base 1.6. Two layouts are narrower on purpose, both on the three equal columns and 2.5 rem
  gap of the home quotes. *Text beside a painting:* the home Consulting section, the `/work/` items and About's "Teaching
  and mentoring" put their text in columns 1 and 2 and a watercolour painting in column 3 from 48 em (about 70 characters
  a line at 1440 px, a text column about 595 px wide); below 48 em the painting stacks, at most 20 rem wide and
  left-aligned, after the button on the home page and under the heading on `/work/` and About. On `/work/`, "Earlier
  work" has no painting but keeps the same two columns for its text, and the section intros (`.sec-intro`) still run the
  full width. *The home Work section:* its three groups (Enterprise work, his own company, Open source) are
  three equal columns from 64 em, two from 48 em, and stacked, with a rule between them, below that; where the browser
  has subgrid, each group's heading, one-line description and list start on shared lines.
- **Logo.** The S4 ink stamp: a round rubber stamp in bottle green, with a bold outer ring, a thin inner ring and a
  bold handwritten "GV" in the middle. `images/brand/gv-stamp-mask.png` (256 × 256) is its alpha as a mask, black on
  clear, and the header paints it in the accent green with CSS (`mask` over `background: var(--accent)`). The favicons are
  not the stamp: they are his portrait (see Favicons). Two of the social cards carry the stamp, the AI-native guide's and
  the video index's, small and inside the card's centre square; the site card and the Rust guide's carry his portrait
  instead and no stamp. The small "AI-native talks
  and consulting" tile carries it too, `images/brand/talks-tile-{36,72}.webp` (the stamp in `#0B6B5D` on white, 78% of the tile; the 36 px one
  drops the thin inner ring, which would smear at that size). Its source is
  `design/logo-v5/S4-ink-stamp.png`. The footer's contact column opens with his full-name signature,
  `images/brand/signature-full-mask.png` and `@2x` (288 × 81 and 576 × 162), a mask trimmed from his drawing, painted in
  ink and linking home.
- **Portrait.** An ink-and-watercolour portrait of him (the P2 drawing, head and shoulders, dark grey shirt, a loose yellow
  wash behind his head), painted on white paper that is cut out to transparent: `images/me/gabriel-portrait-{128,288,400,584,800}.webp`
  (RGBA, square, trimmed to the painting with a small margin; the 128 serves the article byline, the 288, 400, 584 and
  800 serve the home hero and About, the 800 for the home hero on a 2x screen). It has no circle, disc, border or hairline
  (the favicons are the one round crop of it, see Favicons): its own ragged paint edges, soft where the wash
  fades into the paper, are the frame, so it sits straight on the page and over the home shore. Keep it that way, with no
  `border-radius`, clip or `box-shadow` on it. On home, from 48em, it is drawn 120% of its box and centred on it (the box, the
  grid and the text column are unchanged; it spills into the column gap and the gutter), so his head is as big as it was in the
  old round crop. The face, shirt and highlights are opaque; only the outer paint edge is
  partly transparent. The social cards `images/brand/og-site.png` and `og-rust-guide.png` carry the same cut-out on the card's white. Its source is `design/portrait-v2/P2-ink-watercolor.png` (1254 × 1254).
- **Favicons.** His portrait, cropped tight on the head (the top of the hair to just under the beard) and set on a round disc
  filled with the site's yellow `#F2C230`, transparent outside the disc, so the icon stays a circle on a light or a dark browser
  tab (a white disc dissolves into a light tab and leaves a bright rim on a dark one): `favicon.ico` (16, 32 and 48 px),
  `favicon-32.png` and `favicon-192.png`. Google Search asks for a square of at least 8 × 8 px and recommends one larger
  than 48 × 48, in a format it reads (BMP, GIF, ICO, PNG, JPEG, PPM or TIFF, not SVG), so the 192 is the one to offer it.
  `apple-touch-icon.png` (180 × 180) is the same head full bleed on the same
  yellow, opaque and square, because iOS rounds the corners itself and fills any transparency with black. There is no
  SVG icon: the portrait is a watercolour, not vector. Cropped from `images/me/gabriel-portrait-800.webp`. Every page
  links the four (`favicon.ico`, `favicon-192.png`, `favicon-32.png`, the apple-touch icon).
- **Shore.** A pencil-and-watercolour seashore, purely decorative (`alt=""`, still): a low, mirrored band along the bottom of the home hero, under the portrait and the buttons (its sand on the portrait's side, the water and foam towards the right, faded at its top, bottom and ends, hanging a little into the white above the next section), and a thin faded strip that opens every page's footer; `images/sea/pencil-shore-{800,1600}.webp` and `pencil-shore-strip-{1200,2400}.webp`.
- **Watercolour illustrations.** The home Consulting section (the workshop), every `/work/` item but "Earlier work" and About's "Teaching and mentoring"
  section carry an ink-and-watercolour illustration on white paper, with no frame, border or shadow (alt text describes the scene, with no company or
  place names). They are `images/consulting/workshop-{400,800,1200}.webp` (the workshop painting: the home Consulting section, and the `/work/` Talks item
  reuses the same files), `images/work/<name>-{400,800,1200}.webp` (the other 11 `/work/` items) and `images/about/mentoring-{400,800,1200}.webp`
  (4:3, lazy-loaded, with a `srcset` and `sizes` that match the rendered width), made from the 1600 × 1200 PNGs in `design/consulting/`,
  `design/work/` and `design/about/`. Their white margins melt into the page, so, like the portrait, they take no `border-radius`, clip or `box-shadow`.
  The painting sits in column 3 of the three-column grid, top-aligned with the text's first line (the heading on `/work/`): see Widths.
- **Motto.** "Software Engineer since before AI. AI-Native Now." under the name in the header and under the signature in the footer, verbatim.
- **Product logos.** Specmint, Kluris and ConsensFlow use their official artwork,
  `images/brand/{specmint,kluris,consensflow}-logo.webp`, on a small navy `#021720` tile so each keeps its colours.
  The Atlas, Burn The Burnout and InYourMind products (his own company's) have a square tile each, on its own light ground baked into the image
  (`images/brand/{atlas,burn-the-burnout,inyourmind}-tile-{36,72}.webp`), with a hairline round it so a white one reads on the page.
- **Social cards.** 1200 × 630 RGB PNGs under 300 KB, drawn with Pillow in the site's palette and Figtree, all in
  `images/brand/`: `og-site.png` (every page but the two guides, the video index and the video pages: the home page, Work,
  Consulting, About, the Writing index, the 18 articles and `/404.html`), `og-rust-guide.png` (the Rust guide),
  `og-ai-native-guide.png` (the AI-native guide) and `og-videos-index.png` (the video index). Each video page uses its own
  thumbnail (`videos/thumbs/*.jpg`, 1280 × 720) as its social image. Their `og:image:alt` says what the card shows.
  - **The layout rule.** Teams, WhatsApp, Slack's compact view and others crop a card to a square or near-square round its
    centre, so everything that must be seen sits inside the centre square, 630 × 630, x 285 to 915: the portrait, the words,
    the rule under the title and the stamp where a card has one. Nothing is cut at x 285 or at x 915: no text and no stamp
    crosses either line, and the text keeps a margin inside them. The outer bands hold only things that still look whole
    when cut off: white paper and the yellow wash, which is the wash behind his portrait spread out to the two sides. The
    card also has to look composed in the full 1.91:1 view that LinkedIn, X, Slack's large preview and iMessage show.
  - **New file name when a card changes.** Chat apps and LinkedIn cache a preview by its image URL, so a redrawn card
    under its old name would keep showing the old one for anyone who pastes the link again.

### One shell

Every page carries the same shell inline, copied rather than linked: the fonts, the tokens, the base styles, the
header (the stamp, name, and the menu Work, Writing, Videos, Consulting, About, each its own page) and the footer. The footer opens
with the shore strip; its first column is the contact block (`id="contact"`): his full-name signature linking home, the
motto, the email and the phone. Then come the Pages, Open source and Elsewhere (GitHub, LinkedIn, YouTube, Medium)
lists. There is no contact section in `<main>` and no contact page. The reference is **SHELL v2**, `SITE-28-shell/SHELL.md` in the
`site-evidence` folder beside the sites; the home page is its source, byte for byte, and SHELL v2 says which
menu item each page marks as current. Inner pages add the title block (breadcrumb and `h1`, and the dateline on
articles and video pages). On every inner page, the articles and the AI-native guide included, it starts on the wrap's left edge, the
same x as the header's logo, the home page's name and the section names, at every width. On the menu pages (Work,
Consulting, About, Writing, Videos) nothing sits under the `h1`: no sub-header text and no row of links.
A line under the `h1` exists only on `/404.html` (its message) and on the two long guides (their subtitles).

### Article template

An article is `<div class="wrap post">` holding an `<article>` (title block, `div.body`, the author note) and a
"Keep reading" list. The title block starts on the wrap's left edge, with a rule under it across the wrap. From 64 em
`div.body` is the section pages' grid: a 12 rem left column, then the text column, which runs to the wrap's right edge.
Everything in the body (paragraphs, code blocks, tables, figures, `figure.wide` included, quotes, videos) fills the text
column; the "Contents" list, where an article has one, sits in the left column and stays in view while the body scrolls
past, and stops where the body ends, above the author note. Without Contents the left column stays empty, as it does
under a section name. The author note and Keep reading start on the text column. Below 64 em it is one column, in
source order. The AI-native guide uses the same template; its Contents stops at the Forge, which runs edge to edge
between its two bodies. Long URLs in running text wrap. Code blocks and tables scroll sideways inside their own
labelled box (a Tab stop with edge shadows); the page itself never scrolls sideways. Articles with six or more
sections open with a "Contents" heading and a plain list of links. The Rust guide uses the same template: its 17
chapters sit in one block beside Contents, which from 64 em is set a little smaller so the whole list fits in the window,
and marks the chapter you are reading. Its diagrams, its ownership stepper and its visibility explorer keep their own
colours (Java blue, Rust orange); everything around them uses the site's tokens.

A video page (`/videos/<slug>/`) is the same template: the title block with the duration under the byline, then the
player (`div.ratio`, a `youtube-nocookie` iframe that loads at once), the video's own text, a "Watch on YouTube" link, the author note
and "Keep watching", the other two videos. The menu marks Videos as current. The page carries the video's `VideoObject`
(name, description, `thumbnailUrl`, `uploadDate` as YouTube gives it, duration, `embedUrl`, and the page's
`url`, with no `contentUrl`: see SEO) and its breadcrumb in JSON-LD, and its `og:image` is the thumbnail. That `VideoObject` is the only one on the
site for the video: an article that embeds the same video carries none of its own.

### Enhanced Forge Flow

On `/consulting/` (`#forge-flow`) and in the guide: the ten-step delivery loop from the *Becoming an AI Native
Company* deck, with Kluris and Specmint under *Write Spec*, ConsensFlow with example reviewer models under both
review gates, and Kluris under *Update Memory*. It is one `<ol>` on a CSS grid with drawn arrows, so a screen reader
hears only the ordered list: a vertical list below 43.75 em, two rows of five from 43.75 em, one row of ten from
90 em. Its panel runs edge to edge.

### Motion

Almost none. Links and buttons answer the pointer with colour only. The only animations are the Forge trace on
`/consulting/` and in the guide, and the Rust guide's five moving diagrams (each plays once, for about five seconds);
each runs only when its Play button is pressed.
Without JavaScript, or with `prefers-reduced-motion: reduce`, the Play buttons are hidden, nothing moves and every
page shows everything.

### Contacts

The email (`office@ngvoicu.dev`) and the phone are in every page's footer, in the contact column (`#contact`).
Every `mailto:` link is wrapped in `<!--email_off-->…<!--/email_off-->` so Cloudflare's email
obfuscation leaves it alone. Cloudflare also rewrites text that only looks like an address, such as the `git@github.com`
in a `git clone` line, into "[email protected]" and adds a script of its own: wrap that in the same markers. After a
deploy, run the check over every page in the sitemap, not only the home page (see Deploying): it must print `0` for each.

## Anchors that other sites link to

Keep `id="consulting"` on the home page: the product READMEs and sites link to
`https://ngvoicu.dev/#consulting`, which lands on its short consulting section (the menu goes to `/consulting/`). `#open-source`, `#specmint`, `#kluris`, `#consensflow`
and `#work` also still resolve. `videos/thumbs/specmint.jpg` and `videos/thumbs/kluris.jpg`
are hotlinked by the sibling sites (and are the video pages' social images): keep their names and bytes.

## SEO

Every rule here applies to every indexable page, so a new page starts from a page that already follows them.

- **Sitemap.** `sitemap.xml` lists each indexable page once, with a `<lastmod>` on every URL (`YYYY-MM-DD`). Bump a page's
  `lastmod` when its text, structured data or links change; leave it for a style or copyright tweak, because Google only
  uses a `lastmod` that is consistently accurate. No `<changefreq>` and no `<priority>`: Google ignores both. `/404.html`,
  `design/` and the IndexNow key file are not in it. `robots.txt` allows everything except `/design/` and names the sitemap.
- **Titles and descriptions.** A `<title>` is at most 60 characters. A `meta name="description"` is 140–160 characters,
  and `og:description` and `twitter:description` carry the same text.
- **Dates.** `datePublished` is the date a piece was first published anywhere, Medium included, not the day it reached
  this site. `dateModified` changes only when the words change.
- **Structured data.** One `Person` (`"@id": "https://ngvoicu.dev/#person"`), defined in full and identically on the home
  page and About. Every other block (articles, videos, breadcrumbs) refers to it by `@id` and does not repeat it. Never
  `LocalBusiness` or `ProfessionalService`, and no `address`, `geo` or `areaServed`.
- **`VideoObject`.** `name`, `description`, `thumbnailUrl`, `uploadDate` exactly as YouTube gives it (a timezone-aware
  date-time), `duration`, `embedUrl` and the page's `url`. No `contentUrl`: Google says it must be the video file, and a
  watch page is not one.
- **IndexNow.** The key file at the root, `c8042e3ed731c8d3cbcfb6f0514455d5.txt`, holds exactly the key and nothing else (no
  newline). The key is public by design. It lets Bing, Yandex, Naver, Seznam and Yep take the URLs you send them, and the
  list is shared between them. **Google does not use IndexNow:** for Google the sitemap and Search Console are the way.
  How to send URLs is under Deploying.

## Preview locally

```bash
python3 -m http.server 4173 --bind 127.0.0.1
# open http://127.0.0.1:4173/
```

Run it from this folder (or add `--directory` with its path). Pages use root-relative paths (`/fonts/…`,
`/images/…`), so open the site through the server, not as files.

## Deploy

GitHub Pages with a custom domain (`CNAME` → ngvoicu.dev). Push `main` to deploy.
DNS: apex A records to GitHub Pages IPs (185.199.108–111.153) or ALIAS/ANAME to
`ngvoicu.github.io`.
GitHub can't enforce HTTPS here: it holds no certificate for the domain. Cloudflare redirects http to https
with "Always Use HTTPS", and .dev is HSTS-preloaded in browsers.

The empty `.nojekyll` at the root stays. Without it Pages runs Jekyll over the repo, which renders `design/README.md` as a
themed page at `/design/` and publishes a theme stylesheet at `/assets/css/style.css`. With it Pages serves the files as
they are. Nothing here uses Jekyll: no front matter, no Liquid tags, no `_config.yml`, no folder or file that starts with
`_`. The raw `README.md` files and the `design/` files are still public by direct URL.

## Deploying (read this — Pages builds get stuck)

Push `main` to `upstream` (GitHub) and Pages builds automatically, but builds **regularly hang in `"building"`**. After every push:

```bash
gh api repos/ngvoicu/ngvoicu-site/pages/builds/latest --jq .status   # expect "built" within ~1 min
gh api -X POST repos/ngvoicu/ngvoicu-site/pages/builds               # re-queue if it sits in "building"
```

Then confirm the change is actually live: `curl -s https://ngvoicu.dev/ | grep '<something-from-your-change>'`.

Then check Cloudflare's email obfuscation on every page in the sitemap. Every line must start with `0`:

```bash
curl -s https://ngvoicu.dev/sitemap.xml | sed -n 's|.*<loc>\(.*\)</loc>.*|\1|p' | while read -r u; do
  printf '%s  %s\n' "$(curl -s "$u" | grep -c 'cdn-cgi/l/email-protection')" "$u"
done
```

Then tell IndexNow what changed, once the key file answers with the key
(`curl -s https://ngvoicu.dev/c8042e3ed731c8d3cbcfb6f0514455d5.txt`). The first time, send every URL in the sitemap in one
request, so the engines learn the whole site. After that send **only the URLs whose page changed in this deploy**, with the
trailing slash exactly as in the sitemap:

```bash
curl -sS -X POST https://api.indexnow.org/indexnow -H 'Content-Type: application/json; charset=utf-8' -w '\nHTTP %{http_code}\n' -d '{
  "host": "ngvoicu.dev",
  "key": "c8042e3ed731c8d3cbcfb6f0514455d5",
  "keyLocation": "https://ngvoicu.dev/c8042e3ed731c8d3cbcfb6f0514455d5.txt",
  "urlList": ["https://ngvoicu.dev/work/", "https://ngvoicu.dev/articles/"]
}'
```

Expect `200` or `202`, which only means "received". `host` is `ngvoicu.dev`, never `www`. Do not resubmit unchanged URLs.
Google does not read IndexNow: request a recrawl there from Search Console.
