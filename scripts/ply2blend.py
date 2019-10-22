## from: https://developer.blender.org/diffusion/B/browse/master/release/scripts/templates_py/background_job.py

import bpy


def main():
    import sys       # to get command line args
    import argparse  # to parse options for us and print a nice help message

    # get the args passed to blender after "--", all of which are ignored by
    # blender so scripts may receive their own arguments
    argv = sys.argv

    if "--" not in argv:
        argv = []  # as if no args are passed
    else:
        argv = argv[argv.index("--") + 1:]  # get all args after "--"

    # When --help or no args are given, print this help
    usage_text =  "Run blender in background mode with this script:"
    usage_text += "  blender -b ~/blender/default.blend -P " + __file__ + " -- [options]"

    parser = argparse.ArgumentParser(description=usage_text)

    parser.add_argument("-i", "--input", dest="input", metavar='FILE', required=True, help="Input PLY file.")
    parser.add_argument("-o", "--output", dest="output", metavar='FILE', required=True, help="Output file to save the blender curve in. Suffix sets the format: Blender (.blend); DXF (.dxf); STL (.stl); Videoscape (.obj); VRML 1.0 (.wrl)")

    args = parser.parse_args(argv)  # In this example we wont use the args

    if not argv:
        parser.print_help()
        return

    if not args.input:
       print('Need an input file')
       parser.print_help()
       sys.exit(1)

    if not args.output:
       print('Need an output file')
       parser.print_help()
       sys.exit(1)



    scene = bpy.context.scene
    bpy.ops.object.select_all(action='SELECT') # default action is toggle
    bpy.ops.object.delete() # delete all selected objects

    for item in bpy.data.meshes:
        bpy.data.meshes.remove(item) # delete all meshes http://blenderscripting.blogspot.de/2012/03/deleting-objects-from-scene.html


    bpy.ops.import_mesh.ply(filepath= args.input) # https://docs.blender.org/api/blender_python_api_2_76b_release/bpy.ops.import_mesh.html?highlight=ply#bpy.ops.import_mesh.ply

    for obj in scene.objects:
        if obj.type == 'MESH':
            obj.name= args.input
            obj.data.name= args.input
            obj.draw_type= 'BOUNDS'
            for i, mat in enumerate(obj.data.materials):
                mat.name= args.input+str(i)

            for f in obj.data.polygons: ##smooth is set per face! https://blender.stackexchange.com/questions/91685/using-python-to-set-object-shading-to-smooth#91687
                f.use_smooth = True


    if args.output:
        try:
            f = open(args.output, 'w')
            f.close()
            ok = True
        except:
            print("Cannot save to path %r" % save_path)

            import traceback
            traceback.print_exc()

        if ok:
            bpy.ops.wm.save_as_mainfile(filepath=args.output)



if __name__ == "__main__":
    main()
