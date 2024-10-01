"""

Split Binary Data:
This module will take any of the known Binary Dicts
in TLoD and Split the data based on the known file formats
--------------------------------------------------------------------------------------------------------------
Input file: bin_to_split = {'Format': str, 'Data': dict}
Format: TMD_Standard, TMD_CContainer, SAF_CContainer, TIM.
Data: File Binary Data.
--------------------------------------------------------------------------------------------------------------
:RETURN: -> self.converted_data = {'Format': str, 'DataInChunks': dict}
DICT --> 'Data': [BINARY_DATA]
--------------------------------------------------------------------------------------------------------------
Copyright (C) 2024 DooMMetaL

"""
from PyQt6.QtWidgets import QMessageBox
from file_handlers import binary_data_handler, decompress_bpe

class Asset:
    """Split Binary Data based on the File Type\n
    Converting data into chuncks inside self.converted_data"""
    def __init__(self, bin_to_split=dict) -> None:
        self.bin_to_split = bin_to_split
        self.model_converted_data: dict = {'Format': '', 'Data_Table': {}, 'Converted_Data': {}}
        self.animation_converted_data: dict = {}
        self.texture_converted_data: dict = {}
        self.convert_binary_data()
    
    def convert_binary_data(self) -> None:
        self.file_format: str = self.bin_to_split.get('Format')
        self.file_data: list = self.bin_to_split.get('Data')
        
        if self.file_format == 'TMD_Standard': 
            self.split_standard_tmd()
        elif self.file_format == 'TMD_CContainer':
            self.split_cc_tmd()
        elif self.file_format == 'SAF_CContainer':
            self.split_cc_saf()
        elif (self.file_format == 'TIM') or (self.file_format == 'PXL') or (self.file_format == 'MCQ'):
            self.split_texture(texture_format=self.file_format)
        else:
            no_conversion_method = f'Conversion Method for {self.file_format}, NOT IMPLEMENTED!!'
            error_no_conversion_method = QMessageBox.critical(None, 'CRITICAL ERROR!!', f'FATAL!!:\n{no_conversion_method}', QMessageBox.StandardButton.Ok)
            exit()
    
    def split_standard_tmd(self):
        """
        This method takes the Binary Data from a Standard TMD and after split their binary Data,
        converter it into Human readable data. This 4 Examples will show the Dictionary Nesting to Hold the data\n
        {Object Table: {Object_Number_n: {'VertexAddress': INT, 'VertexNumber': INT, 'NormalAddress': INT, 'NormalNumber': INT,
                              'PrimitiveAddress': INT, 'PrimitiveNumber': INT, 'Scale': INT}}}\n\n
        {'Object_Number_n': {'Vertex_Number_n': {'VecX': FLOAT, 'VecY': FLOAT, 'VecZ': FLOAT}}}\n\n
        {'Object_Number_n': {'Normal_Number_n': {'VecX': FLOAT, 'VecY': FLOAT, 'VecZ': FLOAT}}}\n\n
        {'Object_Number_n': {'Primitive_Number_n': 'Primitive_Type_Name': {COLOR AND INDICES = INT, UV = FLOAT, CONFIGURATIONS = BINARY}}}
        """
        bin_clean_type_list = self.file_data[0]
        number_objects = bin_clean_type_list[8:12] #IGNORING THE HEADER, WE KNOW WHICH TYPE IS || IGNORING FIXP AT LEAST NOT NEED TO READ MODEL FILES IN TLOD
        number_objects_int = int.from_bytes(number_objects, 'little', signed=False)
        model_data_end = bin_clean_type_list[12:]
        object_table_dict = self.split_object_table_tmd(number_objs=number_objects_int, model_data=model_data_end)
        vertex_data = binary_data_handler.BinaryDataModel(object_table=object_table_dict, binary_data=model_data_end, type_of_data='Vertex')
        normal_data = binary_data_handler.BinaryDataModel(object_table=object_table_dict, binary_data=model_data_end, type_of_data='Normal')
        primitive_data = binary_data_handler.BinaryDataModel(object_table=object_table_dict, binary_data=model_data_end, type_of_data='Primitive')

        arrage_vnp_data = self.vnp_data_arrager(object_number=number_objects_int, vertex_data=vertex_data.model_converted, normal_data=normal_data.model_converted, primitive_data=primitive_data.model_converted)

        tmd_final_dict = {'Format': 'TMD_Standard', 'Data_Table': object_table_dict, 
                          'Converted_Data': arrage_vnp_data}
        self.model_converted_data = tmd_final_dict

    def split_cc_tmd(self):
        """
        This method takes the Binary Data from a CContainer TMD and after split their binary Data,
        converter it into Human readable data. This 4 Examples will show the Dictionary Nesting to Hold the data\n
        {Object Table: {Object_Number_n: {'VertexAddress': INT, 'VertexNumber': INT, 'NormalAddress': INT, 'NormalNumber': INT,
                              'PrimitiveAddress': INT, 'PrimitiveNumber': INT, 'Scale': INT}}}\n\n
        {'Object_Number_n': {'Vertex_Number_n': {'VecX': FLOAT, 'VecY': FLOAT, 'VecZ': FLOAT}}}\n\n
        {'Object_Number_n': {'Normal_Number_n': {'VecX': FLOAT, 'VecY': FLOAT, 'VecZ': FLOAT}}}\n\n
        {'Object_Number_n': {'Primitive_Number_n': 'Primitive_Type_Name': {COLOR AND INDICES = INT, UV = FLOAT, CONFIGURATIONS = BINARY}}}
        """
        bin_clean_type_list = self.file_data[0]
        number_objects = bin_clean_type_list[20:24] # IGNORING THE HEADER and the CC Container, WE KNOW WHICH TYPE IS || IGNORING FIXP AT LEAST NOT NEED TO READ MODEL FILES IN TLOD
        number_objects_int = int.from_bytes(number_objects, 'little', signed=False)
        model_data_end = bin_clean_type_list[24:]
        object_table_dict = self.split_object_table_tmd(number_objs=number_objects_int, model_data=model_data_end)
        vertex_data = binary_data_handler.BinaryDataModel(object_table=object_table_dict, binary_data=model_data_end, type_of_data='Vertex')
        normal_data = binary_data_handler.BinaryDataModel(object_table=object_table_dict, binary_data=model_data_end, type_of_data='Normal')
        primitive_data = binary_data_handler.BinaryDataModel(object_table=object_table_dict, binary_data=model_data_end, type_of_data='Primitive')

        arrage_vnp_data = self.vnp_data_arrager(object_number=number_objects_int, vertex_data=vertex_data.model_converted, normal_data=normal_data.model_converted, primitive_data=primitive_data.model_converted)

        tmd_final_dict = {'Format': 'TMD_Standard', 'Data_Table': object_table_dict, 
                          'Converted_Data': arrage_vnp_data}
        
        self.model_converted_data = tmd_final_dict

    def split_cc_saf(self):
        """
        This method takes the Binary Data from a CContainer SAF and after split their binary Data,
        converter it into Human readable data. Since Animations have other Structure,
        how this are converted it's slightly different from Models.\n\n\n
        This Example will show the Dictionary Nesting to Hold the data\n
        {Object Table: {Object_Number_n: {'VertexAddress': INT, 'VertexNumber': INT, 'NormalAddress': INT, 'NormalNumber': INT,
                              'PrimitiveAddress': INT, 'PrimitiveNumber': INT, 'Scale': INT}}}\n\n
        """
        bin_clean_type_list = self.file_data[0]
        if b'BPE\x1a' in bin_clean_type_list[0:12]:
            # WORK ON BPE FILE, HERE EXECUTE BPE UNPACKING
            print('Find a BPE\'ed Animation')
            un_bpe_animation = decompress_bpe.BpeFile(binary_data_bpe=bin_clean_type_list)
            bin_clean_type_list = un_bpe_animation.decoded_bpe

        animation_binary_data = bin_clean_type_list[12:]
        saf_animation_converted = binary_data_handler.BinaryDataAnimation(binary_data=animation_binary_data, animation_type='SAF')
        self.animation_converted_data = saf_animation_converted.animation_converted

    def split_texture(self, texture_format=str):
        """
        This method takes the Binary Data from a TIM/PXL/MCQ File and after split their binary Data,
        converter it into Human readable data. Since Textures have other Structure,
        how this are converted it's slightly different from Models or Animations.\n\n\n
        This Example will show the Dictionary Nesting to Hold the data\n
        {Texture_Name: {}\n\n
        """
        bin_clean_type_list = self.file_data[0]
        tim_texture_converted = binary_data_handler.BinaryDataTexture(binary_data=bin_clean_type_list, type_of_texture=texture_format)
        self.texture_converted_data = tim_texture_converted.texture_converted

    def split_object_table_tmd(self, number_objs=int, model_data=bytes) -> dict:
        """
        Will Split the Object Tables present in all the TMD and CTMD Files
        :param 1: -> number of objects
        :param 2: -> Model Data
        :return: split_object_table_tmd() -> Object Table Dict
        """
        object_table: dict = {}
        calculate_total_length_table = number_objs * 28
        table_in_binary: bytes = model_data[0:calculate_total_length_table]
        
        start_slice = 0
        for obj_num in range(0, number_objs):
            this_object = f'Object_Number_{obj_num}'
            
            this_obj_table = table_in_binary[start_slice : (start_slice + 28)]
            obj_vertex_address = int.from_bytes(this_obj_table[0:4], 'little', signed=False)
            obj_vertex_num = int.from_bytes(this_obj_table[4:8], 'little', signed=False)
            obj_normal_address = int.from_bytes(this_obj_table[8:12], 'little', signed=False)
            obj_normal_num = int.from_bytes(this_obj_table[12:16], 'little', signed=False)
            obj_primitives_address = int.from_bytes(this_obj_table[16:20], 'little', signed=False)
            obj_primitives_num = int.from_bytes(this_obj_table[20:24], 'little', signed=False)
            obj_scale = int.from_bytes(this_obj_table[24:28], 'little', signed=False)
            
            composed_table = {f'VertexAddress': obj_vertex_address, f'VertexNumber': obj_vertex_num,
                              f'NormalAddress': obj_normal_address, f'NormalNumber': obj_normal_num,
                              f'PrimitiveAddress': obj_primitives_address, f'PrimitiveNumber': obj_primitives_num,
                              f'Scale': obj_scale}
            
            object_table.update({f'{this_object}': composed_table})
            start_slice += 28

        return object_table
    
    def vnp_data_arrager(self, object_number=int, vertex_data=dict, normal_data=dict, primitive_data=dict) -> dict:
        """
        Vertex-Normal-Primitive Data arrager:\n
        This will arrage the three types of data to be sort in objects\n
        {{Object_0: Vertex_0, Normal_0, Primitives_0}, {Object_n: Vertex_n, Normal_n, Primitives_n}}
        """
        final_objects_dict: dict = {}

        for current_object_number in range(0, object_number):
            get_current_vertex = vertex_data.get(f'Object_Number_{current_object_number}')
            get_current_normal = normal_data.get(f'Object_Number_{current_object_number}')
            get_current_primitives = primitive_data.get(f'Object_Number_{current_object_number}')
            new_dict_sort: dict = {f'Object_Number_{current_object_number}': 
                                   {'Vertex': get_current_vertex, 
                                    'Normal': get_current_normal, 
                                    'Primitives': get_current_primitives}}
            final_objects_dict.update(new_dict_sort)
            
        return final_objects_dict