"""Move an OBJ authored in a hat's model space onto a body's head (bone_hat W0 = identity for the bandido hat):
v_world = v @ W0(body head). python obj_on_head.py POSE_SIM_DIR BODY.gxo IN.obj OUT.obj"""
import sys
import numpy as np
sys.path.insert(0, sys.argv[1])
import pose_sim as ps
bb, _ = ps.parse_model(sys.argv[2])
head = next(b['W0'] for b in bb if ps.norm(b['name']).lower() == 'bip01_head')
out = []
for line in open(sys.argv[3]):
    if line.startswith('v '):
        p = np.array([float(x) for x in line.split()[1:4]] + [1.0]) @ head
        out.append('v %.6f %.6f %.6f\n' % tuple(p[:3]))
    elif line.startswith('vn '):
        n = np.array([float(x) for x in line.split()[1:4]]) @ head[:3, :3]
        out.append('vn %.5f %.5f %.5f\n' % tuple(n / np.linalg.norm(n)))
    else:
        out.append(line)
open(sys.argv[4], 'w').writelines(out)
