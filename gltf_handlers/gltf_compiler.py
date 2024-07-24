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
                    split_primitive = self.split_quad_primitive(primitive=this_primitive)
                else:
                    # TODO Convert from TMD to glTF
                    this_non_change_primitive = get_primitive_nest.get(f'{primitive_type}')
                    final_primitive = {f'{primitive_type}': this_non_change_primitive}
                    recompiled_primitives.update(final_primitive)
            
            final_primitive_compilation: dict = {f'{current_primitive}': recompiled_primitives}
            new_primitives.update(final_primitive_compilation)

        return new_primitives
    
    def split_quad_primitive(self, primitive=dict) -> dict:
        """
        Quad to Tri:\n
        Convert a Primitive Quadrilatera into a Triangle\n
        since glTF format won't support Quads in their Primitives structure
        """
        new_primitive: dict = {}


        return new_primitive