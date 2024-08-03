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
import struct
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
        total_objects_gltf = self.gltf_to_convert.get('ObjectsNumber')
        meshes_gltf = self.gltf_to_convert.get('Meshes')
        binary_buffers_gltf = self.gltf_to_convert.get('Buffers')
        accessors_data_gltf = self.gltf_to_convert.get('Accessors')
        buffersview_gltf = self.gltf_to_convert.get('BufferViews')
        buffer_gltf_total_size = self.gltf_to_convert.get('BufferSizeTotal')
        
        # Setup an empty glTF File
        gltf_file = GLTF2()

        # Setup Asset
        gltf_file.asset.generator = f'TLoD Assets Converter ALPHA 0.1'
        gltf_file.asset.version = f'2.0'
        gltf_file.extensionsUsed = [f'KHR_materials_specular', f'KHR_materials_ior']
        gltf_file.scene = 0
        
        # Setup an Scene
        gltf_scene = Scene()
        gltf_scene.name = 'Scene'
        for this_node in range(0, total_objects_gltf):
            gltf_scene.nodes.append(this_node)
        gltf_file.scenes.append(gltf_scene)
        
        # Setup Nodes
        for this_node_number in range(0, total_objects_gltf):
            gltf_nodes = Node()
            gltf_nodes.mesh = this_node_number
            gltf_nodes.name =  f'{self.gltf_file_name}_ObjNum_{this_node_number}'
            gltf_file.nodes.append(gltf_nodes)

        # Setup Materials - HERE WE ARE IMPLEMENTING VERY BASIC MATERIALS (In future i hope implementing specific materials for each objects)
        for this_object_material in range(0, total_objects_gltf):
            material_gltf = Material()
            material_gltf.doubleSided = True
            material_gltf.extensions = {'KHR_materials_specular': {'specularFactor': 0}, 
                                        'KHR_materials_ior': {'ior': 1.4499999284744263}}
            material_gltf.name = f'{self.gltf_file_name}_ObjNum_{this_object_material}'
            pbr_settings = PbrMetallicRoughness()
            pbr_settings.baseColorFactor = [0.800000011920929, 0.800000011920929, 0.800000011920929, 1]
            pbr_settings.metallicFactor = 0.0
            pbr_settings.roughnessFactor = 0.5
            material_gltf.pbrMetallicRoughness = pbr_settings
            material_gltf.alphaCutoff = None
            gltf_file.materials.append(material_gltf)

        # Setup Meshes (for each node, since TLoD use object by object Animation) -> And Primitives
        # Maybe i could add a single mesh and each primitives block is represented by an object? who knows
        for this_gltf_mesh in meshes_gltf:
            get_this_object = meshes_gltf.get(f'{this_gltf_mesh}')
            change_name_gltf_object = this_gltf_mesh.replace('Object_Number_', f'{self.gltf_file_name}_ObjNum_')
            gltf_mesh = Mesh()
            gltf_mesh.name = change_name_gltf_object
            gltf_primitive = Primitive()
            get_this_primitive_attributes = get_this_object.get('attributes')
            gltf_primitive.attributes.POSITION = get_this_primitive_attributes.get('POSITION')
            gltf_primitive.attributes.NORMAL = get_this_primitive_attributes.get('NORMAL')
            gltf_primitive.attributes.TEXCOORD_0 = get_this_primitive_attributes.get('TEXCOORD_0')
            gltf_primitive.attributes.COLOR_0 = get_this_primitive_attributes.get('COLOR_0')
            gltf_primitive.indices = get_this_object.get('indices')
            gltf_primitive.material = get_this_object.get('material')
            gltf_mesh.primitives.append(gltf_primitive)
            gltf_file.meshes.append(gltf_mesh)
        
        # Setup Accessors
        # POSITION=VEC3 ; NORMAL=VEC3 ; NORMAL=VEC2 ; COLOR_0=VEC3 ; indices=SCALAR
        for this_object in accessors_data_gltf:
            current_accessors_arrays = accessors_data_gltf.get(f'{this_object}')
            for this_accessor in current_accessors_arrays:
                accessor_gltf = Accessor()
                get_accessor_data = current_accessors_arrays.get(f'{this_accessor}')
                accessor_gltf.bufferView = get_accessor_data.get('bufferView')
                accessor_gltf.componentType = get_accessor_data.get('componentType')
                accessor_gltf.count = get_accessor_data.get('count')
                accessor_gltf.type = get_accessor_data.get('type')
                gltf_file.accessors.append(accessor_gltf)
        
        # Setup BufferViews
        for this_object in buffersview_gltf:
            this_bufferviews_in_object = buffersview_gltf.get(f'{this_object}')
            for this_bufferview_data in this_bufferviews_in_object:
                buffer_view = this_bufferviews_in_object.get(f'{this_bufferview_data}')
                this_bufferview_gltf = BufferView()
                this_bufferview_gltf.buffer = buffer_view.get(f'buffer')
                this_bufferview_gltf.byteLength = buffer_view.get(f'byteLength')
                this_bufferview_gltf.byteOffset = buffer_view.get(f'byteOffset')
                this_bufferview_gltf.target = buffer_view.get(f'target')
                gltf_file.bufferViews.append(this_bufferview_gltf)

        # Creating Binary Buffers in GLB Binary Format
        
        binary_file_name = f'{self.gltf_file_name}_buffers.bin'
        buffer_glb_gltf = Buffer()
        buffer_glb_gltf.byteLength = buffer_gltf_total_size
        buffer_glb_gltf.uri = binary_file_name
        gltf_file.buffers.append(buffer_glb_gltf)

        gltf_file.save_json(f'{self.gltf_deploy_path}.gltf')

        """with open(f'{self.gltf_deploy_path}_buffers.bin', 'wb') as gltf_binary_buffer:
            gltf_binary_buffer.write(buffer_binary_joined_final)
            gltf_binary_buffer.close()"""
