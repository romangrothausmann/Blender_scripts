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

    parser.add_argument("-i", "--input", dest="input", metavar='FILE', required=False, help="Input path contained in a text file.")
    parser.add_argument("-o", "--output", dest="output", metavar='FILE', required=False, help="Output file to save the blender curve in. Suffix sets the format: Blender (.blend); DXF (.dxf); STL (.stl); Videoscape (.obj); VRML 1.0 (.wrl)")
    parser.add_argument("-s", "--scale", dest="scale", type=float, required=True, help="desired resolution percentage [0-100] for renders")
    args = parser.parse_args(argv)  # In this example we wont use the args

    if not argv:
        parser.print_help()
        return


    bpy.context.scene.render.resolution_percentage= args.scale



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
