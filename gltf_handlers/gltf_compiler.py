"""

glTF Compiler: this module will take the converted data,
and re-arrage for later being converted into glTF Files.

Copyright (C) 2024 DooMMetaL

"""

import gc

class NewModel:
    def __init__(self, model_data=dict, animation_data=dict | None) -> None:
        self.model_data = model_data
        self.animation_data = animation_data
        self.gltf_format: dict = {}
        self.model_arrager()
    
    def model_arrager(self) -> None:
        gltf_descriptor_data: dict = {}
        gltf_to_binary_data: dict = {}

        tmd_model_data = self.model_data.get(f'Converted_Data')
        tmd_model_objects_number = len(self.model_data.get(f'Data_Table'))

        for tmd_object_number in range(0, tmd_model_objects_number):
            get_this_object = tmd_model_data.get(f'Object_Number_{tmd_object_number}')
            get_vertex_this_object = get_this_object.get(f'Vertex')
            get_normal_this_object = get_this_object.get(f'Normal')
            get_primitives_this_object = get_this_object.get(f'Primitives')
            processes_primitives_to_gltf = self.primitive_tmd_to_gltf(primitives_to_process=get_primitives_this_object)
            primitives_gltf = processes_primitives_to_gltf[0]
            uv_buffers = processes_primitives_to_gltf[1]
            color_buffers = processes_primitives_to_gltf[2]

            descriptor_json: dict = {f'Object_Number_{tmd_object_number}': primitives_gltf}
            buffers: dict = {'Vertices': get_vertex_this_object, 'Normals': get_normal_this_object, 'UV': uv_buffers, 'Color': color_buffers}
            to_compile_binary: dict = {f'Object_Number_{tmd_object_number}': buffers}
            gltf_descriptor_data.update(descriptor_json)
            gltf_to_binary_data.update(to_compile_binary)
        
        del self.model_data
        del self.animation_data
        gc.collect()
        
        self.gltf_format = {'Descriptor': gltf_descriptor_data, 'Buffers': gltf_to_binary_data}
    
    def primitive_tmd_to_gltf(self, primitives_to_process=dict) -> tuple[dict, dict, dict]:
        """
        Primitive TMD to glTF:\n
        Convert a TMD Primitive into a glTF Primitive Type.\n
        Also split the UV and Color data from the TMD Primitive to form an Array.
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
        # VERY BIG TODO: NEED TO SUPER SPLIT MORE AND MORE THIS
        gltf_primitives: dict = {}
        uv_buffer_dict: dict = {}
        color_buffer_dict: dict = {}
        this_index = 0
        for this_new_primitive in new_primitives:
            get_attributes = new_primitives.get(f'{this_new_primitive}')
            adjust_attributes = self.adjust_attributes(attributes=get_attributes, current_index=this_index)
            this_adjusted_attributes = adjust_attributes[0]
            this_uv_buffer = adjust_attributes[1]
            this_color_buffer = adjust_attributes[2]

            this_gltf_primitive = {f'{this_new_primitive}': this_adjusted_attributes}
            gltf_primitives.update(this_gltf_primitive)

            single_line_uv_buffer = {f'{this_new_primitive}': this_uv_buffer}
            uv_buffer_dict.update(single_line_uv_buffer)

            single_line_color_buffer = {f'{this_new_primitive}': this_color_buffer}
            color_buffer_dict.update(single_line_color_buffer)

            this_index += 1

        return gltf_primitives, uv_buffer_dict, color_buffer_dict
    
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
        
        new_primitive_2 = {'vertex0': vertex_index_1, 'vertex1': vertex_index_2, 'vertex2': vertex_index_3, 
                           'normal0': normal_index_1, 'normal1': normal_index_2, 'normal2': normal_index_3, 
                           'u_0': u_1, 'v_0': v_1, 'u_1': u_2, 'v_1': v_2, 'u_2': u_3, 'v_2': v_3, 
                           'r0': r_1, 'g0': g_1, 'b0': b_1, 'r1': r_2, 'g1': g_2, 'b1': b_2, 'r2': r_3, 'g2': g_3, 'b2': b_3}

        return new_primitive_1, new_primitive_2

    def adjust_attributes(self, attributes=dict, current_index=int) -> tuple[dict, list, list]:
        """
        Adjust Attributes:\n
        Will take all the Primitives attributes and do the last re-shaping to work according to glTF Format\n
        after this conversion, the original dict will stop to be used and create a new one with only the Indices for Data.\n
        Also will split the UV and Color data into two list to be send to the Binary Compiler.
        """
        adjusted_primitive: dict = {}
        uv_attribute: list = []
        color_attribute: list = []

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
        
        adjusted_primitive = {'vertex0': get_vertex_0, 'vertex1': get_vertex_1, 'vertex2': get_vertex_2, 
                              'normal0': get_normal_0, 'normal1': get_normal_1, 'normal2': get_normal_2, 
                              'TextureIndex': current_index, 'ColorIndex': current_index}

        uv_attribute = [u_0, v_0, u_1, v_1, u_2, v_2]
        color_attribute = [r_0, g_0, b_0, r_1, g_1, b_1, r_2, g_2, b_2]

        return adjusted_primitive, uv_attribute, color_attribute

