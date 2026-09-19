#!/usr/bin/env python3
"""Compute transitive module dependency closure for the Odoo 19 'Website domain' trim.

Read-only on the Odoo repo. Writes keep/delete lists next to this script
(keep_modules.txt, delete_modules.txt) unless --outdir is given.

Usage:
  python3 compute_closure.py --roots /home/cuong/odoo/addons /home/cuong/odoo/odoo/addons
"""
import ast
import os
import re
import sys

DEFAULT_ROOTS = ['/home/cuong/odoo/addons', '/home/cuong/odoo/odoo/addons']
OUTDIR = os.path.dirname(os.path.abspath(__file__))


def load_manifests(roots):
    addons, errors, origin = {}, {}, {}
    for root in roots:
        for d in sorted(os.listdir(root)):
            path = os.path.join(root, d)
            if not os.path.isdir(path):
                continue
            mf = os.path.join(path, '__manifest__.py')
            if not os.path.exists(mf):
                continue
            if d in addons:
                errors[d] = f'DUPLICATE in {root} (also in {origin[d]})'
                continue
            try:
                raw = open(mf, encoding='utf-8').read().strip()
                if raw.startswith('manifest ='):
                    raw = raw[len('manifest ='):].lstrip()
                elif raw.startswith('manifest='):
                    raw = raw[len('manifest='):].lstrip()
                data = ast.literal_eval(raw)
                if not isinstance(data, dict):
                    raise ValueError('manifest is not a dict')
                deps = data.get('depends', []) or []
                if not isinstance(deps, (list, tuple)):
                    raise ValueError('depends not a list')
                addons[d] = sorted(set(str(x) for x in deps))
                origin[d] = root
            except Exception as e:
                errors[d] = repr(e)
    return addons, errors, origin


def closure(seeds, addons):
    seen = set(seeds)
    stack = list(seeds)
    missing = set()
    while stack:
        m = stack.pop()
        for dep in addons.get(m, []):
            if dep not in addons:
                missing.add(dep)
                continue
            if dep not in seen:
                seen.add(dep)
                stack.append(dep)
    return seen, missing


def prefix_glob(allmods, prefix):
    return {m for m in allmods if m.startswith(prefix)}


def classify(m):
    if re.fullmatch(r'l10n_.*', m):
        return 'Localization (l10n_*)'
    if re.fullmatch(r'test_.*', m):
        return 'Test modules (test_*)'
    if re.fullmatch(r'pos.*', m):
        return 'Point of Sale (pos_*)'
    if re.fullmatch(r'payment_[a-z0-9_]+', m) and m != 'payment':
        return 'Payment providers (payment_*)'
    if re.fullmatch(r'(crm|.*crm.*)', m):
        return 'CRM'
    if re.fullmatch(r'hr.*', m):
        return 'HR'
    if re.fullmatch(r'mrp.*', m):
        return 'Manufacturing (mrp)'
    if re.fullmatch(r'project.*', m):
        return 'Project'
    if re.fullmatch(r'purchase.*', m):
        return 'Purchasing (purchase)'
    if re.fullmatch(r'mass_mailing.*', m):
        return 'Marketing (mass_mailing)'
    if re.fullmatch(r'event.*', m):
        return 'Events'
    if re.fullmatch(r'spreadsheet.*', m):
        return 'Spreadsheets/Dashboards'
    if re.fullmatch(r'(fleet|.*fleet.*)', m):
        return 'Fleet'
    if re.fullmatch(r'.*repair.*', m):
        return 'Repair'
    if re.fullmatch(r'survey.*', m):
        return 'Survey'
    if re.fullmatch(r'lunch', m):
        return 'Lunch'
    if re.fullmatch(r'gamification.*', m):
        return 'Gamification'
    if re.fullmatch(r'google_.*', m) or re.fullmatch(r'microsoft_.*', m):
        return 'External accounts/calendar'
    if re.fullmatch(r'(auth_.*|cloud_storage.*|google_recaptcha|phone_validation|base_.*|bus|web_hierarchy)', m):
        return 'Platform infra (auth/storage)'
    if re.fullmatch(r'(snailmail.*|sms_twilio|iap.*|partner_autocomplete|privacy_lookup|mail_bot.*|mail_group|mail_plugin|data_recycle|certificate|board|digest|rating|web_tour|web_unsplash|link_tracker)', m):
        return 'Platform/comm infra'
    if re.fullmatch(r'(account|account_.*|analytic)', m):
        return 'Accounting (account)'
    if re.fullmatch(r'(stock.*|delivery|delivery_.*|barcodes.*)', m):
        return 'Inventory (stock/delivery)'
    if re.fullmatch(r'(sale.*|sales_team)', m):
        return 'Sales (sale)'
    if re.fullmatch(r'product.*|uom', m):
        return 'Product/UoM'
    return 'Other'


def main(roots, outdir):
    addons, errors, origin = load_manifests(roots)
    ALL = set(addons)
    print(f'Total modules parsed: {len(ALL)}')
    if errors:
        print('MANIFEST PARSE/DUPLICATE ERRORS:')
        for m, e in sorted(errors.items()):
            print(f'  {m}: {e}')

    explicit = [
        'website',           # website builder
        'website_blog',      # blog
        'website_forum',     # forum
        'im_livechat',       # live chat core
        'website_livechat',  # live chat on website
        'website_slides',    # e-learning
        'website_mail',      # website platform infra (also pulled by closure anyway)
        'theme_default',     # website theme configurator references it (no hard depends)
    ]
    glob_seeds = set()
    for p in ['website_sale_', 'website_slides_']:
        glob_seeds |= prefix_glob(ALL, p)
    seeds = (set(explicit) | glob_seeds) & ALL

    print('\nSEED SUMMARY:')
    print(f'  explicit: {sorted(explicit)}')
    print(f'  glob website_sale_* : {sorted(prefix_glob(ALL, "website_sale_"))}')
    print(f'  glob website_slides_*: {sorted(prefix_glob(ALL, "website_slides_"))}')
    print(f'  final seed count: {len(seeds)}')

    kept, missing_deps = closure(sorted(seeds), addons)
    deletes = ALL - kept
    print(f'\nCLOSURE SIZE: kept={len(kept)}  deleted={len(deletes)}  (of {len(ALL)})')
    missing_deps -= seeds
    print(f'DEPENDS REFERENCING MODULES NOT ON DISK (likely enterprise): {sorted(missing_deps) or "none"}')
    bad = sorted(m for m in kept if not set(addons.get(m, [])).issubset(kept))
    print(f'KEPT MODULES WHOSE DEPENDS ESCAPES KEPT SET: {bad or "none (all satisfied)"}')

    with open(os.path.join(outdir, 'keep_modules.txt'), 'w') as f:
        f.write('\n'.join(sorted(kept)) + '\n')
    with open(os.path.join(outdir, 'delete_modules.txt'), 'w') as f:
        f.write('\n'.join(sorted(deletes)) + '\n')
    print(f'\nWROTE keep_modules.txt ({len(kept)}) and delete_modules.txt ({len(deletes)}) into {outdir}')

    fam = {}
    for m in sorted(deletes):
        fam.setdefault(classify(m), []).append(m)
    print(f'\nDELETE GROUPING ({len(deletes)} total):')
    for g in sorted(fam):
        print(f'  {g} ({len(fam[g])}): {" ".join(fam[g])}')

    webdel = sorted(m for m in deletes if m.startswith(('website_', 'theme_')))
    print(f'\nDELETED website_*/theme_* ({len(webdel)}): {" ".join(webdel)}')
    return 0


if __name__ == '__main__':
    roots = DEFAULT_ROOTS
    outdir = OUTDIR
    args = sys.argv[1:]
    if '--roots' in args:
        i = args.index('--roots')
        roots = args[i + 1:i + 3]
    if '--outdir' in args:
        i = args.index('--outdir')
        outdir = args[i + 1]
    sys.exit(main(roots, outdir))
