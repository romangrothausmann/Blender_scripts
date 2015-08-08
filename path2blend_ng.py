####script to import a path (from a text-file) as a blender curve (e.g. for a camera path)
### based on path2blend_og.py and template.py

### ToDo

### Done
## port IPO creation from path2blend_og.py
## take variing polyline segment lengths into account
## changed from NURBS/POLY to BEZIER curve, needs special changes: http://blender.stackexchange.com/questions/6750/poly-bezier-curve-from-a-list-of-coordinates#comment30542_6751  http://blenderscripting.blogspot.de/2013/06/scripting-3d-bezier-spline-surface.html
## interpolate bezier/spline length

import bpy
import mathutils


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


def bezSegLength(spline):
    #http://blender.stackexchange.com/questions/688/getting-the-list-of-points-that-describe-a-curve-without-converting-to-mesh
    #https://gist.github.com/zeffii/5724956

    segLengthList= []
    knots = spline.bezier_points
    segments = len(knots)

    if segments < 2:
        return

    ## verts per segment
    r = spline.resolution_u + 1

    ## segments in spline
    if not spline.use_cyclic_u:
        segments -= 1

    #master_point_list = []
    for i in range(segments):
        inext = (i + 1) % len(knots)
        knot1 = knots[i].co
        handle1 = knots[i].handle_right
        handle2 = knots[inext].handle_left
        knot2 = knots[inext].co
        bezier = knot1, handle1, handle2, knot2, r
        points = mathutils.geometry.interpolate_bezier(*bezier)
        #master_point_list.extend(points)

        ## knot1 to first sub-point
        p1= knot1
        p2= points[0]
        segLength= (p1 - p2).length

        ## sub-point segments
        for j in range(len(points)-1):
            p1= points[j]
            p2= points[j+1]
            segLength+= (p1 - p2).length

        ## last sub-point to knot2
        p1= points[-1]
        p2= knot2
        segLength+= (p1 - p2).length

        ## append segLength to segLengthList
        segLengthList.append(segLength)

    return(segLengthList)


def bezList2Curve(bezier_vecs):
    ## http://blenderscripting.blogspot.de/2011/05/blender-25-python-bezier-from-list-of.html

    '''
    Take a list or vector triples and converts them into a bezier curve object
    '''

    curvedata= bpy.data.curves.new(name='CurveData', type='CURVE')
    curvedata.dimensions = '3D'

    polyline= curvedata.splines.new('BEZIER')
    polyline.resolution_u= 100
    polyline.bezier_points.add(len(bezier_vecs)-1) #http://blender.stackexchange.com/questions/12201/bezier-spline-with-python-adds-unwanted-point
    for i in range(len(bezier_vecs)):
        x, y, z = bezier_vecs[i]
        polyline.bezier_points[i].co = (x, y, z) #http://wiki.blender.org/index.php/Doc:2.4/Manual/Modeling/Curves#Weight
        ##setting handle type is essential if no handle coords are set!!! http://blenderscripting.blogspot.de/2013/06/scripting-3d-bezier-spline-surface.html
        polyline.bezier_points[i].handle_left_type = 'AUTO'
        polyline.bezier_points[i].handle_right_type = 'AUTO'

    polyline.order_u = len(polyline.points)-1
    polyline.use_endpoint_u = True
    polyline.use_cyclic_u = False

    return(curvedata)


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

    curve= bezList2Curve(path_vecs)
    segLength= bezSegLength(curve.splines[0])
    print("Min: ", min(segLength)," Max: ", max(segLength))

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
    for i in range(len(path_speed)-1): #-1: for # segments in non-cyclic curves
        t_sum+= segLength[i]

    print(t_sum)

    fc.keyframe_points.insert(0, 0.0) #zero's pos
    sum= 0
    timeSum= 0
    for i in range(len(path_speed)-1): #-1: for # segments in non-cyclic curves
        sum+= segLength[i] #acc. length
        timeSum+= segLength[i] / path_speed[i] #acc. time steps
        kf= fc.keyframe_points.insert(timeSum, sum/t_sum)
        kf.interpolation= 'BEZIER' #http://blender.stackexchange.com/questions/33729/how-to-script-animation-fcurve-made-autoclamped
        #kf.handle_left_type = 'AUTO_CLAMPED'

    ## select path
    bpy.ops.object.select_all(action='DESELECT')
    #bpy.ops.object.select_name(name = "Path")#before 2.62
    bpy.ops.object.select_pattern(pattern= "Path")#since 2.62: http://stackoverflow.com/questions/19472499/blender-2-6-select-object-by-name-through-python

    ## select animation lay-out
    ## http://blender.stackexchange.com/questions/8428/how-to-set-set-screen-type-with-python
    #bpy.context.window.screen = bpy.data.screens['Animation']#segfaults
    #bpy.context.window_manager.windows[0].screen = bpy.data.screens['Animation']#segfaults
    bpy.ops.screen.screen_set(delta=-1)#workaround forbpy.context.window.screen = bpy.data.screens['Animation']
    bpy.ops.screen.screen_set(delta=-1)#delta can only be +/-1

    ## set 3D-View Cam clip: http://blenderartists.org/forum/archive/index.php/t-273243.html
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces[0].clip_end = 9999999
            area.spaces[0].region_3d.view_perspective = 'ORTHO' #'PERSP'|'CAMERA' #http://blenderartists.org/forum/archive/index.php/t-327216.html
            for region in area.regions:
                if region.type == 'WINDOW':
                    #override = bpy.context.copy()
                    #override = {'area': area, 'region': region}
                    override = {'window': bpy.context.window, 'screen': bpy.context.window.screen, 'area': area, 'region': region} #http://blender.stackexchange.com/questions/6101/poll-failed-context-incorrect-example-bpy-ops-view3d-background-image-add    http://www.blender.org/api/blender_python_api_2_69_1/bpy.ops.html#overriding-context
                    #bpy.ops.view3d.view_all(override) #http://blender.stackexchange.com/questions/7418/zoom-to-selection-in-python-gives-runtimeerror

        if area.type == 'GRAPH_EDITOR':
            area.spaces[0].auto_snap= 'NONE' #http://www.blender.org/api/blender_python_api_2_75_3/bpy.types.SpaceGraphEditor.html?highlight=auto_snap#bpy.types.SpaceGraphEditor.auto_snap
            for region in area.regions:
                if region.type == 'WINDOW':
                    override = bpy.context.copy()
                    #override = {'area': area, 'region': region}
                    override = {'window': bpy.context.window, 'screen': bpy.data.screens['Animation'], 'area': area, 'region': region}
                    #override = {'window': bpy.context.window, 'screen': bpy.data.screens['Animation'], 'area': bpy.context.screen.areas['GRAPH_EDITOR'], 'region': bpy.context.screen.areas['GRAPH_EDITOR'].regions['WINDOW']}
                    #bpy.ops.graph.view_all(override)


    ## http://blenderartists.org/forum/showthread.php?269166-Operator-bpy-ops-uv-project_from_view-poll%28%29-failed-context-is-incorrect
    # for window in bpy.context.window_manager.windows:
    #     screen = window.screen
    #     for area in screen.areas:
    #         print(window, screen, area.type)
    #         if area.type == 'VIEW_3D':
    #             for space in area.spaces:
    #                 print(window, screen, area.type, space.type)
    #                 if space.type == 'VIEW_3D':
    #                     for region in area.regions:
    #                         print(window, screen, area.type, space.type, region.type)
    #                         if region.type == 'WINDOW':
    #                             override = {'window': window, 'screen': screen, 'area': area, 'space': space, 'region': region, 'edit_object': bpy.context.edit_object, 'scene': bpy.context.scene, 'blend_data': bpy.context.blend_data}
    #                             #bpy.ops.uv.project_from_view(override, orthographic=False, correct_aspect=True, clip_to_bounds=False, scale_to_bounds=True)
    #                             print(window, screen, area.type, space.type, region.type)
    #                             if bpy.ops.graph.view_all.poll():
    #                                 print("can poll")
    #                                 bpy.ops.view3d.view_all(override)
    #                             else:
    #                                 print("can't poll")
                  
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            for space in area.spaces:
                for region in area.regions:
                    print(window, screen, area.type, space.type, region.type)
                    override = {'window': window, 'screen': screen, 'area': area, 'space': space, 'region': region, 'scene': bpy.context.scene}
                                #bpy.ops.uv.project_from_view(override, orthographic=False, correct_aspect=True, clip_to_bounds=False, scale_to_bounds=True)
                    if bpy.ops.view3d.view_all.poll():
                        print("can poll")
                        bpy.ops.view3d.view_all(override)
                    # else:
                    #     print("can't poll")
                  

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
