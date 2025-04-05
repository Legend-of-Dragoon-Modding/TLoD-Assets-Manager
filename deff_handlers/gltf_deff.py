"""

glTF DEFF: this module will take the DEFF converted data,
and re-shape it for later being converted into glTF/Buffer Files.
I redo this module specially to handle DEFF format,
since DEFF is a 'Complete Scene' rather than a 'Single Model'.
Also in a future will add the Camera Control here too, so in the
module previously written would need A LOT of refactor, just to convert
a single model and then adapt everything to convert DEFF.

NOTE: Since DEFF Structure and workflow is way different to the classic
single model approach, each Model involved in DEFF have their own Animation.
Even if an Static Model, that will have an Static Animation.

Copyright (C) 2024 DooMMetaL
---------------------------------------------------------
Thanks a lot to Cyril Richon for the code snippet:
this code line convert sRGB to Linear sRGB
https://www.cyril-richon.com/blog/2019/1/23/python-srgb-to-linear-linear-to-srgb

"""
import gc
import math
import numpy
from scipy.spatial.transform import Rotation

class NewGltfDeff:
    def __init__(self, deff_name=str, data_to_convert=dict, deff_total_frames=int) -> None:
        """
        glTF DEFF:\n
        This is the actual module which will take the converted data\n
        and write it into glTF File.
        """
        self.deff_name = deff_name
        self.data_to_convert = data_to_convert
        self.deff_total_frames = deff_total_frames
        self.gltf_format: dict = {}
        self.deff_to_gltf_dict()
    
    def deff_to_gltf_dict(self) -> None:
        """
        DEFF To glTF Dict:\n
        Take all the DEFF Data and create a dict to later write the glTF File and Buffer.
        """
        #First i need to get everything split and sorted at same level
        models_dict: dict = {}
        animations_dict: dict = {}
        current_object_index = 0
        for this_model_name in self.data_to_convert:
            current_model_complete_data = self.data_to_convert.get(f'{this_model_name}')
            denest_current_model_data = current_model_complete_data.get('ModelData')
            get_current_model_data = denest_current_model_data.get('Converted_Data')
            get_current_animation_data = current_model_complete_data.get('ModelAnimation')
            
            """
            Changing the Generic 'Object_Number_n' to 'NameOfModel_n', this is good to avoid name
            shadowing in Blender Importing, since all objects will be in a single Hierarchy.
            """
            #Models
            this_model_objects: dict = {}
            for current_object in get_current_model_data:
                object_name: str = ''
                if this_model_name not in current_object:
                    object_name = current_object.replace('Object_Number_', f'{this_model_name}_')
                else:
                    object_name = current_object 
                object_new_model_data = {f'{object_name}': get_current_model_data.get(f'{current_object}')}
                this_model_objects.update(object_new_model_data)
            conform_model = {f'{current_object_index}': {'Name': this_model_name, 'Data': this_model_objects}}
            models_dict.update(conform_model)

            """
            Here simply maintain the same Model->Animation relation Index
            """
            #Animations
            conform_animation = {f'{current_object_index}': {'Name': this_model_name, 'Data': get_current_animation_data}}
            animations_dict.update(conform_animation)

            current_object_index += 1
        #Take the New conformed Data and re-shape it into glTF Dict
        conformed_gltf = self.generate_gltf_data(model_dict=models_dict, animation_dict=animations_dict)
    
    def generate_gltf_data(self, model_dict=dict, animation_dict=dict) -> None:
        """
        Model Arrager: \n
        Generate the glTF Data in form of dicts.\n
        To later be used in glTF Converter final step. Writting the glTF file.
        """

        total_models_number = len(model_dict)
        total_animations_number = len(animation_dict)

        if total_models_number != total_animations_number:
            print(f'CRITICAL ERROR: Models and Animations do not MATCH\nModels in DEFF {total_models_number} - Animations in DEFF {total_animations_number}')
            print(f'Closing the tool to avoid further errors...')
            exit()

        for current_model in range(0, total_models_number):
            get_model = model_dict.get(f'{current_model}')
            get_model_name = get_model.get('Name')
            get_model_data = get_model.get('Data')

            gltf_total_objects: int = 0
            gltf_meshes_data: dict = {}
            gltf_to_binary_data: dict = {}
            gltf_accessors: dict = {}
            gltf_buffersview: dict = {}

            this_data_index = 0 # This Value actually is the number of position in the arrage in Meshes Primitives and Accessors
            buffer_size = 0
            for current_object in get_model_data:
                get_this_object = get_model_data.get(f'{current_object}')
                object_converted = self.object_to_gltf_buffer(object_to_process=get_this_object)
                object_buffers = object_converted.get('CompiledBuffers')
                this_buffer_array_size = len(object_buffers)
                elements_counts = object_converted.get('Counts')
                elements_sizes = object_converted.get('BuffersSizes')
                vertex_minmax_range = object_converted.get('VertexRange')

                current_bufferview = self.generate_bufferview(bv_current_size_array=buffer_size, bv_elements_sizes=elements_sizes)
                current_mesh = self.generate_mesh_data(current_index=this_data_index, current_object_number=gltf_total_objects)
                current_accesor = self.generate_accessor(current_index=this_data_index, current_object_name=current_object, mesh_element_count=elements_counts, vertex_range=vertex_minmax_range)

                buffers_to_compile_binary: dict = {f'{current_object}': object_buffers}
                buffers_view = {f'{current_object}': current_bufferview}
                mesh_data = {f'{current_object}': current_mesh}

                gltf_meshes_data.update(mesh_data)
                gltf_to_binary_data.update(buffers_to_compile_binary)
                gltf_accessors.update(current_accesor)
                gltf_buffersview.update(buffers_view)

                this_data_index += 6
                buffer_size += this_buffer_array_size
                gltf_total_objects += 1

            # I can use gltf_total_objects to link the nodes for Animations
            # Animations are Object Dependant... so i cannot have all animations for each object in a single array, at least if i cannot make Animation Links well
            # At this moment Animation Data, contains the Animation in a Array formed this way:
            # ThisModel->Object->AllKeyframes->EachTransform(Tx,Ty,Tz,Rx,Ry,Rz,Sx,Sy,Sz)
            get_current_anim_dict = animation_dict.get(f'{current_model}')
            animation_name = get_current_anim_dict.get('Name')
            animation_data = get_current_anim_dict.get('Data')

            this_animation_index = this_data_index
            this_animation_buffer_size = buffer_size
            gltf_animations: dict = {}
            total_anim_buffer_sizes: list = []
            for this_object_animated_name in animation_data:
                object_animation_data = animation_data.get(f'{this_object_animated_name}')
                this_anim_total_transforms = object_animation_data.get(f'TotalTransforms')
                this_anim_object_count = object_animation_data.get(f'ObjectCount')
                this_anim_animation_type = object_animation_data.get(f'AnimationType')
                this_anim_start_frame = object_animation_data.get(f'StartFrame')
                this_anim_end_frame = object_animation_data.get(f'EndFrame')
                this_anim_data = object_animation_data.get(f'AnimationsData')
                total_frames = this_anim_end_frame - this_anim_start_frame
                if total_frames < 1:
                    print(f'CRITICAL ERROR!!: Total Frames can\'t be lowwer than 1, calculation obtained: {total_frames}\nAnimation Processed: {animation_name}')
                    print(f'Closing tool to avoid further errors...')
                    exit()
                generate_gltf_animation_buffers = self.animation_to_gltf_buffer(animation_data=this_anim_data, 
                                                                                total_transforms=this_anim_total_transforms, total_frames=total_frames)
                gltf_animation_data = generate_gltf_animation_buffers[0]
                gltf_animation_info = generate_gltf_animation_buffers[1]
                get_size_info = gltf_animation_info.get('BufferSizeSum')

                gltf_generate_links = self.generate_animation_link(objs_nums=this_anim_object_count, anim_name=this_object_animated_name, last_accessor_num=this_animation_index)
                gltf_generate_anim_accessors = self.generate_animation_accessors(objs_nums=gltf_total_objects, anim_info=gltf_animation_info, current_bufferview_index=this_animation_index)
                gltf_generate_anim_bufferviews_size = self.generate_animation_bufferview(bv_current_size_array=this_animation_buffer_size, anim_info=gltf_animation_info)
                gltf_generate_anim_bufferviews = gltf_generate_anim_bufferviews_size[0]
                next_anim_bufferviews_size = gltf_generate_anim_bufferviews_size[1]
                gltf_animation_link = gltf_generate_links[0]
                next_animation_index = gltf_generate_links[1]
                this_animation = {f'Animation_{this_object_animated_name}': {'AnimLinks': gltf_animation_link, 'AnimAccessors': gltf_generate_anim_accessors, 
                                                                    'AnimBuffersView': gltf_generate_anim_bufferviews, 'AnimBuffers': gltf_animation_data}}

                gltf_animations.update(this_animation)
                total_anim_buffer_sizes.append(get_size_info)
                this_animation_index += next_animation_index
                this_animation_buffer_size += next_anim_bufferviews_size
            
            total_gltf_bin_size = sum(total_anim_buffer_sizes) + buffer_size
            current_model_gltf = {'ObjectsNumber': gltf_total_objects, 'Meshes': gltf_meshes_data, 'Buffers': gltf_to_binary_data, 
                                  'Accessors': gltf_accessors, 'BufferViews': gltf_buffersview, 'BufferSizeTotal': total_gltf_bin_size, 
                                  'Animations': gltf_animations, 'Name': get_model_name}
            
            this_gltf_file = {f'{current_model}': current_model_gltf}
            self.gltf_format.update(this_gltf_file)
        del self.data_to_convert
        gc.collect()

    def object_to_gltf_buffer(self, object_to_process=dict) -> dict[bytes, list, list, dict]:
        """
        Take Model Data of a SINGLE Object from TMDs gather Vertices, Normals, UV, Color and Indices\n
        to generate Buffers for glTF Binary Format.\n
        Also will take the Quads (4Vertex TMD Primitives and convert them into the 3Vertex Equivalent)\n
        -> Using quad_to_tri() Method
        Also will calculate the counts for put them into the Accessors value.\n
        For more information look on gltf_handlers/gltf_compiler.py -> object_to_gltf_buffer().
        """
        buffers_this_object: dict[bytes, list, list, dict] = {}
        vertex_array = object_to_process.get(f'Vertex')
        normal_array = object_to_process.get(f'Normal')
        primitives_to_process = object_to_process.get(f'Primitives')

        self.new_vertex_array: list = [] # NEW GENERATED VERTEX ARRAY, Based on the Vertex Index Supply
        self.new_normal_array: list = [] # NEW GENERATED NORMAL ARRAY, Based on the Normal Index Supply
        self.new_uv_array: list = [] # NEW GENERATED UV ARRAY, Based on the New Primitive Generated
        self.new_color_adjust_array: list = [] # NEW GENERATED COLOR ARRAY, Based on the Color Adjust made by glTF format
        self.new_col_array: list = [] # NEW GENERATED COLOR ARRAY, Based on the New Primitive Generated
        self.new_primitive_array: dict = {} # NEW GENERATED PRIMITIVE ARRAY, Based on the Original TMD Primitive/s
        self.new_vertex_index_array: list = [] # NEW GENERATED VERTEX INDEX ARRAY

        self.generic_vertex_index = 0
        self.primitive_number_new = 0
        for primitive_number in primitives_to_process:
            current_primitive_data = primitives_to_process.get(f'{primitive_number}')
            for primitive_type in current_primitive_data:
                this_primitive_type_data = current_primitive_data.get(f'{primitive_type}')
                if ('No-Texture_' in primitive_type) and ('NLSC_' not in primitive_type):
                    self.process_lsc_prim_no_texture(prim_type=primitive_type, prim_data=this_primitive_type_data, vertex_data=vertex_array, normal_data=normal_array)
                elif ('_Texture_' in primitive_type) and ('NLSC_' not in primitive_type):
                    self.process_lsc_prim_textured(prim_type=primitive_type, prim_data=this_primitive_type_data, vertex_data=vertex_array, normal_data=normal_array)
                elif ('No-Texture_' in primitive_type) and ('NLSC_' in primitive_type):
                    self.process_nlsc_prim_no_texture(prim_type=primitive_type, prim_data=this_primitive_type_data, vertex_data=vertex_array)
                elif ('_Texture_' in primitive_type) and ('NLSC_' in primitive_type):
                    self.process_nlsc_prim_textured(prim_type=primitive_type, prim_data=this_primitive_type_data, vertex_data=vertex_array)

        vertex_index_count = 0
        for this_primitive_index in self.new_primitive_array:
            # Convert the Vertex Indices as SCALAR [Unsigned INT 16 Bit] - Vertex Index
            get_vertex_index = self.new_primitive_array.get(f'{this_primitive_index}')
            vi_0_binary = int.to_bytes(get_vertex_index.get(f'vertex0'), length=2, byteorder='little', signed=False)
            vi_1_binary = int.to_bytes(get_vertex_index.get(f'vertex1'), length=2, byteorder='little', signed=False)
            vi_2_binary = int.to_bytes(get_vertex_index.get(f'vertex2'), length=2, byteorder='little', signed=False)
            vertex_index_array = [vi_0_binary, vi_1_binary, vi_2_binary]
            final_vertex_index = b''.join(vertex_index_array)
            self.new_vertex_index_array.append(final_vertex_index)
            vertex_index_count += 3

        #Calculations for Min/Max[X, Y, Z] Vertex for glTF Format
        all_vertex_x = []
        all_vertex_y = []
        all_vertex_z = []
        for current_vertex in vertex_array:
            current_vertex_data = vertex_array.get(f'{current_vertex}')
            this_vertex_x = current_vertex_data.get(f'VecX')
            this_vertex_y = current_vertex_data.get(f'VecY')
            this_vertex_z = current_vertex_data.get(f'VecZ')
            all_vertex_x.append(this_vertex_x)
            all_vertex_y.append(this_vertex_y)
            all_vertex_z.append(this_vertex_z)
        
        all_vertex_x_minimum = min(all_vertex_x)
        all_vertex_y_minimum = min(all_vertex_y)
        all_vertex_z_minimum = min(all_vertex_z)

        all_vertex_x_maximum = max(all_vertex_x)
        all_vertex_y_maximum = max(all_vertex_y)
        all_vertex_z_maximum = max(all_vertex_z)

        vertex_minimum = {'XMin': all_vertex_x_minimum, 'YMin': all_vertex_y_minimum, 'ZMin': all_vertex_z_minimum}
        vertex_maximum = {'XMax': all_vertex_x_maximum, 'YMax': all_vertex_y_maximum, 'ZMax': all_vertex_z_maximum}
        vertex_range = {'Minimum': vertex_minimum, 'Maximum': vertex_maximum}

        vertex_count = len(self.new_vertex_array)
        normal_count = len(self.new_normal_array)

        processed_vertex_buffer = b''.join(self.new_vertex_array)
        processed_normal_buffer = b''.join(self.new_normal_array)
        processed_uv_buffer = b''.join(self.new_uv_array)
        processed_color_adjust_buffer = b''.join(self.new_color_adjust_array)
        processed_color_buffer = b''.join(self.new_col_array)
        processed_vertex_index_buffer = b''.join(self.new_vertex_index_array)

        processed_vertex_bytes_len = len(processed_vertex_buffer)
        processed_normal_bytes_len = len(processed_normal_buffer)
        processed_uv_bytes_len = len(processed_uv_buffer)
        processed_color_adjust_len = len(processed_color_adjust_buffer)
        processed_color_bytes_len = len(processed_color_buffer)
        processed_vertex_index_bytes_len = len(processed_vertex_index_buffer)

        # Checking if the size and padding are multiple of 4 bytes... yeah 32bit hell
        final_vertex_buffer_and_length = self.check_alignment(old_array=processed_vertex_buffer, array_length=processed_vertex_bytes_len, array_type='Vertex Array')
        final_vertex_buffer = final_vertex_buffer_and_length[0]
        final_vertex_bytes_len = final_vertex_buffer_and_length[1]

        final_normal_buffer_and_length = self.check_alignment(old_array=processed_normal_buffer, array_length=processed_normal_bytes_len, array_type='Normal Array')
        final_normal_buffer = final_normal_buffer_and_length[0]
        final_normal_bytes_len = final_normal_buffer_and_length[1]

        final_uv_buffer_and_length = self.check_alignment(old_array=processed_uv_buffer, array_length=processed_uv_bytes_len, array_type='UV Array')
        final_uv_buffer = final_uv_buffer_and_length[0]
        final_uv_buffer_len = final_uv_buffer_and_length[1]

        final_color_adjust_buffer_and_length = self.check_alignment(old_array=processed_color_adjust_buffer, array_length=processed_color_adjust_len, array_type='Color Adjust Array')
        final_color_adjust_buffer = final_color_adjust_buffer_and_length[0]
        final_color_adjust_buffer_len = final_color_adjust_buffer_and_length[1]

        final_color_buffer_and_length = self.check_alignment(old_array=processed_color_buffer, array_length=processed_color_bytes_len, array_type='Color Array')
        final_color_buffer = final_color_buffer_and_length[0]
        final_color_buffer_len = final_color_buffer_and_length[1]

        final_vertex_index_buffer_and_length = self.check_alignment(old_array=processed_vertex_index_buffer, array_length=processed_vertex_index_bytes_len, array_type='Vertex Index')
        final_vertex_index_buffer = final_vertex_index_buffer_and_length[0]
        final_vertex_index_buffer_len = final_vertex_index_buffer_and_length[1]

        # Joining all the Buffers
        buffers_compiled: list = [final_vertex_buffer, final_normal_buffer, final_uv_buffer, final_color_adjust_buffer, final_color_buffer, final_vertex_index_buffer]
        final_buffers_compiled = b''.join(buffers_compiled)

        #Counts will be in this order: VertexCount, NormalCount, ScalarCount
        count_elements_list: list = [vertex_count, normal_count, vertex_index_count]

        #Need to work on Elements offset to send it to the BufferView
        buffer_element_sizes: list = [final_vertex_bytes_len, final_normal_bytes_len, final_uv_buffer_len, final_color_adjust_buffer_len, final_color_buffer_len, final_vertex_index_buffer_len]

        buffers_this_object = {'CompiledBuffers': final_buffers_compiled, 'Counts': count_elements_list, 'BuffersSizes': buffer_element_sizes, 'VertexRange': vertex_range}
        
        return buffers_this_object

    def process_lsc_prim_no_texture(self, prim_type=str, prim_data=dict, vertex_data=dict, normal_data=dict) -> None:
        """
        Process LSC Primitive No-Texture:
        Take the TMD Primitive Data for Non Textured Primitives and convert them into glTF arrays\n
        for 4 Vertex split data into 2 Triangles.
        """

        if '4Vertex_' in prim_type:
            quad_to_triangle_0: dict = {}
            quad_to_triangle_1: dict = {}

            vertex_index_0 = prim_data.get('vertex0')
            vertex_index_1 = prim_data.get('vertex1')
            vertex_index_2 = prim_data.get('vertex2')
            vertex_index_3 = prim_data.get('vertex3')

            normal_index_0 = prim_data.get('normal0')
            normal_index_1 = prim_data.get('normal1')
            normal_index_2 = prim_data.get('normal2')
            normal_index_3 = prim_data.get('normal3')

            self.vertex_to_gltf_4vertex(vertex_array=vertex_data, vind_0=vertex_index_0, vind_1=vertex_index_1, vind_2=vertex_index_2, vind_3=vertex_index_3)
            self.normal_to_gltf_4vertex(normal_array=normal_data, nind_0=normal_index_0, nind_1=normal_index_1, nind_2=normal_index_2, nind_3=normal_index_3)
            self.non_uv_to_gltf_4vertex()
            self.adjust_color_4v()
            self.color_to_gltf_4vertex(prim_data=prim_data)
            
            quad_to_triangle_0 = {'vertex0': self.generic_vertex_index, 'vertex1': self.generic_vertex_index + 1, 'vertex2': self.generic_vertex_index + 2}
            
            quad_to_triangle_1 = {'vertex0': self.generic_vertex_index + 3, 'vertex1': self.generic_vertex_index + 4, 'vertex2': self.generic_vertex_index + 5}

            new_triangle_0 = {f'Prim_Num_{self.primitive_number_new}': quad_to_triangle_0}
            new_triangle_1 = {f'Prim_Num_{self.primitive_number_new + 1}': quad_to_triangle_1}
            self.new_primitive_array.update(new_triangle_0)
            self.new_primitive_array.update(new_triangle_1)
            self.generic_vertex_index += 6
            self.primitive_number_new += 2

        else:
            single_triangle: dict = {}

            vertex_index_0 = prim_data.get('vertex0')
            vertex_index_1 = prim_data.get('vertex1')
            vertex_index_2 = prim_data.get('vertex2')

            normal_index_0 = prim_data.get('normal0')
            normal_index_1 = prim_data.get('normal1')
            normal_index_2 = prim_data.get('normal2')

            self.vertex_to_gltf_3vertex(vertex_array=vertex_data, vind_0=vertex_index_0, vind_1=vertex_index_1, vind_2=vertex_index_2)
            self.normal_to_gltf_3vertex(normal_array=normal_data, nind_0=normal_index_0, nind_1=normal_index_1, nind_2=normal_index_2)
            self.non_uv_to_gltf_3vertex()
            self.adjust_color_3v()
            self.color_to_gltf_3vertex(prim_data=prim_data)
            
            single_triangle = {'vertex0': self.generic_vertex_index, 'vertex1': self.generic_vertex_index + 1, 'vertex2': self.generic_vertex_index + 2}
            
            new_single_triangle = {f'Prim_Num_{self.primitive_number_new}': single_triangle}
            self.new_primitive_array.update(new_single_triangle)

            self.generic_vertex_index += 3
            self.primitive_number_new += 1

    def process_lsc_prim_textured(self, prim_type=str, prim_data=dict, vertex_data=dict, normal_data=dict) -> None:
        """
        Process LSC Primitive Textured:
        Take the TMD Primitive Data for Textured Primitives and convert them into glTF arrays\n
        for 4 Vertex split data into 2 Triangles.
        """

        if '4Vertex_' in prim_type:
            quad_to_triangle_0: dict = {}
            quad_to_triangle_1: dict = {}

            vertex_index_0 = prim_data.get('vertex0')
            vertex_index_1 = prim_data.get('vertex1')
            vertex_index_2 = prim_data.get('vertex2')
            vertex_index_3 = prim_data.get('vertex3')

            normal_index_0 = prim_data.get('normal0')
            normal_index_1 = prim_data.get('normal1')
            normal_index_2 = prim_data.get('normal2')
            normal_index_3 = prim_data.get('normal3')

            self.vertex_to_gltf_4vertex(vertex_array=vertex_data, vind_0=vertex_index_0, vind_1=vertex_index_1, vind_2=vertex_index_2, vind_3=vertex_index_3)
            self.normal_to_gltf_4vertex(normal_array=normal_data, nind_0=normal_index_0, nind_1=normal_index_1, nind_2=normal_index_2, nind_3=normal_index_3)
            self.uv_to_gltf_4vertex(prim_data=prim_data)
            self.adjust_color_4v()
            self.non_color_to_gltf_4vertex()
            
            quad_to_triangle_0 = {'vertex0': self.generic_vertex_index, 'vertex1': self.generic_vertex_index + 1, 'vertex2': self.generic_vertex_index + 2}
            
            quad_to_triangle_1 = {'vertex0': self.generic_vertex_index + 3, 'vertex1': self.generic_vertex_index + 4, 'vertex2': self.generic_vertex_index + 5}

            new_triangle_0 = {f'Prim_Num_{self.primitive_number_new}': quad_to_triangle_0}
            new_triangle_1 = {f'Prim_Num_{self.primitive_number_new + 1}': quad_to_triangle_1}
            self.new_primitive_array.update(new_triangle_0)
            self.new_primitive_array.update(new_triangle_1)
            self.generic_vertex_index += 6
            self.primitive_number_new += 2

        else:
            single_triangle: dict = {}

            vertex_index_0 = prim_data.get('vertex0')
            vertex_index_1 = prim_data.get('vertex1')
            vertex_index_2 = prim_data.get('vertex2')

            normal_index_0 = prim_data.get('normal0')
            normal_index_1 = prim_data.get('normal1')
            normal_index_2 = prim_data.get('normal2')

            self.vertex_to_gltf_3vertex(vertex_array=vertex_data, vind_0=vertex_index_0, vind_1=vertex_index_1, vind_2=vertex_index_2)
            self.normal_to_gltf_3vertex(normal_array=normal_data, nind_0=normal_index_0, nind_1=normal_index_1, nind_2=normal_index_2)
            self.uv_to_gltf_3vertex(prim_data=prim_data)
            self.adjust_color_3v()
            self.non_color_to_gltf_3vertex()
            
            single_triangle = {'vertex0': self.generic_vertex_index, 'vertex1': self.generic_vertex_index + 1, 'vertex2': self.generic_vertex_index + 2}
            
            new_single_triangle = {f'Prim_Num_{self.primitive_number_new}': single_triangle}
            self.new_primitive_array.update(new_single_triangle)

            self.generic_vertex_index += 3
            self.primitive_number_new += 1

    def process_nlsc_prim_no_texture(self, prim_type=str, prim_data=dict, vertex_data=dict) -> None:
        """
        Process NLSC Primitive No-Texture:
        Take the TMD Primitive Data for Non Textured Primitives and convert them into glTF arrays\n
        for 4 Vertex split data into 2 Triangles,\n
        NLSC Have no Normal Data, so we generate 0.0 Normal Data in here.
        """

        if '4Vertex_' in prim_type:
            quad_to_triangle_0: dict = {}
            quad_to_triangle_1: dict = {}

            vertex_index_0 = prim_data.get('vertex0')
            vertex_index_1 = prim_data.get('vertex1')
            vertex_index_2 = prim_data.get('vertex2')
            vertex_index_3 = prim_data.get('vertex3')

            self.vertex_to_gltf_4vertex(vertex_array=vertex_data, vind_0=vertex_index_0, vind_1=vertex_index_1, vind_2=vertex_index_2, vind_3=vertex_index_3)
            self.non_normal_to_gltf_4vertex()
            self.non_uv_to_gltf_4vertex()
            self.adjust_color_4v()
            self.color_to_gltf_4vertex(prim_data=prim_data)
            
            quad_to_triangle_0 = {'vertex0': self.generic_vertex_index, 'vertex1': self.generic_vertex_index + 1, 'vertex2': self.generic_vertex_index + 2}
            
            quad_to_triangle_1 = {'vertex0': self.generic_vertex_index + 3, 'vertex1': self.generic_vertex_index + 4, 'vertex2': self.generic_vertex_index + 5}

            new_triangle_0 = {f'Prim_Num_{self.primitive_number_new}': quad_to_triangle_0}
            new_triangle_1 = {f'Prim_Num_{self.primitive_number_new + 1}': quad_to_triangle_1}
            self.new_primitive_array.update(new_triangle_0)
            self.new_primitive_array.update(new_triangle_1)
            self.generic_vertex_index += 6
            self.primitive_number_new += 2

        else:
            single_triangle: dict = {}

            vertex_index_0 = prim_data.get('vertex0')
            vertex_index_1 = prim_data.get('vertex1')
            vertex_index_2 = prim_data.get('vertex2')

            self.vertex_to_gltf_3vertex(vertex_array=vertex_data, vind_0=vertex_index_0, vind_1=vertex_index_1, vind_2=vertex_index_2)
            self.non_normal_to_gltf_3vertex()
            self.non_uv_to_gltf_3vertex()
            self.adjust_color_3v()
            self.color_to_gltf_3vertex(prim_data=prim_data)
            
            single_triangle = {'vertex0': self.generic_vertex_index, 'vertex1': self.generic_vertex_index + 1, 'vertex2': self.generic_vertex_index + 2}
            
            new_single_triangle = {f'Prim_Num_{self.primitive_number_new}': single_triangle}
            self.new_primitive_array.update(new_single_triangle)

            self.generic_vertex_index += 3
            self.primitive_number_new += 1

    def process_nlsc_prim_textured(self, prim_type=str, prim_data=dict, vertex_data=dict) -> None:
        """
        Process LSC Primitive Textured:
        Take the TMD Primitive Data for Textured Primitives and convert them into glTF arrays\n
        for 4 Vertex split data into 2 Triangles,\n
        NLSC Have no Normal Data, so we generate 0.0 Normal Data in here.
        """

        if '4Vertex_' in prim_type:
            quad_to_triangle_0: dict = {}
            quad_to_triangle_1: dict = {}

            vertex_index_0 = prim_data.get('vertex0')
            vertex_index_1 = prim_data.get('vertex1')
            vertex_index_2 = prim_data.get('vertex2')
            vertex_index_3 = prim_data.get('vertex3')

            self.vertex_to_gltf_4vertex(vertex_array=vertex_data, vind_0=vertex_index_0, vind_1=vertex_index_1, vind_2=vertex_index_2, vind_3=vertex_index_3)
            self.non_normal_to_gltf_4vertex()
            self.uv_to_gltf_4vertex(prim_data=prim_data)
            self.adjust_color_4v()
            self.color_to_gltf_4vertex(prim_data=prim_data)
            
            quad_to_triangle_0 = {'vertex0': self.generic_vertex_index, 'vertex1': self.generic_vertex_index + 1, 'vertex2': self.generic_vertex_index + 2}
            
            quad_to_triangle_1 = {'vertex0': self.generic_vertex_index + 3, 'vertex1': self.generic_vertex_index + 4, 'vertex2': self.generic_vertex_index + 5}

            new_triangle_0 = {f'Prim_Num_{self.primitive_number_new}': quad_to_triangle_0}
            new_triangle_1 = {f'Prim_Num_{self.primitive_number_new + 1}': quad_to_triangle_1}
            self.new_primitive_array.update(new_triangle_0)
            self.new_primitive_array.update(new_triangle_1)
            self.generic_vertex_index += 6
            self.primitive_number_new += 2

        else:
            single_triangle: dict = {}

            vertex_index_0 = prim_data.get('vertex0')
            vertex_index_1 = prim_data.get('vertex1')
            vertex_index_2 = prim_data.get('vertex2')

            self.vertex_to_gltf_3vertex(vertex_array=vertex_data, vind_0=vertex_index_0, vind_1=vertex_index_1, vind_2=vertex_index_2)
            self.non_normal_to_gltf_3vertex()
            self.uv_to_gltf_3vertex(prim_data=prim_data)
            self.adjust_color_3v()
            self.color_to_gltf_3vertex(prim_data=prim_data)
            
            single_triangle = {'vertex0': self.generic_vertex_index, 'vertex1': self.generic_vertex_index + 1, 'vertex2': self.generic_vertex_index + 2}
            
            new_single_triangle = {f'Prim_Num_{self.primitive_number_new}': single_triangle}
            self.new_primitive_array.update(new_single_triangle)

            self.generic_vertex_index += 3
            self.primitive_number_new += 1

    def vertex_to_gltf_4vertex(self, vertex_array=dict, vind_0=str, vind_1=str, vind_2=str, vind_3=str) -> None:
        """
        Vertex to glTF 4 Vertex:\n
        Take the original Vertex Index from TMD Primitive and original Vertex Array,\n
        generate a new array of Vertex, the Vertex Index is assigned directly to the new Primitive.\n
        Since it's a 4 Vertex Primitive (Quad) i convert it into two 3 Vertex Primitives (Triangles).
        """
        # glTF Vertex Conversion
        vertex_0 = vertex_array.get(f'Vertex_Number_{vind_0}')
        vertex_1 = vertex_array.get(f'Vertex_Number_{vind_1}')
        vertex_2 = vertex_array.get(f'Vertex_Number_{vind_2}')
        vertex_3 = vertex_array.get(f'Vertex_Number_{vind_3}')
        vertex_array_0_32bit = numpy.array([vertex_0.get('VecX'), vertex_0.get('VecY'), vertex_0.get('VecZ')], dtype="float32")
        vertex_array_1_32bit = numpy.array([vertex_1.get('VecX'), vertex_1.get('VecY'), vertex_1.get('VecZ')], dtype="float32")
        vertex_array_2_32bit = numpy.array([vertex_2.get('VecX'), vertex_2.get('VecY'), vertex_2.get('VecZ')], dtype="float32")
        vertex_array_3_32bit = numpy.array([vertex_3.get('VecX'), vertex_3.get('VecY'), vertex_3.get('VecZ')], dtype="float32")
        vertex_array_0_bin = vertex_array_0_32bit.tobytes()
        vertex_array_1_bin = vertex_array_1_32bit.tobytes()
        vertex_array_2_bin = vertex_array_2_32bit.tobytes()
        vertex_array_3_bin = vertex_array_3_32bit.tobytes()
        self.new_vertex_array.append(vertex_array_2_bin)
        self.new_vertex_array.append(vertex_array_1_bin)
        self.new_vertex_array.append(vertex_array_0_bin)
        self.new_vertex_array.append(vertex_array_1_bin)
        self.new_vertex_array.append(vertex_array_2_bin)
        self.new_vertex_array.append(vertex_array_3_bin)
    
    def vertex_to_gltf_3vertex(self, vertex_array=dict, vind_0=str, vind_1=str, vind_2=str) -> None:
        """
        Vertex to glTF 3 Vertex:\n
        Take the original Vertex Index from TMD Primitive and original Vertex Array,\n
        generate a new array of Vertex, the Vertex Index is assigned directly to the new Primitive.\n
        """
        # glTF Vertex Conversion
        vertex_0 = vertex_array.get(f'Vertex_Number_{vind_0}')
        vertex_1 = vertex_array.get(f'Vertex_Number_{vind_1}')
        vertex_2 = vertex_array.get(f'Vertex_Number_{vind_2}')
        vertex_array_0_32bit = numpy.array([vertex_0.get('VecX'), vertex_0.get('VecY'), vertex_0.get('VecZ')], dtype="float32")
        vertex_array_1_32bit = numpy.array([vertex_1.get('VecX'), vertex_1.get('VecY'), vertex_1.get('VecZ')], dtype="float32")
        vertex_array_2_32bit = numpy.array([vertex_2.get('VecX'), vertex_2.get('VecY'), vertex_2.get('VecZ')], dtype="float32")
        vertex_array_0_bin = vertex_array_0_32bit.tobytes()
        vertex_array_1_bin = vertex_array_1_32bit.tobytes()
        vertex_array_2_bin = vertex_array_2_32bit.tobytes()
        self.new_vertex_array.append(vertex_array_0_bin)
        self.new_vertex_array.append(vertex_array_1_bin)
        self.new_vertex_array.append(vertex_array_2_bin)

    def normal_to_gltf_4vertex(self, normal_array=dict, nind_0=str, nind_1=str, nind_2=str, nind_3=str) -> None:
        """
        Normal to glTF 4 Vertex:\n
        Take the original Normal Index from TMD Primitive and original Normal Array,\n
        generate a new array of Normal, the Normal Index is assigned directly to the new Primitive.\n
        Since it's a 4 Vertex Primitive (Quad) i convert it into two 3 Vertex Primitives (Triangles) Normal Array.
        """
        # glTF Normal Conversion
        if (nind_0 != None) and ((nind_1 == None) and (nind_2 == None) and (nind_3 == None)):
            normal_0 = normal_array.get(f'Normal_Number_{nind_0}')
            normal_array_0_32bit = numpy.array([(normal_0.get('VecX') / 4096), (normal_0.get('VecY') / 4096), (normal_0.get('VecZ') / 4096)], dtype="float32")
            normal_array_0_bin = normal_array_0_32bit.tobytes()
            self.new_normal_array.append(normal_array_0_bin)
            self.new_normal_array.append(normal_array_0_bin)
            self.new_normal_array.append(normal_array_0_bin)
            self.new_normal_array.append(normal_array_0_bin)
            self.new_normal_array.append(normal_array_0_bin)
            self.new_normal_array.append(normal_array_0_bin)
        else:
            normal_0 = normal_array.get(f'Normal_Number_{nind_0}')
            normal_1 = normal_array.get(f'Normal_Number_{nind_1}')
            normal_2 = normal_array.get(f'Normal_Number_{nind_2}')
            normal_3 = normal_array.get(f'Normal_Number_{nind_3}')
            normal_array_0_32bit = numpy.array([(normal_0.get('VecX') / 4096), (normal_0.get('VecY') / 4096), (normal_0.get('VecZ') / 4096)], dtype="float32")
            normal_array_1_32bit = numpy.array([(normal_1.get('VecX') / 4096), (normal_1.get('VecY') / 4096), (normal_1.get('VecZ') / 4096)], dtype="float32")
            normal_array_2_32bit = numpy.array([(normal_2.get('VecX') / 4096), (normal_2.get('VecY') / 4096), (normal_2.get('VecZ') / 4096)], dtype="float32")
            normal_array_3_32bit = numpy.array([(normal_3.get('VecX') / 4096), (normal_3.get('VecY') / 4096), (normal_3.get('VecZ') / 4096)], dtype="float32")
            normal_array_0_bin = normal_array_0_32bit.tobytes()
            normal_array_1_bin = normal_array_1_32bit.tobytes()
            normal_array_2_bin = normal_array_2_32bit.tobytes()
            normal_array_3_bin = normal_array_3_32bit.tobytes()
            self.new_normal_array.append(normal_array_2_bin)
            self.new_normal_array.append(normal_array_1_bin)
            self.new_normal_array.append(normal_array_0_bin)
            self.new_normal_array.append(normal_array_1_bin)
            self.new_normal_array.append(normal_array_2_bin)
            self.new_normal_array.append(normal_array_3_bin)

    def normal_to_gltf_3vertex(self, normal_array=dict, nind_0=str, nind_1=str, nind_2=str) -> None:
        """
        Normal to glTF 3 Vertex:\n
        Take the original Normal Index from TMD Primitive and original Normal Array,\n
        generate a new array of Normal, the Normal Index is assigned directly to the new Primitive.\n
        """
        # glTF Normal Conversion
        if (nind_0 != None) and ((nind_1 == None) and (nind_2 == None)):
            normal_0 = normal_array.get(f'Normal_Number_{nind_0}')
            normal_array_0_32bit = numpy.array([(normal_0.get('VecX') / 4096), (normal_0.get('VecY') / 4096), (normal_0.get('VecZ') / 4096)], dtype="float32")
            normal_array_0_bin = normal_array_0_32bit.tobytes()
            self.new_normal_array.append(normal_array_0_bin)
            self.new_normal_array.append(normal_array_0_bin)
            self.new_normal_array.append(normal_array_0_bin)
        
        else:
            normal_0 = normal_array.get(f'Normal_Number_{nind_0}')
            normal_1 = normal_array.get(f'Normal_Number_{nind_1}')
            normal_2 = normal_array.get(f'Normal_Number_{nind_2}')
            normal_array_0_32bit = numpy.array([(normal_0.get('VecX') / 4096), (normal_0.get('VecY') / 4096), (normal_0.get('VecZ') / 4096)], dtype="float32")
            normal_array_1_32bit = numpy.array([(normal_1.get('VecX') / 4096), (normal_1.get('VecY') / 4096), (normal_1.get('VecZ') / 4096)], dtype="float32")
            normal_array_2_32bit = numpy.array([(normal_2.get('VecX') / 4096), (normal_2.get('VecY') / 4096), (normal_2.get('VecZ') / 4096)], dtype="float32")
            normal_array_0_bin = normal_array_0_32bit.tobytes()
            normal_array_1_bin = normal_array_1_32bit.tobytes()
            normal_array_2_bin = normal_array_2_32bit.tobytes()
            self.new_normal_array.append(normal_array_0_bin)
            self.new_normal_array.append(normal_array_1_bin)
            self.new_normal_array.append(normal_array_2_bin)

    def uv_to_gltf_4vertex(self, prim_data=dict) -> None:
        """
        UV to glTF 4 Vertex:\n
        Take the original UV Data from TMD Primitive,\n
        generate a new array of UV, the UV Index is assigned directly to the new Primitive.\n
        Since it's a 4 Vertex Primitive (Quad) i convert it into two 3 Vertex Primitives (Triangles) UV Array.
        """
        #Convert the UV Data into VEC2 [32 Bit Float]
        u0 = prim_data.get('u0')
        v0 = prim_data.get('v0')
        u1 = prim_data.get('u1')
        v1 = prim_data.get('v1')
        u2 = prim_data.get('u2')
        v2 = prim_data.get('v2')
        u3 = prim_data.get('u3')
        v3 = prim_data.get('v3')
        # Vertex UV 0
        u0_32bit = numpy.array([u0], dtype="float32")
        v0_32bit = numpy.array([v0], dtype="float32")
        u0_bin = u0_32bit.tobytes()
        v0_bin = v0_32bit.tobytes()
        uv_0_bin = [u0_bin, v0_bin]
        join_uv_0 = b''.join(uv_0_bin)
        # Vertex UV 1
        u1_32bit = numpy.array([u1], dtype="float32")
        v1_32bit = numpy.array([v1], dtype="float32")
        u1_bin = u1_32bit.tobytes()
        v1_bin = v1_32bit.tobytes()
        uv_1_bin = [u1_bin, v1_bin]
        join_uv_1 = b''.join(uv_1_bin)
        # Vertex UV 2
        u2_32bit = numpy.array([u2], dtype="float32")
        v2_32bit = numpy.array([v2], dtype="float32")
        u2_bin = u2_32bit.tobytes()
        v2_bin = v2_32bit.tobytes()
        uv_2_bin = [u2_bin, v2_bin]
        join_uv_2 = b''.join(uv_2_bin)
        # Vertex UV 3
        u3_32bit = numpy.array([u3], dtype="float32")
        v3_32bit = numpy.array([v3], dtype="float32")
        u3_bin = u3_32bit.tobytes()
        v3_bin = v3_32bit.tobytes()
        uv_3_bin = [u3_bin, v3_bin]
        join_uv_3 = b''.join(uv_3_bin)
        # Appending the UV for each vertex this way:
        # Triangle 1: Vertex 2, Vertex 1, Vertex 0 ; Triangle 2: Vertex 1, Vertex 2, Vertex 3
        self.new_uv_array.append(join_uv_2)
        self.new_uv_array.append(join_uv_1)
        self.new_uv_array.append(join_uv_0)
        self.new_uv_array.append(join_uv_1)
        self.new_uv_array.append(join_uv_2)
        self.new_uv_array.append(join_uv_3)
    
    def uv_to_gltf_3vertex(self, prim_data=dict) -> None:
        """
        UV to glTF 3 Vertex:\n
        Take the original UV Data from TMD Primitive,\n
        generate a new array of UV, the UV Index is assigned directly to the new Primitive.\n
        """
        #Convert the UV Data into VEC2 [32 Bit Float]
        u0 = prim_data.get('u0')
        v0 = prim_data.get('v0')
        u1 = prim_data.get('u1')
        v1 = prim_data.get('v1')
        u2 = prim_data.get('u2')
        v2 = prim_data.get('v2')
        # Vertex UV 0
        u0_32bit = numpy.array([u0], dtype="float32")
        v0_32bit = numpy.array([v0], dtype="float32")
        u0_bin = u0_32bit.tobytes()
        v0_bin = v0_32bit.tobytes()
        uv_0_bin = [u0_bin, v0_bin]
        join_uv_0 = b''.join(uv_0_bin)
        # Vertex UV 1
        u1_32bit = numpy.array([u1], dtype="float32")
        v1_32bit = numpy.array([v1], dtype="float32")
        u1_bin = u1_32bit.tobytes()
        v1_bin = v1_32bit.tobytes()
        uv_1_bin = [u1_bin, v1_bin]
        join_uv_1 = b''.join(uv_1_bin)
        # Vertex UV 2
        u2_32bit = numpy.array([u2], dtype="float32")
        v2_32bit = numpy.array([v2], dtype="float32")
        u2_bin = u2_32bit.tobytes()
        v2_bin = v2_32bit.tobytes()
        uv_2_bin = [u2_bin, v2_bin]
        join_uv_2 = b''.join(uv_2_bin)
        # Appending the UV for each vertex this way:
        # Triangle: Vertex 0, Vertex 1, Vertex 2
        self.new_uv_array.append(join_uv_0)
        self.new_uv_array.append(join_uv_1)
        self.new_uv_array.append(join_uv_2)

    def non_uv_to_gltf_4vertex(self) -> None:
        """
        Non UV to glTF 4 Vertex:\n
        Fill the UV array with a default UV Array to keep the Binary Data file\n
        with a correct padding.
        """
        # For 4 Vertex the number of UV Data would be 6 since i need to split the Quad into a Tri
        for ver_n in range(0, 6):
            u_32bit = numpy.array([0.0], dtype="float32")
            v_32bit = numpy.array([0.0], dtype="float32")
            u_bin = u_32bit.tobytes()
            v_bin = v_32bit.tobytes()
            uv_bin = [u_bin, v_bin]
            join_uv = b''.join(uv_bin)
            self.new_uv_array.append(join_uv)

    def non_uv_to_gltf_3vertex(self) -> None:
        """
        Non UV to glTF 3 Vertex:\n
        Fill the UV array with a default UV Array to keep the Binary Data file\n
        with a correct padding.
        """
        for ver_n in range(0, 3):
            u_32bit = numpy.array([0.0], dtype="float32")
            v_32bit = numpy.array([0.0], dtype="float32")
            u_bin = u_32bit.tobytes()
            v_bin = v_32bit.tobytes()
            uv_bin = [u_bin, v_bin]
            join_uv = b''.join(uv_bin)
            self.new_uv_array.append(join_uv)

    def color_to_gltf_4vertex(self, prim_data=dict) -> None:
        """
        Color to glTF 4 Vertex:\n
        Take the original Color Data from TMD Primitive,\n
        generate a new array of Color, the Color Index is assigned directly to the new Primitive.\n
        Since it's a 4 Vertex Primitive (Quad) i convert it into two 3 Vertex Primitives (Triangles) Color Array.
        """
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

        if b3 == None:
            r1 = r2 = r3 = r0
            g1 = g2 = g3 = g0
            b1 = b2 = b3 = b0
        
        r0 = self.color_srgb_to_linear(color=(r0 / 256))
        g0 = self.color_srgb_to_linear(color=(g0 / 256))
        b0 = self.color_srgb_to_linear(color=(b0 / 256))
        r1 = self.color_srgb_to_linear(color=(r1 / 256))
        g1 = self.color_srgb_to_linear(color=(g1 / 256))
        b1 = self.color_srgb_to_linear(color=(b1 / 256))
        r2 = self.color_srgb_to_linear(color=(r2 / 256))
        g2 = self.color_srgb_to_linear(color=(g2 / 256))
        b2 = self.color_srgb_to_linear(color=(b2 / 256))
        r3 = self.color_srgb_to_linear(color=(r3 / 256))
        g3 = self.color_srgb_to_linear(color=(g3 / 256))
        b3 = self.color_srgb_to_linear(color=(b3 / 256))

        # Convert the Color Data into VEC4 [32 Bit Float]
        # Vertex Color 0
        r0_32bit = numpy.array([(r0)], dtype="float32")
        g0_32bit = numpy.array([(g0)], dtype="float32")
        b0_32bit = numpy.array([(b0)], dtype="float32")
        r0_bin = r0_32bit.tobytes()
        g0_bin = g0_32bit.tobytes()
        b0_bin = b0_32bit.tobytes()
        rgb_bin_0 = [r0_bin, g0_bin, b0_bin]
        join_rgba_vertex_0 = b''.join(rgb_bin_0)
        # Vertex Color 1
        r1_32bit = numpy.array([(r1)], dtype="float32")
        g1_32bit = numpy.array([(g1)], dtype="float32")
        b1_32bit = numpy.array([(b1)], dtype="float32")
        r1_bin = r1_32bit.tobytes()
        g1_bin = g1_32bit.tobytes()
        b1_bin = b1_32bit.tobytes()
        rgb_bin_1 = [r1_bin, g1_bin, b1_bin]
        join_rgba_vertex_1 = b''.join(rgb_bin_1)
        # Vertex Color 2
        r2_32bit = numpy.array([(r2)], dtype="float32")
        g2_32bit = numpy.array([(g2)], dtype="float32")
        b2_32bit = numpy.array([(b2)], dtype="float32")
        r2_bin = r2_32bit.tobytes()
        g2_bin = g2_32bit.tobytes()
        b2_bin = b2_32bit.tobytes()
        rgb_bin_2 = [r2_bin, g2_bin, b2_bin]
        join_rgba_vertex_2 = b''.join(rgb_bin_2)
        # Vertex Color 3
        r3_32bit = numpy.array([(r3)], dtype="float32")
        g3_32bit = numpy.array([(g3)], dtype="float32")
        b3_32bit = numpy.array([(b3)], dtype="float32")
        r3_bin = r3_32bit.tobytes()
        g3_bin = g3_32bit.tobytes()
        b3_bin = b3_32bit.tobytes()
        rgb_bin_3 = [r3_bin, g3_bin, b3_bin]
        join_rgba_vertex_3 = b''.join(rgb_bin_3)
        # Appending the color for each vertex this way:
        # Triangle 1: Vertex 2, Vertex 1, Vertex 0 ; Triangle 2: Vertex 1, Vertex 2, Vertex 3
        self.new_col_array.append(join_rgba_vertex_2)
        self.new_col_array.append(join_rgba_vertex_1)
        self.new_col_array.append(join_rgba_vertex_0)
        self.new_col_array.append(join_rgba_vertex_1)
        self.new_col_array.append(join_rgba_vertex_2)
        self.new_col_array.append(join_rgba_vertex_3)

    def color_to_gltf_3vertex(self, prim_data=dict) -> None:
        """
        Color to glTF 3 Vertex:\n
        Take the original Color Data from TMD Primitive,\n
        generate a new array of Color, the Color Index is assigned directly to the new Primitive.\n
        """

        r0 = prim_data.get('r0')
        g0 = prim_data.get('g0')
        b0 = prim_data.get('b0')
        r1 = prim_data.get('r1')
        g1 = prim_data.get('g1')
        b1 = prim_data.get('b1')
        r2 = prim_data.get('r2')
        g2 = prim_data.get('g2')
        b2 = prim_data.get('b2')

        if b2 == None:
            r1 = r2 = r0
            g1 = g2 = g0
            b1 = b2 = b0

        r0 = self.color_srgb_to_linear(color=(r0 / 256))
        g0 = self.color_srgb_to_linear(color=(g0 / 256))
        b0 = self.color_srgb_to_linear(color=(b0 / 256))
        r1 = self.color_srgb_to_linear(color=(r1 / 256))
        g1 = self.color_srgb_to_linear(color=(g1 / 256))
        b1 = self.color_srgb_to_linear(color=(b1 / 256))
        r2 = self.color_srgb_to_linear(color=(r2 / 256))
        g2 = self.color_srgb_to_linear(color=(g2 / 256))
        b2 = self.color_srgb_to_linear(color=(b2 / 256))

        # Convert the Color Data into VEC4 [32 Bit Float]
        # Vertex Color 0
        r0_32bit = numpy.array([(r0)], dtype="float32")
        g0_32bit = numpy.array([(g0)], dtype="float32")
        b0_32bit = numpy.array([(b0)], dtype="float32")
        r0_bin = r0_32bit.tobytes()
        g0_bin = g0_32bit.tobytes()
        b0_bin = b0_32bit.tobytes()
        rgb_bin_0 = [r0_bin, g0_bin, b0_bin]
        join_rgba_vertex_0 = b''.join(rgb_bin_0)
        # Vertex Color 1
        r1_32bit = numpy.array([(r1)], dtype="float32")
        g1_32bit = numpy.array([(g1)], dtype="float32")
        b1_32bit = numpy.array([(b1)], dtype="float32")
        r1_bin = r1_32bit.tobytes()
        g1_bin = g1_32bit.tobytes()
        b1_bin = b1_32bit.tobytes()
        rgb_bin_1 = [r1_bin, g1_bin, b1_bin]
        join_rgba_vertex_1 = b''.join(rgb_bin_1)
        # Vertex Color 2
        r2_32bit = numpy.array([(r2)], dtype="float32")
        g2_32bit = numpy.array([(g2)], dtype="float32")
        b2_32bit = numpy.array([(b2)], dtype="float32")
        r2_bin = r2_32bit.tobytes()
        g2_bin = g2_32bit.tobytes()
        b2_bin = b2_32bit.tobytes()
        rgb_bin_2 = [r2_bin, g2_bin, b2_bin]
        join_rgba_vertex_2 = b''.join(rgb_bin_2)
        # Appending the color for each vertex this way:
        # Triangle: Vertex 0, Vertex 1, Vertex 2
        self.new_col_array.append(join_rgba_vertex_0)
        self.new_col_array.append(join_rgba_vertex_1)
        self.new_col_array.append(join_rgba_vertex_2)

    def non_color_to_gltf_4vertex(self) -> None:
        """
        Non Color to glTF 4 Vertex:\n
        Fill the Color array with a default Color Array to keep the Binary Data file\n
        with a correct padding.
        """
        # For 4 Vertex the number of Color Data would be 6 since i need to split the Quad into a Tri
        for nvertex in range(0, 6):
            r_32bit = numpy.array([0.0], dtype="float32")
            g_32bit = numpy.array([0.0], dtype="float32")
            b_32bit = numpy.array([0.0], dtype="float32")
            r_bin = r_32bit.tobytes()
            g_bin = g_32bit.tobytes()
            b_bin = b_32bit.tobytes()
            rgb_bin = [r_bin, g_bin, b_bin]
            join_rgba_vertex_n = b''.join(rgb_bin)
            self.new_col_array.append(join_rgba_vertex_n)
    
    def non_color_to_gltf_3vertex(self) -> None:
        """
        Non Color to glTF 3 Vertex:\n
        Fill the Color array with a default Color Array to keep the Binary Data file\n
        with a correct padding.
        """
        for nvertex in range(0, 3):
            r_32bit = numpy.array([0.0], dtype="float32")
            g_32bit = numpy.array([0.0], dtype="float32")
            b_32bit = numpy.array([0.0], dtype="float32")
            r_bin = r_32bit.tobytes()
            g_bin = g_32bit.tobytes()
            b_bin = b_32bit.tobytes()
            rgb_bin = [r_bin, g_bin, b_bin]
            join_rgba_vertex_n = b''.join(rgb_bin)
            self.new_col_array.append(join_rgba_vertex_n)

    def non_normal_to_gltf_4vertex(self) -> None:
        """
        Non Normal to glTF 4 Vertex:\n
        Fill the Normal array with a default Normal Array to keep the Binary Data file\n
        with a correct padding.
        TO-DO: ACCESSOR_VECTOR3_NON_UNIT -> Produces a Vector3 at accessor indices n..n+n is not of unit length: n.nnnnnnn.
        """
        # For 4 Vertex the number of Normal Data would be 6 since i need to split the Quad into a Tri
        for nvertex in range(0, 6):
            normal_array_32bit = numpy.array([0.000000000000, 0.000000000000, 0.000000000000], dtype="float32")
            normal_array_bin = normal_array_32bit.tobytes()
            self.new_normal_array.append(normal_array_bin)
    
    def non_normal_to_gltf_3vertex(self) -> None:
        """
        Non Normal to glTF 3 Vertex:\n
        Fill the Normal array with a default Normal Array to keep the Binary Data file\n
        with a correct padding.
        TO-DO: ACCESSOR_VECTOR3_NON_UNIT -> Produces a Vector3 at accessor indices n..n+n is not of unit length: n.nnnnnnn.
        """
        for nvertex in range(0, 3):
            normal_array_32bit = numpy.array([0.000000000000, 0.000000000000, 0.000000000000], dtype="float32")
            normal_array_bin = normal_array_32bit.tobytes()
            self.new_normal_array.append(normal_array_bin)

    def adjust_color_4v(self) -> None:
        """
        Adjust Color 4 Vertex:\n
        Adding the Pre-multiplier for 4 Vertex Primitives, this is done as in Blender.
        Since it's a 4 Vertex Primitive (Quad) i convert it into two 3 Vertex Primitives (Triangles) Color Array.
        """
        for coladvertex in range(0, 6):
            color_adjust_bin_array = b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
            self.new_color_adjust_array.append(color_adjust_bin_array)

    def adjust_color_3v(self) -> None:
        """
        Adjust Color 3 Vertex:\n
        Adding the Pre-multiplier for 4 Vertex Primitives, this is done as in Blender.
        """
        for coladvertex in range(0, 3):
            color_adjust_bin_array = b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
            self.new_color_adjust_array.append(color_adjust_bin_array)

    def color_srgb_to_linear(self, color=float) -> float:
        """
        Convert The sRGB Color space from Vertex Color into Linear sRGB.\n
        glTF NEED that colors being in Linear sRGB.
        Thanks a lot to Cyril Richon for the code snippet:\n
        https://www.cyril-richon.com/blog/2019/1/23/python-srgb-to-linear-linear-to-srgb
        """
        lrgb: float = 0.0
        if color <= 0.0404482362771082:
            lrgb = color / 12.92
        else:
            lrgb = pow(((color + 0.055) / 1.055), 2.4)
        return lrgb

    def check_alignment(self, old_array=bytes, array_length=int, array_type=str) -> tuple[bytes, int]:
        """
        Check Alignnment:\n
        Check the alignment of an array to keep the 32 bit align.\n
        This is important to know if we need to add padding values at the end of the file.
        """
        pad_value = b'\x00'
        final_array_buffer: bytes = b''
        final_array_length: int = 0

        if self.check_if_multiple(mul=array_length, base=4) == False:
            padding_multiply = self.closest_multiple(mul=array_length, base=4)
            add_this_pad = [old_array, (pad_value * padding_multiply)]
            final_array_buffer = b''.join(add_this_pad)
            final_array_length = len(final_array_buffer)
            #print(f'Adding PAD to {array_type}')
        else:
            final_array_buffer = old_array
            final_array_length = array_length

        return final_array_buffer, final_array_length

    def check_if_multiple(self, mul=int, base=int) -> bool:
        """
        Check if Multiple:\n
        Check if a Value [mul] is multiple of Base[base] number.
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

    def generate_bufferview(self, bv_current_size_array=int, bv_elements_sizes=list) -> dict:
        """
        Generate BufferView:\n
        Generate BufferView Data for an glTF Array,\n
        for that we previously calculate full size of it and each element size.
        """
        object_buffer_view: dict = {}

        internal_offset = bv_current_size_array
        accessor_number = 0
        for bv_element in bv_elements_sizes:
            current_target = 0
            if (accessor_number == 5):
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

    def generate_mesh_data(self, current_index=int, current_object_number=int) -> dict:
        """
        Generate Mesh Data:\n
        Generate the Mesh Data for glTF.\n
        """
        this_gltf_primitive: dict = {}
        this_position = current_index
        this_normal = current_index + 1
        this_texcoord = current_index + 2
        this_color_0 = current_index + 3
        this_color_1 = current_index + 4
        this_vertex_indices = current_index + 5
        this_material = current_object_number


        this_attributes: dict = {'POSITION': this_position, 'NORMAL': this_normal,
                                    'TEXCOORD_0': this_texcoord, 'COLOR_0': this_color_0, 'COLOR_1': this_color_1}
        this_gltf_primitive: dict = {'attributes': this_attributes, 'indices': this_vertex_indices, 'material': this_material}

        return this_gltf_primitive

    def generate_accessor(self, current_index=int, current_object_name=str, mesh_element_count=dict, vertex_range=dict) -> dict:
        """
        Generate Accessor:
        Generate the Accessor data for each Mesh in the Scece in glTF.
        """
        vertex_count = mesh_element_count[0]
        normal_count = mesh_element_count[1]
        element_count = mesh_element_count[2]

        this_accessor: dict = {}
        this_object_accessor_position: dict = {'bufferView': current_index, 'componentType': 5126, 'count': vertex_count, 'type': 'VEC3', 'VertexRange': vertex_range}
        this_object_accessor_normal: dict = {'bufferView': current_index + 1, 'componentType': 5126, 'count': normal_count, 'type': 'VEC3'}
        this_object_accessor_textcoord: dict = {'bufferView': current_index + 2, 'componentType': 5126, 'count': vertex_count, 'type': 'VEC2'}
        this_object_accessor_color_0: dict = {'bufferView': current_index + 3, 'componentType': 5121, 'count': vertex_count, 'type': 'VEC4'}
        this_object_accessor_color_1: dict = {'bufferView': current_index + 4, 'componentType': 5126, 'count': vertex_count, 'type': 'VEC3'}
        this_object_accessor_vertex_indices: dict = {'bufferView': current_index + 5, 'componentType': 5123, 'count': element_count, 'type': 'SCALAR'}

        this_accessor = {f'{current_object_name}':
                         {'AccPos': this_object_accessor_position, 'AccNor': this_object_accessor_normal, 
                          'AccTex': this_object_accessor_textcoord, 'AccAdjCol': this_object_accessor_color_0, 
                          'AccCol': this_object_accessor_color_1, 'AccVInd': this_object_accessor_vertex_indices}}
        
        return this_accessor

    def animation_to_gltf_buffer(self, animation_data=dict, total_transforms=int, total_frames=int) -> dict:
        """
        Animation to glTF Buffer:\n
        Take the Original Animation Data (SAF, CMB, LMB) and convert it into a suitable Buffer Data for glTF.
        Return -> Animation Buffer and Animation Info
        """
        """
        Animation Data: Receive Keyframes (Transforms) from the Current Animated Object
        """
        gltf_animation_data_buffer: dict = {}

        #First we generate the time-keyframing and the Keyframe Array
        keyframes_time_placement: list = []
        keyframe_factor = (total_frames / 20) / total_transforms # This value would change related to the total frames vs frames vs transforms
        current_time = 0.0
        for keyframe in range(0, total_transforms):
            keyframe_time_float = numpy.array([current_time], dtype='float32')
            keyframe_time_float_bin = keyframe_time_float.tobytes()
            keyframes_time_placement.append(keyframe_time_float_bin)
            current_time += keyframe_factor
        
        k_time_place_joined = b''.join(keyframes_time_placement)
        k_time_place_bytelength = len(k_time_place_joined)
        # Checking if the size and padding are multiple of 4 bytes... Keyframes
        final_kfr_bufferlength = self.check_alignment(old_array=k_time_place_joined, array_length=k_time_place_bytelength, array_type='Keyframe Array')
        final_kframe_buffer = final_kfr_bufferlength[0]
        final_kframes_bytes_len = final_kfr_bufferlength[1]
        final_keyframe_buffer: dict = {'KeyframeData': final_kframe_buffer}
        
        #Second we take the Trans/Rot/Scale data from each object and re-generate the array
        #But need to place the Keyframe Timeline first
        anim_buffer_sizes: dict = {}
        total_buffer_size: list = []
        keyframe_buffer_size = {'KeyframePlacementSize': final_kframes_bytes_len}
        anim_buffer_sizes.update(keyframe_buffer_size)
        total_buffer_size.append(final_kframes_bytes_len)

        model_transformations: dict = {}
        for current_object in animation_data:
            object_keyframes = animation_data.get(f'{current_object}')
            this_object_translation: list = []
            this_object_rotation: list = []
            this_object_scale: list = []
            for current_keyframe in object_keyframes:
                current_keyframe_transforms = object_keyframes.get(f'{current_keyframe}')
                rx = current_keyframe_transforms.get(f'Rx')
                ry = current_keyframe_transforms.get(f'Ry')
                rz = current_keyframe_transforms.get(f'Rz')
                tx = current_keyframe_transforms.get(f'Tx')
                ty = current_keyframe_transforms.get(f'Ty')
                tz = current_keyframe_transforms.get(f'Tz')
                sx = current_keyframe_transforms.get(f'Sx')
                sy = current_keyframe_transforms.get(f'Sy')
                sz = current_keyframe_transforms.get(f'Sz')
                # Convert EULER Rotations to Array of Quaternion Rotations
                complete_rotation_array = self.euler_to_quaternion_array(euler_x=rx, euler_y=ry, euler_z=rz)
                this_object_rotation.append(complete_rotation_array)
                # Convert Locations into Array
                complete_translation_array = self.translation_to_array(transx=tx, transy=ty, transz=tz)
                this_object_translation.append(complete_translation_array)
                # Convert Scales into Array and handling if No Rotation data present in the transform
                complete_scale_array = self.scale_to_array(scalex=sx, scaley=sy, scalez=sz)
                this_object_scale.append(complete_scale_array)
            
            translation_joined = b''.join(this_object_translation)
            translation_len = len(translation_joined)
            rotation_joined = b''.join(this_object_rotation)
            rotation_len = len(rotation_joined)
            scale_joined = b''.join(this_object_scale)
            scale_len = len(scale_joined)

            # Checking if the size and padding are multiple of 4 bytes... Translation
            final_trans_buffer_and_length = self.check_alignment(old_array=translation_joined, array_length=translation_len, array_type='Translation Array')
            final_trans_buffer = final_trans_buffer_and_length[0]
            final_trans_bytes_len = final_trans_buffer_and_length[1]
            # Checking if the size and padding are multiple of 4 bytes... Rotation
            final_rot_buffer_and_length = self.check_alignment(old_array=rotation_joined, array_length=rotation_len, array_type='Rotation Array')
            final_rot_buffer = final_rot_buffer_and_length[0]
            final_rot_bytes_len = final_rot_buffer_and_length[1]
            # Checking if the size and padding are multiple of 4 bytes... Scale
            final_scale_buffer_and_length = self.check_alignment(old_array=scale_joined, array_length=scale_len, array_type='Scale Array')
            final_scale_buffer = final_scale_buffer_and_length[0]
            final_scale_bytes_len = final_scale_buffer_and_length[1]

            translation_dict: dict = {'TransData': final_trans_buffer}
            rotation_dict: dict = {'RotData': final_rot_buffer}
            scale_dict: dict = {'ScaleData': final_scale_buffer}

            this_object_transformations: dict = {f'{current_object}': {'Translation': translation_dict, 'Rotation': rotation_dict, 'Scale': scale_dict}}
            current_anim_buffer_size: dict = {f'{current_object}': {'TransLen': final_trans_bytes_len, 'RotLen': final_rot_bytes_len, 'ScaleLen': final_scale_bytes_len}}

            anim_buffer_sizes.update(current_anim_buffer_size)
            model_transformations.update(this_object_transformations)
            total_buffer_size.append(final_trans_bytes_len)
            total_buffer_size.append(final_rot_bytes_len)
            total_buffer_size.append(final_scale_bytes_len)

        finished_animation_buffer: dict = {'Count': total_transforms, 
                                           'Buffers': {'KeyframeBuffer': final_keyframe_buffer, 
                                                       'TransformationBuffer': model_transformations}}

        total_anim_buffer_size = sum(total_buffer_size)
        gltf_animation_data_buffer = finished_animation_buffer
        animation_info = {'Keyframes': total_transforms, 'Min': 0.0, 'Max': (keyframe_factor - 0.2), 'BufferSizes': anim_buffer_sizes,
                          'BufferSizeSum': total_anim_buffer_size}

        return gltf_animation_data_buffer, animation_info

    def euler_to_quaternion_array(self, euler_x=float, euler_y=float, euler_z=float) -> bytes:
        """
        EULER to Quaternion:\n
        Convert EULER Degrees Rotations into Quaternion Rotations,\n
        to later being compiled into a Float32 Array.
        Returns -> Quaternion Rotations 32 bit Float Array - VEC4.
        """
        gltf_quaternion: bytes = b''
        # Create a rotation object from Euler angles specifying axes of rotation
        new_array = numpy.array([euler_x, euler_y, euler_z], dtype='float32')
        rotation_from_euler = Rotation.from_euler('xyz', new_array, degrees=True)
        # Convert to quaternions
        rotation_to_quat = rotation_from_euler.as_quat()
        rotation_array = numpy.array(rotation_to_quat, dtype='float32')
        gltf_quaternion = rotation_array.tobytes()

        return gltf_quaternion
    
    def translation_to_array(self, transx=float, transy=float, transz=float) -> bytes:
        """
        Translation to Array:\n
        Manipulate if needed Translation data,\n
        to later being compiled into a Float32 Array.
        Returns -> Locations 32 bit Float Array - VEC3.
        """
        gltf_translation: bytes = b''
        location_array = numpy.array([transx, transy, transz], dtype='float32')
        gltf_translation = location_array.tobytes()

        return gltf_translation
    
    def scale_to_array(self, scalex=float|None, scaley=float|None, scalez=float|None) -> bytes:
        """
        Scale to Array:\n
        Take the Scale data to later being compiled into a Float32 Array,\n
        In case that Scale Data is None, will generate 1.0 Values as default.
        This to comply to glTF Format.
        SAF and CMB had no Scale Data, while LMBType[Any] have.
        Returns -> Scale 32 bit Float Array - VEC3.
        """
        gltf_scale: bytes = b''
        if scalex == None:
            scalex = scaley = scalez = 1.0
        scale_array = numpy.array([scalex, scaley, scalez], dtype='float32')
        gltf_scale = scale_array.tobytes()

        return gltf_scale

    def generate_animation_link(self, objs_nums=int, anim_name=str, last_accessor_num=int) -> tuple[dict, int]:
        """
        Generate Animation Link:\n
        Generate Channels and Samplers for linking Animation.
        """
        gltf_animation_link: dict = {}

        gltf_channel_data: dict = {}
        gltf_samplers_data: dict = {}
        new_accessor_num = last_accessor_num + 1
        current_sampler = 0
        for node_number in range(0, objs_nums):
            for this_sampler in range(0, 3):
                path_name: str = ''
                node_name = node_number
                if this_sampler == 0:
                    path_name = 'translation'
                elif this_sampler == 1:
                    path_name = 'rotation'
                elif this_sampler == 2:
                    path_name = 'scale'
                channel_data = {f'Channel_{current_sampler}': {'Sampler': current_sampler, 'Node': node_name, 'Path': path_name}}
                samplers_data = {f'Sampler_{current_sampler}': {'Input': last_accessor_num, 'Interpolation': 'LINEAR', 'output': new_accessor_num}}
                gltf_channel_data.update(channel_data)
                gltf_samplers_data.update(samplers_data)
                current_sampler += 1
                new_accessor_num += 1
        
        next_accessor = current_sampler + 1
        compiled_anim_link: dict = {'Channels': gltf_channel_data, 'Name': anim_name, 'Samplers': gltf_samplers_data}
        gltf_animation_link.update(compiled_anim_link)

        return gltf_animation_link, next_accessor

    def generate_animation_accessors(self, objs_nums=int, anim_info=dict, current_bufferview_index=int) -> dict:
        """
        Generate Animation Accessors:\n
        Generate the required Animations Accessors to be link by the Animation,
        Returns -> gltf_accessor_animations Dict.
        """
        """
        As in Mesh Accessors the BufferView and format it's the same,
        but since i will be working with SEVERAL animations in a single file the general structure is:
        {
        Accessor for Time - Keyframes Animation 0
        Accessor for Translation 0
        Accessor for Rotation 0
        Accessor for Scale 0
        Accessor for Translation 1
        Accessor for Rotation 1
        Accessor for Scale 1
        .......
        Accessor for Time - Keyframes Animation N
        Accessor for Translation N
        Accessor for Rotation N
        Accessor for Scale N
        Accessor for Translation N + 1
        Accessor for Rotation N + 1
        Accessor for Scale N + 1
        }
        So Accessor for Time is used only once for an animation,
        while Translation/Rotation/Scale depends on the number of objects,
        this means that depending on how many objects and animations exist will be
        the final number of accessors.
        TYPE FOR KEYFRAME/TIME DATA is SCALAR
        TYPE FOR LOCATION DATA is VEC3
        TYPE FOR ROTATION DATA is VEC4
        TYPE FOR SCALE DATA is VEC3
        COUNT FOR ALL THE TRANSFORMATION DATA and KEYFRAME/TIME is the same number as Total Keyframes
        """
        gltf_accessor_animations: dict = {}
        bufferview_count_init = current_bufferview_index

        count = anim_info.get('Keyframes')
        min_time_value = anim_info.get('Min')
        max_time_value = anim_info.get('Max')

        
        bufferview_keyframe_dict = {f'Accessor_{bufferview_count_init}': {'BufferView': bufferview_count_init, 'ComponentType': 5126, 
                                                                    'Count': count, 'Min': min_time_value, 'Max': max_time_value, 
                                                                    'Type': 'SCALAR'}}
        gltf_accessor_animations.update(bufferview_keyframe_dict)

        bufferview_count_next = bufferview_count_init + 1 # Need to jump +1 because the first is already used by a unique Keyframe timeline
        next_accessor = 0
        for this_obj in range(0, objs_nums):
            for this_transform in range(0, 3):
                current_accesor = next_accessor + bufferview_count_next
                bufferview_type: str = ''
                if (this_transform == 0) or (this_transform == 2):
                    bufferview_type = 'VEC3'
                else:
                    bufferview_type = 'VEC4'
                bufferview_trans_scale_dict = {f'Accessor_{current_accesor}': {'BufferView': current_accesor, 'ComponentType': 5126, 
                                                                               'Count': count, 'Type': bufferview_type}}
                gltf_accessor_animations.update(bufferview_trans_scale_dict)
                
                next_accessor += 1

        return gltf_accessor_animations

    def generate_animation_bufferview(self, bv_current_size_array=int, anim_info=dict) -> tuple[dict, int]:
        animation_bufferview: dict = {}
        buffersizes = anim_info.get('BufferSizes')
        
        current_external_size = bv_current_size_array
        current_internal_size = 0
        buffer_count = 0
        for this_buffer_name in buffersizes:
            byte_length: int = 0
            byte_offset: int = 0
            if this_buffer_name == 'KeyframePlacementSize':
                byte_length = buffersizes.get(f'{this_buffer_name}')
                byte_offset = current_external_size + current_internal_size
                this_buffer_view: dict = {f'BufferView_{this_buffer_name}_{buffer_count}': 
                                          {'buffer': 0, 'byteLength': byte_length, 'byteOffset': byte_offset}}
                animation_bufferview.update(this_buffer_view)
                buffer_count += 1
                current_internal_size += byte_length
            else:
                this_object_buffer = buffersizes.get(f'{this_buffer_name}')
                for this_transform_name in this_object_buffer:
                    byte_length = this_object_buffer.get(f'{this_transform_name}')
                    byte_offset = current_external_size + current_internal_size
                    this_buffer_view: dict = {f'BufferView_{this_transform_name}_{buffer_count}': 
                                              {'buffer': 0, 'byteLength': byte_length, 'byteOffset': byte_offset}}
                    animation_bufferview.update(this_buffer_view)
                    buffer_count += 1
                    current_internal_size += byte_length

        return animation_bufferview, current_internal_size