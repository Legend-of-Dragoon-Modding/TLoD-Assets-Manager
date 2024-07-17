"""

Collada Compiler:
Compile a processed Model Data into DAE (Digital Asset Exchange - Collaborative - Collada) format
to later been write into a dae file, you'll see some balancing act, because TLoD Models Format
and DAE Format shares some similitudes, but also are pretty different in other terms.
--------------------------------------------------------------------------------------------------------------
Input Data: Processed Model Data DICT, previous data processed by the tools
--------------------------------------------------------------------------------------------------------------
:RETURN: -> self.compiled_collada_data = {}
--------------------------------------------------------------------------------------------------------------
Copyright (C) 2024 DooMMetaL

"""
from PyQt6.QtWidgets import QMessageBox

class ColladaFileFormat:
    def __init__(self, processed_model_data=dict) -> None:
        self.compiled_collada_data: dict = {}
        self.total_objects: dict = {}
        self.total_primitives: dict = {}
        self.processed_model_data = processed_model_data
        self.compile_collada_format()
    
    def compile_collada_format(self) -> None:
        total_number_objects = len(self.processed_model_data.get('Data_Table'))
        model_data_get = self.processed_model_data.get('Converted_Data')
        vertex_data_get = model_data_get.get(f'Vertex_Data')
        normal_data_get = model_data_get.get(f'Normal_Data')
        primitive_data_get = model_data_get.get(f'Primitive_Data')

        get_data_table = self.processed_model_data.get('Data_Table')
        for object_name in get_data_table:
            this_object_table = get_data_table.get(f'{object_name}')
            this_primitives_in_object = this_object_table.get(f'PrimitiveNumber')
            self.total_primitives.update({f'{object_name}': this_primitives_in_object})
        
        self.total_objects.update({'TotalObjects': total_number_objects})
        collada_compiled_data: dict = {}
        for current_object_number in range(0, total_number_objects):
            self.this_object_vertex_data = vertex_data_get.get(f'Object_Number_{current_object_number}')
            self.this_object_normal_data = normal_data_get.get(f'Object_Number_{current_object_number}')
            self.this_object_primitive_data = primitive_data_get.get(f'Object_Number_{current_object_number}')

            self.check_vertex_index_duplicates(object_number=current_object_number)

            collada_mesh_positions = self.get_collada_mesh_positions()
            collada_mesh_normals = self.get_collada_mesh_normals()
            collada_mesh_maps, collada_uv_indices = self.get_collada_mesh_maps()
            collada_mesh_colors, collada_colors_indices = self.get_collada_mesh_colors()
            
            collada_polylist_array = self.create_polylist_array(color_index=collada_colors_indices, uv_index=collada_uv_indices)

            collada_data_build = {'Positions': collada_mesh_positions, 'Normals': collada_mesh_normals, 'Maps': collada_mesh_maps, 'Colors': collada_mesh_colors, 'Polylist': collada_polylist_array}
            collada_compiled_data.update({f'Object_Number_{current_object_number}': collada_data_build})
        self.compiled_collada_data = collada_compiled_data

    def get_collada_mesh_positions(self) -> dict:
        collada_vertex_data: dict = {'MeshPositions': []}
        for this_vertex_row in self.this_object_vertex_data:
            this_vertex = self.this_object_vertex_data.get(f'{this_vertex_row}')
            get_vecx = this_vertex.get('VecX')
            get_vecy = this_vertex.get('VecY')
            get_vecz = this_vertex.get('VecZ')
            collada_vertex_data['MeshPositions'] += get_vecx, get_vecy, get_vecz
        return collada_vertex_data
    
    def get_collada_mesh_normals(self) -> dict:
        collada_normal_data: dict = {'MeshNormals': []}
        for this_normal_row in self.this_object_normal_data:
            this_vertex = self.this_object_normal_data.get(f'{this_normal_row}')
            get_vecx = this_vertex.get('VecX')
            get_vecy = this_vertex.get('VecY')
            get_vecz = this_vertex.get('VecZ')
            collada_normal_data['MeshNormals'] += get_vecx, get_vecy, get_vecz
        return collada_normal_data
    
    def get_collada_mesh_maps(self) -> tuple[dict, dict]:
        collada_mesh_maps: dict = {'MeshMaps': []}
        collada_uv_index: dict = {'UVIndex': []}
        uv_index = 0
        for this_primitive_num in self.this_object_primitive_data:
            this_primitive_data = self.this_object_primitive_data.get(f'{this_primitive_num}')
            for primitive_name in this_primitive_data:
                texture_data: tuple = ()
                if ('4Vertex' in primitive_name) and ('No-Texture' not in primitive_name):
                    prim_inner_data = this_primitive_data.get(f'{primitive_name}')
                    u1_get = prim_inner_data.get("u1")
                    v1_get = 1 - prim_inner_data.get("v1")
                    u3_get = prim_inner_data.get("u3")
                    v3_get = 1 - prim_inner_data.get("v3")
                    u2_get = prim_inner_data.get("u2")
                    v2_get = 1 - prim_inner_data.get("v2")
                    u0_get = prim_inner_data.get("u0")
                    v0_get = 1 - prim_inner_data.get("v0")
                    texture_data = u1_get, v1_get, u3_get, v3_get, u2_get, v2_get, u0_get, v0_get
                    textured_4v_index = uv_index, uv_index + 1, uv_index + 2, uv_index + 3
                    collada_uv_index['UVIndex'] += textured_4v_index
                    uv_index += 4
                elif '3Vertex' in primitive_name and ('No-Texture' not in primitive_name):
                    prim_inner_data = this_primitive_data.get(f'{primitive_name}')
                    u0_get = prim_inner_data.get("u0")
                    v0_get = 1 - prim_inner_data.get("v0")
                    u1_get = prim_inner_data.get("u1")
                    v1_get = 1 - prim_inner_data.get("v1")
                    u2_get = prim_inner_data.get("u2")
                    v2_get = 1 - prim_inner_data.get("v2")
                    texture_data = u0_get, v0_get, u1_get, v1_get, u2_get, v2_get
                    textured_3v_index = uv_index, uv_index + 1, uv_index + 2
                    collada_uv_index['UVIndex'] += textured_3v_index
                    uv_index += 3
                elif ('4Vertex' in primitive_name) and ('No-Texture' in primitive_name):
                    texture_data = 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01
                    untextured_4v_index = uv_index, uv_index + 1, uv_index + 2, uv_index + 3
                    collada_uv_index['UVIndex'] += untextured_4v_index
                    uv_index += 4
                elif ('3Vertex' in primitive_name) and ('No-Texture' in primitive_name):
                    texture_data = 0.01, 0.01, 0.01, 0.01, 0.01, 0.01
                    untextured_3v_index = uv_index, uv_index + 1, uv_index + 2
                    collada_uv_index['UVIndex'] += untextured_3v_index
                    uv_index += 3
                else:
                    primitive_type_error_uv = f'Primitive Type: {primitive_name}, not catch for UV Mapping!!'
                    prim_type_error_uv_messagebox = QMessageBox.critical(None, 'CRITICAL ERROR!!', f'{primitive_type_error_uv}', QMessageBox.StandardButton.Ok)
                    exit()
                collada_mesh_maps['MeshMaps'] += texture_data
        return collada_mesh_maps, collada_uv_index
    
    def get_collada_mesh_colors(self) -> tuple[dict, dict]:
        collada_mesh_colors: dict = {'MeshColors': []}
        collada_colors_indices: dict = {'ColorIndex': []}
        """Collada format seems to handle transparency in Colored surface, have to research how this really works"""
        color_indices_list: list = []
        color_number = 0
        for this_primitive_num in self.this_object_primitive_data:
            this_primitive_data = self.this_object_primitive_data.get(f'{this_primitive_num}')
            for primitive_name in this_primitive_data:
                color_data: tuple = ()
                get_this_primitive_data = this_primitive_data.get(f'{primitive_name}')
                if ('4Vertex' in primitive_name) and (get_this_primitive_data.get("r3") != None) and (get_this_primitive_data.get("b3") != None): # Gradation 4 Vertex
                    alpha_value = 1
                    r0_get = get_this_primitive_data.get(f'r0') / 256
                    g0_get = get_this_primitive_data.get(f'g0') / 256
                    b0_get = get_this_primitive_data.get(f'b0') / 256
                    r1_get = get_this_primitive_data.get(f'r1') / 256
                    g1_get = get_this_primitive_data.get(f'g1') / 256
                    b1_get = get_this_primitive_data.get(f'b1') / 256
                    r2_get = get_this_primitive_data.get(f'r2') / 256
                    g2_get = get_this_primitive_data.get(f'g2') / 256
                    b2_get = get_this_primitive_data.get(f'b2') / 256
                    r3_get = get_this_primitive_data.get(f'r3') / 256
                    g3_get = get_this_primitive_data.get(f'g3') / 256
                    b3_get = get_this_primitive_data.get(f'b3') / 256
                    color_data = r0_get, g0_get, b0_get, alpha_value, r2_get, g2_get, b2_get, alpha_value, r3_get, g3_get, b3_get, alpha_value, r1_get, g1_get, b1_get, alpha_value
                    collada_mesh_colors['MeshColors'] += color_data
                    color_index_0 = color_number + 3
                    color_index_1 = color_number + 2
                    color_index_2 = color_number + 1
                    color_index_3 = color_number
                    color_indices_list.append(color_index_0)
                    color_indices_list.append(color_index_1)
                    color_indices_list.append(color_index_2)
                    color_indices_list.append(color_index_3)
                    color_number += 4
                elif ('4Vertex' in primitive_name) and (get_this_primitive_data.get("r0") != None) and (get_this_primitive_data.get("b0") != None): # FLAT 4 Vertex
                    alpha_value = 1
                    r0_get = get_this_primitive_data.get(f'r0') / 256
                    g0_get = get_this_primitive_data.get(f'g0') / 256
                    b0_get = get_this_primitive_data.get(f'b0') / 256
                    color_data = r0_get, g0_get, b0_get, alpha_value, r0_get, g0_get, b0_get, alpha_value, r0_get, g0_get, b0_get, alpha_value, r0_get, g0_get, b0_get, alpha_value
                    collada_mesh_colors['MeshColors'] += color_data
                    color_index_0 = color_number + 3
                    color_index_1 = color_number + 2
                    color_index_2 = color_number + 1
                    color_index_3 = color_number
                    color_indices_list.append(color_index_0)
                    color_indices_list.append(color_index_1)
                    color_indices_list.append(color_index_2)
                    color_indices_list.append(color_index_3)
                    color_number += 4
                elif ('3Vertex' in primitive_name) and (get_this_primitive_data.get("r2") != None) and (get_this_primitive_data.get("b2") != None): # Gradation 3 Vertex
                    alpha_value = 1
                    r0_get = get_this_primitive_data.get(f'r0') / 256
                    g0_get = get_this_primitive_data.get(f'g0') / 256
                    b0_get = get_this_primitive_data.get(f'b0') / 256
                    r1_get = get_this_primitive_data.get(f'r1') / 256
                    g1_get = get_this_primitive_data.get(f'g1') / 256
                    b1_get = get_this_primitive_data.get(f'b1') / 256
                    r2_get = get_this_primitive_data.get(f'r2') / 256
                    g2_get = get_this_primitive_data.get(f'g2') / 256
                    b2_get = get_this_primitive_data.get(f'b2') / 256
                    color_data = r2_get, g2_get, b2_get, alpha_value, r1_get, g1_get, b1_get, alpha_value, r0_get, g0_get, b0_get, alpha_value
                    collada_mesh_colors['MeshColors'] += color_data
                    color_index_0 = color_number + 2
                    color_index_1 = color_number + 1
                    color_index_2 = color_number
                    color_indices_list.append(color_index_0)
                    color_indices_list.append(color_index_1)
                    color_indices_list.append(color_index_2)
                    color_number += 3
                elif ('3Vertex' in primitive_name) and (get_this_primitive_data.get("r0") != None) and (get_this_primitive_data.get("b0") != None): # FLAT 3 Vertex
                    alpha_value = 1
                    r0_get = get_this_primitive_data.get(f'r0') / 256
                    g0_get = get_this_primitive_data.get(f'g0') / 256
                    b0_get = get_this_primitive_data.get(f'b0') / 256
                    color_data = r0_get, g0_get, b0_get, alpha_value, r0_get, g0_get, b0_get, alpha_value, r0_get, g0_get, b0_get, alpha_value
                    collada_mesh_colors['MeshColors'] += color_data
                    color_index_0 = color_number + 2
                    color_index_1 = color_number + 1
                    color_index_2 = color_number
                    color_indices_list.append(color_index_0)
                    color_indices_list.append(color_index_1)
                    color_indices_list.append(color_index_2)
                    color_number += 3
                elif ('4Vertex' in primitive_name) and (get_this_primitive_data.get("r0") == None): # Fully Textured FLAT 4 Vertex
                    color_data = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1
                    collada_mesh_colors['MeshColors'] += color_data
                    color_index_0 = color_number + 3
                    color_index_1 = color_number + 2
                    color_index_2 = color_number + 1
                    color_index_3 = color_number
                    color_indices_list.append(color_index_0)
                    color_indices_list.append(color_index_1)
                    color_indices_list.append(color_index_2)
                    color_indices_list.append(color_index_3)
                    color_number += 4
                elif ('3Vertex' in primitive_name) and (get_this_primitive_data.get("r0") == None): # Fully Textured FLAT 3 Vertex
                    color_data = 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1
                    collada_mesh_colors['MeshColors'] += color_data
                    color_index_0 = color_number + 2
                    color_index_1 = color_number + 1
                    color_index_2 = color_number
                    color_indices_list.append(color_index_0)
                    color_indices_list.append(color_index_1)
                    color_indices_list.append(color_index_2)
                    color_number += 3
                else:
                    primitive_type_error_colors = f'Primitive Type: {primitive_name}, not catch for Colors!!'
                    prim_type_error_colors_messagebox = QMessageBox.critical(None, 'CRITICAL ERROR!!', f'{primitive_type_error_colors}', QMessageBox.StandardButton.Ok)
                    exit()
        collada_colors_indices.update({'ColorIndex': color_indices_list})
        return collada_mesh_colors, collada_colors_indices
    
    def create_polylist_array(self, color_index=dict, uv_index=dict) -> dict:
        polylist_array: dict = {'VCount': [], 'P-Array': []}
        #POLYLIST -  P ARRAY - sorting: vertex_index, normal_index, texcoord (uv), color_index
        this_color_index = color_index.get(f'ColorIndex')
        this_uv_index = uv_index.get(f'UVIndex')
        current_index = 0
        count_vertex_number_list: list = []
        for this_primitive in self.this_object_primitive_data:
            primitive_data_get = self.this_object_primitive_data.get(f'{this_primitive}')
            total_p_array: tuple = ()
            for primitive_type in primitive_data_get:
                primitive_inner_data = primitive_data_get.get(f'{primitive_type}')
                if ('4Vertex' in primitive_type) and (primitive_inner_data.get('normal3') != None):
                    vertex_index_0 = primitive_inner_data.get('vertex1')
                    normal_index_0 = primitive_inner_data.get('normal1')
                    uv_index_0 = this_uv_index[current_index]
                    color_index_0 = this_color_index[current_index]
                    vertex_index_1 = primitive_inner_data.get('vertex3')
                    normal_index_1 = primitive_inner_data.get('normal3')
                    uv_index_1 = this_uv_index[current_index + 1]
                    color_index_1 = this_color_index[current_index + 1]
                    vertex_index_2 = primitive_inner_data.get('vertex2')
                    normal_index_2 = primitive_inner_data.get('normal2')
                    uv_index_2 = this_uv_index[current_index + 2]
                    color_index_2 = this_color_index[current_index + 2]
                    vertex_index_3 = primitive_inner_data.get('vertex0')
                    normal_index_3 = primitive_inner_data.get('normal0')
                    uv_index_3 = this_uv_index[current_index + 3]
                    color_index_3 = this_color_index[current_index + 3]
                    total_p_array = vertex_index_0, normal_index_0, uv_index_0, color_index_0, vertex_index_1, normal_index_1, uv_index_1, color_index_1, vertex_index_2, normal_index_2, uv_index_2, color_index_2, vertex_index_3, normal_index_3, uv_index_3, color_index_3
                    polylist_array['P-Array'] += total_p_array
                    current_index += 4
                    count_vertex_number_list.append(4)
                elif ('3Vertex' in primitive_type)and (primitive_inner_data.get('normal3') != None):
                    vertex_index_0 = primitive_inner_data.get('vertex0')
                    normal_index_0 = primitive_inner_data.get('normal0')
                    uv_index_0 = this_uv_index[current_index]
                    color_index_0 = this_color_index[current_index]
                    vertex_index_1 = primitive_inner_data.get('vertex1')
                    normal_index_1 = primitive_inner_data.get('normal1')
                    uv_index_1 = this_uv_index[current_index + 1]
                    color_index_1 = this_color_index[current_index + 1]
                    vertex_index_2 = primitive_inner_data.get('vertex2')
                    normal_index_2 = primitive_inner_data.get('normal2')
                    uv_index_2 = this_uv_index[current_index + 2]
                    color_index_2 = this_color_index[current_index + 2]
                    total_p_array = vertex_index_0, normal_index_0, uv_index_0, color_index_0, vertex_index_1, normal_index_1, uv_index_1, color_index_1, vertex_index_2, normal_index_2, uv_index_2, color_index_2
                    polylist_array['P-Array'] += total_p_array
                    current_index += 3
                    count_vertex_number_list.append(3)
                elif ('4Vertex' in primitive_type) and (primitive_inner_data.get('normal3') == None):
                    vertex_index_0 = primitive_inner_data.get('vertex1')
                    normal_index_0 = 0
                    uv_index_0 = this_uv_index[current_index]
                    color_index_0 = this_color_index[current_index]
                    vertex_index_1 = primitive_inner_data.get('vertex3')
                    normal_index_1 = 0
                    uv_index_1 = this_uv_index[current_index + 1]
                    color_index_1 = this_color_index[current_index + 1]
                    vertex_index_2 = primitive_inner_data.get('vertex2')
                    normal_index_2 = 0
                    uv_index_2 = this_uv_index[current_index + 2]
                    color_index_2 = this_color_index[current_index + 2]
                    vertex_index_3 = primitive_inner_data.get('vertex0')
                    normal_index_3 = 0
                    uv_index_3 = this_uv_index[current_index + 3]
                    color_index_3 = this_color_index[current_index + 3]
                    total_p_array = vertex_index_0, normal_index_0, uv_index_0, color_index_0, vertex_index_1, normal_index_1, uv_index_1, color_index_1, vertex_index_2, normal_index_2, uv_index_2, color_index_2, vertex_index_3, normal_index_3, uv_index_3, color_index_3
                    polylist_array['P-Array'] += total_p_array
                    current_index += 4
                    count_vertex_number_list.append(4)
                elif ('3Vertex' in primitive_type)and (primitive_inner_data.get('normal3') == None):
                    vertex_index_0 = primitive_inner_data.get('vertex0')
                    normal_index_0 = 0
                    uv_index_0 = this_uv_index[current_index]
                    color_index_0 = this_color_index[current_index]
                    vertex_index_1 = primitive_inner_data.get('vertex1')
                    normal_index_1 = 0
                    uv_index_1 = this_uv_index[current_index + 1]
                    color_index_1 = this_color_index[current_index + 1]
                    vertex_index_2 = primitive_inner_data.get('vertex2')
                    normal_index_2 = 0
                    uv_index_2 = this_uv_index[current_index + 2]
                    color_index_2 = this_color_index[current_index + 2]
                    total_p_array = vertex_index_0, normal_index_0, uv_index_0, color_index_0, vertex_index_1, normal_index_1, uv_index_1, color_index_1, vertex_index_2, normal_index_2, uv_index_2, color_index_2
                    polylist_array['P-Array'] += total_p_array
                    current_index += 3
                    count_vertex_number_list.append(3)
        polylist_array.update({'VCount': count_vertex_number_list})
        return polylist_array
    
    def check_vertex_index_duplicates(self, object_number=int) -> None:
        # AT THE MOMENT ADD A COLOR DUPLICATION SEEMS TO BE OVERKILL
        vertex_index_to_check: list = []
        primitives_to_replacement: list = []
        for this_primitive_num in self.this_object_primitive_data:
            this_primitive_data = self.this_object_primitive_data.get(f'{this_primitive_num}')
            for primitive_name in this_primitive_data:
                get_primitive_inner_data = this_primitive_data.get(f'{primitive_name}')
                if '4Vertex' in primitive_name:
                    vertex_4v_array = get_primitive_inner_data.get(f'vertex1'), get_primitive_inner_data.get(f'vertex3'), get_primitive_inner_data.get(f'vertex2'), get_primitive_inner_data.get(f'vertex0')
                    vertex_index_to_check.append(vertex_4v_array)
                    primitive_to_replace = this_primitive_num, primitive_name
                    primitives_to_replacement.append(primitive_to_replace)
                else:
                    vertex_3v_array = get_primitive_inner_data.get(f'vertex0'), get_primitive_inner_data.get(f'vertex1'), get_primitive_inner_data.get(f'vertex2')
                    vertex_index_to_check.append(vertex_3v_array)
                    primitive_to_replace = this_primitive_num, primitive_name
                    primitives_to_replacement.append(primitive_to_replace)
        
        compare_this_vertex_index = vertex_index_to_check
        set_this_to_compare = set(vertex_index_to_check)
        if len(set_this_to_compare) != len(compare_this_vertex_index):
            print(f'Object number: {object_number} ==> Duplicated Indices in a Primitive Found!, we must change some values to prevent automatic removing of them in 3D Softwares')

            get_index_repeated = [index for index, item in enumerate(vertex_index_to_check) if item in vertex_index_to_check[:index]]
            vertices_index_to_set = []
            replace_here: list = []
            for index_repeat in get_index_repeated:
                this_repeat = vertex_index_to_check[index_repeat]
                this_prim_name = primitives_to_replacement[index_repeat]
                replace_here.append(this_prim_name)
                for single_vertex_index in this_repeat:
                    vertices_index_to_set.append(single_vertex_index)
            
            vertices_check_set = list(set(vertices_index_to_set))
            max_vertex = len(self.this_object_vertex_data)
            new_vertex_index: list = []
            new_index = max_vertex
            for get_this_vertex in vertices_check_set:
                copy_this_vertex = self.this_object_vertex_data.get(f'Vertex_Number_{get_this_vertex}')
                new_vertex_generated = {f'Vertex_Number_{new_index}': copy_this_vertex}
                self.this_object_vertex_data.update(new_vertex_generated)
                new_vertex_index.append(new_index)
                new_index += 1
            
            for replacement in replace_here:
                primitive_name_to_replace = replacement[0]
                primitive_type_to_replace = replacement[1]
                get_primitive_to_replace_name = self.this_object_primitive_data.get(f'{primitive_name_to_replace}')
                get_primitive_to_replace = get_primitive_to_replace_name.get(f'{primitive_type_to_replace}')
                if "4Vertex" in primitive_type_to_replace:
                    get_vertex0 = get_primitive_to_replace.get('vertex0')
                    get_vertex1 = get_primitive_to_replace.get('vertex1')
                    get_vertex2 = get_primitive_to_replace.get('vertex2')
                    get_vertex3 = get_primitive_to_replace.get('vertex3')
                    if get_vertex0 in vertices_check_set:
                        get_index_for_checked = vertices_check_set.index(get_vertex0)
                        get_new_index_from_check = new_vertex_index[get_index_for_checked]
                        get_primitive_to_replace['vertex0'] = get_new_index_from_check
                    if get_vertex1 in vertices_check_set:
                        get_index_for_checked = vertices_check_set.index(get_vertex1)
                        get_new_index_from_check = new_vertex_index[get_index_for_checked]
                        get_primitive_to_replace['vertex1'] = get_new_index_from_check
                    if get_vertex2 in vertices_check_set:
                        get_index_for_checked = vertices_check_set.index(get_vertex2)
                        get_new_index_from_check = new_vertex_index[get_index_for_checked]
                        get_primitive_to_replace['vertex2'] = get_new_index_from_check
                    if get_vertex3 in vertices_check_set:
                        get_index_for_checked = vertices_check_set.index(get_vertex3)
                        get_new_index_from_check = new_vertex_index[get_index_for_checked]
                        get_primitive_to_replace['vertex3'] = get_new_index_from_check
                elif "3Vertex" in primitive_type_to_replace:
                    get_vertex0 = get_primitive_to_replace.get('vertex0')
                    get_vertex1 = get_primitive_to_replace.get('vertex1')
                    get_vertex2 = get_primitive_to_replace.get('vertex2')
                    if get_vertex0 in vertices_check_set:
                        get_index_for_checked = vertices_check_set.index(get_vertex0)
                        get_new_index_from_check = new_vertex_index[get_index_for_checked]
                        get_primitive_to_replace['vertex0'] = get_new_index_from_check
                    if get_vertex1 in vertices_check_set:
                        get_index_for_checked = vertices_check_set.index(get_vertex1)
                        get_new_index_from_check = new_vertex_index[get_index_for_checked]
                        get_primitive_to_replace['vertex1'] = get_new_index_from_check
                    if get_vertex2 in vertices_check_set:
                        get_index_for_checked = vertices_check_set.index(get_vertex2)
                        get_new_index_from_check = new_vertex_index[get_index_for_checked]
                        get_primitive_to_replace['vertex2'] = get_new_index_from_check
        else:
            print(f'Object Number: {object_number} have no Duplicated Indices in Primitives')