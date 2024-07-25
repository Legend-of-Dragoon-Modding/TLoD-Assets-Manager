"""

glTF Compiler: this module will take the converted data,
and re-arrage for later being converted into glTF Files.

Copyright (C) 2024 DooMMetaL

"""

class NewModel:
    def __init__(self, model_data=dict, animation_data=dict | None) -> None:
        self.model_data = model_data
        self.animation_data = animation_data
        self.gltf_format: dict = {}
        self.model_arrager()
    
    def model_arrager(self) -> None:
        gltf_data: dict = {}

        tmd_model_data = self.model_data.get(f'Converted_Data')
        tmd_model_objects_number = len(self.model_data.get(f'Data_Table'))

        for tmd_object_number in range(0, tmd_model_objects_number):
            get_this_object = tmd_model_data.get(f'Object_Number_{tmd_object_number}')
            get_vertex_this_object = get_this_object.get(f'Vertex')
            get_normal_this_object = get_this_object.get(f'Normal')
            get_primitives_this_object = get_this_object.get(f'Primitives')
            processes_primitives_to_gltf = self.primitive_tmd_to_gltf(primitives_to_process=get_primitives_this_object)
    
    def primitive_tmd_to_gltf(self, primitives_to_process=dict) -> dict:
        """
        Primitive TMD to glTF:\n
        Convert a TMD Primitive into a glTF Primitive Type\n
        """
        new_primitives: dict = {}

        for current_primitive in primitives_to_process:
            get_primitive_nest = primitives_to_process.get(f'{current_primitive}')
            recompiled_primitives: dict = {}
            for primitive_type in get_primitive_nest:
                if '4Vertex' in primitive_type:
                    # TODO Convert from TMD to glTF
                    this_primitive = get_primitive_nest.get(f'{primitive_type}')
                    # First we split the Quads into Triangles, so glTF Primitive Format is achieved
                    split_primitive = self.split_quad_primitive(primitive_properties=this_primitive, primitive_type=primitive_type)
                else:
                    # TODO Convert from TMD to glTF
                    this_non_change_primitive = get_primitive_nest.get(f'{primitive_type}')
                    final_primitive = {f'{primitive_type}': this_non_change_primitive}
                    recompiled_primitives.update(final_primitive)
            
            final_primitive_compilation: dict = {f'{current_primitive}': recompiled_primitives}
            new_primitives.update(final_primitive_compilation)

        print(new_primitives)
        return new_primitives
    
    def split_quad_primitive(self, primitive_properties=dict, primitive_type=str) -> dict:
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
        
        if normal_index_0 == None:
            normal_index_0 = 0
            normal_index_1 = 0
            normal_index_2 = 0
            normal_index_3 = 0
        
        if u_0 == None:
            u_0 = 0.0
            v_0 = 0.0
            u_1 = 0.0
            v_1 = 0.0
            u_2 = 0.0
            v_2 = 0.0
            u_3 = 0.0
            v_3 = 0.0
        
        if (r_0 == None) and (b_3 == None):
            r_0 = 0
            g_0 = 0
            b_0 = 0
            r_1 = 0
            g_1 = 0
            b_1 = 0
            r_2 = 0
            g_2 = 0
            b_2 = 0
            r_3 = 0
            g_3 = 0
            b_3 = 0



        return new_primitive_1, new_primitive_2