#!/usr/bin/env python3
"""Trim an Odoo 19 working copy down to the DX-OS website-domain keep-list.

Usage:
  python3 trim_odoo.py --repo /path/to/odoo-copy [--dry-run]

Reads keep_modules.txt sitting next to this script. Deletes whole addon
directories (under <repo>/addons and <repo>/odoo/addons) whose name is not in
the keep-list. Never edits file contents: Odoo source stays byte-identical
for every module that survives, which is what the OLP PoF rule
("khong chinh sua ma nguon thu vien dinh kem") requires.

Typical flow:
  git -C /home/cuong/odoo worktree add /home/cuong/odoo-dxos-clean 19.0
  python3 DXOS/tools/trim_odoo.py --repo /home/cuong/odoo-dxos-clean --dry-run
  python3 DXOS/tools/trim_odoo.py --repo /home/cuong/odoo-dxos-clean
"""
import argparse
import os
import shutil
import sys


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo', required=True, help='path to an Odoo working copy (clone or git worktree)')
    ap.add_argument('--keep-list', default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                         'keep_modules.txt'))
    ap.add_argument('--dry-run', action='store_true', help='only print what would be deleted')
    a = ap.parse_args()

    keep = {line.strip() for line in open(a.keep_list, encoding='utf-8') if line.strip()}
    roots = [os.path.join(a.repo, 'addons'), os.path.join(a.repo, 'odoo', 'addons')]

    found = set()
    removed = 0
    for root in roots:
        if not os.path.isdir(root):
            print(f'WARN: missing addon root {root}', file=sys.stderr)
            continue
        for d in sorted(os.listdir(root)):
            path = os.path.join(root, d)
            if not os.path.isdir(path) or not os.path.exists(os.path.join(path, '__manifest__.py')):
                continue
            if d in keep:
                found.add(d)
                continue
            removed += 1
            print(('dry-run delete: ' if a.dry_run else 'delete: ') + os.path.relpath(path, a.repo))
            if not a.dry_run:
                shutil.rmtree(path)

    missing = sorted(keep - found)
    print(f'kept={len(found)} removed={removed} dry_run={a.dry_run}')
    if missing:
        print(f'WARN: keep-list entries not found on disk: {missing}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
