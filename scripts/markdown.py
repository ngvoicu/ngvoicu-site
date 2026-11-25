#!/usr/bin/env python3
"""The markdown version of every page in sitemap.xml, written beside the page as index.html.md.

    python3 scripts/markdown.py           write or refresh every index.html.md, and delete any whose page is gone
    python3 scripts/markdown.py --check   change nothing; exit 1 if a markdown file is missing, out of step with its
                                          page or left over from a page that is gone, if a page lacks its two
                                          <link>s, or if llms.txt and the sitemap disagree

A markdown version says what the page shows on a phone without JavaScript (the Rust guide's diagrams then have
their text versions), from the page's <main>: navigation (breadcrumb, Contents, Keep reading), buttons, SVG and
anything hidden are left out. Code blocks keep their lines and lose the display line numbers; a table cell that
spans columns is repeated in each column it spans; links and images become absolute URLs; a YouTube player becomes
a link to the video. The front matter carries the page's title, description and canonical URL, and its dates.

Standard library only, nothing to install. Run it from anywhere after editing a page, and commit what it writes.
--check compares the converter with the files it wrote; whether the converter reads the pages right is checked
from outside it, in a browser (see the README).
"""
import html
import json
import os
import re
import sys
from html.parser import HTMLParser

SITE = "https://ngvoicu.dev"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD_NAME = "index.html.md"

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
# Left out wherever they are: not text a reader reads in <main>.
DROP_TAGS = {"script", "style", "svg", "button", "template", "nav", "form", "dialog", "noscript", "head", "select", "input"}
# Hidden on a phone without JavaScript (the CSS of the Rust guide): the drawn diagrams, which have HTML text
# versions (.figalt, .vx-alt, .st-alt) beside them, and the controls of the interactive ones.
DROP_CLASSES = {"figwin", "idea-win", "vx-win", "st-mem", "js-only", "js-only-block", "fig-hint", "play", "skip"}
BLOCK = {"address", "article", "aside", "blockquote", "details", "dd", "div", "dl", "dt", "fieldset", "figcaption",
         "figure", "footer", "h1", "h2", "h3", "h4", "h5", "h6", "header", "hr", "iframe", "li", "main", "ol", "p",
         "pre", "section", "summary", "table", "ul", "caption", "tbody", "thead", "tfoot", "tr", "td", "th"}
HEADINGS = {"h1", "h2", "h3", "h4", "h5", "h6"}


class Node:
    __slots__ = ("tag", "attrs", "children", "parent")

    def __init__(self, tag, attrs, parent):
        self.tag, self.attrs, self.children, self.parent = tag, attrs, [], parent

    @property
    def classes(self):
        return set((self.attrs.get("class") or "").split())


class TreeBuilder(HTMLParser):
    """A plain DOM tree. The pages are hand-written and well formed; a stray end tag is an error."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root", {}, None)
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        node = Node(tag, {k: (v if v is not None else "") for k, v in attrs}, self.cur)
        self.cur.children.append(node)
        if tag not in VOID:
            self.cur = node

    def handle_startendtag(self, tag, attrs):
        self.cur.children.append(Node(tag, {k: (v if v is not None else "") for k, v in attrs}, self.cur))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        n = self.cur
        while n is not None and n.tag != tag:
            n = n.parent
        if n is None:
            raise ValueError(f"end tag </{tag}> with no open <{tag}> (line {self.getpos()[0]})")
        if n is not self.cur and self.cur.tag not in ("p", "li"):
            raise ValueError(f"</{tag}> closes <{self.cur.tag}> (line {self.getpos()[0]})")
        self.cur = n.parent

    def handle_data(self, data):
        self.cur.children.append(data)


def find(node, tag):
    for c in node.children:
        if isinstance(c, Node):
            if c.tag == tag:
                return c
            r = find(c, tag)
            if r:
                return r
    return None


def dropped(n):
    a = n.attrs
    if n.tag in DROP_TAGS or "hidden" in a or a.get("aria-hidden") == "true":
        return True
    if n.classes & DROP_CLASSES:
        return True
    # the stepper's text version hides the parts of later steps
    if "hide" in n.classes and has_ancestor_class(n, "st-alt"):
        return True
    return False


def has_ancestor_class(n, cls):
    p = n.parent
    while p is not None:
        if isinstance(p, Node) and cls in p.classes:
            return True
        p = p.parent
    return False


def absolute(url, page_path):
    url = (url or "").strip()
    if not url:
        return url
    if re.match(r"^[a-z][a-z0-9+.-]*:", url, re.I):
        return url
    if url.startswith("//"):
        return "https:" + url
    if url.startswith("#"):
        return SITE + page_path + url
    if url.startswith("/"):
        return SITE + url
    # relative to the page's folder
    base = page_path if page_path.endswith("/") else page_path.rsplit("/", 1)[0] + "/"
    parts = []
    for seg in (base + url).split("/"):
        if seg == "..":
            if parts:
                parts.pop()
        elif seg != ".":
            parts.append(seg)
    return SITE + "/".join(parts)


def url_md(u):
    """A link destination markdown reads back unchanged."""
    u = u.replace(" ", "%20").replace("(", "%28").replace(")", "%29").replace("<", "%3C").replace(">", "%3E")
    return u


# ---------- inline ----------

ESC_INLINE = re.compile(r"([\\`*\[\]<>|])")


def esc_text(s):
    s = ESC_INLINE.sub(r"\\\1", s)
    # an underscore can open or close emphasis only at a word edge
    s = re.sub(r"(?<![A-Za-z0-9])_|_(?![A-Za-z0-9])", r"\\_", s)
    # text that would read as an entity
    s = re.sub(r"&(?=#?[A-Za-z0-9]+;)", "&amp;", s)
    # ~~ would read as strikethrough in GFM
    s = s.replace("~", "\\~")
    return s


def code_span(text):
    text = re.sub(r"\s+", " ", text)
    longest = max((len(m) for m in re.findall(r"`+", text)), default=0)
    fence = "`" * (longest + 1)
    pad = " " if text.startswith("`") or text.endswith("`") or (text.startswith(" ") and text.endswith(" ") and text.strip()) else ""
    return f"{fence}{pad}{text}{pad}{fence}"


def raw_text(n):
    out = []
    for c in n.children:
        if isinstance(c, str):
            out.append(c)
        elif not dropped(c):
            out.append("\n" if c.tag == "br" else raw_text(c))
    return "".join(out)


GLUE_TAGS = {"b", "strong", "span", "i", "em", "small", "time", "a"}


class Inline:
    """Inline content as a list of pieces; ' ' runs are collapsed at the end. '\n' marks a hard line break."""

    def __init__(self, page):
        self.page = page

    def render(self, nodes):
        parts = []
        prev = None
        for c in nodes:
            if isinstance(c, str):
                parts.append(esc_text(re.sub(r"[ \t\r\n\f]+", " ", c)))
                prev = None
                continue
            if dropped(c):
                continue
            # two elements set side by side with nothing between them, which the page shows as separate blocks
            # (a term and its explanation in a box): keep a space between them
            rendered = self.element(c)
            if prev is not None and c.tag in GLUE_TAGS and prev.tag in GLUE_TAGS and not re.match(r"[,.;:!?)]", rendered):
                parts.append(" ")
            # a diagram's heading and its note, drawn on two lines with nothing between them in the source
            elif c.tag == "span" and isinstance(c.parent, Node) and c.parent.tag == "p" and c.parent.classes & {"fa-h", "fa-gh"}:
                parts.append(" ")
            parts.append(rendered)
            prev = c
        return "".join(parts)

    def element(self, n):
        t = n.tag
        if t == "br":
            return "\n"
        if t == "img":
            alt = re.sub(r"\s+", " ", n.attrs.get("alt", "")).strip()
            if not alt:
                return ""
            return f"![{esc_text(alt)}]({url_md(absolute(n.attrs.get('src', ''), self.page))})"
        if t in ("code", "kbd", "samp", "tt"):
            text = raw_text(n)
            return code_span(text) if text.strip() else text
        inner = self.render(n.children)
        if t in ("strong", "b"):
            return wrap(inner, "**")
        if t in ("em", "i", "cite"):
            return wrap(inner, "*")
        if t == "a":
            href = n.attrs.get("href")
            if not href or not inner.strip():
                return inner
            lead, core, trail = split_space(inner)
            return f"{lead}[{core}]({url_md(absolute(href, self.page))}){trail}"
        if t in BLOCK:
            # a block inside inline content (a list item's paragraph, a table cell's list): its own line
            return "\n" + inner.strip() + "\n"
        return inner


def split_space(s):
    m = re.match(r"^(\s*)(.*?)(\s*)$", s, re.S)
    return m.group(1), m.group(2), m.group(3)


def wrap(inner, mark):
    lead, core, trail = split_space(inner)
    if not core:
        return inner
    if "\n" in core:  # emphasis cannot cross a line break: mark each line
        return lead + "\n".join(wrap(x, mark) if x.strip() else x for x in core.split("\n")) + trail
    return f"{lead}{mark}{core}{mark}{trail}"


def tidy_inline(s, hard_breaks=True):
    """Collapse spaces; turn the '\n' marks into hard line breaks (or spaces); escape what would start a block."""
    lines = [re.sub(r" {2,}", " ", x).strip() for x in s.split("\n")]
    lines = [x for x in lines if x]
    if not hard_breaks:  # one line (a heading, a table cell): only its start can be misread
        one = " ".join(lines)
        return ("\\" + one) if one.startswith("#") else one
    lines = [escape_line_start(x) for x in lines]
    return "\\\n".join(lines)


def escape_line_start(x):
    if re.match(r"^(#{1,6}(\s|$)|[-+*](\s|$)|>|=+\s*$|-{3,}\s*$)", x):
        return "\\" + x
    m = re.match(r"^(\d{1,9})([.)])(\s|$)", x)
    if m:
        return m.group(1) + "\\" + x[len(m.group(1)):]
    return x


# ---------- blocks ----------

class Blocks:
    def __init__(self, page):
        self.page = page
        self.inline = Inline(page)

    def render(self, node):
        """The blocks of a container: runs of inline content become paragraphs, block children their own blocks."""
        blocks, run = [], []

        def flush():
            if run:
                text = tidy_inline(self.inline.render(run))
                if text:
                    blocks.append(text)
                run.clear()

        for c in node.children:
            if isinstance(c, str) or (c.tag not in BLOCK and c.tag != "img") or (c.tag == "img" and run_has_text(run)):
                if isinstance(c, Node) and dropped(c):
                    continue
                run.append(c)
                continue
            if dropped(c):
                continue
            if c.tag == "img":
                run.append(c)
                continue
            flush()
            blocks.extend(self.block(c))
        flush()
        return blocks

    def block(self, n):
        t = n.tag
        if t in HEADINGS:
            text = tidy_inline(self.inline.render(n.children), hard_breaks=False)
            return ["#" * int(t[1]) + " " + text] if text else []
        if t == "p" or t == "summary" or t == "dt" or t == "figcaption" or t == "caption":
            if t == "dt" or t == "summary":
                text = tidy_inline(self.inline.render(n.children))
                return [wrap(text, "**")] if text else []
            return self.render(n)
        if t == "hr":
            return ["---"]
        if t == "pre":
            return self.pre(n)
        if t in ("ul", "ol"):
            return [self.list(n)] if self.list(n) else []
        if t == "blockquote":
            inner = "\n\n".join(self.render(n))
            return ["\n".join(("> " + x) if x else ">" for x in inner.split("\n"))] if inner else []
        if t == "table":
            return self.table(n)
        if t == "iframe":
            return self.iframe(n)
        if t == "li":  # a stray list item outside a list
            return self.render(n)
        return self.render(n)

    def pre(self, n):
        out = []
        label = n.attrs.get("data-name")
        if label:
            out.append(f"*{esc_text(label)}*")
        code = code_text(n)
        longest = max((len(m) for m in re.findall(r"`{3,}", code)), default=2)
        fence = "`" * (longest + 1)
        out.append(f"{fence}\n{code}\n{fence}")
        return out

    def list(self, n):
        ordered = n.tag == "ol"
        num = int(n.attrs.get("start", "1") or 1)
        items = []
        for li in n.children:
            if isinstance(li, str) or li.tag != "li" or dropped(li):
                continue
            mark = f"{num}. " if ordered else "- "
            num += 1
            blocks = self.render(li)
            if not blocks:
                continue
            pad = " " * len(mark)
            lines = []
            for i, b in enumerate(blocks):
                for j, line in enumerate(b.split("\n")):
                    if i == 0 and j == 0:
                        lines.append(mark + line)
                    else:
                        lines.append((pad + line) if line else "")
                if i < len(blocks) - 1 and not re.match(r"^(- |\d+\. )", blocks[i + 1]):
                    lines.append("")
            # an item is loose (blank lines inside) when it holds more than a line and its own sub-list
            items.append(("\n".join(lines), sum(1 for b in blocks if not re.match(r"^(- |\d+\. )", b)) > 1))
        if not items:
            return ""
        loose = any(multi for _, multi in items)
        return ("\n\n" if loose else "\n").join(x for x, _ in items)

    def table(self, n):
        out = []
        cap = find(n, "caption")
        if cap is not None and not dropped(cap):
            out.extend(self.render(cap))
        rows, head = [], 0
        for section in [n] + [c for c in n.children if isinstance(c, Node) and c.tag in ("thead", "tbody", "tfoot")]:
            for tr in section.children:
                if isinstance(tr, str) or tr.tag != "tr" or dropped(tr):
                    continue
                row, all_th = [], True
                for cell in tr.children:
                    if isinstance(cell, str) or cell.tag not in ("td", "th") or dropped(cell):
                        continue
                    all_th = all_th and cell.tag == "th"
                    text = tidy_inline(self.inline.render(cell.children), hard_breaks=False)
                    text = text.replace("\\\n", " ")
                    span = int(cell.attrs.get("colspan", "1") or 1)
                    row.append((text, span))
                if row:
                    if section.tag == "thead" or (not rows and all_th):
                        head += 1
                    rows.append(row)
        if not rows:
            return out
        width = max(sum(n for _, n in r) for r in rows)
        # a cell that spans some columns says the same for each of them, so it is repeated in each; a cell that
        # spans the whole row is a group heading, written once in the first column
        rows = [[text] + [""] * (width - 1) if len(r) == 1 and n == width else [t for t, k in r for _ in range(k)]
                for r in rows for text, n in [r[0]]]
        rows = [r + [""] * (width - len(r)) for r in rows]
        if head != 1:
            # markdown tables have exactly one header row: a table without one gets an empty one
            if head == 0:
                rows.insert(0, [""] * width)
        lines = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * width]
        lines += ["| " + " | ".join(r) + " |" for r in rows[1:]]
        out.append("\n".join(lines))
        return out

    def iframe(self, n):
        src = n.attrs.get("src", "")
        title = esc_text(n.attrs.get("title", "") or "Video")
        m = re.search(r"/embed/([A-Za-z0-9_-]{6,})", src)
        if m and m.group(1) != "videoseries":
            return [f"[{title}](https://www.youtube.com/watch?v={m.group(1)})"]
        m = re.search(r"[?&]list=([A-Za-z0-9_-]+)", src)
        if m:
            return [f"[{title}](https://www.youtube.com/playlist?list={m.group(1)})"]
        return [f"[{title}]({url_md(absolute(src, self.page))})"] if src else []


def run_has_text(run):
    return any(isinstance(x, str) and x.strip() or isinstance(x, Node) for x in run)


def code_text(pre):
    """The code as a reader copies it: each line-span (.ol) a line, the line numbers (.ln) left out."""
    out = []

    def walk(n):
        for c in n.children:
            if isinstance(c, str):
                out.append(c)
            elif c.tag == "br":
                out.append("\n")
            elif "ln" in c.classes or dropped(c):
                continue
            else:
                walk(c)
                if "ol" in c.classes and not "".join(out).endswith("\n"):
                    out.append("\n")

    walk(pre)
    text = "".join(out).replace("\u00a0", " ")
    if text.startswith("\n"):  # HTML drops the newline right after <pre>
        text = text[1:]
    lines = [x.rstrip() for x in text.split("\n")]
    while lines and not lines[-1]:
        lines.pop()
    while lines and not lines[0]:
        lines.pop(0)
    return "\n".join(lines)


# ---------- pages ----------

def head_meta(doc, attr, key):
    m = re.search(r'<meta\s+%s="%s"\s+content="([^"]*)"' % (attr, re.escape(key)), doc)
    return html.unescape(m.group(1)) if m else ""


def page_dates(doc):
    pub = mod = ""
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', doc, re.S):
        data = json.loads(block)
        nodes = data.get("@graph", [data]) if isinstance(data, dict) else data
        for n in nodes:
            if isinstance(n, dict) and n.get("@type") in ("Article", "VideoObject"):
                pub = pub or n.get("datePublished") or n.get("uploadDate", "")
                mod = mod or n.get("dateModified", "")
    return pub[:10], mod[:10]


def page_markdown(page_path):
    doc = open(os.path.join(ROOT, page_path.lstrip("/"), "index.html"), encoding="utf-8").read()
    tb = TreeBuilder()
    tb.feed(doc)
    tb.close()
    main = find(tb.root, "main")
    if main is None:
        raise ValueError(f"{page_path}: no <main>")
    title = html.unescape(re.search(r"<title>(.*?)</title>", doc, re.S).group(1).strip())
    canonical = re.search(r'<link rel="canonical" href="([^"]+)"', doc).group(1)
    pub, mod = page_dates(doc)
    front = ["---", f"title: {json.dumps(title, ensure_ascii=False)}",
             f"description: {json.dumps(head_meta(doc, 'name', 'description'), ensure_ascii=False)}",
             f"canonical: {canonical}", "author: Gabriel Voicu"]
    if pub:
        front.append(f"published: {pub}")
    if mod:
        front.append(f"updated: {mod}")
    front.append("---")
    body = "\n\n".join(b for b in Blocks(page_path).render(main) if b.strip())
    return "\n".join(front) + "\n\n" + body.strip() + "\n", doc


def sitemap_paths():
    xml = open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read()
    return [u[len(SITE):] for u in re.findall(r"<loc>([^<]+)</loc>", xml)]


def existing_markdown():
    found = []
    for d, dirs, files in os.walk(ROOT):
        dirs[:] = [x for x in dirs if not x.startswith(".") and x != "design"]
        if MD_NAME in files:
            found.append("/" + os.path.relpath(d, ROOT).replace(os.sep, "/").strip(".").strip("/") + "/")
    return [p.replace("//", "/") for p in found]


def main():
    check = "--check" in sys.argv[1:]
    problems = []
    paths = sitemap_paths()
    for p in paths:
        md, doc = page_markdown(p)
        for link in (f'<link rel="alternate" type="text/markdown" href="{p}{MD_NAME}">',
                     '<link rel="describedby" href="/llms.txt">'):
            if link not in doc:
                problems.append(f"{p}: no {link}")
        target = os.path.join(ROOT, p.lstrip("/"), MD_NAME)
        old = open(target, encoding="utf-8").read() if os.path.exists(target) else None
        if old != md:
            if check:
                problems.append(f"{p}{MD_NAME}: {'missing' if old is None else 'out of step with its page'}")
            else:
                with open(target, "w", encoding="utf-8") as f:
                    f.write(md)
                print("wrote", p + MD_NAME)
    for p in existing_markdown():
        if p not in paths:
            if check:
                problems.append(f"{p}{MD_NAME}: its page is not in sitemap.xml")
            else:
                os.remove(os.path.join(ROOT, p.lstrip("/"), MD_NAME))
                print("deleted", p + MD_NAME)
    llms = os.path.join(ROOT, "llms.txt")
    if os.path.exists(llms):
        text = open(llms, encoding="utf-8").read()
        listed = re.findall(r"\]\(%s(/[^)]*?)%s\)" % (re.escape(SITE), re.escape(MD_NAME)), text)
        for p in paths:
            if p not in listed:
                problems.append(f"llms.txt: {p} not listed")
        for p in sorted(set(listed) - set(paths)):
            problems.append(f"llms.txt: lists {p}{MD_NAME}, which is not a page in sitemap.xml")
    else:
        problems.append("llms.txt: missing")
    for line in problems:
        print(line, file=sys.stderr)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
