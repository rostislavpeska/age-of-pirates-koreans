#!/usr/bin/env python
"""Build the Korean building visuals into the vanilla Town Center, Barracks and Stable animfiles.

Koreans (civ zpKoreans) use the vanilla protos ypBarracksJapanese and ypStableJapanese (and TownCenter), so
every tech, card, AI rule and trigger that names them keeps working; only the look differs. Animfiles
cannot be patched partially, so the mod ships a full copy of each vanilla animfile with:

  * the Korean model's <definebone> lines that vanilla lacks (after the last vanilla one);
  * the Korean model's <submodel> blocks (after the last vanilla submodel);
  * one more child of the Japanese "Tech" logic, <zpkoreanvisuals>. It is the LAST child, so it wins
    over colonialize/industrialize while the owner has the tech - the vanilla pattern of
    <dehciturbidepalace> in the Mediterranean branch of town_center.xml and of the mod's
    <zpazteccitydefendersetup> in dock.xml. Inside it a nested switch: <none> = the vanilla
    Discovery Age look (generic Asian, as Japan), <colonialize> = the Korean model from the first
    upgrade (Colonial Age) on; the castle switches on its own first upgrade, <ypfrontiercastle>.

zpKoreanVisuals is activated only by zpAge0Korean (data/techtreemods.xml), so Japanese buildings
stay Japanese. Every byte of the base file is kept (the base is AoP's own override of that animfile when AoP has
one, else vanilla from the installed game). The Korean model animfiles are read from this repo's art/ (moved from
AoP on 2026-10-09: all Korean content lives here for now, owner). tools/build.py writes the merged files into this repo; they are never edited by hand
and never live in AoP's art/ (they would replace every civ's Town Center for AoP players without the add-on). The one
exception is AOP_HOSTED below: an animfile AoP already overrides (the castle, the consulate), whose Korean branch AoP
carries itself.

    python tools/korean_visuals.py            # summary of what tools/build.py generates
"""
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))      # this add-on
# the AoP checkout next to this repo (both live in <profile>/mods/local), read only
AOP = os.environ.get('AOP_ROOT') or os.path.join(os.path.dirname(REPO), 'age-of-pirates')
BARTOOL = os.path.join(AOP, '.claude', 'skills', 'aoe3de-bar-archives', 'scripts', 'bartool.py')
BS = chr(92)

# (vanilla archive animfile, mod output, Korean source animfile, culture branch, add attack anims[, first upgrade tech])
# The first upgrade tech switches to the Korean model: 'colonialize' (the age) for buildings whose vanilla look changes by
# age; the castle changes by its OWN upgrades (ypfrontiercastle / ypfortifiedcastle), so its Korean look comes with the
# castle's first upgrade (owner 2026-10-10: "as castle 1st upgrade Korean variant", "you need to edit vanilla anim file
# too", "Check barracks and stables", "So two places - final (castle variant) + test bed").
# Korean Town Center: ON by the owner's go of 2026-10-08 ("So GO with the Town center modification") while
# `gr2_lint.py --profile korean_tc art/buildings/korean_tc` still FAILs 6 checks (texture budget, texel density,
# UV lineage - the open texturing work, AGENTS.md rule 13). Overriding town_center.xml touches every civ's Town
# Center; --check keeps its vanilla bytes honest.
BUILDINGS = [
    ('Art/buildings/town_center/town_center.xml.XMB', 'art/buildings/town_center/town_center.xml',
     'art/buildings/korean_tc/korean_tc.xml', 'japanese', False),
    ('Art/buildings/asian_civs/bansho/bansho.xml.XMB', 'art/buildings/asian_civs/bansho/bansho.xml',
     'art/zbench_korean_military/barracks/korean_barracks_physics.xml', 'japanese', True),
    ('Art/buildings/asian_civs/stable/stable.xml.XMB', 'art/buildings/asian_civs/stable/stable.xml',
     'art/zbench_korean_military/stable/korean_stable_physics.xml', 'japanese', False),
    # Korean castle (owner 2026-10-10: "implement the model to the game incl. destruction and construction", then "as
    # castle 1st upgrade Korean variant"): the vanilla Japanese castle until the castle's first upgrade (ypFrontierCastle),
    # the Korean castle from it on - ypFrontierCastle stays active, so the Fortified castle keeps the Korean look too (one
    # Korean castle model so far; the Industrial one waits). The test bed zzTESTKoreanCastle shows it directly.
    # gr2_lint korean_castle / korean_castle_con pass
    ('Art/buildings/asian_civs/castle/castle.xml.XMB', 'art/buildings/asian_civs/castle/castle.xml',
     'art/buildings/korean_castle/korean_castle.xml', 'japanese', False, 'ypfrontiercastle'),
    # Korean Dock (owner 2026-10-10: "export dock to the game - construction, destruction - ... then add as age1 Korean
    # Dock"): YPDockAsian's animfile, which AoP does not override. First upgrade 'none' = the Korean Dock from the
    # Discovery Age on (no vanilla branch inside the marker); one Korean Dock model so far, so it holds in every age.
    # gr2_lint korean_dock / korean_dock_con (tools/gr2_lint/profiles.json)
    ('Art/buildings/asian_civs/dock/dock.xml.XMB', 'art/buildings/asian_civs/dock/dock.xml',
     'art/buildings/korean_dock/korean_dock.xml', 'japanese', False, 'none'),
    # Korean Consulate (owner 2026-10-11: "add both models into game - incl damaged and construction states"; "Oh no, in Korean
    # mod", "Same monastery, but override in both using aop code"). AoP overrides consulate.xml, so a copy here lost to it
    # (the Japanese consulate in the owner's game, 2026-10-11: "Consulate still original Japanese ... follow pattern"):
    # AoP hosts the branch, like the castle (AOP_HOSTED). First upgrade 'none' = the Korean Consulate from the Discovery Age
    # (owner "From Discovery"). gr2_lint korean_consulate / korean_consulate_con (tools/gr2_lint/profiles.json)
    ('Art/buildings/asian_civs/consulate/consulate.xml.XMB', 'art/buildings/asian_civs/consulate/consulate.xml',
     'art/buildings/korean_consulate/korean_consulate.xml', 'japanese', False, 'none'),
    # Korean Monastery (owner 2026-10-11: "add both models into game - incl damaged and construction states"; "Oh no, in Korean
    # mod", "Same monastery, but override in both using aop code"): this add-on ships the merged animfile, built on AoP's own
    # override when AoP has one, else vanilla. First upgrade 'none' = the Korean Monastery from the Discovery Age (owner "From
    # Discovery"). gr2_lint korean_monastery / korean_monastery_con (tools/gr2_lint/profiles.json)
    ('Art/buildings/asian_civs/monastery/monastery.xml.XMB', 'art/buildings/asian_civs/monastery/monastery.xml',
     'art/buildings/korean_monastery/korean_monastery.xml', 'japanese', False, 'none'),
    # Korean Rice Paddy (owner 2026-10-11: "finish the last model - the very simplest one - Rice paddy ... in the Korean style
    # with proper roof", "for field. you create only the shelter. rest is generic and should be reused", "and Ricepaddy also
    # needs construction and destruction"): the Korean shelter on the vanilla field (paddy / paddy_con attachments, footprint,
    # asi_2x2 kit); AoP does not override rice_paddy.xml. First upgrade 'none' = the Korean Rice Paddy from the Discovery Age
    # (the Consulate / Monastery precedent). gr2_lint korean_rice_paddy / korean_rice_paddy_con (tools/gr2_lint/profiles.json)
    ('Art/buildings/asian_civs/rice_paddy/rice_paddy.xml.XMB', 'art/buildings/asian_civs/rice_paddy/rice_paddy.xml',
     'art/buildings/korean_rice_paddy/korean_rice_paddy.xml', 'japanese', False, 'none'),
    # Korean Market (owner 2026-10-11: "When done, add the market to the game as market asian", "same as japanese / chinese",
    # "plus the destruction test bed"): ypTradeMarketAsian's animfile, which AoP does not override; the Japanese and Chinese
    # markets are culture branches of it. First upgrade 'none' = the Korean Market from the Discovery Age (the Dock / Consulate /
    # Monastery / Rice Paddy precedent; one Korean Market model so far, so it holds in every age). gr2_lint korean_market /
    # korean_market_con (tools/gr2_lint/profiles.json)
    ('Art/buildings/asian_civs/trade_market/trade_market.xml.XMB', 'art/buildings/asian_civs/trade_market/trade_market.xml',
     'art/buildings/korean_market/korean_market.xml', 'japanese', False, 'none'),
]

MARKER = 'zpkoreanvisuals'

# Hosted by AoP (owner 2026-10-10: "OR AoP can directly have Korean civ in that file. If civ doesn't exist nothing
# happens", "So only castle.xml edit"): AoP ships its own castle.xml override, so a copy here lost to it whenever AoP
# stood above the add-on in mod priority (the Japanese castle in game, 2026-10-10). AoP's file now carries the Korean
# branch itself - inert without this add-on, where zpKoreanVisuals never exists (the pattern of AoP's zpAotWKhmers,
# keyed on Age of the World's Age0Khmers). This add-on ships no copy; the Korean source stays here
# (art/buildings/korean_castle/korean_castle.xml). tools/build.py --check fails when AoP's file drifts from it, and
# `python tools/korean_visuals.py --write-aop` refreshes AoP's file. The rule for every building (owner 2026-10-11, "follow
# pattern"): an animfile AoP overrides is hosted by AoP, never shipped here - AoP has priority 1 above this add-on, so a copy
# here never shows. tests/test_no_shadowed_files.py fails when this add-on ships a replacing file AoP also ships.
AOP_HOSTED = ('art/buildings/asian_civs/castle/castle.xml', 'art/buildings/asian_civs/consulate/consulate.xml')

# The vanilla barracks fires from its RangedAttack/RangedAttackShip anims (barracks.tactics); the Korean
# bench animfile has none, so the merged copy adds them to the Korean built submodel (vanilla bansho text,
# simskeleton = the Korean damaged model, as in art/buildings/korean_tc/korean_tc.xml).
ATTACK_ANIMS = '''    <anim>RangedAttack<assetreference type="GrannyAnim">
        <file>animation_library{bs}building{bs}ranged_attack</file>
        <tag type="Attack">0.45</tag>
        <tag type="SpecificSoundSet" checkvisible="1" set="RifleShot">0.45</tag>
      </assetreference>
      <component>LIVE</component>
      <simskeleton>
        <model>{damaged}</model>
      </simskeleton>
    </anim>
    <anim>RangedAttackShip<assetreference type="GrannyAnim">
        <file>animation_library{bs}building{bs}ranged_attack</file>
        <tag type="Attack">0.45</tag>
        <tag type="SpecificSoundSet" checkvisible="1" set="RifleShot">0.45</tag>
      </assetreference>
      <component>LIVE</component>
      <simskeleton>
        <model>{damaged}</model>
      </simskeleton>
    </anim>
'''


def vanilla_text(archive_path):
    out = subprocess.run([sys.executable, BARTOOL, 'cat', archive_path], capture_output=True, check=True)
    return out.stdout.decode('utf-8-sig').replace('\r\n', '\n')


def read(path, root=AOP):
    return open(os.path.join(root, path), 'rb').read().decode('utf-8-sig').replace('\r\n', '\n')


def korean_parts(text, add_attack):
    bones = re.findall(r'<definebone>([^<]+)</definebone>', text)
    subs = re.findall(r'(  <submodel>.*?</submodel>\n)', text, re.S)
    assert subs, 'no submodels'
    m = re.search(r'\n  <component>[^<]*(<logic type="BuildingCompletion">.*?\n    </logic>)\n  </component>\n</animfile>',
                  text, re.S)
    assert m, 'no top-level BuildingCompletion component'
    completion = m.group(1)
    if add_attack:
        built = [i for i, s in enumerate(subs) if re.match(r'  <submodel>\w+_built\b', s)]
        assert len(built) == 1, built
        s = subs[built[0]]
        assert '<anim>RangedAttack' not in s
        dmg = re.search(r'<simskeleton>\s*<model>([^<]+)</model>', s).group(1)
        i = s.rindex('  </submodel>')
        subs[built[0]] = s[:i] + ATTACK_ANIMS.format(bs=BS, damaged=dmg) + s[i:]
    return bones, subs, completion


def tech_logic_span(text, culture):
    """(start, end) of the <logic type="Tech"> block directly inside <culture> of the Culture logic."""
    c0 = text.index('<%s>' % culture)
    c1 = text.index('</%s>' % culture, c0)
    t0 = text.index('<logic type="Tech">', c0)
    assert t0 < c1
    depth, pos = 0, t0
    for m in re.finditer(r'<logic\b|</logic>', text[t0:c1]):
        depth += 1 if m.group(0) == '<logic' else -1
        if depth == 0:
            return t0, t0 + m.end()
    raise ValueError('unbalanced Tech logic in <%s>' % culture)


def merge(vanilla, korean_text, culture, add_attack, first='colonialize'):
    bones, subs, completion = korean_parts(korean_text, add_attack)
    have = {b.lower() for b in re.findall(r'<definebone>([^<]+)</definebone>', vanilla)}
    vsubs = {s.lower() for s in re.findall(r'<submodel>([^<\s]+)', vanilla)}
    for s in subs:
        name = re.match(r'  <submodel>([^<\s]+)', s).group(1)
        assert name.lower() not in vsubs, 'submodel name collides with vanilla: ' + name
    out = vanilla
    # 1. bones vanilla lacks, after the last vanilla definebone
    new_bones, seen = [], set()
    for b in bones:
        if b.lower() not in have and b.lower() not in seen:
            seen.add(b.lower()); new_bones.append('  <definebone>%s</definebone>\n' % b)
    if new_bones:
        last = out.rindex('</definebone>\n') + len('</definebone>\n')
        out = out[:last] + ''.join(new_bones) + out[last:]
    # 2. Korean submodels after the last vanilla submodel
    last = out.rindex('</submodel>\n') + len('</submodel>\n')
    out = out[:last] + ''.join(subs) + out[last:]
    # 3. the marker branch, last child of the culture's Tech logic. Inside it a nested age switch (owner
    #    2026-10-08: "Age0 is generic asian (same as Japan) and age1 and age2 (1st upgrade is the new one"):
    #      <none>         the vanilla Discovery Age branch, verbatim
    #      <colonialize>  the Korean model - from the first upgrade on; colonialize stays active, so it holds
    #                     through Industrial/Imperial too (one Korean model so far)
    t0, t1 = tech_logic_span(out, culture)
    close = out.rindex('</logic>', t0, t1)
    line0 = out.rindex('\n', 0, close) + 1
    ind = out[line0:close]                       # indentation of the Tech logic's closing tag
    if ind.strip():                              # a compact base (AoP's castle.xml: one line per culture branch):
        none = re.match(r'<logic type="Tech">\s*(<none>.*?</none>)', out[t0:t1], re.S)   # the marker goes in inline
        block = ''.join(['<%s><logic type="Tech">' % MARKER, none.group(1) if none and first != 'none' else '',
                         '<%s>' % first, completion, '</%s></logic></%s>' % (first, MARKER)])
        return out[:close] + block + out[close:]
    none = re.search(r'\n(%s  <none>\n.*?\n%s  </none>)\n' % (ind, ind), out[t0:t1], re.S)
    korean = '\n'.join((ind + '        ' + l[4:]) if l.startswith('    ') else (ind + '        ' + l)
                       for l in completion.split('\n'))
    parts = ['%s  <%s>' % (ind, MARKER), '%s    <logic type="Tech">' % ind]
    if none and first != 'none':                 # the vanilla stable has no <none> branch; first 'none' = Korean from age 1
        parts.append('\n'.join('    ' + l for l in none.group(1).split('\n')))
    parts += ['%s      <%s>' % (ind, first), korean, '%s      </%s>' % (ind, first),
              '%s    </logic>' % ind, '%s  </%s>' % (ind, MARKER)]
    out = out[:line0] + '\n'.join(parts) + '\n' + out[line0:]
    return out


def strip(text, korean_text):
    """AoP's own animfile back from an AoP-hosted merge: the Korean submodels and the marker branch removed (a no-op on
    a file without them). Only for merges that add no definebone (the castle: its 39 bones are AoP's)."""
    for name in re.findall(r'(?m)^  <submodel>([^<\s]+)', korean_text):
        text = re.sub(r'  <submodel>%s(?=[<\s]).*?</submodel>\n' % re.escape(name), '', text, count=1, flags=re.S)
    text = re.sub(r'(?ms)^[ \t]*<%s>.*?</%s>\n' % (MARKER, MARKER), '', text)     # indented base: own lines
    return re.sub(r'(?s)<%s>.*?</%s>' % (MARKER, MARKER), '', text)                # compact base: inline


def canon(e):
    return (e.tag, sorted(e.attrib.items()), (e.text or '').strip(), [canon(c) for c in e])


def verify(text, culture, first='colonialize'):
    root = ET.fromstring(text)
    # case-insensitive: vanilla town_center.xml itself refers to lak_sub_construction_stage_02 in another case
    names = {(s.text or '').strip().lower() for s in root.iter('submodel')}
    refs = {r.get('ref').lower() for r in root.iter('submodelref')}
    missing = refs - names
    assert not missing, 'unresolved submodelref: %s' % sorted(missing)
    for comp in root.findall('component'):
        for lg in comp.findall('logic'):
            br = lg.find(culture)
            if br is None:
                continue
            tech = br.find('logic')
            kids = [c.tag for c in tech]
            assert kids[-1] == MARKER, kids
            inner = tech.find(MARKER).find('logic')
            assert inner.get('type') == 'Tech'
            ages = [c.tag for c in inner]
            assert ages[-1] == first and ages[:-1] in ([], ['none']), ages
            if 'none' in kids and first != 'none':   # the Discovery Age branch is a copy of vanilla's (indentation aside)
                assert canon(inner.find('none')) == canon(tech.find('none'))
            return kids + ['/'.join(ages)]
    raise AssertionError('no %s branch' % culture)


def build(aop_root=AOP):
    """{add-on relative path: CRLF bytes} for every Korean building animfile this add-on ships (not the AoP-hosted)."""
    out = {}
    for archive, out_path, src, culture, attack, *opt in BUILDINGS:
        if out_path in AOP_HOSTED:
            continue
        first = opt[0] if opt else 'colonialize'
        own = os.path.join(aop_root, out_path)
        base = read(out_path, aop_root) if os.path.isfile(own) else vanilla_text(archive)
        merged = merge(base, read(src, REPO), culture, attack, first)   # the Korean model: this repo
        out[out_path] = (merged.replace('\n', '\r\n').encode('utf-8'), verify(merged, culture, first),
                         'AoP override' if os.path.isfile(own) else 'vanilla')
    return out


def aop_hosted(aop_root=AOP):
    """{AoP relative path: (wanted CRLF bytes, AoP's current bytes, Tech children)} for the animfiles AoP hosts: AoP's
    own file with the Korean parts stripped, merged again with this repo's Korean source."""
    out = {}
    for archive, out_path, src, culture, attack, *opt in BUILDINGS:
        if out_path not in AOP_HOSTED:
            continue
        first = opt[0] if opt else 'colonialize'
        korean = read(src, REPO)
        have = open(os.path.join(aop_root, out_path), 'rb').read()
        merged = merge(strip(read(out_path, aop_root), korean), korean, culture, attack, first)
        out[out_path] = (merged.replace('\n', '\r\n').encode('utf-8'), have, verify(merged, culture, first))
    return out


def main():
    for path, (data, kids, base) in build().items():
        print('%-50s base %-12s %7d bytes  Tech children %s' % (path, base, len(data), kids))
    for path, (want, have, kids) in aop_hosted().items():
        state = 'current' if want == have else 'STALE'
        if state == 'STALE' and '--write-aop' in sys.argv:
            open(os.path.join(AOP, path), 'wb').write(want)
            state = 'written'
        print('%-50s hosted by AoP %-8s %7d bytes  Tech children %s' % (path, state, len(want), kids))
    return 0


if __name__ == '__main__':
    sys.exit(main())
