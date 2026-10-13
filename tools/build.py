#!/usr/bin/env python
"""Build step of the Koreans add-on. This repository is the single source of truth: edit its files directly.

Run after every edit, before a game test or a commit:

    python tools/build.py            # update the generated files in place
    python tools/build.py --check    # exit 1 if a generated file is stale (tests run this)

Generated files - never edit them by hand, edit the source named here:

  data/<file>.xml.xmb              compiled from data/<file>.xml (the engine reads the twin); the same for
                                   data/abilities/<file>.xml
  data/strings/<lang>/stringmods.xml.xmb
                                   compiled from data/strings/english/stringmods.xml into every language folder
                                   (new strings are English only; owner rule 2026-10-08)
  art/buildings/town_center/town_center.xml, art/buildings/asian_civs/bansho/bansho.xml,
  art/buildings/asian_civs/stable/stable.xml, art/buildings/asian_civs/dock/dock.xml,
  art/buildings/asian_civs/monastery/monastery.xml, art/buildings/asian_civs/rice_paddy/rice_paddy.xml,
  art/buildings/asian_civs/trade_market/trade_market.xml
                                   vanilla plus the Korean branch (tools/korean_visuals.py); AoP overrides none of them

Hosted by AoP, not shipped here (owner 2026-10-10 castle, 2026-10-11 consulate, korean_visuals.AOP_HOSTED):
art/buildings/asian_civs/castle/castle.xml, art/buildings/asian_civs/consulate/consulate.xml - AoP overrides them and has
priority 1 above this add-on, so AoP's own file carries the Korean branch (inert without this add-on). --check fails when
AoP's file drifts from the Korean source; `python tools/korean_visuals.py --write-aop` refreshes it.
  sound/soundsetsde.mods.xml       AoP's file + tools/korean_soundsets.xml (the engine's merge of this file across
                                   two mods is unverified, so the add-on carries both)
  sound/ypsettlerasian_snds.xml    AoP's copy if any, else vanilla, with Korean voices for zpKoreans
                                   (tools/korean_sounds.py)
  sound/*wagon*_snds.xml, sound/ypfishingboatasian_snds.xml
                                   AoP's copy if any, else vanilla, with a zpKoreans choice after every Japanese
                                   one: the Japanese voices as their Korean twins (tools/korean_sounds.py)
  art/units/korean_monk/*.xml, data/tactics/zpmonkkorean.tactics
                                   the Korean monk's animfiles and tactics (tools/korean_monk.py)
  art/units/korean_jochong/*.xml|.material, art/units/korean_jangchang/*.xml|.material,
  art/units/korean_gakgung/*.xml|.material
                                   the Korean infantry's animfiles and materials (tools/korean_infantry.py; their models:
                                   tools/korean_infantry_model.py)
  art/units/korean_lancer/*.xml|.material, art/units/korean_horse_archer/*.xml|.material
                                   the Korean cavalry's animfiles and materials (tools/korean_cavalry.py; their GR2
                                   clones are written by that script, vanilla bytes)

Every runtime XML (.xml .material .lgt .tactics .personality) under art/ data/ game/ sound/ is written with CRLF
line endings: an LF-only file is silently ignored by the engine.

Needs the AoP checkout next to this repo (../age-of-pirates, or the AOP_ROOT environment variable) for its
archive tools (read only) and the installed game for the vanilla animfiles.
"""
import argparse
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import korean_visuals  # noqa: E402
import korean_sounds  # noqa: E402
import korean_monk  # noqa: E402
import korean_infantry  # noqa: E402
import korean_cavalry  # noqa: E402

AOP = korean_visuals.AOP
sys.path.insert(0, os.path.join(AOP, '.claude', 'skills', 'aoe3de-bar-archives', 'scripts'))
import bartool  # noqa: E402
import xmbc  # noqa: E402

RUNTIME_XML = ('.xml', '.material', '.lgt', '.tactics', '.personality')
GAME_DIRS = ('art', 'data', 'game', 'sound')
CRLF, LF = b'\r\n', b'\n'


def crlf(data):
    return data.replace(CRLF, LF).replace(LF, CRLF)


def compile_xmb(name, data):
    """alz4-wrapped XMB of an XML file; refuses one that does not decode back identically."""
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, name)
        open(p, 'wb').write(data)
        xmb, root = xmbc.compile_xml(p)
        if xmbc.canon(bartool.xmb_to_element(xmb)) != xmbc.canon(root):
            sys.exit('%s: XMB does not decode back to the source - refusing to build' % name)
        return xmbc.wrap_alz4(xmb)


def merged_soundsets():
    aop = open(os.path.join(AOP, 'sound', 'soundsetsde.mods.xml'), 'rb').read().decode('utf-8-sig')
    k = open(os.path.join(HERE, 'korean_soundsets.xml'), 'rb').read().decode('utf-8-sig')
    aop, k = aop.replace('\r\n', '\n'), k.replace('\r\n', '\n')
    body = k[k.index('<soundsetdefmods>') + len('<soundsetdefmods>\n'):k.rindex('</soundsetdefmods>')]
    names = [n.split('"')[0] for n in body.split('<soundset name="')[1:]]
    clash = [n for n in names if '<soundset name="%s"' % n in aop]
    if clash:
        sys.exit('Korean soundsets already defined in AoP sound/soundsetsde.mods.xml: %s' % clash)
    end = aop.rindex('</soundsetdefmods>')
    return crlf((aop[:end] + body + aop[end:]).encode('utf-8'))


def rel(path):
    return os.path.relpath(path, REPO).replace(os.sep, '/')


def build():
    """{repo-relative path: bytes} of every file this step owns (CRLF-normalised sources + generated files)."""
    out = {}
    for top in GAME_DIRS:
        for d, _, files in os.walk(os.path.join(REPO, top)):
            for f in files:
                if f.endswith(RUNTIME_XML):
                    p = os.path.join(d, f)
                    out[rel(p)] = crlf(open(p, 'rb').read())
    data_dir = os.path.join(REPO, 'data')
    for f in sorted(os.listdir(data_dir)):
        if f.endswith('.xml'):
            out['data/%s.xmb' % f] = compile_xmb(f, out['data/' + f])
    for f in sorted(os.listdir(os.path.join(data_dir, 'abilities'))):
        if f.endswith('.xml'):
            out['data/abilities/%s.xmb' % f] = compile_xmb(f, out['data/abilities/' + f])
    strings = os.path.join(data_dir, 'strings')
    xmb = compile_xmb('stringmods.xml', out['data/strings/english/stringmods.xml'])
    for lang in sorted(os.listdir(strings)):
        if os.path.isdir(os.path.join(strings, lang)):
            out['data/strings/%s/stringmods.xml.xmb' % lang] = xmb
    for path, (data, _, _) in korean_visuals.build().items():
        out[path] = data
    out.update(korean_sounds.build())
    out.update(korean_monk.build())
    out.update(korean_infantry.build())
    out.update(korean_cavalry.build())
    out['sound/soundsetsde.mods.xml'] = merged_soundsets()
    return out


def stale(files):
    bad = []
    for path, data in files.items():
        p = os.path.join(REPO, *path.split('/'))
        if not os.path.isfile(p) or open(p, 'rb').read() != data:
            bad.append(path)
    return bad


def hosted_problems():
    """AoP-hosted animfiles: a copy in this repo (it would shadow AoP's when the add-on stands above AoP) or an AoP
    file that drifted from this repo's Korean source."""
    bad = ['%s: AoP hosts this file - delete the add-on copy' % p for p in korean_visuals.AOP_HOSTED
           if os.path.isfile(os.path.join(REPO, *p.split('/')))]
    bad += ['%s: AoP copy is stale - run python tools/korean_visuals.py --write-aop' % p
            for p, (want, have, _) in korean_visuals.aop_hosted().items() if want != have]
    return bad


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    files = build()
    bad = stale(files)
    hosted = hosted_problems()
    for line in hosted:
        print('AOP-HOSTED', line)
    if a.check:
        for path in bad:
            print('STALE', path)
        print('%d files, %s' % (len(files), 'up to date' if not bad else '%d stale' % len(bad)))
        return 1 if bad or hosted else 0
    for path in bad:
        p = os.path.join(REPO, *path.split('/'))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'wb').write(files[path])
    print('%d files checked, %d written' % (len(files), len(bad)))
    return 1 if hosted else 0


if __name__ == '__main__':
    sys.exit(main())
