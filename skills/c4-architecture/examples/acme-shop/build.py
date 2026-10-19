#!/usr/bin/env python3
"""Worked example: the C4 page of "Acme Shop", a FICTIONAL online store, built on c4kit.

Acme Shop does not exist: every name, path, number and link below is invented to show the patterns.
There is no checkout to read, so the build defaults --repo to a path that does not exist (c4kit then skips
the src-path check) and --src-base to an example GitHub URL. Build from the skill directory with:

    python3 examples/acme-shop/build.py --out /tmp/c4-acme.html

For a real repo, pass --repo <checkout> instead and drop the --src-base default.
Every coordinate below was placed by hand, then fixed through the visual QA loop
(references/layout-gotchas.md). Copy the shapes of these functions, not their numbers.
"""
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'scripts'))
import c4kit as c  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULTS = ['--repo', '/nonexistent/acme-shop', '--src-base', 'https://github.com/example/acme-shop/blob/main/']

LEVELS = [('l1', 'L1  System context', 'shoppers, staff, payments, email'),
          ('l2', 'L2  Containers and cloud', 'SPA, API, worker, Postgres, queue'),
          ('l3', 'L3  Components', 'modules inside the API service'),
          ('l4', 'L4  Checkout', 'order states, outbox, sequence')]


# ------------------------------------------------------------------ L1 context
def l1():
    b = []
    b.append(c.person(40, 90, 240, 170, 'Shopper', '[Person]', ['Browses the catalog, pays,', 'tracks orders']))
    b.append(c.person(40, 330, 240, 150, 'Staff', '[Person, staff role]', ['Edits products,', 'ships and refunds']))
    b.append(c.box(440, 196, 300, 170, 'kf', 'Acme Shop', '[Software system]',
                   ['Online store: catalog, cart,', 'checkout, order tracking.', 'Owns orders and stock.']))
    b.append(c.box(920, 150, 250, 170, 'gh', 'Payment provider', '[External: Stripe-like]',
                   ['Payment intents, captures,', 'refunds; sends signed', 'webhooks']))
    b.append(c.box(920, 400, 250, 120, 'x', 'Email service', '[External: email API]',
                   ['Order confirmations,', 'shipping notices']))
    b.append(c.box(440, 452, 300, 92, 'g', 'Cloud platform', '[Platform]', ['Hosts containers, DB, queue, storage']))
    # edges
    b.append(c.edge('M280 230 H 438', 'p'))
    b.append(c.label(359, 220, 'shops, pays'))
    b.append(c.label(359, 248, '[HTTPS]'))
    b.append(c.edge('M280 420 H 360 V 340 H 438', 'p'))
    b.append(c.label(368, 392, ['manages', '[HTTPS, login]'], 'start'))
    b.append(c.edge('M740 230 H 918', 'k', 'ahk'))
    b.append(c.label(829, 220, 'charges cards [REST]'))
    b.append(c.edge('M918 290 H 742', 'h dash', 'ahh'))
    b.append(c.label(829, 312, 'payment webhooks'))
    b.append(c.edge('M740 345 H 820 V 460 H 918', 'k', 'ahk'))
    b.append(c.label(812, 420, 'sends email', 'end'))
    b.append(c.edge('M590 366 V 450', 'g dash', 'ahg'))
    b.append(c.label(600, 414, 'runs on', 'start'))
    return c.svg(1200, 560, ''.join(b), 'L1 System context: Acme Shop, its users, payments and email')


# ------------------------------------------------------------------ L2a runtime
def l2a():
    b = []
    b.append(c.boundary(20, 40, 196, 460, 'x', 'Browser'))
    b.append(c.person(36, 80, 164, 150, 'Shopper', '[Person]', ['Opens the shop']))
    b.append(c.box(36, 300, 164, 180, 'k', 'Storefront', '[Container: SPA]',
                   ['React + Vite;', 'static files from', 'the bucket;', 'calls /api/*']))
    b.append(c.boundary(240, 20, 662, 630, 'g', 'Cloud account acme-prod', 'one region; staging has the same shape'))
    b.append(c.box(260, 250, 164, 150, 'g', 'Load balancer', '[Managed L7]',
                   ['TLS termination;', '/api/* to the API,', 'the rest to the', 'bucket via CDN']))
    b.append(c.boundary(484, 90, 400, 286, 'k', 'Container service', '[one image, 2 modes]'))
    b.append(c.box(500, 140, 176, 220, 'kf', 'api', '[Container: FastAPI]',
                   ['REST: catalog, cart,', 'checkout, orders,', 'staff admin,', 'webhooks;', '2-6 replicas']))
    b.append(c.box(692, 140, 176, 220, 'k', 'worker', '[Container: worker]',
                   ['same image, worker', 'mode; relays the', 'outbox, runs jobs;', '1 replica']))
    b.append(c.box(260, 470, 164, 150, 'g', 'Object storage', '[Bucket + CDN]',
                   ['SPA build,', 'product images']))
    b.append(c.box(500, 470, 176, 150, 'g', 'Postgres', '[Managed, PG 16]',
                   ['orders, stock,', 'outbox table;', 'daily backups'], shape='db'))
    b.append(c.box(692, 470, 176, 150, 'g', 'Job queue', '[Managed queue]',
                   ['one job per', 'outbox row;', 'at-least-once']))
    b.append(c.box(990, 100, 190, 150, 'gh', 'Payment provider', '[External]',
                   ['intents, captures,', 'refunds; webhooks', 'to /api/webhooks']))
    b.append(c.box(990, 290, 190, 110, 'x', 'Email service', '[External]', ['transactional', 'email API']))
    # edges
    b.append(c.edge('M118 230 V 298', 'p'))
    b.append(c.label(126, 268, 'opens', 'start'))
    b.append(c.edge('M200 360 H 258'))
    b.append(c.edge('M424 300 H 498'))
    b.append(c.label(454, 290, '/api/*'))
    b.append(c.edge('M342 400 V 468', 'g', 'ahg'))
    b.append(c.label(350, 440, 'static files', 'start'))
    b.append(c.edge('M588 362 V 468', 'k', 'ahk'))
    b.append(c.label(580, 440, 'SQL', 'end'))
    b.append(c.edge('M716 362 V 410 H 650 V 468', 'k', 'ahk'))
    b.append(c.label(724, 398, 'polls outbox', 'start'))
    b.append(c.edge('M820 362 V 468', 'k', 'ahk'))
    b.append(c.label(812, 446, 'jobs', 'end'))
    b.append(c.edge('M868 190 H 988', 'k', 'ahk'))
    b.append(c.label(946, 172, ['capture,', 'refund']))
    b.append(c.edge('M1085 98 V 66 H 656 V 138', 'h dash', 'ahh'))
    b.append(c.label(946, 56, 'webhooks'))
    b.append(c.edge('M868 330 H 988', 'k', 'ahk'))
    b.append(c.label(946, 320, 'send'))
    return c.svg(1200, 670, ''.join(b), 'L2 Containers: the Acme Shop services inside one cloud account')


# ------------------------------------------------------------------ L2b delivery
def l2b():
    b = []
    xs = [30, 330, 630, 930]
    cards = [('gh', 'Git repo', '[acme-shop, main]', ['monorepo: web/, api/,', 'infra/, .ci/']),
             ('gh', 'CI pipeline', '[.ci/pipeline.yml]', ['lint, unit tests,', 'build one image']),
             ('g', 'Image registry', '[Managed registry]', ['acme-shop:<sha>;', 'tags never reused']),
             ('g', 'Rolling deploy', '[Container service]', ['migrations first, then', 'api + worker, same digest'])]
    for x, (kind, title, typ, lines) in zip(xs, cards):
        b.append(c.box(x, 40, 210, 120, kind, title, typ, lines))
    for i, lab in enumerate(['push', 'push image', 'deploy']):
        x = xs[i] + 210
        b.append(c.edge(f'M{x} 100 H {xs[i+1]-2}', 'k', 'ahk'))
        b.append(c.label(x + 45, 90, lab))
    b.append(c.text(30, 196, 'Every merge to main runs the whole chain; staging deploys first, prod after a manual approval in CI.', 'y'))
    return c.svg(1200, 214, ''.join(b), 'L2 Delivery: how a commit reaches production')


# ------------------------------------------------------------------ L3 components of the API
def l3():
    b = []
    b.append(c.boundary(20, 20, 860, 510, 'k', 'api', '[Container: FastAPI, api/src/acme/]'))
    b.append(c.box(300, 60, 280, 100, 'k', 'routes', '[HTTP routers]', ['catalog, cart, checkout,', 'orders, admin, webhooks']))
    b.append(c.box(48, 210, 200, 100, 'k', 'auth', '[middleware]', ['session cookie;', 'staff role check']))
    b.append(c.box(300, 210, 280, 112, 'kf', 'checkout', '[service]',
                   ['Validates the cart, reserves', 'stock, opens a payment intent']))
    b.append(c.box(670, 210, 190, 100, 'k', 'catalog', '[service]', ['products, prices,', 'stock levels']))
    b.append(c.box(48, 380, 200, 110, 'k', 'payments', '[provider adapter]', ['intents, refunds;', 'verifies webhook', 'signatures']))
    b.append(c.box(300, 380, 280, 110, 'k', 'orders', '[state machine]', ['Allowed transitions only;', 'each writes an outbox row']))
    b.append(c.box(670, 380, 190, 110, 'k', 'db', '[SQLAlchemy repos]', ['one transaction', 'per request']))
    b.append(c.box(920, 60, 250, 100, 'k', 'Storefront', '[Container: SPA]', ['React app in the browser']))
    b.append(c.box(48, 640, 200, 80, 'gh', 'Payment provider', '[External]'))
    b.append(c.box(670, 620, 190, 120, 'g', 'Postgres', '[Managed, PG 16]', shape='db'))
    # edges
    b.append(c.edge('M918 110 H 582'))
    b.append(c.label(750, 100, 'JSON over HTTPS'))
    b.append(c.edge('M300 120 H 148 V 208', 'k', 'ahk'))
    b.append(c.label(156, 190, 'guards', 'start'))
    b.append(c.edge('M440 160 V 208', 'k', 'ahk'))
    b.append(c.label(448, 190, 'POST /checkout', 'start'))
    b.append(c.edge('M580 140 H 765 V 208', 'k', 'ahk'))
    b.append(c.label(757, 190, 'GET /products', 'end'))
    b.append(c.edge('M580 266 H 668', 'k', 'ahk'))
    b.append(c.label(625, 256, 'reserve'))
    b.append(c.edge('M330 322 V 345 H 148 V 378', 'k', 'ahk'))
    b.append(c.label(156, 366, 'create intent', 'start'))
    b.append(c.edge('M440 322 V 378', 'k', 'ahk'))
    b.append(c.label(448, 356, 'place order', 'start'))
    b.append(c.edge('M580 435 H 668', 'k', 'ahk'))
    b.append(c.label(625, 425, 'save'))
    b.append(c.edge('M765 310 V 378', 'k', 'ahk'))
    b.append(c.label(773, 350, 'stock rows', 'start'))
    b.append(c.edge('M148 490 V 638', 'h', 'ahh'))
    b.append(c.label(156, 590, 'HTTPS, API key', 'start'))
    b.append(c.edge('M765 490 V 618', 'k', 'ahk'))
    b.append(c.label(773, 590, 'SQL, pool of 10', 'start'))
    return c.svg(1200, 760, ''.join(b), 'L3 Components inside the API service')


# ------------------------------------------------------------------ L4a order state machine
def l4a():
    b = []
    S = {'cart': (30, 180, 'st0', 'cart'), 'pending': (270, 180, 'st3', 'pending'),
         'paid': (510, 180, 'st1', 'paid'), 'shipped': (750, 180, 'st2', 'shipped'),
         'delivered': (990, 180, 'st5', 'delivered'), 'cancelled': (270, 340, 'st6', 'cancelled'),
         'refunded': (750, 340, 'st6', 'refunded')}
    for k, (x, y, cls, lab) in S.items():
        b.append(c.state(x, y, 150, lab, cls, busy='lock' if k == 'pending' else None))
    E = [('M180 208 H 268', 'checkout', 225, 198, 'middle'),
         ('M420 208 H 508', 'authorized', 465, 198, 'middle'),
         ('M660 208 H 748', 'ship', 705, 198, 'middle'),
         ('M900 208 H 988', 'carrier scan', 945, 198, 'middle'),
         ('M345 236 V 338', 'payment fails', 353, 290, 'start'),
         ('M585 236 V 368 H 748', 'staff cancels', 593, 290, 'start'),
         ('M1065 236 V 368 H 902', 'return accepted', 1073, 300, 'start')]
    for d, lab, lx, ly, an in E:
        b.append(c.edge(d, 'bad' if lab in ('payment fails', 'staff cancels', 'return accepted') else ''))
        b.append(c.label(lx, ly, lab, an))
    b.append(c.edge('M292 182 C 278 128, 352 128, 338 180', 'ok'))
    b.append(c.label(316, 124, 'card retry'))
    b.append(c.label(353, 305, '(or 30 min timeout)', 'start'))
    b.append(c.text(30, 440, 'Each arrow is one transaction: the order row and an outbox row change together. "lock" = stock is'
                    ' held while pending.', 'd'))
    body = f'<g transform="translate(0 -80)">{"".join(b)}</g>'  # states were placed with 80 units of spare top margin
    return c.svg(1200, 380, body, 'L4 Order state machine')


# ------------------------------------------------------------------ L4b worker outbox loop
def l4b():
    steps = [['claim', 'rows'], ['publish'], ['receive', 'job'], ['call', 'provider'], ['record', 'result'], ['ack or', 'retry']]
    hub = [('one pass', 'ht'), ('every 2 s,', 'hs'), ('one worker', 'hs'), ('worker.run_once', 'hm')]
    body = c.ring(steps, hub, href='pass-')
    return c.svg(620, 640, body, 'L4 The worker loop: six steps every 2 seconds', 'c4 ringsvg')


# ------------------------------------------------------------------ L4c checkout sequence
def l4c():
    L = {'shop': (90, 'Shopper', 'p'), 'spa': (290, 'Storefront', 'k'), 'api': (500, 'api', 'kf'),
         'pg': (700, 'Postgres', 'g'), 'pay': (900, 'Payments', 'gh'), 'wk': (1100, 'worker', 'k')}
    M = [
        ('Checkout', [('shop', 'spa', 'Place order', ''),
                      ('spa', 'api', 'POST /checkout', ''),
                      ('api', 'pg', 'Tx: pending, hold stock', ''),
                      ('api', 'pay', 'create payment intent', ''),
                      ('pay', 'api', 'client secret', 'ret'),
                      ('api', 'spa', 'order id + secret', 'ret')]),
        ('Pay', [('spa', 'pay', 'confirm card (provider widget)', 'h'),
                 ('pay', 'api', 'webhook: authorized', 'h'),
                 ('api', 'pg', 'Tx: paid + outbox row', '')]),
        ('Fulfil', [('wk', 'pg', 'claim outbox rows', ''),
                    ('wk', 'pay', 'capture payment', ''),
                    ('wk', 'pg', 'mark row done', '')]),
    ]
    body, h = c.sequence(L, M)
    return c.svg(1200, h, body, 'L4 One checkout, as a sequence')


if __name__ == '__main__':
    c.build({'LEVELS': LEVELS, 'L1': l1(), 'L2A': l2a(), 'L2B': l2b(), 'L3': l3(),
             'L4A': l4a(), 'L4B': l4b(), 'L4C': l4c()},
            template=os.path.join(HERE, 'page.html'), argv=DEFAULTS + sys.argv[1:])
