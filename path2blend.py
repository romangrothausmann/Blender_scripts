####script to import a path (from a text-file) as a blender curve (e.g. for a camera path)

### based on poly-path2blender-curve_06.py

##from http://www.blender.org/documentation/249PythonDoc/Curve-module.html
##see also http://blenderartists.org/forum/archive/index.php/t-149736.html
##see also http://dataorigami.blogspot.de/2009/07/how-to-draw-curve-in-blender-using.html

## needs to be run in interactive mode to assign speed-ipo to curve (possibly this action is not available through the python API...) http://blenderartists.org/forum/archive/index.php/t-149736.html

## vglrun /opt/compilation/blender-2.49b/build_minimal/bin/blender ~/blender/default.blend  -P ~/blender_py/poly-path2blender-curve_05.py -- -i path_02.txt -o path.blend -e 1

##NOTE: script expects CONSTANT STEP SIZE along whole path! The correct/foolproof way would be to take the bezier-curve length as the x-coord of the keyfream to be inserted. This seems not so easy, see e.g. :   http://blenderartists.org/forum/archive/index.php/t-264469.html   http://blenderartists.org/forum/archive/index.php/t-206790.html

## choose animation layout
## select curve
## in the IPO-editor instead of object choose path
## then select in the IPO-editor in up/donw arrow box the IP:PathPos, move mouse a bit if no pop-down appears that at least shows "ADD NEW"
## save blend-file
## start blender >= 2.64 (>= rev=50953) and open the blend-file (Appending does not work!) and save it again (http://projects.blender.org/scm/viewvc.php/trunk/blender/source/blender/blenkernel/intern/ipo.c?view=markup&root=bf-blender&sortby=log&pathrev=50953)
## now the curve can be appended within blender 2.64
## or use csv2fcurve http://sourceforge.net/projects/csv-fc-importer/
### http://blenderartists.org/forum/showthread.php?209181-A-Script-to-Import-a-CSV-File-and-Create-F-Curves-%28for-Blender-2-5x-or-later%29
### http://blenderartists.org/forum/showthread.php?103587-A-Script-to-Import-a-CSV-File-and-Create-IPO-Curves-Meshes-%28for-Blender-2-4x%29



import sys, os, getopt, string
import optparse  # to parse options for us and print a nice help message
import Blender as B



def read_cf(fn):

    #input_fields= 4 
    in_file= open(fn,  "r")
    dll= []

    while True:
        #dl= [0] * input_fields #create a new list for each in_line!
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
        #dl= [0] * (len(sl) - 1) #create a new list for each in_line!
        for i in range(0, len(sl)):
        #for i in range(0, len(dl)): #skipping reading of index-number
            dl[i]= float(sl[i])
        dll.append(dl) 
    in_file.close()
    return(dll)


def bezList2Curve(bezier_vecs, n):
    '''
    Take a list or vector triples and converts them into a bezier curve object
    '''
    
    def bezFromVecs(vecs):
        '''
        Bezier triple from 3 vecs, shortcut functon
        '''
        #bt= BezTriple.New(vecs[0].x, vecs[0].y, vecs[0].z,  vecs[1].x, vecs[1].y, vecs[1].z,  vecs[2].x, vecs[2].y, vecs[2].z)
        bt= B.BezTriple.New(vecs[0], vecs[1], vecs[2])
        
        #bt.handleTypes= (B.BezTriple.HandleTypes.FREE, B.BezTriple.HandleTypes.FREE)
        bt.handleTypes= (B.BezTriple.HandleTypes.AUTO, B.BezTriple.HandleTypes.AUTO)
        
        return bt
    
               # Create the curve data with one point
    cu= B.Curve.New()
    cu.appendNurb(bezFromVecs(bezier_vecs[0])) # We must add with a point to start with
    cu_nurb= cu[0] # Get the first curve just added in the CurveData
    
    
    i= 1 # skip first vec triple because it was used to init the curve

    while i<len(bezier_vecs):
        bt_vec_triple= bezier_vecs[i]
        bt= bezFromVecs(bt_vec_triple)
        cu_nurb.append(bt)
#        i+=1
        i+=n

    # ##Set both handles to auto for each point
    # AUTO = B.BezTriple.HandleTypes.AUTO
    # for point in cu_nurb:
    #     point.handleTypes= [AUTO, AUTO]

    cu_nurb.flagU= 1 # Set curve cyclic
    cu.update()

   
    # Add the Curve into the scene
    cu.setFlag(cu.getFlag() | 1) #3D-flag; new blender api?: cu.dimensions = "3D"
    cu.setFlag(cu.getFlag() | 8) #CurvePath-flag
    cu.setFlag(cu.getFlag() | 16) #CurveFollow-flag
    #cu.flagU = 1 # Set curve cyclic
    #scn= B.Scene.GetCurrent()
    #ob = scn.objects.new(cu)
    #return ob
    return cu


def main(): #



    # get the args passed to blender after "--", all of which are ignored by blender specifically
    # so python may receive its own arguments
    argv= sys.argv

    if '--' not in argv:
       argv = [] # as if no args are passed
    else:
       argv = argv[argv.index('--')+1: ]  # get all args after "--"

    # When --help or no args are given, print this help
    usage_text =  'Run blender in background mode with this script:'
    usage_text += '  blender -b ~/blender/default.blend -P <skript_name> -- [options]'

    parser = optparse.OptionParser(usage = usage_text)

    parser.add_option('-i', '--input', dest='input', help='Input path contained in a text file.', type='string')
    parser.add_option('-o', '--output', dest='output', help='Output file to save the blender curve in. Suffix sets the format: Blender (.blend); DXF (.dxf); STL (.stl); Videoscape (.obj); VRML 1.0 (.wrl)', type='string')
    parser.add_option('-e', '--every', dest='every', default=1, help='Only import every Nth vertex.', type='int')

    options, args = parser.parse_args(argv)

    if not argv:
       parser.print_help()
       sys.exit(1)

    if not options.input:
       print 'Need an input file'
       parser.print_help()
       sys.exit(1)

    if not options.output:
       print 'Need an output file'
       parser.print_help()
       sys.exit(1)



    path_list= read_cf(options.input) 
    path_list= [ x for x in path_list if x[4] <= 1 ] ##skip branching nodes
    #print path_list
    path_vecs= [ x[1:4] for x in path_list] ##just copy x y z columns
    #path_ana= [ x[4] for x in path_list] 
    path_speed= [ x[5] for x in path_list] 
    #print path_vecs
    #print len(path_list), len(path_vecs)
    curve= bezList2Curve(path_vecs, options.every)

    scn= B.Scene.GetCurrent()
    ob = scn.objects.new(curve)
    #curvedata = ob.data


    #curve.setIpo(B.Ipo.New("Curve", "PathPos"))
    #curve[0].ipo=(B.Ipo.New("Curve", "PathPos"))
    #curve.ipo=(B.Ipo.New("Curve", "PathPos"))
    #ob.insertShapeKey() 
    #curve.insertShapeKey() 
    #ob.insertPathKey() 
    #curve.key.ipo=(B.Ipo.New("Key", "PathPos"))
    #ob.key.ipo=(B.Ipo.New("Curve", "PathPos"))
    #ob.insertIpoKey(B.Ipo.CU_SPEED)
    #ob.ipo=(B.Ipo.New("Curve", "PathPos"))
    #curvedata.ipo=(B.Ipo.New("Curve", "PathPos"))

    print ob.type
    print type(curve)
    #print curve.subtype
    if type(curve) != B.Types.CurveType:
        print ob.type 
        print " is not of type " 
        print B.Types.CurveType 
        print " but of type: " 
        print type(curve)

    #### add IPO-speed (F-Curves in > 2.5)
    #### http://wiki.blender.org/index.php/Dev:2.4/Source/Python/Ipo
    #### Speed curve is not speed but position along path!!! http://wiki.blender.org/index.php/Doc:2.4/Manual/Constraints/Relationship/Follow_Path
    #### manual editing see: http://blenderartists.org/forum/showthread.php?115409-Camera-and-path-speed
    #### python creation: http://www.packtpub.com/article/blender-2.49-scripting-shape-keys-ipo-and-poses

    #ipo= B.Ipo.Get('PathPos')
    #ipo= curve.getIpo()
    ipo= B.Ipo.New("Curve", "PathPos") #create new IPO-Object for a Curve-Ob    
    # ipo= ob.getIpo()
    # if ipo == None:
    #     ipo= B.Ipo.New("Curve", "PathPos") #create new IPO-Object for a Curve-Object
    #     #ipo= B.Ipo.New("Object", "PathPos") #create new IPO-Object for a Curve-Object
    print ipo.curveConsts
    # #     ob.setIpo(ipo)

    # print ipo.name, type(ipo)

    # print "Printing icus of ipo: ",
    # for icus in ipo:
    #     print icus.name, 
    # print "done"


    # # icu= ipo[B.Ipo.CU_SPEED] #get Speed-Curve of IPO-Object
    ipc= ipo.getCurve("Speed")
    #icu= ipo["Speed"]
    #icu= B.Ipo.CU_SPEED #get Speed-Curve of IPO-Object
    if ipc == None:
        print "Creating IPC 'Speed'"
        ipc= ipo.addCurve("Speed")
        #icu= ipo.addCurve(B.Ipo.CU_SPEED)

    #ipc.append(B.BezTriple.New(1,0,0))

    # # icu= ipo[B.Ipo.CU_SPEED] #get Speed-Curve of IPO-Object
    # # print icu.name

    print "Printing icus of ipo: ",
    for icus in ipo:
        print icus.name, 
    print "done"
    
    # icu= B.Ipo.CU_SPEED #get Speed-Curve of IPO-Object
    # #print icu
    # #print ipo.getBlocktype()
    
    # #ipo[icu]= (1,x[1])
    # #ipo[B.Ipo.CU_SPEED]= (1,x[1])

    #i= 1+options.every
    i= 0
    t_sum= 0
    while i<len(path_speed):
        t_sum+= path_speed[i]
        i+= options.every

    print t_sum

    sum= 0
    ipc.append(B.BezTriple.New(0,0,0)) #zero's pos
    #i= 1+options.every
    i= 1
    while i<len(path_speed):
    #for i in range(0, len(path_speed)):
        #ipo[B.Ipo.CU_SPEED]= (i, path_speed[i])
        sum+= path_speed[i]
        ipc.append(B.BezTriple.New(i,sum/t_sum,0))
        #ipc.append(path_speed[i])

        i+= options.every

    #ipo[icu].interpolation = B.IpoCurve.InterpTypes.BEZIER
    ipo[B.Ipo.CU_SPEED].interpolation = B.IpoCurve.InterpTypes.BEZIER
    #ob.setIpo(ipo)
    #ob.setIpo(icu)

    B.Set("compressfile", 1)
    B.Save(options.output, 1)


	
if __name__ == '__main__':
    main()

