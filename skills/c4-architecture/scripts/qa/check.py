#!/usr/bin/env python3
"""Static checks for a built C4 page. Usage: check.py PAGE.html  (exit 1 on failure)."""
import re
import sys
from html.parser import HTMLParser

page = open(sys.argv[1]).read()
HTMLParser().feed(page)  # raises on badly broken markup
res = {
    'svg': page.count('<svg'),
    'external_scripts': len(re.findall(r'<script[^>]+src=', page)),
    'level_ids': [f'l{i}' for i in range(1, 5) if f'id="l{i}"' in page],
    'leftover_placeholders': page.count('{{'),
    'src_links': page.count('class="src"'),
}
ok = res['svg'] >= 4 and not res['external_scripts'] and len(res['level_ids']) == 4 and not res['leftover_placeholders']
print(res, 'PASS' if ok else 'FAIL')
sys.exit(0 if ok else 1)
