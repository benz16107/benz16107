"""Business card print files -> one-colour display meshes for GitHub. Run from the repo root:
`uv run --with trimesh --with numpy --with shapely python3 scripts/card-build.py`. Only card.stl is committed.
card.stl: binary, full detail. card-inline.stl: ASCII, low poly, for a ```stl block in the README.
The print is flush multi-colour, so the inlays are raised (front) or dropped (back) by LIFT mm, or a
one-colour model would be a blank slab. The low-poly inlays are rebuilt from their simplified outlines,
because quadric decimation stalls at ~26k triangles on the text."""
import sys, glob
import numpy as np, trimesh
from shapely.ops import unary_union
from shapely.geometry import Polygon

OUT = '/home/ben/Code/projects/terminal-card/out/'
LIFT, TOL = 0.4, float(sys.argv[1]) if len(sys.argv) > 1 else 0.06  # TOL: outline simplification in mm

def load(n): return trimesh.load(glob.glob(OUT + n + '_*.stl')[0])

def outline(m, up):
    """2D union of the faces pointing up (up=1) or down (up=-1)."""
    tris = m.triangles[m.face_normals[:, 2] * up > 0.9][:, :, :2]
    return unary_union([Polygon(t) for t in tris if Polygon(t).area > 1e-9]).buffer(0)

TEXT = len(sys.argv) < 3 or sys.argv[2] != 'notext'

def extrude(geom, z0, h, tol):
    geom = geom.simplify(tol, preserve_topology=True)
    parts = [geom] if geom.geom_type == 'Polygon' else list(geom.geoms)
    meshes = []
    for p in parts:
        if p.area < 0.01: continue
        if not TEXT and p.bounds[3] < 46: continue  # body text lines; the title bar starts at y 46
        e = trimesh.creation.extrude_polygon(p, abs(h)); e.apply_translation([0, 0, z0 if h > 0 else z0 - abs(h)])
        e.update_faces(e.face_normals[:, 2] * np.sign(h) > -0.5)  # the face resting on the slab is hidden
        meshes.append(e)
    return meshes

body = load('1')
slab = body.convex_hull
full = [slab, load('2').apply_translation([0, 0, -LIFT])] + [load(n).apply_translation([0, 0, LIFT]) for n in '3456']
trimesh.util.concatenate(full).export('card.stl')

low = [trimesh.creation.extrude_polygon(outline(body, 1).convex_hull.simplify(0.05), 1.0)]  # plain slab, few triangles
counts = {}
low += extrude(outline(load('2'), -1), 0, -LIFT, 0.01); counts['slab+qr'] = sum(len(m.faces) for m in low)  # QR modules are rectangles, keep them exact
for n in '3456':
    e = extrude(outline(load(n), 1), 1.0, LIFT, TOL); low += e; counts[n] = sum(len(m.faces) for m in e)
print(counts)
small = trimesh.util.concatenate(low)
small.apply_translation(-small.bounds.mean(axis=0).round(2))  # centred, so the viewer orbits the card's middle

def fmt(a): return ' '.join(('%.2f' % x).rstrip('0').rstrip('.').replace('-0', '-0') if abs(x) >= 0.005 else '0' for x in a)
lines = ['solid card']
for tri, nrm in zip(small.triangles, small.face_normals):
    lines += ['facet normal ' + fmt(nrm), 'outer loop', *['vertex ' + fmt(p) for p in tri], 'endloop', 'endfacet']
lines.append('endsolid card')
txt = '\n'.join(lines) + '\n'
open('card-inline.stl', 'w').write(txt)
assert txt.count('endfacet') == len(small.faces)
print('full', sum(len(m.faces) for m in full), 'tris', round(len(open('card.stl', 'rb').read()) / 1e6, 2), 'MB | inline',
      len(small.faces), 'tris', round(len(txt) / 1024), 'KB, tol', TOL)
small.export('card-inline-bin.stl')
