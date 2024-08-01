"""

glTF Compiler: this module will take the converted data,
and re-arrage for later being converted into glTF Files.

Copyright (C) 2024 DooMMetaL

"""

import gc
import struct

class NewModel:
    def __init__(self, model_data=dict, animation_data=dict | None, file_name=str) -> None:
        self.model_data = model_data
        self.animation_data = animation_data
        self.file_name = file_name
        self.gltf_format: dict = {}
        self.model_arrager()
    
    def model_arrager(self) -> None:
        gltf_meshes_data: dict = {}
        gltf_to_binary_data: dict = {}
        gltf_accessors: dict = {}

        tmd_model_data = self.model_data.get(f'Converted_Data')
        tmd_model_objects_number = len(self.model_data.get(f'Data_Table'))

        this_data_index = 0 # This Value actually is the number of position in the arrage in Meshes Primitives and Accessors
        for tmd_object_number in range(0, tmd_model_objects_number):
            #print(f'OBJECT NUMBER {tmd_object_number}')
            get_this_object = tmd_model_data.get(f'Object_Number_{tmd_object_number}')
            get_vertex_this_object = get_this_object.get(f'Vertex')
            get_normal_this_object = get_this_object.get(f'Normal')
            get_primitives_this_object = get_this_object.get(f'Primitives')
            object_converted = self.tmd_to_gltf_buffer(primitives_to_process=get_primitives_this_object, 
                                                       vertex_array=get_vertex_this_object, normal_array=get_normal_this_object)
            
            current_mesh = self.generate_mesh_data(current_index=this_data_index)
            
            buffers_to_compile_binary: dict = {f'Object_Number_{tmd_object_number}': None}

            current_accesor = self.generate_accessor(current_index=this_data_index, current_object_number=tmd_object_number, mesh_element_count=[1,2])

            gltf_meshes_data.update(current_mesh)
            gltf_to_binary_data.update(buffers_to_compile_binary)
            gltf_accessors.update(current_accesor)

            #print(f'Accessor DATA: Vertices: {None}')

            this_data_index += 5
        
        del self.model_data
        del self.animation_data
        gc.collect()
        
        self.gltf_format = {'Meshes': gltf_meshes_data, 'Buffers': gltf_to_binary_data, 'Accessors': gltf_accessors}

    def generate_mesh_data(self, current_index=int, current_object_number=int) -> dict:
        mesh_data: dict = {}
        this_position = current_index
        this_normal = current_index + 1
        this_texcoord = current_index + 2
        this_color_0 = current_index + 3
        this_indices = current_index + 4
        this_material = current_object_number

        this_attributes: dict = {'POSITION': this_position, 'NORMAL': this_normal,
                                    'TEXCOORD_0': this_texcoord, 'COLOR_0': this_color_0}
        this_gltf_primitive: dict = {'attributes': this_attributes, 'indices': this_indices, 'material': this_material}
        
        mesh_data = {f'Object_Number_{current_object_number}': this_gltf_primitive}

        return mesh_data

    def generate_accessor(self, current_index=int, current_object_number=int, mesh_element_count=dict) -> dict:
        """
        Generate Accessor:
        As the name states, will generate the Accessor data for each Mesh in the Scece.
        """
        this_accessor: dict = {}
        this_object_accessor_position: dict = {'bufferView': current_index, 'componentType': 5126, 'count': None, 'type': 'VEC3'}
        this_object_accessor_normal: dict = {'bufferView': current_index + 1, 'componentType': 5126, 'count': None, 'type': 'VEC3'}
        this_object_accessor_textcoord: dict = {'bufferView': current_index + 2, 'componentType': 5126, 'count': None, 'type': 'VEC2'}
        this_object_accessor_color_0: dict = {'bufferView': current_index + 3, 'componentType': 5126, 'count': None, 'type': 'VEC3'}
        this_object_accessor_vertex_indices: dict = {'bufferView': current_index + 4, 'componentType': 5123, 'count': None, 'type': 'SCALAR'}

        this_accessor = {f'Object_Number_{current_object_number}':
                         {'AccPos': this_object_accessor_position, 'AccNor': this_object_accessor_normal, 
                          'AccTex': this_object_accessor_textcoord, 'AccCol': this_object_accessor_color_0, 
                          'AccInd': this_object_accessor_vertex_indices}}
        
        return this_accessor

    def tmd_to_gltf_buffer(self, primitives_to_process=dict, vertex_array=dict, normal_array=dict) -> None:
        """
        Take TMD Data and gather Vertices, Normals, UV, Color and Indices\n
        to generate Buffers for glTF Binary Format.\n
        Also will take the Quads (4Vertex TMD Primitives and convert them into the 3Vertex Equivalent)\n
        -> Using split_quad_primitive() Method
        """
        new_primitives: dict = {}
        print(len(primitives_to_process))

        """Each Primitive would be build by 3 Vertices, 3 Normals, 3 UVs, 3 Colors and a Pair of 3 Indices
        each element will be:
        3 Vertices: 1 VEC3 == 3 Floats 32 Bits and each Float is 4 Bytes long, so 3*4 = 12 Bytes each VEC3
        3 Normals: 1 VEC3 == 3 Floats 32 Bits and each Float is 4 Bytes long, so 3*4 = 12 Bytes each VEC3
        6 UV: 2 VEC2 == 2 Floats 32 Bits and each Float is 4 Bytes long, so 2*4 = 8 Bytes each VEC2
        3 Colors: 1 VEC4 == 4 Floats 32 Bits and each Float is 4 Bytes long, so 4*4 = 16 Bytes each VEC4
        3 Indices: 1 SCALAR = Unsigned Integer 16 Bit each is 2 Bytes long, so 3*2 = 6 Bytes each SCALAR
        """

    def check_if_multiple(self, mul=int, base=int) -> bool:
        checking_bool: bool = False
        if mul % base:
            True
        else:
            False

        return checking_bool
    
    def closest_multiple(self, mul=int, base=int) -> int:
        multiple = int(round(mul / base) * 4)

        return multiple

