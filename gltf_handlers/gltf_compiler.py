"""

glTF Compiler: this module will take the converted data,
and re-arrage for later being converted into glTF Files.

Copyright (C) 2024 DooMMetaL

"""

import gc
import struct
import math
import numpy

class NewGltfModel:
    def __init__(self, model_data=dict, animation_data=dict | None, file_name=str) -> None:
        """Create a glTF Model Object from TMD Files"""
        self.model_data = model_data
        self.animation_data = animation_data
        self.file_name = file_name
        self.gltf_format: dict = {}
        self.model_arrager()
    
    def model_arrager(self) -> None:
        """
        Model Arrager: \n
        Arrage Model data to fit into glTF file format
        """
        gltf_total_objects: int = 0
        gltf_meshes_data: dict = {}
        gltf_to_binary_data: dict = {}
        gltf_accessors: dict = {}
        gltf_buffersview: dict = {}

        tmd_model_data = self.model_data.get(f'Converted_Data')
        tmd_model_info = self.model_data.get(f'Data_Table')
        tmd_model_objects_number = len(self.model_data.get(f'Data_Table'))

        this_data_index = 0 # This Value actually is the number of position in the arrage in Meshes Primitives and Accessors
        buffer_size = 0
        for tmd_object_number in range(0, tmd_model_objects_number):
            print(f'OBJECT NUMBER {tmd_object_number}')
            get_this_object = tmd_model_data.get(f'Object_Number_{tmd_object_number}')
            get_this_info = tmd_model_info.get(f'Object_Number_{tmd_object_number}')
            get_vertex_this_object = get_this_object.get(f'Vertex')
            get_normal_this_object = get_this_object.get(f'Normal')
            get_primitives_this_object = get_this_object.get(f'Primitives')
            object_converted = self.tmd_to_gltf_buffer(primitives_to_process=get_primitives_this_object, 
                                                       vertex_array=get_vertex_this_object, normal_array=get_normal_this_object, 
                                                       object_info=get_this_info)
            
            object_buffers = object_converted.get('CompiledBuffers')
            this_buffer_array_size = len(object_buffers)

            elements_counts = object_converted.get('Counts')

            elements_sizes = object_converted.get('BuffersSizes')

            current_bufferview = self.generate_bufferview(bv_current_size_array=buffer_size, bv_elements_sizes=elements_sizes)
            
            current_mesh = self.generate_mesh_data(current_index=this_data_index, current_object_number=tmd_object_number)
            
            current_accesor = self.generate_accessor(current_index=this_data_index, current_object_number=tmd_object_number, mesh_element_count=elements_counts)

            buffers_to_compile_binary: dict = {f'Object_Number_{tmd_object_number}': object_buffers}

            buffers_view = {f'Object_Number_{tmd_object_number}': current_bufferview}

            mesh_data = {f'Object_Number_{tmd_object_number}': current_mesh}

            gltf_meshes_data.update(mesh_data)
            gltf_to_binary_data.update(buffers_to_compile_binary)
            gltf_accessors.update(current_accesor)
            gltf_buffersview.update(buffers_view)

            this_data_index += 5
            buffer_size += this_buffer_array_size
            gltf_total_objects += 1
        
        del self.model_data
        del self.animation_data
        gc.collect()
        
        self.gltf_format = {'ObjectsNumber': gltf_total_objects, 'Meshes': gltf_meshes_data, 'Buffers': gltf_to_binary_data, 
                            'Accessors': gltf_accessors, 'BufferViews': gltf_buffersview, 'BufferSizeTotal': buffer_size}

    def generate_mesh_data(self, current_index=int, current_object_number=int) -> dict:
        """
        Generate Mesh Data:\n
        Generate the Mesh Data for glTF based in Index for Accessors
        """
        this_gltf_primitive: dict = {}
        this_position = current_index
        this_normal = current_index + 1
        this_texcoord = current_index + 2
        this_color_0 = current_index + 3
        this_vertex_indices = current_index + 4
        this_material = current_object_number


        this_attributes: dict = {'POSITION': this_position, 'NORMAL': this_normal,
                                    'TEXCOORD_0': this_texcoord, 'COLOR_0': this_color_0}
        this_gltf_primitive: dict = {'attributes': this_attributes, 'indices': this_vertex_indices, 'material': this_material}

        return this_gltf_primitive

    def generate_accessor(self, current_index=int, current_object_number=int, mesh_element_count=dict) -> dict:
        """
        Generate Accessor:
        As the name states, will generate the Accessor data for each Mesh in the Scece.
        """
        vertex_count = mesh_element_count[0]
        normal_count = mesh_element_count[1]
        element_count = mesh_element_count[2]

        this_accessor: dict = {}
        this_object_accessor_position: dict = {'bufferView': current_index, 'componentType': 5126, 'count': vertex_count, 'type': 'VEC3'}
        this_object_accessor_normal: dict = {'bufferView': current_index + 1, 'componentType': 5126, 'count': normal_count, 'type': 'VEC3'}
        this_object_accessor_textcoord: dict = {'bufferView': current_index + 2, 'componentType': 5126, 'count': vertex_count, 'type': 'VEC2'}
        this_object_accessor_color_0: dict = {'bufferView': current_index + 3, 'componentType': 5126, 'count': vertex_count, 'type': 'VEC4'}
        this_object_accessor_vertex_indices: dict = {'bufferView': current_index + 4, 'componentType': 5123, 'count': element_count, 'type': 'SCALAR'}

        this_accessor = {f'Object_Number_{current_object_number}':
                         {'AccPos': this_object_accessor_position, 'AccNor': this_object_accessor_normal, 
                          'AccTex': this_object_accessor_textcoord, 'AccCol': this_object_accessor_color_0, 
                          'AccVInd': this_object_accessor_vertex_indices}}
        
        return this_accessor

    def tmd_to_gltf_buffer(self, primitives_to_process=dict, vertex_array=dict, normal_array=dict, object_info=dict) -> dict[bytes, list]:
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
        buffers_this_object: dict[bytes, list] = {}

        obj_vertex_buffer: list = [] # Came from the Original TMD Vertex Array
        obj_normal_buffer: list = [] # Came from TMD Normal Array [Index are not used, use Normal array instead]
        obj_vindex_buffer: list = [] # Came from TMD Primitive IndexVertex Array
        obj_uv_buffer: list = [] # Came from TMD Primitive UV Array
        obj_color_buffer: list = [] # Came from TMD Primitive Color Array

        vertex_count: int = 0
        normal_count: int = 0

        vertex_count = object_info.get('VertexNumber')
        normal_count = object_info.get('NormalNumber')
        # With this hacky thing i avoid having 0 normals at Normal Count... Sorry Monoxide :')
        # TODO: WHAT's GOING ON WITH THIS SHITTY NORMALS???
        if normal_count != vertex_count:
            normal_count = vertex_count
        
        for vertex in vertex_array:
            get_this_vertex = vertex_array.get(f'{vertex}')
            vertex_array_0_32bit = numpy.array([get_this_vertex.get('VecX'), get_this_vertex.get('VecY'), get_this_vertex.get('VecZ')], dtype="float32")
            vertex_array_0_bin = vertex_array_0_32bit.tobytes()
            obj_vertex_buffer.append(vertex_array_0_bin)
        
        for normal in normal_array:
            get_this_normal = normal_array.get(f'{normal}')
            normal_array_0_32bit = numpy.array([(get_this_normal.get('VecX') / 4096), get_this_normal.get('VecY') / 4096, get_this_normal.get('VecZ') / 4096], dtype="float32")
            normal_array_0_bin = normal_array_0_32bit.tobytes()
            obj_normal_buffer.append(normal_array_0_bin)
        
        if len(obj_normal_buffer) < vertex_count:
            obj_normal_buffer = obj_normal_buffer[0:1] * vertex_count
 
        self.vertex_index_this_obj: list = []
        self.vertex_uv_this_obj: dict = {}
        self.vertex_color_this_obj: dict = {}
        for current_primitive_tmd in primitives_to_process:
            this_primitive_data = primitives_to_process.get(f'{current_primitive_tmd}')
            for primitive_type in this_primitive_data:
                getting_data = this_primitive_data.get(f'{primitive_type}')
                if f'4Vertex' in primitive_type:
                    two_triangles = self.quad_to_tri(prim_data=getting_data)
                    triangle_0 = two_triangles[0]
                    triangle_1 = two_triangles[1]
                    self.create_buffer_triangle(triangle_data=triangle_0)
                    self.create_buffer_triangle(triangle_data=triangle_1)
                else:
                    self.create_buffer_triangle(triangle_data=getting_data)
        
        vertex_index_count = 0
        for this_vertex_index in self.vertex_index_this_obj:
            # Convert the Vertex Indices as SCALAR [Unsigned INT 16 Bit] - Vertex Index
            vi_0_binary = int.to_bytes(this_vertex_index[0], length=2, byteorder='little', signed=False)
            vi_1_binary = int.to_bytes(this_vertex_index[1], length=2, byteorder='little', signed=False)
            vi_2_binary = int.to_bytes(this_vertex_index[2], length=2, byteorder='little', signed=False)
            vertex_index_array = [vi_0_binary, vi_1_binary, vi_2_binary]
            final_vertex_index = b''.join(vertex_index_array)
            obj_vindex_buffer.append(final_vertex_index)
            vertex_index_count += 3
        
        length_vertex_uv_obj = len(self.vertex_uv_this_obj)
        init_uv_list = [None] * length_vertex_uv_obj
        for this_vertex_uv in self.vertex_uv_this_obj:
            # Convert the UV Data into VEC2 [32 Bit Float]
            get_uv = self.vertex_uv_this_obj.get(f'{this_vertex_uv}')
            convert_index_int = int(this_vertex_uv)
            u_32bit = numpy.array([get_uv[0]], dtype="float32")
            v_32bit = numpy.array([get_uv[1]], dtype="float32")
            u_bin = u_32bit.tobytes()
            v_bin = v_32bit.tobytes()
            uv_bin = [u_bin, v_bin]
            join_uv = b''.join(uv_bin)
            init_uv_list[convert_index_int] = join_uv
        obj_uv_buffer = init_uv_list
        
        length_vertex_color_obj = len(self.vertex_color_this_obj)
        init_color_list = [None] * length_vertex_color_obj
        for this_vertex_color in self.vertex_color_this_obj:
            # Convert the Color Data into VEC4 [32 Bit Float]
            get_color = self.vertex_color_this_obj.get(f'{this_vertex_color}')
            convert_color_index_int = int(this_vertex_color)
            r_32bit = numpy.array([get_color[0]], dtype="float32")
            g_32bit = numpy.array([get_color[1]], dtype="float32")
            b_32bit = numpy.array([get_color[2]], dtype="float32")
            alpha_32bit = numpy.array([1.0], dtype="float32")
            r_bin = r_32bit.tobytes()
            g_bin = g_32bit.tobytes()
            b_bin = b_32bit.tobytes()
            alpha_bin = alpha_32bit.tobytes()
            rgb_bin = [r_bin, g_bin, b_bin, alpha_bin]
            join_rgba = b''.join(rgb_bin)
            init_color_list[convert_color_index_int] = join_rgba
        obj_color_buffer = init_color_list

        # Joining the data
        final_vertex_buffer = b''.join(obj_vertex_buffer)
        final_normal_buffer = b''.join(obj_normal_buffer)
        final_uv_buffer = b''.join(obj_uv_buffer)
        final_color_buffer = b''.join(obj_color_buffer)
        final_vindex_buffer = b''.join(obj_vindex_buffer)

        final_vertex_b_len = len(final_vertex_buffer)
        final_normal_b_len = len(final_normal_buffer)
        final_uv_b_len = len(final_uv_buffer)
        final_color_b_len = len(final_color_buffer)
        final_vindex_b_len = len(final_vindex_buffer)

        pad_value = b'\x00\x00\x00\x00'
        pad_value_short = b'\x00'

        if self.check_if_multiple(mul=final_vertex_b_len, base=4) == False:
            padding_multiply = self.closest_multiple(mul=final_vertex_b_len, base=4)
            add_this_pad = [final_vertex_buffer, pad_value * padding_multiply]
            final_vertex_buffer = b''.join(add_this_pad)
            final_vertex_b_len = len(final_vertex_buffer)
            print("Adding PAD to Vertex Array")
        
        if self.check_if_multiple(mul=final_normal_b_len, base=4) == False:
            padding_multiply = self.closest_multiple(mul=final_normal_b_len, base=4)
            add_this_pad = [final_normal_buffer, pad_value * padding_multiply]
            final_normal_buffer = b''.join(add_this_pad)
            final_normal_b_len = len(final_normal_buffer)
            print("Adding PAD to Normal Array")
        
        if self.check_if_multiple(mul=final_uv_b_len, base=4) == False:
            padding_multiply = self.closest_multiple(mul=final_uv_b_len, base=4)
            add_this_pad = [final_uv_buffer, pad_value * padding_multiply]
            final_uv_buffer = b''.join(add_this_pad)
            final_uv_b_len = len(final_uv_buffer)
            print("Adding PAD to UV Array")
        
        if self.check_if_multiple(mul=final_color_b_len, base=4) == False:
            padding_multiply = self.closest_multiple(mul=final_color_b_len, base=4)
            add_this_pad = [final_color_buffer, pad_value * padding_multiply]
            final_color_buffer = b''.join(add_this_pad)
            final_color_b_len = len(final_color_buffer)
            print("Adding PAD to Color Array")

        if self.check_if_multiple(mul=final_vindex_b_len, base=4) == False:
            padding_multiply = self.closest_multiple(mul=final_vindex_b_len, base=4)
            add_this_pad = [final_vindex_buffer, pad_value_short * padding_multiply]
            final_vindex_buffer = b''.join(add_this_pad)
            final_vindex_b_len = len(final_vindex_buffer)
            print("Adding PAD to Vertex Index Array")

        buffers_compiled: list = [final_vertex_buffer, final_normal_buffer, final_uv_buffer, final_color_buffer, final_vindex_buffer]
        final_buffers_compiled = b''.join(buffers_compiled)
        """Counts will be in this order: VertexCount, NormalCount, Vec3Count, ScalarCount"""
        count_elements_list: list = [vertex_count, normal_count, vertex_index_count]

        # Need to work on Elements offset to send it to the BufferView
        buffer_element_sizes: list = [final_vertex_b_len, final_normal_b_len, final_uv_b_len, final_color_b_len, final_vindex_b_len]

        buffers_this_object = {'CompiledBuffers': final_buffers_compiled, 'Counts': count_elements_list, 'BuffersSizes': buffer_element_sizes}
        
        return buffers_this_object

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
        
        triangle_0 = {'vertex0': vertex_index_2, 'vertex1': vertex_index_1, 'vertex2': vertex_index_0,
                      'normal0': normal_index_2, 'normal1': normal_index_1, 'normal2': normal_index_0, 
                      'u0': u0, 'v0': v0, 'u1': u1, 'v1': v1, 'u2': u2, 'v2': v2, 
                      'r0': r0, 'g0': g0, 'b0': b0, 'r1': r1, 'g1': g1, 'b1': b1, 'r2': r2, 'g2': g2, 'b2': b2}
        
        triangle_1 = {'vertex0': vertex_index_1, 'vertex1': vertex_index_2, 'vertex2': vertex_index_3,
                      'normal0': normal_index_1, 'normal1': normal_index_2, 'normal2': normal_index_3, 
                      'u0': u1, 'v0': v1, 'u1': u2, 'v1': v2, 'u2': u3, 'v2': v3, 
                      'r0': r1, 'g0': g1, 'b0': b1, 'r1': r2, 'g1': g2, 'b1': b2, 'r2': r3, 'g2': g3, 'b2': b3}

        return triangle_0, triangle_1

    def create_buffer_triangle(self, triangle_data=dict) -> None:
        """
        Create Buffer Triangle:\n
        will take a single Triangle Data to convert into Buffers,\n
        adjust the data and write the buffers as Bytes
        """
        """
        At the moment there is no value empty, so even if a triangle
        have no normal, uv or color, will be fill with default values
        WARNING: USING THE SAME VERTEX INDEX FOR NORMAL, there is a difference???
        """
        vertex_index_0 = triangle_data.get('vertex0')
        vertex_index_1 = triangle_data.get('vertex1')
        vertex_index_2 = triangle_data.get('vertex2')

        u0 = triangle_data.get('u0')
        v0 = triangle_data.get('v0')
        u1 = triangle_data.get('u1')
        v1 = triangle_data.get('v1')
        u2 = triangle_data.get('u2')
        v2 = triangle_data.get('v2')

        r0 = triangle_data.get('r0')
        g0 = triangle_data.get('g0')
        b0 = triangle_data.get('b0')

        r1 = triangle_data.get('r1')
        g1 = triangle_data.get('g1')
        b1 = triangle_data.get('b1')

        r2 = triangle_data.get('r2')
        g2 = triangle_data.get('g2')
        b2 = triangle_data.get('b2')

        
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
        

        this_vertex_index_array = vertex_index_0, vertex_index_1, vertex_index_2
        self.vertex_index_this_obj.append(this_vertex_index_array)

        this_vertex_uv_0 = {f'{vertex_index_0}': [u0, v0]}
        this_vertex_uv_1 = {f'{vertex_index_1}': [u1, v1]}
        this_vertex_uv_2 = {f'{vertex_index_2}': [u2, v2]}

        self.vertex_uv_this_obj.update(this_vertex_uv_0)
        self.vertex_uv_this_obj.update(this_vertex_uv_1)
        self.vertex_uv_this_obj.update(this_vertex_uv_2)

        this_vertex_color_0 = {f'{vertex_index_0}': [r0 / 256, g0 / 256, b0 / 256]}
        this_vertex_color_1 = {f'{vertex_index_1}': [r1 / 256, g1 / 256, b1 / 256]}
        this_vertex_color_2 = {f'{vertex_index_2}': [r2 / 256, g2 / 256, b2 / 256]}

        self.vertex_color_this_obj.update(this_vertex_color_0)
        self.vertex_color_this_obj.update(this_vertex_color_1)
        self.vertex_color_this_obj.update(this_vertex_color_2)

    def generate_bufferview(self, bv_current_size_array=int, bv_elements_sizes=list) -> dict:
        """
        Generate BufferView:\n
        Generate BufferView Data from previous full size of array and each element size
        """
        object_buffer_view: dict = {}

        internal_offset = bv_current_size_array
        accessor_number = 0
        for bv_element in bv_elements_sizes:
            current_target = 0
            if (accessor_number == 4):
                current_target = 34963
            else:
                current_target = 34962
            
            buffer = 0
            byte_length = bv_element
            byte_offset = internal_offset
            target = current_target

            this_buffer_view: dict = {f'BufferView_{accessor_number}': 
                                      {'buffer': buffer, 'byteLength': byte_length, 'byteOffset': byte_offset, 'target': target}}

            object_buffer_view.update(this_buffer_view)

            internal_offset += bv_element
            accessor_number += 1

        return object_buffer_view

    def check_if_multiple(self, mul=int, base=int) -> bool:
        """
        Check if Multiple:\n
        Check if a value is multiple of base number.
        """
        checking_bool: bool = False
        if mul % base == 0:
            checking_bool = True
        else:
            checking_bool = False

        return checking_bool
    
    def closest_multiple(self, mul=int, base=int) -> int:
        """
        Closest Multiple:\n
        Check the closest upper value taking in care a base number.
        """
        calculate_bigger = int(math.ceil(mul / base) * base)
        multiple = calculate_bigger - mul

        return multiple

