## from: http://blender.stackexchange.com/questions/2573/render-with-opengl-from-the-command-line

import bpy

from bpy.app.handlers import persistent

@persistent
def do_render_opengl(dummy):
    # bpy.ops.render.opengl(animation=True, view_context=False)
    bpy.ops.render.opengl(animation=True, view_context=True)
    # bpy.ops.render.render(animation=True) # same as from command line
    bpy.ops.wm.quit_blender()

bpy.app.handlers.load_post.append(do_render_opengl)

