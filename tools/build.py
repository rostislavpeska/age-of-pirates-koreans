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
  art/buildings/asian_civs/stable/stable.xml
                                   AoP's override of that animfile when AoP has one, else vanilla, plus the Korean
                                   branch (tools/korean_visuals.py; the Korean models stay in AoP's art/)
  sound/soundsetsde.mods.xml       AoP's file + tools/korean_soundsets.xml (the engine's merge of this file across
                                   two mods is unverified, so the add-on carries both)
  sound/ypsettlerasian_snds.xml    AoP's copy if any, else vanilla, with Korean voices for zpKoreans
                                   (tools/korean_sounds.py)
  sound/*wagon*_snds.xml, sound/ypfishingboatasian_snds.xml
                                   AoP's copy if any, else vanilla, with a zpKoreans choice after every Japanese
                                   one: the Japanese voices as their Korean twins (tools/korean_sounds.py)
  art/units/korean_monk/*.xml, data/tactics/zpmonkkorean.tactics
                                   the Korean monk's animfiles and tactics (tools/korean_monk.py)

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
    out['sound/soundsetsde.mods.xml'] = merged_soundsets()
    return out


def stale(files):
    bad = []
    for path, data in files.items():
        p = os.path.join(REPO, *path.split('/'))
        if not os.path.isfile(p) or open(p, 'rb').read() != data:
            bad.append(path)
    return bad


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    files = build()
    bad = stale(files)
    if a.check:
        for path in bad:
            print('STALE', path)
        print('%d files, %s' % (len(files), 'up to date' if not bad else '%d stale' % len(bad)))
        return 1 if bad else 0
    for path in bad:
        p = os.path.join(REPO, *path.split('/'))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'wb').write(files[path])
    print('%d files checked, %d written' % (len(files), len(bad)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
