"""data/homecityprotounits.xml: the home city's own unit list (citizens, performers, the explorer) = vanilla plus the
Korean explorer. The engine shows a civ's explorer from the entry with its <civilization> and <explorer />: a <visual>
animfile standing at <bone> with a <script>; the entry name is no proto (vanilla ExplorerDEHetmanPolish - Poland's
mounted Hetman - is not in protoy.xml). Without an entry the Korean home city had no explorer (owner 2026-10-17:
"Korean explorer is missing"). Not an additive *mods.xml file, so the add-on ships the whole file (tools/build.py);
built on AoP's copy would be needed if AoP ever ships one (then it must host the entry: aoe3de-multi-mod).
Audit: Blendify journal 2026-10-17-claude-opus-5.5-26.

The Korean monk rides his horse (units/korean_monk/korean_monk_horse.xml, zpMonkKorean's animfile) at the ground bone
bone_explorer_special, which tools/homecity_explorer.py puts left of the Customs House; clicking him frames that corner
with the Customs House's camera.
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
    <selectable />
    <explorer />
    <camera>china\china_homecity_dock_camera.cam</camera>
    <widescreencamera>china\china_homecity_dock_widescreencamera.cam</widescreencamera>
  </protounit>
'''


def build():
    """{repo path: CRLF bytes}"""
    assert not os.path.isfile(os.path.join(korean_visuals.AOP, *PATH.split('/'))), \
        f'AoP ships {PATH}: it outranks the add-on, so AoP must host the Korean entry (aoe3de-multi-mod)'
    text = korean_visuals.vanilla_text(VANILLA)
    assert '<homecityprotounits>' in text and 'zpKoreans' not in text, 'unexpected vanilla homecityprotounits.xml'
    end = text.rindex('</homecityprotounits>')
    return {PATH: (text[:end] + ENTRY + text[end:]).replace('\n', '\r\n').encode('utf-8')}
