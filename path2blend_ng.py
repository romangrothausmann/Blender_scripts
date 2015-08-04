####script to import a path (from a text-file) as a blender curve (e.g. for a camera path)
### based on path2blend_og.py and template.py

### ToDo
## port IPO creation from path2blend_og.py

import bpy


def read_cf(fn):

    in_file= open(fn,  "r")
    dll= []

    while True:
        in_line = in_file.readline()
        if not in_line:
            break

        in_line = in_line[:-1] #drop last char '\n' ;-)
        if (len(in_line) == 0): #skip empty lines
            continue
        if (in_line[0] == "#"): #skip comments
            continue
        sl= in_line.split() #split at white space
        dl= [0] * len(sl) #create a new list for each in_line!
        for i in range(0, len(sl)):
            dl[i]= float(sl[i])
        dll.append(dl)
    in_file.close()
    return(dll)


def bezList2Curve(bezier_vecs, n):
    ## http://blenderscripting.blogspot.de/2011/05/blender-25-python-bezier-from-list-of.html

    '''
    Take a list or vector triples and converts them into a bezier curve object
    '''

    curvedata= bpy.data.curves.new(name='Curve', type='CURVE')  
    curvedata.dimensions = '3D'  
  
    polyline = curvedata.splines.new('NURBS')
    polyline.points.add(len(bezier_vecs)-1)    
    for num in range(len(bezier_vecs)):    
        x, y, z = bezier_vecs[num]    
        polyline.points[num].co = (x, y, z, 1)    
    
    polyline.order_u = len(polyline.points)-1  
    polyline.use_endpoint_u = True  

    return curvedata


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

    parser.add_argument("-i", "--input", dest="input", metavar='FILE', required=True, help="Input path contained in a text file.")
    parser.add_argument("-o", "--output", dest="output", metavar='FILE', required=True, help="Output file to save the blender curve in. Suffix sets the format: Blender (.blend); DXF (.dxf); STL (.stl); Videoscape (.obj); VRML 1.0 (.wrl)")
    parser.add_argument("-e", "--every", dest="every", type=int, required=True, default=1, help="Only import every Nth vertex.")

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



    # Clear existing objects.
    scene = bpy.context.scene
    scene.camera = None
    for obj in scene.objects:
        scene.objects.unlink(obj)


    path_list= read_cf(args.input)
    path_list= [ x for x in path_list if x[4] <= 1 ] ##skip branching nodes
    path_vecs= [ x[1:4] for x in path_list] ##just copy x y z columns
    path_ana= [ x[4] for x in path_list]
    path_speed= [ x[5] for x in path_list]

    curve= bezList2Curve(path_vecs, args.every)

    ob = bpy.data.objects.new("Path", curve)    
    ob.location = (0,0,0) #object origin    
    bpy.context.scene.objects.link(ob)    


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
