"""Segment ClinicalTrials.gov eligibility free text into an item tree.

Deterministic and conservative: it keeps every source line accounted for
(items, headings, hints) and records the basis of any structural guess so the
reviewer can see it.  Flat bullet lists carry no real nesting information; where
we guess, the item is marked `structure_basis="heuristic"`.
"""
import re
from dataclasses import dataclass, field

SECTION_RE = re.compile(r"^(inclusion|exclusion)\s+criteria\s*:?\s*$", re.I)
HEAD_NAMED_RE = re.compile(r"^(main\s+)?(inclusion|exclusion)\s+criteria\s*:?\s*$", re.I)
MARK_RE = re.compile(r"^(?P<ind>[ \t]*)(?P<m>\d+[.)]|[a-z][.)]|[*•\-–])[ \t]+(?P<t>\S.*)$")
CAPS_TAIL_RE = re.compile(r"(?<=[.;])\s+(FOR\s+[A-Z][A-Z ,/-]{6,})$")
INLINE_LETTER_RE = re.compile(r"(?:(?<=:)|(?<=;))\s*([a-h])\.\s*(?=[A-Z])")


def normalize(text: str) -> str:
    """Undo markdown escaping some clients add; unify newlines."""
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\t", "   ")
    return re.sub(r"\\([<>\[\]&*_#~|()])", r"\1", text)


@dataclass
class Item:
    kind: str                 # section|numeric|letter|bullet|heading|hint|plain|inline
    indent: int
    marker: str
    text: str
    start: int
    end: int
    section: str | None = None
    children: list = field(default_factory=list)
    hint: str | None = None
    structure_basis: str = "explicit"   # explicit | heuristic

    @property
    def colon(self) -> bool:
        return self.text.rstrip().endswith(":")


def _is_heading(s: str) -> bool:
    if HEAD_NAMED_RE.match(s):
        return True
    letters = re.sub(r"[^A-Za-z]", "", s)
    return bool(letters) and letters.isupper() and len(letters) > 6


def parse_items(text: str):
    """Flat list of Items in source order."""
    items: list[Item] = []
    section = None
    pos = 0
    for line in text.split("\n"):
        start, end = pos, pos + len(line)
        pos = end + 1
        s = line.strip()
        if not s:
            continue
        indent = len(line) - len(line.lstrip(" "))
        sm = SECTION_RE.match(s)
        if sm and indent == 0:
            section = sm.group(1).lower()
            items.append(Item("section", 0, "", s, start, end, section=section))
            continue
        # a caps "FOR ..." heading can trail a sentence on the same line
        tail = None
        mk = MARK_RE.match(line)
        body = mk.group("t").strip() if mk else s
        tm = CAPS_TAIL_RE.search(body)
        if tm:
            tail = tm.group(1)
            body = body[: tm.start()].rstrip()
        if mk:
            m = mk.group("m")
            kind = "numeric" if m[0].isdigit() else "letter" if m[0].isalpha() else "bullet"
            items.append(Item(kind, len(mk.group("ind")), m, body, start, end - (len(tail) + 1 if tail else 0), section=section))
        elif _is_heading(body) and not tail:
            if items and items[-1].kind == "heading" and not items[-1].text.endswith(":") and body.isupper():
                items[-1].text += " " + body       # merge wrapped caps heading
                items[-1].end = end
            else:
                items.append(Item("heading", indent, "", body, start, end, section=section))
        elif items and items[-1].kind != "section":
            items[-1].text += " " + body            # continuation line
            items[-1].end = end - (len(tail) + 1 if tail else 0)
        else:
            items.append(Item("plain", indent, "", body, start, end, section=section))
        if tail:
            items.append(Item("heading", indent, "", tail, end - len(tail), end, section=section))
    for it in items:
        if it.kind == "heading" and it.text.upper().startswith("FOR "):
            it.kind = "hint"
    return items


def _captures(top: Item, it: Item) -> bool:
    """Does `top` (same indent as `it`) adopt `it` as a child?  Flat markdown-style
    lists hide nesting, so these are heuristics and get flagged."""
    if top.kind == "heading":
        return it.kind not in ("heading", "numeric")
    if top.kind in ("numeric", "letter") and top.colon and it.kind == "heading":
        return True
    if top.kind == "bullet" and top.colon and "following" in top.text.lower():
        return it.kind == "bullet" and it.text[:1].islower()
    return False


def build_tree(items):
    """Nest items.  Returns list of top-level Items (sections are kept as markers)."""
    roots, stack = [], []
    pending_hint = {}
    for it in items:
        if it.kind == "section":
            stack.clear(); pending_hint.clear()
            roots.append(it)
            continue
        if it.kind == "hint":
            pending_hint[it.indent] = it.text
            roots_or_parent = stack[-1].children if stack else roots
            roots_or_parent.append(it)
            continue
        while stack:
            top = stack[-1]
            if top.indent < it.indent or (top.indent == it.indent and _captures(top, it)):
                break
            stack.pop()
        if it.kind == "heading":
            pending_hint.pop(it.indent, None)
        if stack and stack[-1].indent == it.indent:
            it.structure_basis = "heuristic"
        if it.indent in pending_hint and it.kind in ("bullet", "numeric", "letter"):
            it.hint = pending_hint[it.indent]
        (stack[-1].children if stack else roots).append(it)
        stack.append(it)
    return roots


def split_inline_letters(item: Item):
    """'... criteria: a.Blood routine: ...; b.Liver ...' -> synthetic children."""
    text = item.text
    ms = list(INLINE_LETTER_RE.finditer(text))
    if len(ms) < 2 or [m.group(1) for m in ms] != [chr(ord("a") + i) for i in range(len(ms))]:
        return item.text, []
    head = text[: ms[0].start()].strip()
    parts = []
    for i, m in enumerate(ms):
        seg_end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        parts.append((m.group(1) + ".", text[m.end(): seg_end].strip().rstrip(";")))
    return head, parts
