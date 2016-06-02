## snippet to copy matrix_world of active object to all other selected objects
## use e.g. to copy pos of cam with follow-path-constraint to another, independent cam
## load in blender text editor and apply/run with Alt+p


import bpy

aobj= bpy.context.scene.objects.active
#print(obj.matrix_world.translation)
print(aobj.matrix_world) # http://blender.stackexchange.com/questions/28031/getting-the-location-of-rigid-body-object-at-current-keyframe

impObjs = bpy.context.selected_objects[:]
for obj in impObjs:
    if(obj != aobj):
        obj.matrix_world= aobj.matrix_world

