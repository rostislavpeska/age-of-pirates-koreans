"""data/homecityprotounits.xml: the home city's own unit list (citizens, performers, the explorer) = vanilla plus the
Korean explorer and the Korean copies of five Chinese customization units (PERFORMERS). The engine shows a civ's explorer from the entry with its <civilization> and <explorer />: a <visual>
animfile standing at <bone> with a <script>; the entry name is no proto (vanilla ExplorerDEHetmanPolish - Poland's
mounted Hetman - is not in protoy.xml). Without an entry the Korean home city had no explorer (owner 2026-10-17:
"Korean explorer is missing"). Not an additive *mods.xml file, so the add-on ships the whole file (tools/build.py);
built on AoP's copy would be needed if AoP ever ships one (then it must host the entry: aoe3de-multi-mod).
Audit: Blendify journal 2026-10-17-claude-opus-5.5-26.

The Korean monk rides his horse (units/korean_monk/korean_monk_horse.xml, zpMonkKorean's animfile) at the ground bone
bone_explorer_special, which tools/homecity_explorer.py puts left of the Customs House. He is NOT <selectable />: a
click opens the engine's explorer skin panel, whose skins come from no data a mod can extend (journal
2026-10-17-claude-opus-5.5-36/-37), so for the Koreans it hid the home city UI with no zoom (owner 2026-10-17). His
hover text is the Unit prop of the same name in data/asianhomecityprops.xml.
"""
import os

import korean_visuals

PATH = 'data/homecityprotounits.xml'
VANILLA = 'Data/homecityprotounits.xml.XMB'
ENTRY = r'''  <protounit>
    <name>ExplorerZPKorean</name>
    <civilization>zpKoreans</civilization>
    <visual>units\korean_monk\korean_monk_horse.xml</visual>
    <bone>bone_explorer_special</bone>
    <script>explorer</script>
    <explorer />
    <camera>china\china_homecity_dock_camera.cam</camera>
    <widescreencamera>china\china_homecity_dock_widescreencamera.cam</widescreencamera>
  </protounit>
'''


# Chinese home city customizations the Koreans get verbatim (owner 2026-10-17: "include some Chinese compatible HC
# customizations verbatim ... no overengineering. If we're not able to adopt verbatim, then strip"). Their units carry
# <culturegroup>Chinese</culturegroup> and the Koreans are Japanese culture, so each Korean unit is the vanilla entry
# with only its name (= the Korean prop's name, data/asianhomecityprops.xml) and <civilization>zpKoreans</civilization>
# changed; the props copy the vanilla prop records (same building, strings, icon). Juggler, not Torchy: juggling and
# plate spinning (beona) were the Joseon namsadang troupes' street acts.
PERFORMERS = {'ChineseJuggler': 'Korean_Juggler', 'ChinesePeasantVendor': 'Korean_PeasantVendor',
              'ChineseThug': 'Korean_Thug', 'ChinesePeasantFisherman': 'Korean_PeasantFisherman',
              'ChineseOx': 'Korean_Ox'}


def korean_unit(text, name, korean):
    """the vanilla <protounit> block named `name`, renamed and bound to the Korean civ"""
    i = text.index(f'    <name>{name}</name>\n'); s = text.rindex('  <protounit>\n', 0, i)
    e = text.index('  </protounit>\n', i) + len('  </protounit>\n'); block = text[s:e]
    assert block.count('<culturegroup>Chinese</culturegroup>') == 1, f'{name}: not a Chinese culture-group unit'
    return block.replace(f'<name>{name}</name>', f'<name>{korean}</name>').replace(
        '<culturegroup>Chinese</culturegroup>', '<civilization>zpKoreans</civilization>')


def build():
    """{repo path: CRLF bytes}"""
    assert not os.path.isfile(os.path.join(korean_visuals.AOP, *PATH.split('/'))), \
        f'AoP ships {PATH}: it outranks the add-on, so AoP must host the Korean entry (aoe3de-multi-mod)'
    text = korean_visuals.vanilla_text(VANILLA)
    assert '<homecityprotounits>' in text and 'zpKoreans' not in text, 'unexpected vanilla homecityprotounits.xml'
    end = text.rindex('</homecityprotounits>')
    add = ENTRY + ''.join(korean_unit(text, n, k) for n, k in PERFORMERS.items())
    return {PATH: (text[:end] + add + text[end:]).replace('\n', '\r\n').encode('utf-8')}
