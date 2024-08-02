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
        tmd_model_info = self.model_data.get(f'Data_Table')
        tmd_model_objects_number = len(self.model_data.get(f'Data_Table'))

        this_data_index = 0 # This Value actually is the number of position in the arrage in Meshes Primitives and Accessors
        for tmd_object_number in range(0, tmd_model_objects_number):
            #print(f'OBJECT NUMBER {tmd_object_number}')
            get_this_object = tmd_model_data.get(f'Object_Number_{tmd_object_number}')
            get_this_info = tmd_model_info.get(f'Object_Number_{tmd_object_number}')
            get_vertex_this_object = get_this_object.get(f'Vertex')
            get_normal_this_object = get_this_object.get(f'Normal')
            get_primitives_this_object = get_this_object.get(f'Primitives')
            object_converted = self.tmd_to_gltf_buffer(primitives_to_process=get_primitives_this_object, 
                                                       vertex_array=get_vertex_this_object, normal_array=get_normal_this_object, 
                                                       object_info=get_this_info)
            
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

    def tmd_to_gltf_buffer(self, primitives_to_process=dict, vertex_array=dict, normal_array=dict, object_info=dict) -> None:
        """
        Take TMD Data of a SINGLE Object from TMDs gather Vertices, Normals, UV, Color and Indices\n
        to generate Buffers for glTF Binary Format.\n
        Also will take the Quads (4Vertex TMD Primitives and convert them into the 3Vertex Equivalent)\n
        -> Using quad_to_tri() Method
        Also will calculate the counts for put them into the Accessors value
        """
        """Each Primitive would be build by 3 Vertices, 3 Normals, 3 UVs, 3 Colors and a Pair of 3 Indices
        Even for Non Textured, Non Colored or Non Normal Triangles, all the data will be fill with
        default values, to avoid confusion in the Arrays
        each element will be:
        3 Vertices: 1 VEC3 == 3 Floats 32 Bits and each Float is 4 Bytes long, so 3*4 = 12 Bytes each VEC3
        3 Normals: 1 VEC3 == 3 Floats 32 Bits and each Float is 4 Bytes long, so 3*4 = 12 Bytes each VEC3
        6 UV: 2 VEC2 == 2 Floats 32 Bits and each Float is 4 Bytes long, so 2*4 = 8 Bytes each VEC2
        3 Colors: 1 VEC4 == 4 Floats 32 Bits and each Float is 4 Bytes long, so 4*4 = 16 Bytes each VEC4
        3 Indices: 1 SCALAR = Unsigned Integer 16 Bit each is 2 Bytes long, so 3*2 = 6 Bytes each SCALAR
        """
        buffers_this_object: dict = {}

        obj_vindex_buffer: list = [] # Came from TMD Primitive IndexVertex Array
        obj_nindex_buffer: list = [] # Came from TMD Primitive IndexNormal Array
        obj_uv_buffer: list = [] # Came from TMD Primitive UV Array
        obj_color_buffer: list = [] # Came from TMD Primitive Color Array
        obj_vertex_buffer: list = [] # Came from the Original TMD Vertex Array
        obj_normal_buffer: list = [] # Came from the Original TMD Normal Array

        vertex_count: int = 0
        normal_count: int = 0
        single_element_count = 0
        multi_element_count = 0
        for current_primitive_tmd in primitives_to_process:
            this_primitive_data = primitives_to_process.get(f'{current_primitive_tmd}')
            for primitive_type in this_primitive_data:
                getting_data = this_primitive_data.get(f'{primitive_type}')
                if f'4Vertex' in primitive_type:
                    two_triangles = self.quad_to_tri(prim_data=getting_data)
                    triangle_0 = two_triangles[0]
                    triangle_1 = two_triangles[1]
                    create_buffer_0 = self.create_buffer_triangle(triangle_data=triangle_0)
                    create_buffer_1 = self.create_buffer_triangle(triangle_data=triangle_1)

                    buffer_0_vi = create_buffer_0.get('VertexIndex')
                    buffer_0_ni = create_buffer_0.get('NormalIndex')
                    buffer_0_uv = create_buffer_0.get('UV')
                    buffer_0_rgba = create_buffer_0.get('RGBA')

                    buffer_1_vi = create_buffer_1.get('VertexIndex')
                    buffer_1_ni = create_buffer_1.get('NormalIndex')
                    buffer_1_uv = create_buffer_1.get('UV')
                    buffer_1_rgba = create_buffer_1.get('RGBA')

                    obj_vindex_buffer.append(buffer_0_vi)
                    obj_vindex_buffer.append(buffer_1_vi)
                    obj_nindex_buffer.append(buffer_0_ni)
                    obj_nindex_buffer.append(buffer_1_ni)
                    obj_uv_buffer.append(buffer_0_uv)
                    obj_uv_buffer.append(buffer_1_uv)
                    obj_color_buffer.append(buffer_0_rgba)
                    obj_color_buffer.append(buffer_1_rgba)

                    single_element_count += 2
                    multi_element_count += 6
                
                else:
                    create_buffer_3v = self.create_buffer_triangle(triangle_data=getting_data)
                    buffer_3v_vi = create_buffer_3v.get('VertexIndex')
                    buffer_3v_ni = create_buffer_3v.get('NormalIndex')
                    buffer_3v_uv = create_buffer_3v.get('UV')
                    buffer_3v_rgba = create_buffer_3v.get('RGBA')

                    obj_vindex_buffer.append(buffer_3v_vi)
                    obj_nindex_buffer.append(buffer_3v_ni)
                    obj_uv_buffer.append(buffer_3v_uv)
                    obj_color_buffer.append(buffer_3v_rgba)

                    single_element_count += 1
                    multi_element_count += 3
        
        vertex_count = object_info.get('VertexNumber')
        normal_count = object_info.get('NormalNumber')
        # With this hacky thing i avoid having 0 normals at Normal Count... Sorry Monoxide :')
        if normal_count == 0:
            normal_count = 1
        
        for vertex in vertex_array:
            get_this_vertex = vertex_array.get(f'{vertex}')
            get_x_v = struct.pack('<f', get_this_vertex.get('VecX'))
            get_y_v = struct.pack('<f', get_this_vertex.get('VecY'))
            get_z_v = struct.pack('<f', get_this_vertex.get('VecZ'))
            obj_vertex_buffer.append(get_x_v)
            obj_vertex_buffer.append(get_y_v)
            obj_vertex_buffer.append(get_z_v)
        
        for normal in normal_array:
            get_this_normal = normal_array.get(f'{normal}')
            get_x_n = struct.pack('<f', get_this_normal.get('VecX'))
            get_y_n = struct.pack('<f', get_this_normal.get('VecY'))
            get_z_n = struct.pack('<f', get_this_normal.get('VecZ'))
            obj_normal_buffer.append(get_x_n)
            obj_normal_buffer.append(get_y_n)
            obj_normal_buffer.append(get_z_n)
        
        # TODO: Now it's time to join
        


    def quad_to_tri(self, prim_data=dict) -> tuple[dict, dict]:
        """
        Quadrilateral to Triangle Binary:\n
        This Method will take a Quadrilateral TMD Primitive Data, convert it into Two Triangles.
        """
        triangle_0: dict = {}
        triangle_1: dict = {}

        vertex_index_0 = prim_data.get('vertex0')
        vertex_index_1 = prim_data.get('vertex1')
        vertex_index_2 = prim_data.get('vertex2')
        vertex_index_3 = prim_data.get('vertex3')

        normal_index_0 = prim_data.get('normal0')
        normal_index_1 = prim_data.get('normal1')
        normal_index_2 = prim_data.get('normal2')
        normal_index_3 = prim_data.get('normal3')

        u0 = prim_data.get('u0')
        v0 = prim_data.get('v0')
        u1 = prim_data.get('u1')
        v1 = prim_data.get('v1')
        u2 = prim_data.get('u2')
        v2 = prim_data.get('v2')
        u3 = prim_data.get('u3')
        v3 = prim_data.get('v3')

        r0 = prim_data.get('r0')
        g0 = prim_data.get('g0')
        b0 = prim_data.get('b0')
        r1 = prim_data.get('r1')
        g1 = prim_data.get('g1')
        b1 = prim_data.get('b1')
        r2 = prim_data.get('r2')
        g2 = prim_data.get('g2')
        b2 = prim_data.get('b2')
        r3 = prim_data.get('r3')
        g3 = prim_data.get('g3')
        b3 = prim_data.get('b3')
        
        triangle_0 = {'vertex0': vertex_index_0, 'vertex1': vertex_index_1, 'vertex2': vertex_index_2,
                      'normal0': normal_index_0, 'normal1': normal_index_1, 'normal2': normal_index_2, 
                      'u0': u0, 'v0': v0, 'u1': u1, 'v1': v1, 'u2': u2, 'v2': v2, 
                      'r0': r0, 'g0': g0, 'b0': b0, 'r1': r1, 'g1': g1, 'b1': b1, 'r2': r2, 'g2': g2, 'b2': b2}
        
        triangle_1 = {'vertex0': vertex_index_0, 'vertex1': vertex_index_2, 'vertex2': vertex_index_3,
                      'normal0': normal_index_0, 'normal1': normal_index_2, 'normal2': normal_index_3, 
                      'u0': u0, 'v0': v0, 'u1': u2, 'v1': v2, 'u2': u3, 'v2': v3, 
                      'r0': r0, 'g0': g0, 'b0': b0, 'r1': r2, 'g1': g2, 'b1': b2, 'r2': r3, 'g2': g3, 'b2': b3}

        return triangle_0, triangle_1

    def create_buffer_triangle(self, triangle_data=dict) -> dict:
        """
        Create Buffer Triangle:\n
        will take a single Triangle Data to convert into Buffers,\n
        adjust the data and write the buffers as Bytes
        """
        """
        At the moment there is no value empty, so even if a triangle
        have no normal, uv or color, will be fill with default values
        """
        triangle_buffer: dict = {}
        vertex_index_0 = triangle_data.get('vertex0')
        vertex_index_1 = triangle_data.get('vertex1')
        vertex_index_2 = triangle_data.get('vertex2')

        normal_index_0 = triangle_data.get('normal0')
        normal_index_1 = triangle_data.get('normal1')
        normal_index_2 = triangle_data.get('normal2')

        u0 = triangle_data.get('u0')
        v0 = triangle_data.get('v0')
        u1 = triangle_data.get('u1')
        v1 = triangle_data.get('v1')
        u2 = triangle_data.get('u2')
        v2 = triangle_data.get('v2')

        r0 = triangle_data.get('r0')
        g0 = triangle_data.get('g0')
        b0 = triangle_data.get('b0')
        alpha_0 = 1.0
        r1 = triangle_data.get('r1')
        g1 = triangle_data.get('g1')
        b1 = triangle_data.get('b1')
        alpha_1 = 1.0
        r2 = triangle_data.get('r2')
        g2 = triangle_data.get('g2')
        b2 = triangle_data.get('b2')
        alpha_2 = 1.0

        """
        If Normal is None, will be assigned 0 as the Index. 
        In case that only exist one Normal, the other three will be assigned with the same
        """
        if normal_index_0 == None:
            normal_index_0 = normal_index_1 = normal_index_2 = 0
        elif (normal_index_0 != None) and (normal_index_2 == None):
            normal_index_1 = normal_index_2 = normal_index_0
        
        """
        If UV Data is None, everything will be assigned with 0.0 UV Vector
        """
        if u0 == None:
            u0 = v0 = u1 = v1 = u2 = v2 = 0.0
        
        """
        If Color is None, all colors will be assigned to form Black.
        In case that only exist one color, other three will be assigned with the same to fill a solid color
        """
        if r0 == None:
            r0 = g0 = b0 = r1 = g1 = b1 = r2 = g2 = b2 = 0.0
        elif (r0 != None) and (b2 == None):
            r1 = r2 = r0
            g1 = g2 = g0
            b1 = b2 = b0
        
        # Convert the Vertex Indices as SCALAR [Unsigned INT 16 Bit] - Vertex Index
        vi_0_binary = int.to_bytes(vertex_index_0, length=2, byteorder='little', signed=False)
        vi_1_binary = int.to_bytes(vertex_index_1, length=2, byteorder='little', signed=False)
        vi_2_binary = int.to_bytes(vertex_index_2, length=2, byteorder='little', signed=False)
        # Convert the Normal Indices as SCALAR [Unsigned INT 16 Bit] - Normal Index
        ni_0_binary = int.to_bytes(normal_index_0, length=2, byteorder='little', signed=False)
        ni_1_binary = int.to_bytes(normal_index_1, length=2, byteorder='little', signed=False)
        ni_2_binary = int.to_bytes(normal_index_2, length=2, byteorder='little', signed=False)

        # Convert the UV Data into VEC2 [32 Bit Float]
        u0_bin = struct.pack('<f', u0)
        v0_bin = struct.pack('<f', v0)
        u1_bin = struct.pack('<f', u1)
        v1_bin = struct.pack('<f', v1)
        u2_bin = struct.pack('<f', u2)
        v2_bin = struct.pack('<f', v2)

        # Convert Color Data into VEC4 [32 Bit Float]
        r0_bin = struct.pack('<f', r0)
        g0_bin = struct.pack('<f', g0)
        b0_bin = struct.pack('<f', b0)
        alpha_0_bin = struct.pack('<f', alpha_0)
        r1_bin = struct.pack('<f', r1)
        g1_bin = struct.pack('<f', g1)
        b1_bin = struct.pack('<f', b1)
        alpha_1_bin = struct.pack('<f', alpha_1)
        r2_bin = struct.pack('<f', r2)
        g2_bin = struct.pack('<f', g2)
        b2_bin = struct.pack('<f', b2)
        alpha_2_bin = struct.pack('<f', alpha_2)

        vertex_index_array = [vi_0_binary, vi_1_binary, vi_2_binary]
        final_vertex_index = b''.join(vertex_index_array)
        
        normal_index_array = [ni_0_binary, ni_1_binary, ni_2_binary]
        final_normal_index = b''.join(normal_index_array)

        uv_array = [u0_bin, v0_bin, u1_bin, v1_bin, u2_bin, v2_bin]
        final_uv_array = b''.join(uv_array)

        color_array = [r0_bin, g0_bin, b0_bin, alpha_0_bin, r1_bin, g1_bin, b1_bin, alpha_1_bin, r2_bin, g2_bin, b2_bin, alpha_2_bin]
        final_color_array = b''.join(color_array)

        triangle_buffer = {'VertexIndex': final_vertex_index, 'NormalIndex': final_normal_index, 'UV': final_uv_array, 'RGBA': final_color_array}

        return triangle_buffer

    def check_if_multiple(self, mul=int, base=int) -> bool:
        """
        Check if Multiple:\n
        Check if a value is multiple of base number.
        """
        checking_bool: bool = False
        if mul % base:
            True
        else:
            False

        return checking_bool
    
    def closest_multiple(self, mul=int, base=int) -> int:
        """
        Closest Multiple:\n
        Check the closest upper value taking in care a base number.
        """
        multiple = int(round(mul / base) * 4)

        return multiple

