# Model briefs (agent briefs per Korean model)

Owner, 18 Oct 2026: "model must be refreshed from game" and "Each model should have agent brief informing about
decisions and possible false positives during tests". The rule and the template are in Blendify
`docs/architecture/model-briefs.md` (branch `docs/model-briefs`, until merged). Incidents: INC-436, INC-437.

**Before you touch a model, read its brief.** It holds:
- the current edit base, which is a port of the installed game files;
- the owner's decisions, quoted;
- the pages shared on purpose;
- what is frozen;
- the known false positives per gate.

When a gate hits a listed reading, report it as `KNOWN (brief: <entry>)` next to the raw verdict, not as a new defect.

**Refresh from the game** after every install, and before work whenever the brief's hashes differ from the installed
files:

```
python C:/work/monastery-installed-port-r1/port_installed_building_r1.py --building <name> [--art-dir zbench_korean_military/<name>] --origin-x <x> --out <new folder>
```

The port must report PASS with position and UV error 0. Then record its path, sha and date in the brief.

| Model | Brief | State (18 Oct 2026) |
| --- | --- | --- |
| Colonial castle | [korean_castle.md](korean_castle.md) | denser roof installed 18 Oct, game test pending |
| Industrial castle | [korean_castle_industrial.md](korean_castle_industrial.md) | unchanged |
| Consulate | [korean_consulate.md](korean_consulate.md) | r7b installed and committed 18 Oct, game test pending |
| Monastery | [korean_monastery.md](korean_monastery.md) | installed and committed (bacae7f) |
| Barracks | [korean_barracks.md](korean_barracks.md) | installed and committed 18 Oct, game test pending |
| Stable | [korean_stable.md](korean_stable.md) | installed and committed 18 Oct, game test pending |
| Houses A/B/C, Dock, Market, Rice Paddy, TC | missing | to write (INC-437) |
