## from: https://developer.blender.org/diffusion/B/browse/master/release/scripts/templates_py/background_job.py
## translation from paraview script paraview/simple/vis_SRV-curved.py
## based on http://wiki.blender.org/index.php/Dev:Py/Scripts/Cookbook/Code_snippets/Materials_and_textures


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

    parser.add_argument("-o", "--output", dest="output", metavar='FILE', required=True, help="Output file to save the blender curve in. Suffix sets the format: Blender (.blend); DXF (.dxf); STL (.stl); Videoscape (.obj); VRML 1.0 (.wrl)")

    args = parser.parse_args(argv)  # In this example we wont use the args

    if not argv:
        parser.print_help()
        return

    if not args.output:
       print('Need an output file')
       parser.print_help()
       sys.exit(1)



    # Clear existing objects.
    scene = bpy.context.scene
    scene.camera = None
    for obj in scene.objects:
        scene.objects.unlink(obj)



    bpy.ops.import_scene.x3d(filepath="yz-plane.x3d") # reader1 = pvs.OpenDataFile("yz-plane.vtp", guiName="plane-"+s+"_x@0250")

    impObjs = bpy.context.selected_objects[:] # all imported objects http://blender.stackexchange.com/questions/24133/modify-obj-after-import-using-python

    for obj in impObjs:
        if obj.type != 'MESH':
            scene.objects.unlink(obj)
        else:
            obj.data.materials.clear() # http://blender.stackexchange.com/questions/2362/how-to-unlink-material-from-a-mesh-with-python-script

            guiName= "plane_x@0250"
            obj.name= guiName
            obj.data.name= guiName

            mat = bpy.data.materials.new(guiName + "_m")
            mat.specular_color= [0, 0, 0] # black to remove specular effects
            obj.data.materials.append(mat)

            layerList= ['G', 'A', 'B']
            for j, s in enumerate(layerList):

                guiName= "plane-"+s+"_x@0250"
                fnPNG= guiName + ".png"
                print(fnPNG)

                # Load image file.             
                try:
                    img = bpy.data.images.load(fnPNG)
                except:
                    raise NameError("Cannot load image %s" % fnPNG)

                cTex= bpy.data.textures.new(fnPNG, type = 'IMAGE') # texProxy.GetProperty("FileName").SetElement(0, fnPNG)
                cTex.image= img
                
                mtex = mat.texture_slots.add() # Add texture slot for color texture
                mtex.scale[1]= -1
                mtex.texture = cTex
                mtex.texture_coords = 'UV'
                mtex.use_map_color_diffuse = True 
                # mtex.use_map_color_emission = True 
                # mtex.emission_color_factor = 0.5
                # mtex.use_map_density = True 
                mtex.mapping = 'FLAT' 


    ## no lamp - no texture (visible)
    lamp_data = bpy.data.lamps.new(name="Hemi", type='HEMI')
    lamp_object = bpy.data.objects.new(name="Hemi", object_data=lamp_data)
    scene.objects.link(lamp_object)


    ## set 3D-View Cam clip: http://blenderartists.org/forum/archive/index.php/t-273243.html
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces[0].clip_end = 9999999
            area.spaces[0].region_3d.view_perspective = 'PERSP' #'ORTHO'|'PERSP'|'CAMERA' #http://blenderartists.org/forum/archive/index.php/t-327216.html
            for space in area.spaces: # iterate through spaces in current VIEW_3D area
                if space.type == 'VIEW_3D': # check if space is a 3D view
                    space.viewport_shade = 'MATERIAL' # or TEXTURE with GLSL http://blender.stackexchange.com/questions/17745/changing-viewport-shading-with-python
            for region in area.regions:
                if region.type == 'WINDOW':
                    override = {'area': area, 'region': region}
                    bpy.ops.view3d.view_all(override) # does not work in batch mode! i.e. with blender -b -P ...  http://blender.stackexchange.com/questions/7418/zoom-to-selection-in-python-gives-runtimeerror


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
