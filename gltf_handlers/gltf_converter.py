"""

glTF Converter: Convert the model from human readable
to glTF (JSON) [Descriptor] and glTF (Binary Blob) [Buffers]
using the pygltflib or Py glTF Lib which is available at:
https://pypi.org/project/pygltflib/ 
--> Copyright (C) 2018, 2023 Luke Miller

-------------------------------------------------------------------------

code which is not part of pygltflib:
Copyright (C) 2024 DooMMetaL

-------------------------------------------------------------------------

DEVELOPER NOTE: since i'm new at this format expect a lot of non expected
behaviors and code stupidity //SORRY

"""

from pygltflib import *

class gltfFile:
    def __init__(self, gltf_to_convert=dict, gltf_file_name=str, gltf_deploy_path=str) -> None:
        """
        glTF Converter: Convert the model from human readable\n
        to glTF (JSON) [Descriptor] and glTF (Binary Blob) [Buffers]\n
        using the pygltflib.
        """
        self.gltf_to_convert = gltf_to_convert
        self.gltf_file_name = gltf_file_name
        self.gltf_deploy_path = gltf_deploy_path
        self.convert_gltf()
    
    def convert_gltf(self) -> None:
        """This actually do the Conversion"""
        descriptor_gltf = self.gltf_to_convert.get(f'Descriptor')
        binary_gltf = self.gltf_to_convert.get(f'Buffers')
        # Setup an empty glTF File
        gltf_file = GLTF2()
        # Setup an Scene
        gltf_scene = Scene()
        gltf_scene.name = 'Scene'
        # Setup number of nodes
        get_total_number_nodes = len(descriptor_gltf)
        for this_node in range(0, get_total_number_nodes):
            gltf_scene.nodes.append(this_node)
        gltf_file.scenes.append(gltf_scene)

        # Setup Meshes (for each node, since TLoD use object by object Animation)
        for this_gltf_object in descriptor_gltf:
            get_this_object = descriptor_gltf.get(f'{this_gltf_object}')
            change_name_gltf_object = this_gltf_object.replace('Object_Number_', f'{self.gltf_file_name}_ObjNum_')
            # Setup the Mesh
            gltf_mesh = Mesh()
            gltf_mesh.name = change_name_gltf_object
            for this_primitive in get_this_object:
                get_this_primitive = get_this_object.get(f'{this_primitive}')
                gltf_primitive = Primitive()
                gltf_primitive.attributes.POSITION = get_this_primitive.get('Vertices')
                gltf_primitive.attributes.NORMAL = get_this_primitive.get('Normals')