#!/usr/bin/env python3
"""c4kit: stdlib-only helpers for hand-authored C4 pages (inline SVG, one self-contained HTML file).

Use from a per-repo build.py:

    sys.path.insert(0, '<skill>/scripts'); import c4kit as c
    def l1(): return c.svg(1200, 560, c.box(...) + c.edge(...), 'L1 System context')
    c.build({'L1': l1(), ...}, template='page.html', extra_css=['extra.css'])

Coordinates are SVG user units; every layout is placed by hand. `box` estimates text width and records a WARN
when a line may not fit; the playwright overflow check (scripts/qa) is the source of truth.
"""
import argparse, html, math, os, re, subprocess, sys

KIT = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(os.path.dirname(KIT), 'assets')
WARN = []
FS = {'t': 15.5, 'y': 11.5, 'd': 12.5, 'lb': 12}  # font sizes per text class (match assets/page.css)
CW = {'t': .6, 'y': .56, 'd': .56, 'lb': .56}  # average glyph width / font size


# ------------------------------------------------------------------ primitives
def esc(s):
    return html.escape(str(s), quote=True)


def tw(s, cls):
    """Estimated rendered width of s in class cls."""
    return len(s) * FS.get(cls, 12.5) * CW.get(cls, .56)


def check(s, cls, avail, where):
    if tw(s, cls) > avail:
        WARN.append(f'overflow {where}: "{s}" ~{tw(s, cls):.0f}px > {avail:.0f}px')


def text(x, y, s, cls='d', anchor=None, extra=''):
    a = f' text-anchor="{anchor}"' if anchor else ''
    return f'<text x="{x:g}" y="{y:g}" class="{cls}"{a}{extra}>{esc(s)}</text>'


def box(x, y, w, h, kind, title, typ=None, lines=(), shape='rect', badge=None, pad=14):
    """C4 element: title, [type: tech] line, description lines.

    kind: kf (system in focus) | k (owned) | g (cloud/managed platform) | gh (external SaaS) | p (person) | x (other).
    shape: 'rect' or 'db' (cylinder). badge: short pill text at the top right.
    """
    out = [f'<g class="n {kind}">']
    if shape == 'db':
        ry = 9
        out.append(f'<path d="M{x} {y+ry} a{w/2} {ry} 0 0 1 {w} 0 v{h-2*ry} a{w/2} {ry} 0 0 1 {-w} 0 Z"/>')
        out.append(f'<path class="cap" d="M{x} {y+ry} a{w/2} {ry} 0 0 0 {w} 0"/>')
        ty = y + 2 * ry + 18
    else:
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/>')
        ty = y + 25
    avail = w - 2 * pad
    out.append(text(x + pad, ty, title, 't'))
    check(title, 't', avail - (60 if badge else 0), title)
    cy = ty
    if typ:
        cy += 17
        out.append(text(x + pad, cy, typ, 'y'))
        check(typ, 'y', avail, title)
    cy += 6
    for ln in lines:
        cy += 16
        out.append(text(x + pad, cy, ln, 'd'))
        check(ln, 'd', avail, title)
    if cy + 8 > y + h:
        WARN.append(f'vertical overflow in {title}: needs {cy + 8 - y:.0f} > {h}')
    if badge:
        bw = len(badge) * 6.4 + 14
        out.append(f'<g class="badge"><rect x="{x+w-bw-10}" y="{y+10}" width="{bw}" height="18" rx="9"/>'
                   f'<text x="{x+w-10-bw/2}" y="{y+23}" text-anchor="middle">{esc(badge)}</text></g>')
    out.append('</g>')
    return ''.join(out)


def person(x, y, w, h, title, typ, lines=()):
    """Person: head circle on top of a box; h includes the 34px head."""
    cx = x + w / 2
    return (f'<g class="n p"><circle cx="{cx}" cy="{y+20}" r="20"/>'
            + box(x, y + 34, w, h - 34, 'p', title, typ, lines)[len('<g class="n p">'):])


def boundary(x, y, w, h, kind, label, sub=None):
    """Dashed frame (project, process, browser). Label sits top-left; keep edge labels off its border lines."""
    out = [f'<g class="bd {kind}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16"/>',
           text(x + 16, y + 24, label, 'bl')]
    if sub:
        out.append(text(x + 16, y + 41, sub, 'y'))
    out.append('</g>')
    return ''.join(out)


MARKER = {'': 'ah', 'k': 'ahk', 'g': 'ahg', 'h': 'ahh', 'bad': 'ahb', 'p': 'ah', 'ok': 'ah'}


def edge(d, cls='', marker=None):
    """Arrow along SVG path d. cls: '' k g h p bad ok, plus 'dash'. marker defaults from the colour class."""
    if marker is None:
        colour = next((c for c in cls.split() if c in MARKER), '')
        marker = MARKER[colour]
    m = f' marker-end="url(#{marker})"' if marker else ''
    return f'<path class="e {cls}" d="{d}"{m}/>'


def label(x, y, lines, anchor='middle', cls='lb'):
    """Edge label (white halo). Multi-line: 14.5px leading. Place in gaps, never on a line or border."""
    if isinstance(lines, str):
        lines = [lines]
    return ''.join(text(x, y + i * 14.5, ln, cls, anchor) for i, ln in enumerate(lines))


def svg(vb_w, vb_h, body, title, cls='c4'):
    return (f'<svg class="{cls}" viewBox="0 0 {vb_w} {vb_h}" role="img" aria-label="{esc(title)}">'
            f'<title>{esc(title)}</title>{body}</svg>')


def _marker(mid, colour):
    return (f'<marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="{colour}"/></marker>')


DEFS = ('<svg class="defs" width="0" height="0" aria-hidden="true" focusable="false"><defs>'
        + _marker('ah', '#5a6478') + _marker('ahk', '#2f4b8a') + _marker('ahg', '#1f7a74')
        + _marker('ahh', '#7a4e86') + _marker('ahb', '#c2453a')
        + '</defs></svg>')


# ------------------------------------------------------------------ hero lens (4 nested, clickable frames)
LENS_GEOM = [(8, 8, 524, 364), (78, 72, 446, 292), (160, 136, 356, 220), (246, 200, 262, 148)]


def lens(levels, active=None, mini=False):
    """levels: 4 tuples (id, label, sub), outermost first, e.g. ('l4', 'L4  The engine', 'tick loop, slots').

    Full lens = hero (frames link to sections, spinning dot in the core). mini=True = the small
    "you are here" inset at each level head, with the active frame filled.
    """
    assert len(levels) == 4, 'the lens has exactly 4 frames (L1..L4)'
    parts = []
    for i, ((lid, lab, sub), (x, y, w, h)) in enumerate(zip(levels, LENS_GEOM)):
        on = ' on' if lid == active else ''
        inner = f'<rect class="lf lf{i+1}{on}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{18-i*2}"/>'
        if not mini:
            inner += text(x + 18, y + 30, lab, 'lt') + text(x + 18, y + 49, sub, 'ls')
            check(sub, 'd', w - 36, f'lens {lid}')
        parts.append(inner if mini else f'<a href="#{lid}" class="lz">{inner}</a>')
    if not mini:
        cx, cy = 446, 300
        parts.append(f'<g class="core"><circle cx="{cx}" cy="{cy}" r="26"/>'
                     f'<g class="spin" style="transform-origin:{cx}px {cy}px">'
                     f'<circle class="dot" cx="{cx}" cy="{cy-26}" r="5"/></g></g>')
    cls = 'lens mini' if mini else 'lens'
    title = f'You are at {active.upper()}' if mini else 'Zoom levels of this page'
    return f'<svg class="{cls}" viewBox="0 0 540 380" role="img" aria-label="{title}"><title>{title}</title>{"".join(parts)}</svg>'


# ------------------------------------------------------------------ L4 pattern helpers
def state(x, y, w, lab, cls, h=56, busy=None):
    """State pill for state machines. cls: st0..st6 / ex0..ex3 (see page.css). busy: small dark tag top-right."""
    out = (f'<g class="state {cls}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{min(28, h/2)}"/>'
           + text(x + w / 2, y + h / 2 + 6, lab, 'sl', 'middle') + '</g>')
    if busy:
        out += (f'<g class="busy"><rect x="{x+w-52}" y="{y-11}" width="46" height="20" rx="10"/>'
                + text(x + w - 29, y + 3, busy, 'bz', 'middle') + '</g>')
    return out


def ring(steps, hub, cx=310, cy=316, r=206, arc_note=None, href='step-'):
    """Loop diagram: numbered step discs on a ring around a hub, with a spinning dot.

    steps: [['line1', 'line2'], ...] (first step drawn hollow = pre-loop step). hub: [(text, cls)] with cls in
    ht/hs/hm. Each disc links to #{href}{n}; pair the figure with an <ol class="ticks"> whose items have those ids.
    """
    b = [f'<circle class="ring" cx="{cx}" cy="{cy}" r="{r}"/>']
    R = r + 54
    if arc_note:
        a0, a1 = math.radians(-50), math.radians(230)
        b.append(f'<path class="arc" d="M{cx+R*math.cos(a0):.1f} {cy+R*math.sin(a0):.1f} A{R} {R} 0 1 1 '
                 f'{cx+R*math.cos(a1):.1f} {cy+R*math.sin(a1):.1f}"/>')
        b.append(text(cx, cy + R + 22, arc_note, 'lb', 'middle'))
    b.append(f'<g class="spin" style="transform-origin:{cx}px {cy}px"><circle class="dot" cx="{cx}" cy="{cy-r}" r="7"/></g>')
    n = len(steps)
    for i, nm in enumerate(steps):
        a = math.radians(-90 + i * 360 / n)
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        cls = 'stn g1' if i == 0 and arc_note else 'stn'
        t = ''.join(text(x, y + 10 + j * 15 - (len(nm) - 1) * 7, s, 'sn', 'middle') for j, s in enumerate(nm))
        b.append(f'<a href="#{href}{i+1}" class="{cls}"><circle cx="{x:.1f}" cy="{y:.1f}" r="50"/>'
                 f'{text(x, y - 18, str(i + 1), "num", "middle")}{t}</a>')
    gaps = [24 if hub[i - 1][1] == 'ht' or c == 'hm' else 18 for i, (_, c) in enumerate(hub) if i]
    hy = cy - sum(gaps) / 2 + 11  # optical centre of the baseline run
    hb = [f'<g class="hub"><circle cx="{cx}" cy="{cy}" r="96"/>']
    for i, (s, c) in enumerate(hub):
        hy += gaps[i - 1] if i else 0
        hb.append(text(cx, hy, s, c, 'middle'))
    b.append(''.join(hb) + '</g>')
    return ''.join(b)


SEQ_KIND = {'': ('k', 'ahk'), 'ret': ('dash', 'ah'), 'h': ('h', 'ahh'), 'g': ('g', 'ahg'), 'bad': ('bad', 'ahb')}


def sequence(lifelines, phases, width=1200, step=34):
    """Sequence diagram body (wrap with svg(width, H, body, title); returns (body, H)).

    lifelines: {key: (x, name, kind)}; phases: [(phase name, [(from, to, label, kind)])], kind in '' ret h g bad.
    Numbered badges sit at the sender end; leftward labels end-anchor before the badge so they never collide.
    """
    y, n, bands, msgs = 120, 0, [], []
    for bi, (ph, ms) in enumerate(phases):
        y0 = y - 22
        for f, t, lab, k in ms:
            n += 1
            x1, x2 = lifelines[f][0], lifelines[t][0]
            dirn = 1 if x2 > x1 else -1
            cls, mk = SEQ_KIND[k]
            msgs.append(edge(f'M{x1 + dirn*6} {y} H {x2 - dirn*8}', cls, mk))
            bx = x1 + 16 * dirn
            msgs.append(f'<g class="sq"><circle cx="{bx}" cy="{y-10}" r="8"/>' + text(bx, y - 6.5, str(n), 'sqn', 'middle') + '</g>')
            if dirn > 0:
                msgs.append(text((x1 + x2) / 2 + 10, y - 6, lab, 'lb', 'middle'))
                check(lab, 'lb', abs(x2 - x1) - 40, f'seq {n}')
            else:
                msgs.append(text(bx - 14, y - 6, lab, 'lb', 'end'))
                check(lab, 'lb', abs(x2 - x1) - 40, f'seq {n}')
            y += step
        bands.append(f'<rect class="band b{bi%2}" x="0" y="{y0}" width="{width}" height="{y - y0 - 12}"/>'
                     + text(10, y0 + 15, ph, 'bandl'))
        y += 6
    H = y + 10
    heads = []
    for x, nm, kind in lifelines.values():
        heads.append(f'<line class="life" x1="{x}" y1="80" x2="{x}" y2="{H-10}"/>')
        heads.append(f'<g class="n {kind}"><rect x="{x-72}" y="30" width="144" height="46" rx="10"/>'
                     + text(x, 58, nm, 't', 'middle') + '</g>')
        check(nm, 't', 128, f'lifeline {nm}')
    return ''.join(bands + heads + msgs), H


# ------------------------------------------------------------------ page assembly
def _git(repo, *args):
    try:
        return subprocess.check_output(['git', '-C', repo, *args], text=True, stderr=subprocess.DEVNULL).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ''


def _github_blob(repo, sha):
    url = _git(repo, 'remote', 'get-url', 'origin')
    m = re.match(r'(?:git@github\.com:|https://github\.com/)([^/]+/[^/]+?)(?:\.git)?$', url)
    return f'https://github.com/{m.group(1)}/blob/{sha}/' if m and sha else ''


def src_base(repo, out, sha):
    """Prefix for {{src:path}} links: relative when the page lives in the repo, else GitHub blob URL, else file://."""
    if os.path.abspath(out).startswith(repo + os.sep):
        rel = os.path.relpath(repo, os.path.dirname(out))
        return '' if rel == '.' else rel + '/'
    return _github_blob(repo, sha) or f'file://{repo}/'


def build(figs, template=None, extra_css=(), extra_defs='', argv=None):
    """Fill the template and write the page. Returns the output path.

    Placeholders: {{CSS}} {{DEFS}} {{LENS}} {{MINI:l1..l4}} {{FIG:<name>}} {{GIT:sha}} {{GIT:branch}}
    {{src:path|label}}. Any leftover '{{' (e.g. an unfilled {{TODO: ...}}) aborts the build.
    figs: {'<name>': svg string, 'LEVELS': [4 lens tuples]}.
    extra_defs: project-specific <pattern>/<marker> markup injected into the shared <defs>.
    """
    ap = argparse.ArgumentParser(description='Build the C4 architecture page.')
    ap.add_argument('--repo', help='target repo root (default: git toplevel of cwd)')
    ap.add_argument('--out', help='output HTML (default: <repo>/docs/architecture-c4.html)')
    ap.add_argument('--src-base', help='prefix for source links (default: relative, GitHub blob URL, or file://)')
    a = ap.parse_args(argv)
    repo = os.path.abspath(a.repo or _git(os.getcwd(), 'rev-parse', '--show-toplevel') or os.getcwd())
    out = os.path.abspath(a.out or os.path.join(repo, 'docs', 'architecture-c4.html'))
    sha = _git(repo, 'rev-parse', '--short', 'HEAD')
    base = a.src_base if a.src_base is not None else src_base(repo, out, _git(repo, 'rev-parse', 'HEAD'))

    css = open(os.path.join(ASSETS, 'page.css')).read() + ''.join('\n' + open(p).read() for p in extra_css)
    page = open(template or os.path.join(ASSETS, 'page.html')).read()
    levels = figs.get('LEVELS')
    repl = {'{{CSS}}': css, '{{DEFS}}': DEFS.replace('</defs>', extra_defs + '</defs>'),
            '{{GIT:sha}}': esc(sha or 'unknown'),
            '{{GIT:branch}}': esc(_git(repo, 'rev-parse', '--abbrev-ref', 'HEAD') or 'unknown')}
    if levels:
        repl['{{LENS}}'] = lens(levels)
        for lid, _, _ in levels:
            repl['{{MINI:' + lid + '}}'] = lens(levels, lid, True)
    for k, v in figs.items():
        if k != 'LEVELS':
            if '{{FIG:' + k + '}}' not in page:
                WARN.append(f'figure {k} has no {{{{FIG:{k}}}}} in the template (not shown)')
            repl['{{FIG:' + k + '}}'] = v.replace('<svg', f'<svg data-fig="{esc(k)}"', 1)
    srcs = sorted(set(re.findall(r'\{\{src:([^|}#]+)', page)))
    if not os.path.isdir(repo):  # no checkout (e.g. the fictional examples/acme-shop): links are not checked
        print(f'note: repo {repo} not found; {len(srcs)} src paths not checked')
        srcs = []
    for p in srcs:
        if not os.path.exists(os.path.join(repo, p)):
            WARN.append(f'src path missing in repo: {p}')
    for k, v in repl.items():
        page = page.replace(k, v)
    page = re.sub(r'\{\{src:([^|}]+)(?:\|([^}]+))?\}\}',
                  lambda m: f'<a class="src" href="{esc(base + m.group(1))}">{esc(m.group(2) or m.group(1))}</a>', page)
    left = [page[i:i + 40].split('\n')[0] for i in (m.start() for m in re.finditer(r'\{\{', page))]
    if left:
        sys.exit(f'unfilled placeholders ({len(left)}): ' + ', '.join(left[:8]))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w') as f:
        f.write(page)
    print('wrote', out, len(page), 'bytes; HEAD', sha or 'unknown', '; src links ->', base or './')
    for w in WARN:
        print('WARN', w)
    return out
