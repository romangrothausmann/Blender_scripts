## script to export the (interpolated) evaluation time of a path created by path2blend_ng.py
## https://blender.stackexchange.com/questions/117974/how-can-i-export-object-position-info-from-blender-to-text-file#118116

import bpy

scn = bpy.context.scene
path = bpy.data.objects["Path"]
cam = bpy.data.objects["Camera"]

curve = path.data.animation_data.action.fcurves.find('eval_time')
mw = cam.matrix_world

with open('data_out.txt', 'w') as out_file:
    for f in range(scn.frame_start, scn.frame_end):
        eT = curve.evaluate(f)
        scn.frame_set(f) # needed for follow path constraint (without baking)
        x, y, z = mw.to_translation() # or loc, rot, scale = obj.matrix_world.decompose() https://docs.blender.org/api/blender_python_api_current/mathutils.html#mathutils.Matrix.decompose
        out_file.write('{},{:.6f},{:.6f},{:.6f},{:.6f}\n'.format(f, eT, x, y, z))
