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
        gltf_descriptor_data: dict = {}
        gltf_to_binary_data: dict = {}
        gltf_accessors: dict = {}

        tmd_model_data = self.model_data.get(f'Converted_Data')
        tmd_model_objects_number = len(self.model_data.get(f'Data_Table'))

        this_meshes_index = 0
        for tmd_object_number in range(0, tmd_model_objects_number):
            get_this_object = tmd_model_data.get(f'Object_Number_{tmd_object_number}')
            get_vertex_this_object = get_this_object.get(f'Vertex')
            get_normal_this_object = get_this_object.get(f'Normal')
            get_primitives_this_object = get_this_object.get(f'Primitives')
            object_converted = self.primitive_tmd_to_gltf_binary(primitives_to_process=get_primitives_this_object, 
                                                                 vertex_array=get_vertex_this_object, normal_array=get_normal_this_object)
            object_buffers = object_converted[0]
            elements_count = object_converted[1]

            this_position = this_meshes_index
            this_normal = this_meshes_index + 1
            this_texcoord = this_meshes_index + 2
            this_color_0 = this_meshes_index + 3
            this_indices = this_meshes_index + 4
            this_material = tmd_object_number

            this_attributes: dict = {'POSITION': this_position, 'NORMAL': this_normal,
                                     'TEXCOORD_0': this_texcoord, 'COLOR_0': this_color_0}
            this_gltf_primitive: dict = {'attributes': this_attributes, 'indices': this_indices, 'material': this_material}
            
            meshes: dict = {f'Object_Number_{tmd_object_number}': this_gltf_primitive}
            buffers_to_compile_binary: dict = {f'Object_Number_{tmd_object_number}': object_buffers}

            this_object_accessor_position: dict = {'bufferView': this_position, 'componentType': 5126, 'count': elements_count, 'type': 'VEC3'}
            this_object_accessor_normal: dict = {'bufferView': this_normal, 'componentType': 5126, 'count': elements_count, 'type': 'VEC3'}
            this_object_accessor_textcoord: dict = {'bufferView': this_texcoord, 'componentType': 5126, 'count': elements_count, 'type': 'VEC2'}
            this_object_accessor_color_0: dict = {'bufferView': this_color_0, 'componentType': 5126, 'count': elements_count, 'type': 'VEC3'}
            this_object_accessor_vertex_indices: dict = {'bufferView': this_indices, 'componentType': 5123, 'count': elements_count, 'type': 'SCALAR'}
            this_object_accessor_normal_indices: dict = {'bufferView': this_indices, 'componentType': 5123, 'count': elements_count, 'type': 'SCALAR'}

            this_accessor: dict = {f'Object_Number_{tmd_object_number}': 
                                   {'AccPos': this_object_accessor_position, 'AccNor': this_object_accessor_normal,
                                    'AccTex': this_object_accessor_textcoord, 'AccCol': this_object_accessor_color_0,
                                    'AccVerInd': this_object_accessor_vertex_indices, 'AccNorInd': this_object_accessor_normal_indices}}
            
            gltf_descriptor_data.update(meshes)
            gltf_to_binary_data.update(buffers_to_compile_binary)
            gltf_accessors.update(this_accessor)
            print(f'Accessor DATA: Vertices: {elements_count}')
            print(f'OBJECT NUMBER {tmd_object_number}')

            this_meshes_index += 5
        
        del self.model_data
        del self.animation_data
        gc.collect()
        
        self.gltf_format = {'Descriptor': gltf_descriptor_data, 'Buffers': gltf_to_binary_data, 'Accessors': gltf_accessors}
    
    def primitive_tmd_to_gltf_binary(self, primitives_to_process=dict, vertex_array=dict, normal_array=dict) -> tuple[dict, int]:
        """
        Take TMD-Primitives Data and gather UV, Color\n
        to generate UV and Colors Buffers for glTF Binary Format.\n
        Also will take the Quads (4Vertex TMD Primitives and convert them into the 3Vertex Equivalent)\n
        -> Using split_quad_primitive() Method
        """
        new_primitives: dict = {}

        # First i need to change Primitive Structure and then i can continue with Conversion
        # TODO I'M A SUCKER I SHOULD DO THIS CHANGE DIRECTLY IN THE CONVERSION FROM BINARY TO HUMAN READABLE, BUT I WILL RESEARCH WHY I DIDN'T DO THIS BEFORE
        new_primitive_number = 0
        for current_primitive in primitives_to_process:
            get_primitive_nest = primitives_to_process.get(f'{current_primitive}')
            for primitive_type in get_primitive_nest:
                if '4Vertex' in primitive_type:
                    # First we split the Quads into Triangles, so glTF Primitive Format is achieved
                    this_primitive = get_primitive_nest.get(f'{primitive_type}')
                    split_primitive = self.split_quad_primitive(primitive_properties=this_primitive)
                    split_primitive_0 = split_primitive[0]
                    split_primitive_1 = split_primitive[1]
                    change_type_primitive = primitive_type.replace("4Vertex", "3Vertex")

                    add_primitive_type = {'PrimType': change_type_primitive}
                    split_primitive_0.update(add_primitive_type)
                    split_primitive_1.update(add_primitive_type)

                    final_primitive_0 = {f'Prim_Num_{new_primitive_number}': split_primitive_0}
                    final_primitive_1 = {f'Prim_Num_{new_primitive_number + 1}': split_primitive_1}
                    new_primitives.update(final_primitive_0)
                    new_primitives.update(final_primitive_1)
                    
                    new_primitive_number += 2
                else:
                    # Since i change the Primitive Structure and Nesting I add this to the primitive
                    this_non_change_primitive = get_primitive_nest.get(f'{primitive_type}')
                    add_primitive_type = {'PrimType': primitive_type}
                    this_non_change_primitive.update(add_primitive_type)
                    final_primitive = {f'Prim_Num_{new_primitive_number}': this_non_change_primitive}
                    new_primitives.update(final_primitive)
                    
                    new_primitive_number += 1
        # Creating UV and Colors Buffers, since in TMD Primitive Format all the buffers are stored in the primitive itself, except for Vertices and Normals
        # All elements will share the count, since i'm filling all the data in there (more zeros, eventually i will do it as proper)
        primitives_buffers_this_object: dict = {}
        this_object_vertices_array: list = []
        this_object_normals_array: list = []
        this_object_uv_array: list = []
        this_object_color_array: list = []
        this_object_index_vertices_array: list = []
        this_object_index_normals_array: list = []
        total_primitives = 0
        for this_new_primitive in new_primitives:
            get_attributes = new_primitives.get(f'{this_new_primitive}')
            generated_buffers = self.generate_buffers(attributes=get_attributes, vertex_array=vertex_array, normal_array=normal_array)
            vertices_get = generated_buffers[0]
            normals_get = generated_buffers[0]
            uv_get = generated_buffers[0]
            colors_get = generated_buffers[0]
            index_vertices_get = generated_buffers[0]
            index_normals_get = generated_buffers[0]
            this_object_vertices_array.append(vertices_get)
            this_object_normals_array.append(normals_get)
            this_object_uv_array.append(uv_get)
            this_object_color_array.append(colors_get)
            this_object_index_vertices_array.append(index_vertices_get)
            this_object_index_normals_array.append(index_normals_get)
            total_primitives += 1
        
        # TODO: Meassure Length and storing bytes in each position with the corresponding length
        join_object_vertices = b''.join(this_object_vertices_array)
        join_object_normals = b''.join(this_object_normals_array)
        join_object_uv = b''.join(this_object_uv_array)
        join_object_color = b''.join(this_object_color_array)
        join_object_vertices_index = b''.join(this_object_index_vertices_array)
        join_object_normals_index = b''.join(this_object_index_normals_array)

        length_object_vertices_array = len(join_object_vertices)
        length_object_normals_array = len(join_object_normals)
        length_object_uv_array = len(join_object_uv)
        length_object_color_array = len(join_object_color)
        length_object_vertices_index_array = len(join_object_vertices_index)
        length_object_normals_index_array = len(join_object_normals_index)

        single_array_block = [join_object_vertices, join_object_normals, join_object_uv, join_object_color, join_object_vertices_index, join_object_normals_index]
        join_single_array_block = b''.join(single_array_block)
        
        length_object_array_block = len(join_single_array_block)
        each_length_arrays = [length_object_vertices_array, length_object_normals_array, length_object_uv_array, length_object_color_array, 
                              length_object_vertices_index_array, length_object_normals_index_array]
        
        offset_vertices = 0
        offset_normal = length_object_vertices_array
        offset_uv = length_object_vertices_array + length_object_normals_array
        offset_color = length_object_vertices_array + length_object_normals_array + length_object_uv_array
        offset_vertices_index = length_object_vertices_array + length_object_normals_array + length_object_uv_array + length_object_color_array
        offset_normals_index = length_object_vertices_array + length_object_normals_array + length_object_uv_array + length_object_color_array + length_object_vertices_index_array
        
        sequenced_lengths = [offset_vertices, offset_normal, offset_uv, offset_color, offset_vertices_index, offset_normals_index]

        primitives_buffers_this_object = {'Buffers': join_single_array_block, 'BufferFullLength': length_object_array_block,
                                          'LengthEachArray': each_length_arrays, 'SequencedLenghts': sequenced_lengths}
        
        print(f'Lengths: Vertex: {length_object_vertices_array}, Normals: {length_object_normals_array}, UV: {length_object_uv_array}, Color: {length_object_color_array}, IndexVertices: {length_object_vertices_index_array}, IndexNormals: {length_object_normals_index_array}')
        
        print(f'Total Block Lenght: {length_object_array_block}')

        return primitives_buffers_this_object, total_primitives
    
    def split_quad_primitive(self, primitive_properties=dict) -> tuple[dict, dict]:
        """
        Quad to Tri:\n
        Convert a Primitive Quadrilatera into a Triangle\n
        since glTF format won't support Quads in their Primitives structure
        """
        new_primitive_1: dict = {}
        new_primitive_2: dict = {}

        vertex_index_0 = primitive_properties.get('vertex0')
        vertex_index_1 = primitive_properties.get('vertex1')
        vertex_index_2 = primitive_properties.get('vertex2')
        vertex_index_3 = primitive_properties.get('vertex3')

        normal_index_0 = primitive_properties.get('normal0')
        normal_index_1 = primitive_properties.get('normal1')
        normal_index_2 = primitive_properties.get('normal2')
        normal_index_3 = primitive_properties.get('normal3')

        u_0 = primitive_properties.get('u0')
        v_0 = primitive_properties.get('v0')
        u_1 = primitive_properties.get('u1')
        v_1 = primitive_properties.get('v1')
        u_2 = primitive_properties.get('u2')
        v_2 = primitive_properties.get('v2')
        u_3 = primitive_properties.get('u3')
        v_3 = primitive_properties.get('v3')

        r_0 = primitive_properties.get('r0')
        g_0 = primitive_properties.get('g0')
        b_0 = primitive_properties.get('b0')
        r_1 = primitive_properties.get('r1')
        g_1 = primitive_properties.get('g1')
        b_1 = primitive_properties.get('b1')
        r_2 = primitive_properties.get('r2')
        g_2 = primitive_properties.get('g2')
        b_2 = primitive_properties.get('b2')
        r_3 = primitive_properties.get('r3')
        g_3 = primitive_properties.get('g3')
        b_3 = primitive_properties.get('b3')
        
        new_primitive_1 = {'vertex0': vertex_index_0, 'vertex1': vertex_index_1, 'vertex2': vertex_index_2, 
                           'normal0': normal_index_0, 'normal1': normal_index_1, 'normal2': normal_index_2, 
                           'u_0': u_0, 'v_0': v_0, 'u_1': u_1, 'v_1': v_1, 'u_2': u_2, 'v_2': v_2, 
                           'r0': r_0, 'g0': g_0, 'b0': b_0, 'r1': r_1, 'g1': g_1, 'b1': b_1, 'r2': r_2, 'g2': g_2, 'b2': b_2}
        
        new_primitive_2 = {'vertex0': vertex_index_0, 'vertex1': vertex_index_2, 'vertex2': vertex_index_3, 
                           'normal0': normal_index_0, 'normal1': normal_index_2, 'normal2': normal_index_3, 
                           'u_0': u_0, 'v_0': v_0, 'u_1': u_2, 'v_1': v_2, 'u_2': u_3, 'v_2': v_3, 
                           'r0': r_0, 'g0': g_0, 'b0': b_0, 'r1': r_2, 'g1': g_2, 'b1': b_2, 'r2': r_3, 'g2': g_3, 'b2': b_3}

        return new_primitive_1, new_primitive_2

    def generate_buffers(self, attributes=dict, vertex_array=dict, normal_array=dict) -> list:
        """
        Generate Buffers:\n
        This Method will take the data from TMD-Primitives and will generate the buffers\n
        for glTF Binary Format, this include IndexVertices, IndexNormals, \n
        UV, Color, Vertex and Normal, converting it into Bytes. This is the Data Format:\n
        POSITION=VEC3 ; Float32Array\n
        NORMAL=VEC3 ; Float32Array\n
        UV=VEC2 ; Float32Array\n
        COLOR_0=VEC3 ; Float32Array\n
        Vertices_indices=SCALAR ; UNSIGNED_INT\n
        Normals_indices=SCALAR ; UNSIGNED_INT\n
        """
        new_vertex_array: list = []
        new_normal_array: list = []
        vertex_index: list = []
        normal_index: list = []
        uv_attribute: list = []
        color_attribute: list = []

        this_primitive_single_buffer: list = {}

        get_vertex_0 = attributes.get('vertex0')
        get_vertex_1 = attributes.get('vertex1')
        get_vertex_2 = attributes.get('vertex2')

        get_normal_0 = attributes.get('normal0')
        get_normal_1 = attributes.get('normal1')
        get_normal_2 = attributes.get('normal2')

        u_0 = attributes.get('u0')
        v_0 = attributes.get('v0')
        u_1 = attributes.get('u1')
        v_1 = attributes.get('v1')
        u_2 = attributes.get('u2')
        v_2 = attributes.get('v2')

        r_0 = attributes.get('r0')
        g_0 = attributes.get('g0')
        b_0 = attributes.get('b0')
        r_1 = attributes.get('r1')
        g_1 = attributes.get('g1')
        b_1 = attributes.get('b1')
        r_2 = attributes.get('r2')
        g_2 = attributes.get('g2')
        b_2 = attributes.get('b2')

        if get_normal_0 == None:
            get_normal_0 = get_normal_1 = get_normal_2 = 0
        elif (get_normal_0 != None) and (get_normal_2 == None):
            get_normal_0 = get_normal_1 = get_normal_2 = get_normal_0
        
        if u_0 == None:
            u_0 = v_0 = u_1 = v_1 = u_2 = v_2 = 0.0
        
        if r_0 == None:
            r_0 = g_0 = b_0 = r_1 = g_1 = b_1 = r_2 = g_2 = b_2 = 0
        elif (r_0 != None) and (b_2 == None):
            r_0 = r_1 = r_2 = r_0
            g_0 = g_1 = g_2 = g_0
            b_0 = b_1 = b_2 = b_0
        
        # Vertex 0 Properties and Array into Binary
        get_vertex_vectors_0 = vertex_array.get(f'{f'Vertex_Number_{get_vertex_0}'}')
        get_x_0 = struct.pack('<f', get_vertex_vectors_0.get(f'VecX'))
        get_y_0 = struct.pack('<f', get_vertex_vectors_0.get(f'VecY'))
        get_z_0 = struct.pack('<f', get_vertex_vectors_0.get(f'VecZ'))
        new_vertex_array.append(get_x_0)
        new_vertex_array.append(get_y_0)
        new_vertex_array.append(get_z_0)
        get_vertex_0_bin = int.to_bytes(0, length=4, byteorder='little', signed=False)

        # Vertex 1 Properties and Array into Binary
        get_vertex_vectors_1 = vertex_array.get(f'Vertex_Number_{get_vertex_1}')
        get_x_1 = struct.pack('<f', get_vertex_vectors_1.get(f'VecX'))
        get_y_1 = struct.pack('<f', get_vertex_vectors_1.get(f'VecY'))
        get_z_1 = struct.pack('<f', get_vertex_vectors_1.get(f'VecZ'))
        new_vertex_array.append(get_x_1)
        new_vertex_array.append(get_y_1)
        new_vertex_array.append(get_z_1)
        get_vertex_1_bin = int.to_bytes(1, length=4, byteorder='little', signed=False)

        # Vertex 2 Properties and Array into Binary
        get_vertex_vectors_2 = vertex_array.get(f'Vertex_Number_{get_vertex_2}')
        get_x_2 = struct.pack('<f', get_vertex_vectors_2.get(f'VecX'))
        get_y_2 = struct.pack('<f', get_vertex_vectors_2.get(f'VecY'))
        get_z_2 = struct.pack('<f', get_vertex_vectors_2.get(f'VecZ'))
        new_vertex_array.append(get_x_2)
        new_vertex_array.append(get_y_2)
        new_vertex_array.append(get_z_2)
        get_vertex_2_bin = int.to_bytes(2, length=4, byteorder='little', signed=False)

        # Normal 0 Properties and Array into Binary
        get_normal_vectors_0 = normal_array.get(f'{f'Normal_Number_{get_normal_0}'}')
        get_n_x_0 = struct.pack('<f', get_normal_vectors_0.get(f'VecX'))
        get_n_y_0 = struct.pack('<f', get_normal_vectors_0.get(f'VecY'))
        get_n_z_0 = struct.pack('<f', get_normal_vectors_0.get(f'VecZ'))
        new_normal_array.append(get_n_x_0)
        new_normal_array.append(get_n_y_0)
        new_normal_array.append(get_n_z_0)
        get_normal_0_bin = int.to_bytes(0, length=4, byteorder='little', signed=False)

        # Normal 1 Properties and Array into Binary
        get_normal_vectors_1 = normal_array.get(f'{f'Normal_Number_{get_normal_1}'}')
        get_n_x_1 = struct.pack('<f', get_normal_vectors_1.get(f'VecX'))
        get_n_y_1 = struct.pack('<f', get_normal_vectors_1.get(f'VecY'))
        get_n_z_1 = struct.pack('<f', get_normal_vectors_1.get(f'VecZ'))
        new_normal_array.append(get_n_x_1)
        new_normal_array.append(get_n_y_1)
        new_normal_array.append(get_n_z_1)
        get_normal_1_bin = int.to_bytes(1, length=4, byteorder='little', signed=False)

        # Normal 2 Properties and Array into Binary
        get_normal_vectors_2 = normal_array.get(f'{f'Normal_Number_{get_normal_2}'}')
        get_n_x_2 = struct.pack('<f', get_normal_vectors_2.get(f'VecX'))
        get_n_y_2 = struct.pack('<f', get_normal_vectors_2.get(f'VecY'))
        get_n_z_2 = struct.pack('<f', get_normal_vectors_2.get(f'VecZ'))
        new_normal_array.append(get_n_x_2)
        new_normal_array.append(get_n_y_2)
        new_normal_array.append(get_n_z_2)
        get_normal_2_bin = int.to_bytes(2, length=4, byteorder='little', signed=False)

        # UV Data into Binary
        u_0_bin = struct.pack('<f', u_0)
        v_0_bin = struct.pack('<f', v_0)
        u_1_bin = struct.pack('<f', u_1)
        v_1_bin = struct.pack('<f', v_1)
        u_2_bin = struct.pack('<f', u_2)
        v_2_bin = struct.pack('<f', v_2)

        # Vertex 0 RGB Calcs and into Binary
        calc_r_0 = struct.pack('<f', round(float(r_0 / 256), 12))
        calc_g_0 = struct.pack('<f', round(float(g_0 / 256), 12))
        calc_b_0 = struct.pack('<f', round(float(b_0 / 256), 12))

        # Vertex 1 RGB Calcs and into Binary
        calc_r_1 = struct.pack('<f', round(float(r_1 / 256), 12))
        calc_g_1 = struct.pack('<f', round(float(g_1 / 256), 12))
        calc_b_1 = struct.pack('<f', round(float(b_1 / 256), 12))

        # Vertex 1 RGB Calcs and into Binary
        calc_r_2 = struct.pack('<f', round(float(r_2 / 256), 12))
        calc_g_2 = struct.pack('<f', round(float(g_2 / 256), 12))
        calc_b_2 = struct.pack('<f', round(float(b_2 / 256), 12))

        # Adding Pad Bytes to the arrays which need it
        padding_value = b'\x00\x00'
        vertex_index = [get_vertex_0_bin, get_vertex_1_bin, get_vertex_2_bin]
        normal_index = [get_normal_0_bin, get_normal_1_bin, get_normal_2_bin]
        uv_attribute = [u_0_bin, v_0_bin, u_1_bin, v_1_bin, u_2_bin, v_2_bin, padding_value, padding_value]
        color_attribute = [calc_r_0, calc_g_0, calc_b_0, calc_r_1, calc_g_1, calc_b_1, calc_r_2, calc_g_2, calc_b_2]

        new_vertex_array_join = b''.join(new_vertex_array)
        new_normal_array_join = b''.join(new_normal_array)
        uv_attribute_join = b''.join(uv_attribute)
        color_attribute_join = b''.join(color_attribute)
        vertex_index_join = b''.join(vertex_index)
        normal_index_join = b''.join(normal_index)

        this_primitive_single_buffer = [new_vertex_array_join, new_normal_array_join, uv_attribute_join, color_attribute_join, vertex_index_join, normal_index_join]

        print(len(vertex_index_join), len(normal_index_join))
        return this_primitive_single_buffer

