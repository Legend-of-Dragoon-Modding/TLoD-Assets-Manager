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
        descriptor_gltf = self.gltf_to_convert.get(f'Descriptor')
        to_binary_buffers_gltf = self.gltf_to_convert.get(f'Buffers')
        accessors_data_gltf = self.gltf_to_convert.get(f'Accessors')
        
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
        get_total_number_nodes = len(descriptor_gltf)
        for this_node in range(0, get_total_number_nodes):
            gltf_scene.nodes.append(this_node)
        gltf_file.scenes.append(gltf_scene)
        
        # Setup Nodes
        for this_node_number in range(0, get_total_number_nodes):
            gltf_nodes = Node()
            gltf_nodes.mesh = this_node_number
            gltf_nodes.name =  f'{self.gltf_file_name}_ObjNum_{this_node_number}'
            gltf_file.nodes.append(gltf_nodes)

        # Setup Materials - HERE WE ARE IMPLEMENTING VERY BASIC MATERIALS (In future i hope implementing specific materials for each objects)
        for this_object_material in range(0, get_total_number_nodes):
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
        for this_gltf_mesh in descriptor_gltf:
            get_this_object = descriptor_gltf.get(f'{this_gltf_mesh}')
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
        # TODO: I THINK I DO ANYTHING BUT A GOOD CALCULATION FOR accessor_gltf.count = get_accessor_data.get('count')
        # ERROR: ACCESSOR_TOO_LONG -> Accessor (offset: %1, length: %2) does not fit referenced bufferView [%3] length %4.
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
        
        # Setup BufferViews and Accessors
        buffers_binary_final: list = []
        byte_offset_previous = 0
        for this_object in to_binary_buffers_gltf:
            get_buffer_object = to_binary_buffers_gltf.get(f'{this_object}')
            get_binary_data_buffer = get_buffer_object.get(f'Buffers')
            get_buffer_full_length = get_buffer_object.get(f'BufferFullLength')
            get_length_each_array = get_buffer_object.get(f'LengthEachArray') # This is each of the buffer length of bytes
            get_length_sum_arrays = get_buffer_object.get(f'SequencedLenghts') # This is each of the summatory of previous lengths but only for this single object

            vertex_buffer_gltf = BufferView()
            vertex_buffer_gltf.buffer = 0
            vertex_buffer_gltf.byteLength = get_length_each_array[0]
            vertex_buffer_gltf.byteOffset = byte_offset_previous + get_length_sum_arrays[0]
            vertex_buffer_gltf.target = 34962

            normal_buffer_gltf = BufferView()
            normal_buffer_gltf.buffer = 0
            normal_buffer_gltf.byteLength = get_length_each_array[1]
            normal_buffer_gltf.byteOffset = byte_offset_previous + get_length_sum_arrays[1]
            normal_buffer_gltf.target = 34962

            uv_buffer_gltf = BufferView()
            uv_buffer_gltf.buffer = 0
            uv_buffer_gltf.byteLength = get_length_each_array[2]
            uv_buffer_gltf.byteOffset = byte_offset_previous + get_length_sum_arrays[2]
            uv_buffer_gltf.target = 34962

            color_buffer_gltf = BufferView()
            color_buffer_gltf.buffer = 0
            color_buffer_gltf.byteLength = get_length_each_array[3]
            color_buffer_gltf.byteOffset = byte_offset_previous + get_length_sum_arrays[3]
            color_buffer_gltf.target = 34962

            ivertex_buffer_gltf = BufferView()
            ivertex_buffer_gltf.buffer = 0
            ivertex_buffer_gltf.byteLength = get_length_each_array[4]
            ivertex_buffer_gltf.byteOffset = byte_offset_previous + get_length_sum_arrays[4]
            ivertex_buffer_gltf.target = 34963

            inormal_buffer_gltf = BufferView()
            inormal_buffer_gltf.buffer = 0
            inormal_buffer_gltf.byteLength = get_length_each_array[5]
            inormal_buffer_gltf.byteOffset = byte_offset_previous + get_length_sum_arrays[5]
            inormal_buffer_gltf.target = 34963

            gltf_file.bufferViews.append(vertex_buffer_gltf)
            gltf_file.bufferViews.append(normal_buffer_gltf)
            gltf_file.bufferViews.append(uv_buffer_gltf)
            gltf_file.bufferViews.append(color_buffer_gltf)
            gltf_file.bufferViews.append(ivertex_buffer_gltf)
            gltf_file.bufferViews.append(inormal_buffer_gltf)

            buffers_binary_final.append(get_binary_data_buffer)

            byte_offset_previous += get_buffer_full_length

        # Creating Binary Buffers in GLB Binary Format
        buffer_binary_joined_final = b''.join(buffers_binary_final)
        length_buffer_binary = len(buffer_binary_joined_final)
        
        binary_file_name = f'{self.gltf_file_name}_buffers.bin'
        buffer_glb_gltf = Buffer()
        buffer_glb_gltf.byteLength = length_buffer_binary
        buffer_glb_gltf.uri = binary_file_name
        gltf_file.buffers.append(buffer_glb_gltf)

        gltf_file.save_json(f'{self.gltf_deploy_path}.gltf')

        with open(f'{self.gltf_deploy_path}_buffers.bin', 'wb') as gltf_binary_buffer:
            gltf_binary_buffer.write(buffer_binary_joined_final)
            gltf_binary_buffer.close()
