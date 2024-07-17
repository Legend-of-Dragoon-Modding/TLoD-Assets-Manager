"""

Collada Writer:
Write a DAE (Digital Asset Exchange - Collaborative - Collada) format file
Processed previously by the Collada Compiler.
--------------------------------------------------------------------------------------------------------------
NOTE FROM ME: I know that exist PyCollada, which is a very good module to do this without much line codes,
the problem comes that you have to import NumPy and i think re-convert all data to NumPy Arrays is a little
overkill for this simple models. I really understand if you need to Convert a 10k+ Vertices models, but in
TLoD at most you have 1k Vertices models like Divine Dragon, the rest are lower to 700, doing this extra
step surely will impact in perfomance (maybe +0.5 seconds in one model, but in bulk Conversion will be a lot)
--------------------------------------------------------------------------------------------------------------
Input Data: Collada Compiled Model DICT.
--------------------------------------------------------------------------------------------------------------
:RETURN: -> None; FILE WRITE ON DISK
--------------------------------------------------------------------------------------------------------------
Copyright (C) 2024 DooMMetaL

"""
import datetime

class ColladaFile:
    def __init__(self, collada_compiled_file=dict, total_objects=dict, total_primitives=dict, animation_data=dict, deploy_file_path=str, origin_file_path=str):
        self.collada_compiled_file = collada_compiled_file
        self.total_objects = total_objects
        self.total_primitives_per_object = total_primitives
        self.animation_data = animation_data
        self.deploy_file_path = deploy_file_path
        self.origin_file_path = origin_file_path
        self.write_collada_file()
    
    def write_collada_file(self) -> None:
        date_conversion = datetime.datetime.now().isoformat(timespec='milliseconds')
        get_number_objects = self.total_objects.get('TotalObjects')
        with open(f'{self.deploy_file_path}.dae', 'w') as collada_file:
            # TOP HEADER
            technical_header = f'<?xml version="1.0" encoding="utf-8"?>\n'
            collada_header = f'<COLLADA xmlns="http://www.collada.org/2005/11/COLLADASchema" version="1.4.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n'
            # ASSET HEADER
            asset_header = f'  <asset>\n    <contributor>\n      <author>TLoD_TMD_Converter_User</author>\n      <authoring_tool>TLoD_TMD_Converter</authoring_tool>\n   <source_data>{self.origin_file_path}</source_data>\n    </contributor>\n    <created>{date_conversion}</created>\n    <modified>{date_conversion}</modified>\n    <unit name="meter" meter="1"/>\n    <up_axis>Z_UP</up_axis>\n  </asset>\n'
            colladada_total_header = technical_header + collada_header + asset_header
            collada_file.write(colladada_total_header)
            # LYBRARY_EFFECTS PROCESSING (ALMOST ALL THE STUFF HERE IS AS BLENDER DEFAULT)
            library_effect_start = f'  <library_effects>\n'
            collada_file.write(library_effect_start)
            for number_effects in range(0, get_number_objects):
                effect_loop_1 = f'    <effect id="Object_Number_{number_effects}-effect">\n      <profile_COMMON>\n        <technique sid="common">\n          <lambert>\n            <emission>\n              <color sid="emission">0 0 0 1</color>\n            </emission>\n'
                effect_loop_2 = f'            <diffuse>\n              <color sid="diffuse">0.8 0.8 0.8 1</color>\n            </diffuse>\n            <index_of_refraction>\n              <float sid="ior">1.45</float>\n            </index_of_refraction>\n'
                effect_loop_3 = f'          </lambert>\n        </technique>\n      </profile_COMMON>\n    </effect>\n'
                effect_total = effect_loop_1 + effect_loop_2 + effect_loop_3
                collada_file.write(effect_total)
            
            # LIBRARY_IMAGES/LIBRARY_MATERIALS PROCESSING (NOT IMPLEMENTED ATM, SO WILL BE BLANK!)
            library_effect_end = f'  </library_effects>\n'
            library_images_blank = f'  <library_images/>\n'
            library_materials_start = f'  <library_materials>\n'
            library_default_together = library_effect_end + library_images_blank + library_materials_start
            collada_file.write(library_default_together)
            for number_material in range(0, get_number_objects):
                material_loop = f'    <material id="Object_Number_{number_material}-material" name="Object_Number_{number_material}">\n      <instance_effect url="#Object_Number_{number_material}-effect"/>\n    </material>\n'
                collada_file.write(material_loop)
            library_materials_end = f'  </library_materials>\n'
            collada_file.write(library_materials_end)

            # LIBRARY_GEOMETRIES PROCESSING (HERE IS WHERE THE FILE GET INTERESTING)
            library_geometries_start = f'  <library_geometries>\n'
            collada_file.write(library_geometries_start)

            for current_object in self.collada_compiled_file:
                """from here i have to write each mesh as source id = Object_Number_0-mesh-positions; 
                Object_Number_0-vert-colors; Object_Number_0-mesh-normals ; Object_Number_0-mesh-map-0 ; 
                mesh-colors-Col ; Object_Number_0-mesh-vertices // polylist"""

                get_current_object_data = self.collada_compiled_file.get(f'{current_object}')
                get_positions = get_current_object_data.get(f'Positions')
                get_normals = get_current_object_data.get(f'Normals')
                get_uvs = get_current_object_data.get('Maps')
                get_colors = get_current_object_data.get('Colors')
                get_polylists = get_current_object_data.get('Polylist')

                geometry_loop_1 = f'    <geometry id="{current_object}-mesh" name="{current_object}">\n      <mesh>\n'
                collada_file.write(geometry_loop_1)
                
                # source id = Object_Number_n-mesh-positions
                get_mesh_positions = get_positions.get(f'MeshPositions')
                mesh_positions_length = len(get_mesh_positions) # full count of vertex (so 1 vertex = 3 values [x, y, z)])
                mesh_position_source_write = f'        <source id="{current_object}-mesh-positions">\n          <float_array id="{current_object}-mesh-positions-array" count="{mesh_positions_length}">'
                collada_file.write(mesh_position_source_write)
                for vector in get_mesh_positions:
                    vector_line = f'{vector} '
                    collada_file.write(vector_line)
                positions_float_array_end = f'</float_array>\n'
                collada_file.write(positions_float_array_end)
                vertex_array_length = mesh_positions_length // 3
                technique_common_loop_1 = f'          <technique_common>\n            <accessor source="#{current_object}-mesh-positions-array" count="{vertex_array_length}" stride="3">\n              <param name="X" type="float"/>\n              <param name="Y" type="float"/>\n              <param name="Z" type="float"/>\n            </accessor>\n          </technique_common>\n'
                collada_file.write(technique_common_loop_1)
                position_source_end = f'        </source>\n'
                collada_file.write(position_source_end)
            
                #  source id = Object_Number_n-mesh-normals
                get_mesh_normals = get_normals.get(f'MeshNormals')
                mesh_normals_length = len(get_mesh_normals) # full count of normals (so 1 normal = 3 values [x, y, z)])
                mesh_normals_source_write = f'        <source id="{current_object}-mesh-normals">\n          <float_array id="{current_object}-mesh-normals-array" count="{mesh_normals_length}">'
                collada_file.write(mesh_normals_source_write)
                for normal_vector in get_mesh_normals:
                    normal_vector_line = f'{normal_vector} '
                    collada_file.write(normal_vector_line)
                normals_float_array_end = f'</float_array>\n'
                collada_file.write(normals_float_array_end)
                normals_array_length = mesh_normals_length // 3
                technique_common_loop_2 = f'          <technique_common>\n            <accessor source="#{current_object}-mesh-normals-array" count="{normals_array_length}" stride="3">\n              <param name="X" type="float"/>\n              <param name="Y" type="float"/>\n              <param name="Z" type="float"/>\n            </accessor>\n          </technique_common>\n'
                collada_file.write(technique_common_loop_2)
                normals_source_end =  f'        </source>\n'
                collada_file.write(normals_source_end)

                # source id = Object_Number_0-mesh-map-0 
                mesh_maps = get_uvs.get(f'MeshMaps')
                mesh_maps_length = len(mesh_maps)
                mesh_maps_source_write = f'        <source id="{current_object}-mesh-map-0">\n          <float_array id="{current_object}-mesh-map-0-array" count="{mesh_maps_length}">'
                collada_file.write(mesh_maps_source_write)
                for vector_uv in mesh_maps:
                    line_vector_uv = f'{vector_uv} '
                    collada_file.write(line_vector_uv)
                uv_float_array_end = f'</float_array>\n'
                collada_file.write(uv_float_array_end)
                technique_common_loop_maps = f'          <technique_common>\n            <accessor source="#{current_object}-mesh-map-0-array" count="{ mesh_maps_length // 2}" stride="2">\n              <param name="S" type="float"/>\n              <param name="T" type="float"/>\n            </accessor>\n          </technique_common>\n'
                collada_file.write(technique_common_loop_maps)
                maps_source_end = f'        </source>\n'
                collada_file.write(maps_source_end)

                #  source id = Object_Number_n-vert-colors
                number_geometry_colors_find = current_object.rfind("_") # Just searching in the Object Name the number to be placed in here
                number_geometry_colors = current_object[number_geometry_colors_find + 1: ] # +1 because will take the underscore as starting point
                mesh_colors = get_colors.get('MeshColors')
                mesh_colors_length = len(mesh_colors)
                mesh_colors_source_write = f'        <source id="{current_object}-mesh-colors-Col{number_geometry_colors}" name="Col{number_geometry_colors}">\n          <float_array id="{current_object}-mesh-colors-Col{number_geometry_colors}-array" count="{mesh_colors_length}">'
                collada_file.write(mesh_colors_source_write)
                for vector_colors in mesh_colors:
                    line_vector_colors = f'{vector_colors} '
                    collada_file.write(line_vector_colors)
                colors_float_array_end = f'</float_array>\n'
                collada_file.write(colors_float_array_end)
                # TODO a very BIG TODO Need to check why the colors count is different from one to another
                technique_common_loop_colors = f'          <technique_common>\n            <accessor source="#{current_object}-mesh-colors-Col{number_geometry_colors}-array" count="{mesh_colors_length // 16}" stride="4">\n              <param name="R" type="float"/>\n              <param name="G" type="float"/>\n              <param name="B" type="float"/>\n              <param name="A" type="float"/>\n            </accessor>\n          </technique_common>\n'
                collada_file.write(technique_common_loop_colors)
                colors_source_end = f'        </source>\n'
                collada_file.write(colors_source_end)

                # Vertices ID
                vertices_id_legend = f'        <vertices id="{current_object}-mesh-vertices">\n          <input semantic="POSITION" source="#{current_object}-mesh-positions"/>\n        </vertices>\n'
                collada_file.write(vertices_id_legend)

                # POLYLIST MATERIAL - header
                current_quantity_primitives = self.total_primitives_per_object.get(f'{current_object}')
                polylist_mat_header = f'        <polylist material="{current_object}-material" count="{current_quantity_primitives}">\n'
                polylist_mat_header_row_0 = f'          <input semantic="VERTEX" source="#{current_object}-mesh-vertices" offset="0"/>\n'
                polylist_mat_header_row_1 = f'          <input semantic="NORMAL" source="#{current_object}-mesh-normals" offset="1"/>\n'
                polylist_mat_header_row_2 = f'          <input semantic="TEXCOORD" source="#{current_object}-mesh-map-0" offset="2" set="0"/>\n'
                polylist_mat_header_row_3 = f'          <input semantic="COLOR" source="#{current_object}-mesh-colors-Col{number_geometry_colors}" offset="3" set="0"/>\n'
                collada_file.write(polylist_mat_header)
                collada_file.write(polylist_mat_header_row_0)
                collada_file.write(polylist_mat_header_row_1)
                collada_file.write(polylist_mat_header_row_2)
                collada_file.write(polylist_mat_header_row_3)

                # v-count
                v_count_start = f'          <vcount>'
                collada_file.write(v_count_start)
                collada_v_count = get_polylists.get(f'VCount')
                for v_count_array in collada_v_count:
                    v_count_line = f'{v_count_array} '
                    collada_file.write(v_count_line)
                v_count_end = f'</vcount>\n'
                collada_file.write(v_count_end)

                # p-array
                p_start = f'          <p>'
                collada_file.write(p_start)
                # loop for the p-array
                collada_p_array = get_polylists.get(f'P-Array')
                for p_array in collada_p_array:
                    p_array_line = f'{p_array} '
                    collada_file.write(p_array_line)
                
                p_end = f'</p>\n'
                collada_file.write(p_end)
                polylist_mat_end = f'        </polylist>\n'
                collada_file.write(polylist_mat_end)                  

                # THIS IS THE VERY END OF THE GEOMETRY LIBRARY BEFORE END THE FILE
                geometry_loop_end = f'      </mesh>\n'
                collada_file.write(geometry_loop_end)
                current_geometry_end = f'    </geometry>\n'
                collada_file.write(current_geometry_end)
            
            library_geometries_end = f'  </library_geometries>\n'
            collada_file.write(library_geometries_end)

            # LIBRARY_ANIMATIONS - HERE GOES THE DATA FROM ANIMATION FILE PROCESS
            library_animations_header = f'  <library_animations>\n'
            collada_file.write(library_animations_header)
            total_keyframes = self.animation_data.get(f'TotalTransforms') // 2 # SAF/CMB/LMB SEEMS TO BE WORKING
            animation_data = self.animation_data.get(f'AnimationData')
            time_keyframe = 2 / 20
            for obj_anm_number in range(0, get_number_objects):
                current_object_animation_data = animation_data.get(f'Object_Number_{obj_anm_number}')
                library_animations_loop = f'    <animation id="action_container-Object_Number_{obj_anm_number}" name="Object_Number_{obj_anm_number}">\n'
                collada_file.write(library_animations_loop)

                ######################################### LOCATION #########################################
                ######################################### LOCATION #########################################

                ########### Location X ###########
                ########### Location X ###########
                obj_rot_loc_nesting_x = f'      <animation id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_X" name="Object_Number_{obj_anm_number}">\n'
                collada_file.write(obj_rot_loc_nesting_x)
                # Translation / Location X - input
                obj_transx_input = f'        <source id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_X-input">\n'
                collada_file.write(obj_transx_input)
                obj_transx_input_array = f'          <float_array id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_X-input-array" count="{total_keyframes}">'
                collada_file.write(obj_transx_input_array)
                frame_count_num = 0.0
                t_keyframes = total_keyframes
                while t_keyframes > 0:
                    number_consecutive_frame = f'{frame_count_num} '
                    collada_file.write(number_consecutive_frame)
                    frame_count_num += time_keyframe
                    t_keyframes -= 1
                obj_transx_input_array_end = f'</float_array>\n'
                collada_file.write(obj_transx_input_array_end)
                technique_common_transx_in_start = f'          <technique_common>\n            <accessor source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_X-input-array" count="{total_keyframes}" stride="1">\n'
                technique_common_transx_in_end = f'              <param name="TIME" type="float"/>\n            </accessor>\n          </technique_common>\n'
                collada_file.write(technique_common_transx_in_start)
                collada_file.write(technique_common_transx_in_end)
                obj_transx_end = f'        </source>\n'
                collada_file.write(obj_transx_end)
                # Translation / Location X - output
                obj_transx_output = f'        <source id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_X-output">\n'
                obj_transx_output_array = f'          <float_array id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_X-output-array" count="{total_keyframes}">'
                collada_file.write(obj_transx_output)
                collada_file.write(obj_transx_output_array)                
                for this_transform_data in current_object_animation_data:
                    current_transform_data = current_object_animation_data.get(f'{this_transform_data}')
                    get_tx = current_transform_data.get('Tx')
                    translation_x_line = f'{get_tx} '
                    collada_file.write(translation_x_line)
                obj_transx_output_array_end = f'</float_array>\n'
                collada_file.write(obj_transx_output_array_end)
                technique_common_transx_out = f'          <technique_common>\n            <accessor source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_X-output-array" count="{total_keyframes}" stride="1">\n              <param name="X" type="float"/>\n            </accessor>\n          </technique_common>\n'
                collada_file.write(technique_common_transx_out)
                obj_transx_output_end = f'        </source>\n'
                collada_file.write(obj_transx_output_end)
                #Translation / Location X - interpolation
                obj_transx_inter = f'        <source id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_X-interpolation">\n'
                obj_transx_inter_na = f'          <Name_array id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_X-interpolation-array" count="{total_keyframes}">'
                collada_file.write(obj_transx_inter)
                collada_file.write(obj_transx_inter_na)
                #linear algorithm to repeat the N number of Keyframes
                t_k_inter = total_keyframes
                while t_k_inter > 0:
                    lin_str = f'LINEAR '
                    collada_file.write(lin_str)
                    t_k_inter -= 1
                obj_transx_inter_na_end = f'</Name_array>\n'
                collada_file.write(obj_transx_inter_na_end)
                technique_common_transx_interp = f'          <technique_common>\n            <accessor source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_X-interpolation-array" count="{total_keyframes}" stride="1">\n              <param name="INTERPOLATION" type="name"/>\n            </accessor>\n          </technique_common>\n        </source>\n'
                collada_file.write(technique_common_transx_interp) # also close the source opener
                # Translation / Location X - sampler
                obj_transx_sampler_start = f'        <sampler id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_X-sampler">\n'
                obj_transx_sem_1 = f'          <input semantic="INPUT" source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_X-input"/>\n'
                obj_transx_sem_2 = f'          <input semantic="OUTPUT" source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_X-output"/>\n'
                obj_transx_sem_3 = f'          <input semantic="INTERPOLATION" source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_X-interpolation"/>\n'
                obj_transx_sampler_end = f'        </sampler>\n'
                collada_file.write(obj_transx_sampler_start)
                collada_file.write(obj_transx_sem_1)
                collada_file.write(obj_transx_sem_2)
                collada_file.write(obj_transx_sem_3)
                collada_file.write(obj_transx_sampler_end)
                # Translation / Location X - channel
                obj_transx_channel = f'        <channel source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_X-sampler" target="Object_Number_{obj_anm_number}/location.X"/>\n'
                collada_file.write(obj_transx_channel)
                #End of nesting
                obj_rot_loc_nesting_end = f'      </animation>\n'
                collada_file.write(obj_rot_loc_nesting_end)
                ########### Location X ###########
                ########### Location X ###########

                ########### Location Y ###########
                ########### Location Y ###########
                obj_rot_loc_nesting_y = f'      <animation id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_Y" name="Object_Number_{obj_anm_number}">\n'
                collada_file.write(obj_rot_loc_nesting_y)
                # Translation / Location Y - input
                obj_transy_input = f'        <source id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_Y-input">\n'
                collada_file.write(obj_transy_input)
                obj_transy_input_array = f'          <float_array id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_Y-input-array" count="{total_keyframes}">'
                collada_file.write(obj_transy_input_array)
                frame_count_num = 0
                t_keyframes = total_keyframes
                while t_keyframes > 0:
                    number_consecutive_frame = f'{frame_count_num} '
                    collada_file.write(number_consecutive_frame)
                    frame_count_num += time_keyframe
                    t_keyframes -= 1
                obj_transy_input_array_end = f'</float_array>\n'
                collada_file.write(obj_transy_input_array_end)
                technique_common_transy_in_start = f'          <technique_common>\n            <accessor source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_Y-input-array" count="{total_keyframes}" stride="1">\n'
                technique_common_transy_in_end = f'              <param name="TIME" type="float"/>\n            </accessor>\n          </technique_common>\n'
                collada_file.write(technique_common_transy_in_start)
                collada_file.write(technique_common_transy_in_end)
                obj_transy_end = f'        </source>\n'
                collada_file.write(obj_transy_end)
                # Translation / Location Y - output
                obj_transy_output = f'        <source id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_Y-output">\n'
                obj_transy_output_array = f'          <float_array id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_Y-output-array" count="{total_keyframes}">'
                collada_file.write(obj_transy_output)
                collada_file.write(obj_transy_output_array)                
                for this_transform_data in current_object_animation_data:
                    current_transform_data = current_object_animation_data.get(f'{this_transform_data}')
                    get_ty = current_transform_data.get('Ty')
                    translation_y_line = f'{get_ty} '
                    collada_file.write(translation_y_line)
                obj_transy_output_array_end = f'</float_array>\n'
                collada_file.write(obj_transy_output_array_end)
                technique_common_transy_out = f'          <technique_common>\n            <accessor source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_Y-output-array" count="{total_keyframes}" stride="1">\n              <param name="Y" type="float"/>\n            </accessor>\n          </technique_common>\n'
                collada_file.write(technique_common_transy_out)
                obj_transy_output_end = f'        </source>\n'
                collada_file.write(obj_transy_output_end)
                #Translation / Location Y - interpolation
                obj_transy_inter = f'        <source id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_Y-interpolation">\n'
                obj_transy_inter_na = f'          <Name_array id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_Y-interpolation-array" count="{total_keyframes}">'
                collada_file.write(obj_transy_inter)
                collada_file.write(obj_transy_inter_na)
                #linear algorithm to repeat the N number of Keyframes
                t_k_inter = total_keyframes
                while t_k_inter > 0:
                    lin_str = f'LINEAR '
                    collada_file.write(lin_str)
                    t_k_inter -= 1
                obj_transy_inter_na_end = f'</Name_array>\n'
                collada_file.write(obj_transy_inter_na_end)
                technique_common_transy_interp = f'          <technique_common>\n            <accessor source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_Y-interpolation-array" count="{total_keyframes}" stride="1">\n              <param name="INTERPOLATION" type="name"/>\n            </accessor>\n          </technique_common>\n        </source>\n'
                collada_file.write(technique_common_transy_interp) # also close the source opener
                # Translation / Location Y - sampler
                obj_transy_sampler_start = f'        <sampler id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_Y-sampler">\n'
                obj_transy_sem_1 = f'          <input semantic="INPUT" source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_Y-input"/>\n'
                obj_transy_sem_2 = f'          <input semantic="OUTPUT" source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_Y-output"/>\n'
                obj_transy_sem_3 = f'          <input semantic="INTERPOLATION" source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_Y-interpolation"/>\n'
                obj_transy_sampler_end = f'        </sampler>\n'
                collada_file.write(obj_transy_sampler_start)
                collada_file.write(obj_transy_sem_1)
                collada_file.write(obj_transy_sem_2)
                collada_file.write(obj_transy_sem_3)
                collada_file.write(obj_transy_sampler_end)
                # Translation / Location Y - channel
                obj_transy_channel = f'        <channel source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_Y-sampler" target="Object_Number_{obj_anm_number}/location.Y"/>\n'
                collada_file.write(obj_transy_channel)
                #End of nesting
                obj_rot_loc_nesting_end = f'      </animation>\n' 
                collada_file.write(obj_rot_loc_nesting_end)
                ########### Location Y ###########
                ########### Location Y ###########

                ########### Location Z ###########
                ########### Location Z ###########
                obj_rot_loc_nesting_z = f'      <animation id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_Z" name="Object_Number_{obj_anm_number}">\n'
                collada_file.write(obj_rot_loc_nesting_z)
                # Translation / Location Z - input
                obj_transz_input = f'        <source id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_Z-input">\n'
                collada_file.write(obj_transz_input)
                obj_transz_input_array = f'          <float_array id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_Z-input-array" count="{total_keyframes}">'
                collada_file.write(obj_transz_input_array)
                frame_count_num = 0
                t_keyframes = total_keyframes
                while t_keyframes > 0:
                    number_consecutive_frame = f'{frame_count_num} '
                    collada_file.write(number_consecutive_frame)
                    frame_count_num += time_keyframe
                    t_keyframes -= 1
                obj_transz_input_array_end = f'</float_array>\n'
                collada_file.write(obj_transz_input_array_end)
                technique_common_transz_in_start = f'          <technique_common>\n            <accessor source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_Z-input-array" count="{total_keyframes}" stride="1">\n'
                technique_common_transz_in_end = f'              <param name="TIME" type="float"/>\n            </accessor>\n          </technique_common>\n'
                collada_file.write(technique_common_transz_in_start)
                collada_file.write(technique_common_transz_in_end)
                obj_transz_end = f'        </source>\n'
                collada_file.write(obj_transz_end)
                # Translation / Location Z - output
                obj_transz_output = f'        <source id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_Z-output">\n'
                obj_transz_output_array = f'          <float_array id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_Z-output-array" count="{total_keyframes}">'
                collada_file.write(obj_transz_output)
                collada_file.write(obj_transz_output_array)                
                for this_transform_data in current_object_animation_data:
                    current_transform_data = current_object_animation_data.get(f'{this_transform_data}')
                    get_tz = current_transform_data.get('Tz')
                    translation_z_line = f'{get_tz} '
                    collada_file.write(translation_z_line)
                obj_transz_output_array_end = f'</float_array>\n'
                collada_file.write(obj_transz_output_array_end)
                technique_common_transz_out = f'          <technique_common>\n            <accessor source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_Z-output-array" count="{total_keyframes}" stride="1">\n              <param name="Z" type="float"/>\n            </accessor>\n          </technique_common>\n'
                collada_file.write(technique_common_transz_out)
                obj_transz_output_end = f'        </source>\n'
                collada_file.write(obj_transz_output_end)
                #Translation / Location Z - interpolation
                obj_transz_inter = f'        <source id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_Z-interpolation">\n'
                obj_transz_inter_na = f'          <Name_array id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_Z-interpolation-array" count="{total_keyframes}">'
                collada_file.write(obj_transz_inter)
                collada_file.write(obj_transz_inter_na)
                #linear algorithm to repeat the N number of Keyframes
                t_k_inter = total_keyframes
                while t_k_inter > 0:
                    lin_str = f'LINEAR '
                    collada_file.write(lin_str)
                    t_k_inter -= 1
                obj_transz_inter_na_end = f'</Name_array>\n'
                collada_file.write(obj_transz_inter_na_end)
                technique_common_transz_interp = f'          <technique_common>\n            <accessor source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_Z-interpolation-array" count="{total_keyframes}" stride="1">\n              <param name="INTERPOLATION" type="name"/>\n            </accessor>\n          </technique_common>\n        </source>\n'
                collada_file.write(technique_common_transz_interp) # also close the source opener
                # Translation / Location Z - sampler
                obj_transz_sampler_start = f'        <sampler id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_Z-sampler">\n'
                obj_transz_sem_1 = f'          <input semantic="INPUT" source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_Z-input"/>\n'
                obj_transz_sem_2 = f'          <input semantic="OUTPUT" source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_Z-output"/>\n'
                obj_transz_sem_3 = f'          <input semantic="INTERPOLATION" source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_Z-interpolation"/>\n'
                obj_transz_sampler_end = f'        </sampler>\n'
                collada_file.write(obj_transz_sampler_start)
                collada_file.write(obj_transz_sem_1)
                collada_file.write(obj_transz_sem_2)
                collada_file.write(obj_transz_sem_3)
                collada_file.write(obj_transz_sampler_end)
                # Translation / Location Z - channel
                obj_transz_channel = f'        <channel source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_location_Z-sampler" target="Object_Number_{obj_anm_number}/location.Z"/>\n'
                collada_file.write(obj_transz_channel)
                #End of nesting
                obj_rot_loc_nesting_end = f'      </animation>\n'
                collada_file.write(obj_rot_loc_nesting_end)
                ########### Location Z ###########
                ########### Location Z ###########

                ######################################### ROTATION #########################################
                ######################################### ROTATION #########################################
                
                ########### Rotation X ###########
                ########### Rotation X ###########
                obj_rot_loc_nesting_rx = f'      <animation id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_X" name="Object_Number_{obj_anm_number}">\n'
                collada_file.write(obj_rot_loc_nesting_rx)
                # Rotation X - input
                obj_rotx_input = f'        <source id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_X-input">\n'
                collada_file.write(obj_rotx_input)
                obj_rotx_input_array = f'          <float_array id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_X-input-array" count="{total_keyframes}">'
                collada_file.write(obj_rotx_input_array)
                frame_count_num = 0
                t_keyframes = total_keyframes
                while t_keyframes > 0:
                    number_consecutive_frame = f'{frame_count_num} '
                    collada_file.write(number_consecutive_frame)
                    frame_count_num += time_keyframe
                    t_keyframes -= 1
                obj_rotx_input_array_end = f'</float_array>\n'
                collada_file.write(obj_rotx_input_array_end)
                technique_common_rotx_in_start = f'          <technique_common>\n            <accessor source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_X-input-array" count="{total_keyframes}" stride="1">\n'
                technique_common_rotx_in_end = f'              <param name="TIME" type="float"/>\n            </accessor>\n          </technique_common>\n'
                collada_file.write(technique_common_rotx_in_start)
                collada_file.write(technique_common_rotx_in_end)
                obj_rotx_end = f'        </source>\n'
                collada_file.write(obj_rotx_end)
                # Rotation X - output
                obj_rotx_output = f'        <source id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_X-output">\n'
                obj_rotx_output_array = f'          <float_array id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_X-output-array" count="{total_keyframes}">'
                collada_file.write(obj_rotx_output)
                collada_file.write(obj_rotx_output_array)                
                for this_transform_data in current_object_animation_data:
                    current_transform_data = current_object_animation_data.get(f'{this_transform_data}')
                    get_rx = current_transform_data.get('Rx')
                    rotation_x_line = f'{get_rx} '
                    collada_file.write(rotation_x_line)
                obj_rotx_output_array_end = f'</float_array>\n'
                collada_file.write(obj_rotx_output_array_end)
                technique_common_rotx_out = f'          <technique_common>\n            <accessor source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_X-output-array" count="{total_keyframes}" stride="1">\n              <param name="ANGLE" type="float"/>\n            </accessor>\n          </technique_common>\n'
                collada_file.write(technique_common_rotx_out)
                obj_rotx_output_end = f'        </source>\n'
                collada_file.write(obj_rotx_output_end)
                # Rotation X - interpolation
                obj_rotx_inter = f'        <source id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_X-interpolation">\n'
                obj_rotx_inter_na = f'          <Name_array id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_X-interpolation-array" count="{total_keyframes}">'
                collada_file.write(obj_rotx_inter)
                collada_file.write(obj_rotx_inter_na)
                #linear algorithm to repeat the N number of Keyframes
                t_k_inter = total_keyframes
                while t_k_inter > 0:
                    lin_str = f'LINEAR '
                    collada_file.write(lin_str)
                    t_k_inter -= 1
                obj_rotx_inter_na_end = f'</Name_array>\n'
                collada_file.write(obj_rotx_inter_na_end)
                technique_common_rotx_interp = f'          <technique_common>\n            <accessor source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_X-interpolation-array" count="{total_keyframes}" stride="1">\n              <param name="INTERPOLATION" type="name"/>\n            </accessor>\n          </technique_common>\n        </source>\n'
                collada_file.write(technique_common_rotx_interp) # also close the source opener
                # Rotation X - sampler
                obj_rotx_sampler_start = f'        <sampler id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_X-sampler">\n'
                obj_rotx_sem_1 = f'          <input semantic="INPUT" source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_X-input"/>\n'
                obj_rotx_sem_2 = f'          <input semantic="OUTPUT" source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_X-output"/>\n'
                obj_rotx_sem_3 = f'          <input semantic="INTERPOLATION" source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_X-interpolation"/>\n'
                obj_rotx_sampler_end = f'        </sampler>\n'
                collada_file.write(obj_rotx_sampler_start)
                collada_file.write(obj_rotx_sem_1)
                collada_file.write(obj_rotx_sem_2)
                collada_file.write(obj_rotx_sem_3)
                collada_file.write(obj_rotx_sampler_end)
                # Rotation X - channel
                obj_rotx_channel = f'        <channel source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_X-sampler" target="Object_Number_{obj_anm_number}/rotationX.ANGLE"/>\n'
                collada_file.write(obj_rotx_channel)
                #End of nesting
                obj_rot_loc_nesting_end = f'      </animation>\n'
                collada_file.write(obj_rot_loc_nesting_end)
                ########### Rotation X ###########
                ########### Rotation X ###########
                
                ########### Rotation Y ###########
                ########### Rotation Y ###########
                obj_rot_loc_nesting_ry = f'      <animation id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_Y" name="Object_Number_{obj_anm_number}">\n'
                collada_file.write(obj_rot_loc_nesting_ry)
                # Rotation Y - input
                obj_roty_input = f'        <source id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_Y-input">\n'
                collada_file.write(obj_roty_input)
                obj_roty_input_array = f'          <float_array id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_Y-input-array" count="{total_keyframes}">'
                collada_file.write(obj_roty_input_array)
                frame_count_num = 0
                t_keyframes = total_keyframes
                while t_keyframes > 0:
                    number_consecutive_frame = f'{frame_count_num} '
                    collada_file.write(number_consecutive_frame)
                    frame_count_num += time_keyframe
                    t_keyframes -= 1
                obj_roty_input_array_end = f'</float_array>\n'
                collada_file.write(obj_roty_input_array_end)
                technique_common_roty_in_start = f'          <technique_common>\n            <accessor source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_Y-input-array" count="{total_keyframes}" stride="1">\n'
                technique_common_roty_in_end = f'              <param name="TIME" type="float"/>\n            </accessor>\n          </technique_common>\n'
                collada_file.write(technique_common_roty_in_start)
                collada_file.write(technique_common_roty_in_end)
                obj_roty_end = f'        </source>\n'
                collada_file.write(obj_roty_end)
                # Rotation Y - output
                obj_roty_output = f'        <source id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_Y-output">\n'
                obj_roty_output_array = f'          <float_array id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_Y-output-array" count="{total_keyframes}">'
                collada_file.write(obj_roty_output)
                collada_file.write(obj_roty_output_array)                
                for this_transform_data in current_object_animation_data:
                    current_transform_data = current_object_animation_data.get(f'{this_transform_data}')
                    get_ry = current_transform_data.get('Ry')
                    rotation_y_line = f'{get_ry} '
                    collada_file.write(rotation_y_line)
                obj_roty_output_array_end = f'</float_array>\n'
                collada_file.write(obj_roty_output_array_end)
                technique_common_roty_out = f'          <technique_common>\n            <accessor source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_Y-output-array" count="{total_keyframes}" stride="1">\n              <param name="ANGLE" type="float"/>\n            </accessor>\n          </technique_common>\n'
                collada_file.write(technique_common_roty_out)
                obj_roty_output_end = f'        </source>\n'
                collada_file.write(obj_roty_output_end)
                # Rotation Y - interpolation
                obj_roty_inter = f'        <source id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_Y-interpolation">\n'
                obj_roty_inter_na = f'          <Name_array id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_Y-interpolation-array" count="{total_keyframes}">'
                collada_file.write(obj_roty_inter)
                collada_file.write(obj_roty_inter_na)
                #linear algorithm to repeat the N number of Keyframes
                t_k_inter = total_keyframes
                while t_k_inter > 0:
                    lin_str = f'LINEAR '
                    collada_file.write(lin_str)
                    t_k_inter -= 1
                obj_roty_inter_na_end = f'</Name_array>\n'
                collada_file.write(obj_roty_inter_na_end)
                technique_common_roty_interp = f'          <technique_common>\n            <accessor source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_Y-interpolation-array" count="{total_keyframes}" stride="1">\n              <param name="INTERPOLATION" type="name"/>\n            </accessor>\n          </technique_common>\n        </source>\n'
                collada_file.write(technique_common_roty_interp) # also close the source opener
                # Rotation Y - sampler
                obj_roty_sampler_start = f'        <sampler id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_Y-sampler">\n'
                obj_roty_sem_1 = f'          <input semantic="INPUT" source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_Y-input"/>\n'
                obj_roty_sem_2 = f'          <input semantic="OUTPUT" source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_Y-output"/>\n'
                obj_roty_sem_3 = f'          <input semantic="INTERPOLATION" source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_Y-interpolation"/>\n'
                obj_roty_sampler_end = f'        </sampler>\n'
                collada_file.write(obj_roty_sampler_start)
                collada_file.write(obj_roty_sem_1)
                collada_file.write(obj_roty_sem_2)
                collada_file.write(obj_roty_sem_3)
                collada_file.write(obj_roty_sampler_end)
                # Rotation Y - channel
                obj_roty_channel = f'        <channel source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_Y-sampler" target="Object_Number_{obj_anm_number}/rotationY.ANGLE"/>\n'
                collada_file.write(obj_roty_channel)
                #End of nesting
                obj_rot_loc_nesting_end = f'      </animation>\n'
                collada_file.write(obj_rot_loc_nesting_end)
                ########### Rotation Y ###########
                ########### Rotation Y ###########
            
                ########### Rotation Z ###########
                ########### Rotation Z ###########
                obj_rot_loc_nesting_rz = f'      <animation id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_Z" name="Object_Number_{obj_anm_number}">\n'
                collada_file.write(obj_rot_loc_nesting_rz)
                # Rotation Z - input
                obj_rotz_input = f'        <source id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_Z-input">\n'
                collada_file.write(obj_rotz_input)
                obj_rotz_input_array = f'          <float_array id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_Z-input-array" count="{total_keyframes}">'
                collada_file.write(obj_rotz_input_array)
                frame_count_num = 0
                t_keyframes = total_keyframes
                while t_keyframes > 0:
                    number_consecutive_frame = f'{frame_count_num} '
                    collada_file.write(number_consecutive_frame)
                    frame_count_num += time_keyframe
                    t_keyframes -= 1
                obj_rotz_input_array_end = f'</float_array>\n'
                collada_file.write(obj_rotz_input_array_end)
                technique_common_rotz_in_start = f'          <technique_common>\n            <accessor source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_Z-input-array" count="{total_keyframes}" stride="1">\n'
                technique_common_rotz_in_end = f'              <param name="TIME" type="float"/>\n            </accessor>\n          </technique_common>\n'
                collada_file.write(technique_common_rotz_in_start)
                collada_file.write(technique_common_rotz_in_end)
                obj_rotz_end = f'        </source>\n'
                collada_file.write(obj_rotz_end)
                # Rotation Z - output
                obj_rotz_output = f'        <source id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_Z-output">\n'
                obj_rotz_output_array = f'          <float_array id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_Z-output-array" count="{total_keyframes}">'
                collada_file.write(obj_rotz_output)
                collada_file.write(obj_rotz_output_array)                
                for this_transform_data in current_object_animation_data:
                    current_transform_data = current_object_animation_data.get(f'{this_transform_data}')
                    get_rz = current_transform_data.get('Rz')
                    rotation_z_line = f'{get_rz} '
                    collada_file.write(rotation_z_line)
                obj_rotz_output_array_end = f'</float_array>\n'
                collada_file.write(obj_rotz_output_array_end)
                technique_common_rotz_out = f'          <technique_common>\n            <accessor source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_Z-output-array" count="{total_keyframes}" stride="1">\n              <param name="ANGLE" type="float"/>\n            </accessor>\n          </technique_common>\n'
                collada_file.write(technique_common_rotz_out)
                obj_rotz_output_end = f'        </source>\n'
                collada_file.write(obj_rotz_output_end)
                # Rotation Z - interpolation
                obj_rotz_inter = f'        <source id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_Z-interpolation">\n'
                obj_rotz_inter_na = f'          <Name_array id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_Z-interpolation-array" count="{total_keyframes}">'
                collada_file.write(obj_rotz_inter)
                collada_file.write(obj_rotz_inter_na)
                #linear algorithm to repeat the N number of Keyframes
                t_k_inter = total_keyframes
                while t_k_inter > 0:
                    lin_str = f'LINEAR '
                    collada_file.write(lin_str)
                    t_k_inter -= 1
                obj_rotz_inter_na_end = f'</Name_array>\n'
                collada_file.write(obj_rotz_inter_na_end)
                technique_common_rotz_interp = f'          <technique_common>\n            <accessor source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_Z-interpolation-array" count="{total_keyframes}" stride="1">\n              <param name="INTERPOLATION" type="name"/>\n            </accessor>\n          </technique_common>\n        </source>\n'
                collada_file.write(technique_common_rotz_interp) # also close the source opener
                # Rotation Z - sampler
                obj_rotz_sampler_start = f'        <sampler id="Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_Z-sampler">\n'
                obj_rotz_sem_1 = f'          <input semantic="INPUT" source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_Z-input"/>\n'
                obj_rotz_sem_2 = f'          <input semantic="OUTPUT" source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_Z-output"/>\n'
                obj_rotz_sem_3 = f'          <input semantic="INTERPOLATION" source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_Z-interpolation"/>\n'
                obj_rotz_sampler_end = f'        </sampler>\n'
                collada_file.write(obj_rotz_sampler_start)
                collada_file.write(obj_rotz_sem_1)
                collada_file.write(obj_rotz_sem_2)
                collada_file.write(obj_rotz_sem_3)
                collada_file.write(obj_rotz_sampler_end)
                # Rotation Z - channel
                obj_rotz_channel = f'        <channel source="#Object_Number_{obj_anm_number}_Object_Number_{obj_anm_number}Action_002_rotation_euler_Z-sampler" target="Object_Number_{obj_anm_number}/rotationZ.ANGLE"/>\n'
                collada_file.write(obj_rotz_channel)
                #End of nesting
                obj_rot_loc_nesting_end = f'      </animation>\n'
                collada_file.write(obj_rot_loc_nesting_end)
                ########### Rotation Z ###########
                ########### Rotation Z ###########
                # END OF THE LOOP
                obj_anm_end = f'    </animation>\n'
                collada_file.write(obj_anm_end)
            
            # END OF ANIMATION LIBRARY
            library_animations_end = f'  </library_animations>\n'
            collada_file.write(library_animations_end)
            
            # LIBRARY_VISUAL_SCENE (JUST DEFAULT AS BLENDER EXAMPLE)
            library_visual_scene_header = f'  <library_visual_scenes>\n    <visual_scene id="Scene" name="Scene">\n'
            collada_file.write(library_visual_scene_header)
            for library_number in range(0, get_number_objects):
                library_visual_scene_loop = f'      <node id="Object_Number_{library_number}" name="Object_Number_{library_number}" type="NODE">\n        <scale sid="scale">1 1 1</scale>\n        <rotate sid="rotationZ">0 0 1 0</rotate>\n        <rotate sid="rotationY">0 1 0 0</rotate>\n        <rotate sid="rotationX">1 0 0 90.00001</rotate>\n        <translate sid="location">0 0 0</translate>\n        <instance_geometry url="#Object_Number_{library_number}-mesh" name="Object_Number_{library_number}">\n          <bind_material>\n            <technique_common>\n              <instance_material symbol="Object_Number_{library_number}-material" target="#Object_Number_{library_number}-material">\n                <bind_vertex_input semantic="UVMap" input_semantic="TEXCOORD" input_set="0"/>\n              </instance_material>\n            </technique_common>\n          </bind_material>\n        </instance_geometry>\n      </node>\n'
                collada_file.write(library_visual_scene_loop)
            library_visual_scene_end = f'    </visual_scene>\n  </library_visual_scenes>\n'
            collada_file.write(library_visual_scene_end)

            # SCENE (JUST DEFAULT AS BLENDER EXAMPLE) // END OF THE FILE WITH </COLLADA>
            scene_write = f'  <scene>\n    <instance_visual_scene url="#Scene"/>\n  </scene>\n'
            collada_end_of_file = f'</COLLADA>'
            end_of_file = scene_write + collada_end_of_file
            collada_file.write(end_of_file)
            collada_file.close()