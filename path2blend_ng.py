####script to import a path (from a text-file) as a blender curve (e.g. for a camera path)
### based on path2blend_og.py and template.py

### ToDo

### Done
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

    curvedata= bpy.data.curves.new(name='CurveData', type='CURVE')  
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

    ## ideas from: http://blenderartists.org/forum/showthread.php?209181-A-Script-to-Import-a-CSV-File-and-Create-F-Curves-%28for-Blender-2-5x-or-later%29
    #action= bpy.data.actions.new("Curve");
    curve.animation_data_create()# http://www.blender.org/api/blender_python_api_2_75_3/bpy.types.AnimData.html#bpy.types.AnimData  http://www.blender.org/api/blender_python_api_2_75_3/bpy.types.ID.html#bpy.types.ID.animation_data_create
    curve.animation_data.action= bpy.data.actions.new("PathPos")# http://www.blender.org/api/blender_python_api_2_75_3/bpy.types.BlendDataActions.html#bpy.types.BlendDataActions.new
    ac= curve.animation_data.action
    fc= ac.fcurves.new('eval_time')# http://www.blender.org/api/blender_python_api_2_75_3/bpy.types.ActionFCurves.html#bpy.types.ActionFCurves.new    'eval_time':  https://www.blender.org/forum/viewtopic.php?t=20371


    ## calc total sum to create normalize Speed IPO
    t_sum= 0
    i= 0
    while i<len(path_speed):
        t_sum+= path_speed[i]
        i+= args.every

    print(t_sum)

    fc.keyframe_points.insert(0, 0.0) #zero's pos
    sum= 0
    i= 0
    while i<len(path_speed):
        sum+= path_speed[i]
        fc.keyframe_points.insert(i+1,sum/t_sum)# +1: use speed for the section of the path that precedes
        i+= args.every


    ## select path
    bpy.ops.object.select_all(action='DESELECT')
    #bpy.ops.object.select_name(name = "Path")#before 2.62
    bpy.ops.object.select_pattern(pattern= "Path")#since 2.62: http://stackoverflow.com/questions/19472499/blender-2-6-select-object-by-name-through-python

    ## select animation lay-out
    ## http://blender.stackexchange.com/questions/8428/how-to-set-set-screen-type-with-python
    print(bpy.context.window.screen)
    print(bpy.data.screens)
    for screen in bpy.data.screens:
        print(screen.name) 

    #bpy.context.window.screen = bpy.data.screens['Animation']#segfaults
    bpy.ops.screen.screen_set(delta=-1)#workaround forbpy.context.window.screen = bpy.data.screens['Animation']
    bpy.ops.screen.screen_set(delta=-1)#delta can only be +/-1

    ## set 3D-View Cam clip: http://blenderartists.org/forum/archive/index.php/t-273243.html
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces[0].clip_end = 9999999
            area.spaces[0].region_3d.view_perspective = 'ORTHO' #'PERSP'|'CAMERA' #http://blenderartists.org/forum/archive/index.php/t-327216.html

    #this only works for specific conditions: http://blender.stackexchange.com/questions/5359/how-to-set-cursor-location-pivot-point-in-script
    # bpy.context.screen.areas['VIEW_3D'].clip_end = 9999999
    # view3d = bpy.context.screen.areas[1].spaces[0]
    # view3d.clip_end = 9999999

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
