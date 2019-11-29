## script to export the (interpolated) evaluation time of a path created by path2blend_ng.py
## https://blender.stackexchange.com/questions/117974/how-can-i-export-object-position-info-from-blender-to-text-file#118116

import bpy

scn = bpy.context.scene
path = bpy.data.objects["Path"]

curve = path.data.animation_data.action.fcurves.find('eval_time')

with open('data_out.txt', 'w') as out_file:
    for f in range(scn.frame_start, scn.frame_end):
        eT = curve.evaluate(f)
        out_file.write('{},{:.3f}\n'.format(f, eT))
