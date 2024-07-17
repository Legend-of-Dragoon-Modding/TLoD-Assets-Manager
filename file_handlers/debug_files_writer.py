"""

Debug Files Writer: 
This module create several "Debugging" files.
-------------------------------------------------------------------------
Plain Texts:
Model Report: contains the model components quantity per objects.
Primitives per Object: contains each primitive type per objects.

PrimData Writer: This util create a 'special' file, which is used in one
of my tools (Blend2TMD), format is PrimData, this file carries the basic
data of each primitive UV from a TLoD model, to be reused in the tool.
-------------------------------------------------------------------------
INPUT: debug_files_flag = {TMDReport: BOOL, PrimPerObj: BOOL, PrimData: BOOL}
-------------------------------------------------------------------------
OUTPUT: Written Files on Disk
-------------------------------------------------------------------------
Copyright (C) 2024 DooMMetaL

"""
import datetime
from collections import Counter

class DebugData:
    def __init__(self, converted_file_path=str, debug_files_flag=dict, file_data=dict) -> None:
        self.converted_file_path = converted_file_path
        self.model_report_bool = debug_files_flag.get(f'TMDReport')
        self.prim_per_obj_bool = debug_files_flag.get(f'PrimPerObj')
        self.primdata_bool = debug_files_flag.get(f'PrimData')
        self.table_objects = file_data.get('Data_Table')
        self.primitives_converted = file_data.get('Converted_Data')
        self.write_model_report()
        self.write_primitive_per_object()
        self.write_primdata_file()
    
    def write_model_report(self) -> None:
        if self.model_report_bool == True:
            total_objects_in_model = len(self.table_objects)
            report_file_path = self.converted_file_path + f'_Model_Report.txt'
            with open(report_file_path, 'w') as write_report_text:
                header_text = f'File: {report_file_path}, was converted with TLoD - Assets Manager by DooMMetaL.\n\n\n'
                write_report_text.write(header_text)
                number_of_vertices: list = []
                number_of_normals: list = []
                number_of_primitives: list = []
                for this_object_number in range(0, total_objects_in_model):
                    get_this_object_table = self.table_objects.get(f'Object_Number_{this_object_number}')
                    get_this_number_vertices = get_this_object_table.get(f'VertexNumber')
                    get_this_number_normals = get_this_object_table.get(f'NormalNumber')
                    get_this_number_primitives = get_this_object_table.get(f'PrimitiveNumber')
                    subtitle_obj = f'Object N° {this_object_number} have:\n'
                    elements_sorted = f'Vertices: {get_this_number_vertices} - Normals: {get_this_number_normals} - Primitives: {get_this_number_primitives}\n\n'
                    write_report_text.write(subtitle_obj)
                    write_report_text.write(elements_sorted)
                    number_of_vertices.append(get_this_number_primitives)
                    number_of_normals.append(get_this_number_normals)
                    number_of_primitives.append(get_this_number_primitives)
                total_number_vertices = sum(number_of_vertices)
                total_number_normals = sum(number_of_normals)
                total_number_primitives = sum(number_of_primitives)
                total_number_vnp = f'\nTotal number of ==> Vertices: {total_number_vertices} - Normals: {total_number_normals} - Primitives: {total_number_primitives}\n\n'
                time_now = f'\nWork finished at: {datetime.datetime.now()}'
                write_report_text.write(total_number_vnp)
                write_report_text.write(time_now)
                write_report_text.close()

    def write_primitive_per_object(self):
        if self.prim_per_obj_bool == True:
            report_prim_file_path = self.converted_file_path + f'_Prim_per_Obj.txt'
            primitive_data_get = self.primitives_converted.get(f'Primitive_Data')
            primitives_per_object = {}
            for object_number in primitive_data_get:
                object_name = object_number
                this_object = primitive_data_get.get(f'{object_name}')
                prim_types_repetition = []
                for this_primitive in this_object:
                    get_types = this_object.get(f'{this_primitive}')
                    for this_type in get_types:
                        prim_types_repetition.append(this_type)
                counter_each_primitive_type = Counter(prim_types_repetition)
                primitive_repeat = {}
                for this_type in counter_each_primitive_type:
                    get_number_repeats = counter_each_primitive_type.get(f'{this_type}')
                    primitive_repeat.update({f'{this_type}': get_number_repeats})
                primitives_per_object.update({f'{object_name}': primitive_repeat})
            
            with open(report_prim_file_path, 'w') as write_prim_per_obj:
                primitive_reporter_superheader = f'PRIMITIVE INSIGHT REPORT\n'
                primitive_reporter_header = f'File: {report_prim_file_path}, was converted using TLoD - Assets Manager by DooMMetaL.\n\n\n'
                primitive_reporter_warning = f'This report file is used to Debug and research about Primitives in Models. \nAlso helps to compare Obj Table Calculation and final extracted primitives.\nIf you are not sure what are you doing, please ignore this file.\n\n'
                header_text_concatenated = primitive_reporter_superheader + primitive_reporter_header + primitive_reporter_warning
                write_prim_per_obj.write(header_text_concatenated)
                separator_from_start = f'{'='*50}\n\n'
                write_prim_per_obj.write(separator_from_start)
                for current_object in primitives_per_object:
                    write_obj_name = f'Primitives converted from: {current_object}\n'
                    write_prim_per_obj.write(write_obj_name)
                    get_prim_types = primitives_per_object.get(f'{current_object}')
                    for this_type in get_prim_types:
                        name_primitive_type = this_type
                        quantity_primitive_type = get_prim_types.get(f'{this_type}')
                        quantity_and_type_line = f'Type: {name_primitive_type} ==> Quantity: {quantity_primitive_type}\n'
                        write_prim_per_obj.write(quantity_and_type_line)
                    separator_from_object = f'\n'
                    write_prim_per_obj.write(separator_from_object)
                time_now = f'{'='*50}\nWork finished at: ' + str(datetime.datetime.now())
                write_prim_per_obj.write(time_now)

    def write_primdata_file(self):
        if self.primdata_bool == True:
            prim_data_filepath = self.converted_file_path + f'.primdata'
            all_objects_primitives_block = self.primitives_converted.get('Primitive_Data')
            texture_data_in_object = []
            number_objects = 0
            for current_object in all_objects_primitives_block:
                primitive_block = all_objects_primitives_block.get(f'{current_object}')
                texture_data_in_primitive = []
                this_number_primitive = 0
                for this_primitive in primitive_block:
                    get_primitive = primitive_block.get(f'{this_primitive}')
                    for name_primitive in get_primitive:
                        primitive_values = get_primitive.get(f'{name_primitive}')
                        if primitive_values.get('u0') != None:
                            start_magic_string_primitive = b'\x50\x52\x49\x4D'
                            primitive_number = int.to_bytes(this_number_primitive, 4, 'little', signed=False)
                            get_cba = primitive_values.get('cba')
                            get_tsb = primitive_values.get('tsb')
                            array_bytes_complete = start_magic_string_primitive + primitive_number + get_cba + get_tsb
                            texture_data_in_primitive.append(array_bytes_complete)
                    this_number_primitive += 1
                joined_texture_data = b''.join(texture_data_in_primitive)
                current_object_bytes = int.to_bytes(number_objects, 4, 'little', signed=False)
                start_magic_string_object = b'\x4F\x42\x4A\x5F'
                end_magic_string_object = b'\x5F\x45\x4E\x44'
                final_texture_process = start_magic_string_object + current_object_bytes + joined_texture_data + current_object_bytes + end_magic_string_object
                texture_data_in_object.append(final_texture_process)
                number_objects += 1
            
            finished_texture_data = b''.join(texture_data_in_object)
            number_objects_bytes = int.to_bytes(number_objects, length=4, byteorder='little', signed=False)
            header_magic = b'\x50\x52\x49\x4D\x44\x41\x54\x41'

            final_package = header_magic + number_objects_bytes + finished_texture_data

            with open(prim_data_filepath, 'wb') as write_data:
                write_data.write(final_package)