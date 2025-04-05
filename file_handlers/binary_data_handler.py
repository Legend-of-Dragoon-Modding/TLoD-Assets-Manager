"""

Binary Data Handler:
This module will take Binary Data and manipulate it\n
to get human readable format or simply split data
--------------------------------------------------------------------------------------------------------------
Input file:  = Binary Data BYTES, Requeried Data
--------------------------------------------------------------------------------------------------------------
:RETURN: -> self.binary_data_converted = {MANIPULATED/CONVERTED Binary Data}
--------------------------------------------------------------------------------------------------------------
Copyright (C) 2024 DooMMetaL

"""
from PyQt6.QtWidgets import QMessageBox
from typing import Any
CONVERT_5_TO_8_BIT = [0, 8, 16, 25, 33, 41, 49, 58, 66, 74, 82, 90, 99, 107, 115, 123, 132, 140, 148, 156, 165, 173, 181, 189, 197, 206, 214, 222, 230, 239, 247, 255]

class BinaryDataModel:
    def __init__(self, object_table=dict, binary_data=bytes, type_of_data=str) -> None:
        self.binary_data = binary_data
        self.object_table = object_table
        self.type_of_data = type_of_data
        self.model_converted: dict = {}
        self.convert_data_from_bin()
    
    def convert_data_from_bin(self) -> None:
        self.get_this_address_from_dict: str = ''
        self.get_this_number_from_dict: str = ''
        self.get_this_last_address_from_dict: str = ''
        
        if self.type_of_data == 'Vertex':
            self.get_this_address_from_dict = f'VertexAddress'
            self.get_this_number_from_dict = f'VertexNumber'
            self.get_this_last_address_from_dict = f'NormalAddress'
        elif self.type_of_data == 'Normal':
            self.get_this_address_from_dict = f'NormalAddress'
            self.get_this_number_from_dict = f'NormalNumber'
            self.get_this_last_address_from_dict = f'NormalAddress'
        elif self.type_of_data == 'Primitive':
            self.get_this_address_from_dict = f'PrimitiveAddress'
            self.get_this_number_from_dict = f'PrimitiveNumber'
            self.get_this_last_address_from_dict = f'VertexAddress'
        else:
            print(f'ERROR!!--> Binary: {self.type_of_data} type, is not currently supported for handling!!')
            exit()
        
        data_address, data_quantity = self.get_data_address_quantity()
        data_slices = self.calculate_data_slices(addresses=data_address)
        data_split_blocks = self.convert_blocks(data_slices=data_slices, data_quantity=data_quantity)
        self.model_converted = data_split_blocks
    
    def get_data_address_quantity(self) -> tuple[list, list]:
        data_address: list = []
        data_quantity: list = []
        
        for object_in_table in self.object_table:
            this_object: dict = self.object_table.get(f'{object_in_table}')
            this_data_address = this_object.get(f'{self.get_this_address_from_dict}')
            this_data_number = this_object.get(f'{self.get_this_number_from_dict}')
            data_address.append(this_data_address)
            data_quantity.append(this_data_number)

        return data_address, data_quantity
    
    def calculate_data_slices(self, addresses=list) -> list:
        data_slice_calculated: list = []

        total_number_objects = len(addresses)
        for object_num in range(0, total_number_objects):
            if object_num != (total_number_objects - 1):
                calculated_slice = [addresses[object_num], addresses[object_num + 1]]
                data_slice_calculated.append(calculated_slice)
            else:
                get_last_address = self.object_table.get(f'Object_Number_0')
                last_address = get_last_address.get(f'{self.get_this_last_address_from_dict}')
                calculated_slice = [addresses[object_num], last_address]
                data_slice_calculated.append(calculated_slice)

        return data_slice_calculated
    
    def convert_blocks(self, data_slices=list, data_quantity=list) -> dict:
        data_converted: dict = {}
        object_number = len(data_quantity)
        
        for current_object in range(0, object_number):
            current_object_name = f'Object_Number_{current_object}'
            
            current_slices = data_slices[current_object]
            start_slice = current_slices[0]
            end_slice = current_slices[1]
            
            if start_slice < end_slice:
                current_block = self.binary_data[start_slice:end_slice]
            else:
                current_block = self.binary_data[start_slice:]

            converted_block: dict = {}
            if self.type_of_data == 'Primitive':
                converted_block = self.convert_primitive_block(bin_block=current_block, current_quantity=data_quantity[current_object], current_obj_num=current_object)
            else:
                converted_block = self.convert_vectors_block(bin_block=current_block, current_quantity=data_quantity[current_object], current_obj_num=current_object)
            
            data_converted.update({f'{current_object_name}': converted_block})

        return data_converted

    def convert_vectors_block(self, bin_block=bytes, current_quantity=int, current_obj_num=int) -> dict:
        data_dict: dict = {}
        
        if (current_quantity == 0) and (self.type_of_data == 'Normal'):
            name = f'{self.type_of_data}_Number_0'
            vector_converted = {'VecX': 0.0, 'VecY': 0.0, 'VecZ': 0.0}
            data_dict.update({f'{name}': vector_converted})
            print(f'This model in Object {current_obj_num}, have totally bugged {self.type_of_data} block Fixing it right now!')
            current_quantity = 1
        else:
            vector_slice = 0
            for current_vectors in range(0, current_quantity):
                name = f'{self.type_of_data}_Number_{current_vectors}'
                vector_block = bin_block[vector_slice : (vector_slice + 8)]
                vect_x, vect_y, vect_z = self.convert_3points_vector(v_block=vector_block)
                vector_converted = {'VecX': vect_x, 'VecY': vect_y, 'VecZ': vect_z}
                data_dict.update({f'{name}': vector_converted})
                vector_slice += 8
        
        number_data_block_converted = len(data_dict)
        if number_data_block_converted != current_quantity: # Just a sanity check if i need to fix some model... sorry user :')
            print(f'This model in Object {current_obj_num}, have totally bugged {self.type_of_data} block:\nexpected: {current_quantity}; obtained: {number_data_block_converted}')
        
        return data_dict
    
    def convert_3points_vector(self, v_block=bytes) -> tuple[float, float, float]:
        """
        Convert Each Vertex Vector [X, Y, Z] and applying it's desired Scale\n(before this one of the last step, i change this right now)
        """
        if self.type_of_data == 'Normal':
            vector_x: float = int.from_bytes(v_block[0:2], 'little', signed=True) / 4096
            vector_y: float = int.from_bytes(v_block[2:4], 'little', signed=True) / 4096
            vector_z: float = int.from_bytes(v_block[4:6], 'little', signed=True) / 4096
        else:
            vector_x: float = int.from_bytes(v_block[0:2], 'little', signed=True) / 1000
            vector_y: float = int.from_bytes(v_block[2:4], 'little', signed=True) / 1000
            vector_z: float = int.from_bytes(v_block[4:6], 'little', signed=True) / 1000

        return vector_x, vector_y, vector_z
    
    def convert_primitive_block(self, bin_block=bytes, current_quantity=int, current_obj_num=int) -> dict:
        """This monster here will Convert the Primitive Packet data into Readable human format"""
        primitive_dict: dict = {}
        next_primitive_in_array = 0
        for this_primitive in range(0, current_quantity):
            decoded_primitive: dict = {f'Prim_Num_{this_primitive}': {}}
            current_primitive = bin_block[next_primitive_in_array:]
            primitive_packet_header = current_primitive[0:4]
            olen = primitive_packet_header[0] # Currently not used and i think will ever use it lol
            ilen = 0 #primitive_packet_header[1] // I don't need this
            flag = primitive_packet_header[2]
            mode = primitive_packet_header[3]

            # FLAG
            key_light_name = f''
            face_var = f'' # Calculated but not used at the moment
            grad_var = f''
            # MODE
            brigth_var = f'' # Calculated but not used at the moment
            translucency_var = f'' # Calculated but not used at the moment ||| can i use this value??
            texture_var = f''
            vertex_var = f''
            shading_var = f''
            
            # FLAG Calcs
            if (flag & (1 << 0)): # NLSC (the bits 3 to 7 are ignored in this case)
                key_light_name = f'NLSC_'
            else: # LSC
                key_light_name = f'LSC_'
            
            if (flag & (1 << 1)):
                face_var = f'double_face'
            else:
                face_var = f'single_face'
            
            if (flag & (1 << 2)):
                grad_var = f'Gradation_'
            else:
                grad_var = f'Solid_'
            
            # MODE Calcs (the bits 5 to 7 are ignored in this case)
            if (mode & (1 << 0)):
                brigth_var = f'BRIGHT OFF'
            else:
                brigth_var = f' BRIGHT ON'
            
            if (mode & (1 << 1)):
                translucency_var = f'Translucent'
            else:
                translucency_var = f'No-Translucent'
            
            if (mode & (1 << 2)):
                texture_var = f'Texture_'
            else:
                texture_var = f'No-Texture_'
            
            if (mode & (1 << 3)):
                vertex_var = f'4Vertex_'
            else:
                vertex_var = f'3Vertex_'
            
            if (mode & (1 << 4)):
                shading_var = f'Gouraud_'
            else:
                shading_var = f'Flat_'
            
            # Setting Primitive Name
            prim_name_key = f'{key_light_name}{vertex_var}{shading_var}{texture_var}{grad_var}{translucency_var}'

            decoded_data_in_primitive: dict = {}
            if key_light_name == f'LSC_':
                if vertex_var == f'3Vertex_':
                    if (texture_var == 'No-Texture_') and (shading_var == f'Gouraud_') and (grad_var == f'Solid_'):
                        decoded_data_in_primitive = {
                        f'r0': int.from_bytes(current_primitive[4:5], byteorder='little'), f'g0': int.from_bytes(current_primitive[5:6], byteorder='little'), f'b0': int.from_bytes(current_primitive[6:7], byteorder='little'), f'mode_val': current_primitive[7:8], 
                        f'normal0': int.from_bytes(current_primitive[8:10], byteorder='little'), f'vertex0': int.from_bytes(current_primitive[10:12], byteorder='little'), 
                        f'normal1': int.from_bytes(current_primitive[12:14], byteorder='little'), f'vertex1': int.from_bytes(current_primitive[14:16], byteorder='little'), 
                        f'normal2': int.from_bytes(current_primitive[16:18], byteorder='little'), f'vertex2': int.from_bytes(current_primitive[18:20], byteorder='little')}
                        ilen = 4
                    
                    elif (texture_var == 'No-Texture_') and (shading_var == f'Flat_') and (grad_var == f'Solid_'):
                        decoded_data_in_primitive = {
                        f'r0': int.from_bytes(current_primitive[4:5], byteorder='little'), f'g0': int.from_bytes(current_primitive[5:6], byteorder='little'), f'b0': int.from_bytes(current_primitive[6:7], byteorder='little'), f'mode_val': current_primitive[7:8], 
                        f'normal0': int.from_bytes(current_primitive[8:10], byteorder='little'), f'vertex0': int.from_bytes(current_primitive[10:12], byteorder='little'), 
                        f'vertex1': int.from_bytes(current_primitive[12:14], byteorder='little'), f'vertex2': int.from_bytes(current_primitive[14:16], byteorder='little')}
                        ilen = 3
                    
                    elif (texture_var == 'No-Texture_') and (shading_var == f'Gouraud_') and (grad_var == f'Gradation_'):
                        decoded_data_in_primitive = {
                        f'r0': int.from_bytes(current_primitive[4:5], byteorder='little'), f'g0': int.from_bytes(current_primitive[5:6], byteorder='little'), f'b0': int.from_bytes(current_primitive[6:7], byteorder='little'), f'mode_val': current_primitive[7:8], 
                        f'r1': int.from_bytes(current_primitive[8:9], byteorder='little'), f'g1': int.from_bytes(current_primitive[9:10], byteorder='little'), f'b1': int.from_bytes(current_primitive[10:11], byteorder='little'), f'pad_val0': current_primitive[11:12], 
                        f'r2': int.from_bytes(current_primitive[12:13], byteorder='little'), f'g2': int.from_bytes(current_primitive[13:14], byteorder='little'), f'b2': int.from_bytes(current_primitive[14:15], byteorder='little'), f'pad_val1': current_primitive[15:16], 
                        f'normal0': int.from_bytes(current_primitive[16:18], byteorder='little'), f'vertex0': int.from_bytes(current_primitive[18:20], byteorder='little'), 
                        f'normal1': int.from_bytes(current_primitive[20:22], byteorder='little'), f'vertex1': int.from_bytes(current_primitive[22:24], byteorder='little'), 
                        f'normal2': int.from_bytes(current_primitive[24:26], byteorder='little'), f'vertex2': int.from_bytes(current_primitive[26:28], byteorder='little')}
                        ilen = 6
                    
                    elif (texture_var == 'No-Texture_') and (shading_var == f'Flat_') and (grad_var == f'Gradation_'):
                        decoded_data_in_primitive = {
                        f'r0': int.from_bytes(current_primitive[4:5], byteorder='little'), f'g0': int.from_bytes(current_primitive[5:6], byteorder='little'), f'b0': int.from_bytes(current_primitive[6:7], byteorder='little'), f'mode_val': current_primitive[7:8], 
                        f'r1': int.from_bytes(current_primitive[8:9], byteorder='little'), f'g1': int.from_bytes(current_primitive[9:10], byteorder='little'), f'b1': int.from_bytes(current_primitive[10:11], byteorder='little'), f'pad_val0': current_primitive[11:12], 
                        f'r2': int.from_bytes(current_primitive[12:13], byteorder='little'), f'g2': int.from_bytes(current_primitive[13:14], byteorder='little'), f'b2': int.from_bytes(current_primitive[14:15], byteorder='little'), f'pad_val1': current_primitive[15:16], 
                        f'normal0': int.from_bytes(current_primitive[16:18], byteorder='little'), f'vertex0': int.from_bytes(current_primitive[18:20], byteorder='little'),
                        f'vertex1': int.from_bytes(current_primitive[20:22], byteorder='little'), f'vertex2': int.from_bytes(current_primitive[22:24], byteorder='little')}
                        ilen = 5
                    
                    elif (texture_var == 'Texture_') and (shading_var == f'Gouraud_'):
                        decoded_data_in_primitive = {
                        f'u0': (int.from_bytes(current_primitive[4:5], byteorder='little') / 256), f'v0': (int.from_bytes(current_primitive[5:6], byteorder='little') / 256), f'cba': current_primitive[6:8], 
                        f'u1': (int.from_bytes(current_primitive[8:9], byteorder='little') / 256), f'v1': (int.from_bytes(current_primitive[9:10], byteorder='little') / 256), f'tsb': current_primitive[10:12], 
                        f'u2': (int.from_bytes(current_primitive[12:13], byteorder='little') / 256), f'v2': (int.from_bytes(current_primitive[13:14], byteorder='little') / 256), f'pad_value0': current_primitive[14:16], 
                        f'normal0': int.from_bytes(current_primitive[16:18], byteorder='little'), f'vertex0': int.from_bytes(current_primitive[18:20], byteorder='little'), 
                        f'normal1': int.from_bytes(current_primitive[20:22], byteorder='little'), f'vertex1': int.from_bytes(current_primitive[22:24], byteorder='little'), 
                        f'normal2': int.from_bytes(current_primitive[24:26], byteorder='little'), f'vertex2': int.from_bytes(current_primitive[26:28], byteorder='little')}
                        ilen = 6
                    
                    elif (texture_var == 'Texture_') and (shading_var == f'Flat_'):
                        decoded_data_in_primitive = {
                        f'u0': (int.from_bytes(current_primitive[4:5], byteorder='little') / 256), f'v0': (int.from_bytes(current_primitive[5:6], byteorder='little') / 256), f'cba': current_primitive[6:8], 
                        f'u1': (int.from_bytes(current_primitive[8:9], byteorder='little') / 256), f'v1': (int.from_bytes(current_primitive[9:10], byteorder='little') / 256), f'tsb': current_primitive[10:12], 
                        f'u2': (int.from_bytes(current_primitive[12:13], byteorder='little') / 256), f'v2': (int.from_bytes(current_primitive[13:14], byteorder='little') / 256), f'pad_value0': current_primitive[14:16], 
                        f'normal0': int.from_bytes(current_primitive[16:18], byteorder='little'), f'vertex0': int.from_bytes(current_primitive[18:20], byteorder='little'), 
                        f'vertex1': int.from_bytes(current_primitive[20:22], byteorder='little'), f'vertex2': int.from_bytes(current_primitive[22:24], byteorder='little')}
                        ilen = 5
                    
                elif vertex_var == f'4Vertex_':
                    if (texture_var == 'No-Texture_') and (shading_var == f'Gouraud_') and (grad_var == f'Solid_'):
                        decoded_data_in_primitive = {
                        f'r0': int.from_bytes(current_primitive[4:5], byteorder='little'), f'g0': int.from_bytes(current_primitive[5:6], byteorder='little'), f'b0': int.from_bytes(current_primitive[6:7], byteorder='little'), f'mode_val': current_primitive[7:8], 
                        f'normal0': int.from_bytes(current_primitive[8:10], byteorder='little'), f'vertex0': int.from_bytes(current_primitive[10:12], byteorder='little'), 
                        f'normal1': int.from_bytes(current_primitive[12:14], byteorder='little'), f'vertex1': int.from_bytes(current_primitive[14:16], byteorder='little'), 
                        f'normal2': int.from_bytes(current_primitive[16:18], byteorder='little'), f'vertex2': int.from_bytes(current_primitive[18:20], byteorder='little'),
                        f'normal3': int.from_bytes(current_primitive[20:22], byteorder='little'), f'vertex3': int.from_bytes(current_primitive[22:24], byteorder='little')}
                        ilen = 5

                    elif (texture_var == 'No-Texture_') and (shading_var == f'Flat_') and (grad_var == f'Solid_'):
                        decoded_data_in_primitive = {
                        f'r0': int.from_bytes(current_primitive[4:5], byteorder='little'), f'g0': int.from_bytes(current_primitive[5:6], byteorder='little'), f'b0': int.from_bytes(current_primitive[6:7], byteorder='little'), f'mode_val': current_primitive[7:8], 
                        f'normal0': int.from_bytes(current_primitive[8:10], byteorder='little'), f'vertex0': int.from_bytes(current_primitive[10:12], byteorder='little'), 
                        f'vertex1': int.from_bytes(current_primitive[12:14], byteorder='little'), f'vertex2': int.from_bytes(current_primitive[14:16], byteorder='little'),
                        f'vertex3': int.from_bytes(current_primitive[16:18], byteorder='little'), f'pad_value0': int.from_bytes(current_primitive[18:20], byteorder='little')}
                        ilen = 4
                    
                    elif (texture_var == 'No-Texture_') and (shading_var == f'Gouraud_') and (grad_var == f'Gradation_'):
                        decoded_data_in_primitive = {
                        f'r0': int.from_bytes(current_primitive[4:5], byteorder='little'), f'g0': int.from_bytes(current_primitive[5:6], byteorder='little'), f'b0': int.from_bytes(current_primitive[6:7], byteorder='little'), f'mode_val': current_primitive[7:8], 
                        f'r1': int.from_bytes(current_primitive[8:9], byteorder='little'), f'g1': int.from_bytes(current_primitive[9:10], byteorder='little'), f'b1': int.from_bytes(current_primitive[10:11], byteorder='little'), f'pad_val0': current_primitive[11:12], 
                        f'r2': int.from_bytes(current_primitive[12:13], byteorder='little'), f'g2': int.from_bytes(current_primitive[13:14], byteorder='little'), f'b2': int.from_bytes(current_primitive[14:15], byteorder='little'), f'pad_val1': current_primitive[15:16], 
                        f'r3': int.from_bytes(current_primitive[16:17], byteorder='little'), f'g3': int.from_bytes(current_primitive[17:18], byteorder='little'), f'b3': int.from_bytes(current_primitive[18:19], byteorder='little'), f'pad_val2': current_primitive[19:20], 
                        f'normal0': int.from_bytes(current_primitive[20:22], byteorder='little'), f'vertex0': int.from_bytes(current_primitive[22:24], byteorder='little'), 
                        f'normal1': int.from_bytes(current_primitive[24:26], byteorder='little'), f'vertex1': int.from_bytes(current_primitive[26:28], byteorder='little'), 
                        f'normal2': int.from_bytes(current_primitive[28:30], byteorder='little'), f'vertex2': int.from_bytes(current_primitive[30:32], byteorder='little'),
                        f'normal3': int.from_bytes(current_primitive[32:34], byteorder='little'), f'vertex3': int.from_bytes(current_primitive[34:36], byteorder='little')}
                        ilen = 8

                    elif (texture_var == 'No-Texture_') and (shading_var == f'Flat_') and (grad_var == f'Gradation_'):
                        decoded_data_in_primitive = {
                        f'r0': int.from_bytes(current_primitive[4:5], byteorder='little'), f'g0': int.from_bytes(current_primitive[5:6], byteorder='little'), f'b0': int.from_bytes(current_primitive[6:7], byteorder='little'), f'mode_val': current_primitive[7:8], 
                        f'r1': int.from_bytes(current_primitive[8:9], byteorder='little'), f'g1': int.from_bytes(current_primitive[9:10], byteorder='little'), f'b1': int.from_bytes(current_primitive[10:11], byteorder='little'), f'pad_val0': current_primitive[11:12], 
                        f'r2': int.from_bytes(current_primitive[12:13], byteorder='little'), f'g2': int.from_bytes(current_primitive[13:14], byteorder='little'), f'b2': int.from_bytes(current_primitive[14:15], byteorder='little'), f'pad_val1': current_primitive[15:16], 
                        f'r3': int.from_bytes(current_primitive[16:17], byteorder='little'), f'g3': int.from_bytes(current_primitive[17:18], byteorder='little'), f'b3': int.from_bytes(current_primitive[18:19], byteorder='little'), f'pad_val2': current_primitive[19:20], 
                        f'normal0': int.from_bytes(current_primitive[20:22], byteorder='little'), f'vertex0': int.from_bytes(current_primitive[22:24], byteorder='little'),
                        f'vertex1': int.from_bytes(current_primitive[24:26], byteorder='little'), f'vertex2': int.from_bytes(current_primitive[26:28], byteorder='little'), 
                        f'vertex3': int.from_bytes(current_primitive[28:30], byteorder='little'), f'pad_val3': int.from_bytes(current_primitive[30:32], byteorder='little')}
                        ilen = 7
                        
                    elif (texture_var == 'Texture_') and (shading_var == f'Gouraud_'):
                        decoded_data_in_primitive = {
                        f'u0': (int.from_bytes(current_primitive[4:5], byteorder='little') / 256), f'v0': (int.from_bytes(current_primitive[5:6], byteorder='little') / 256), f'cba': current_primitive[6:8], 
                        f'u1': (int.from_bytes(current_primitive[8:9], byteorder='little') / 256), f'v1': (int.from_bytes(current_primitive[9:10], byteorder='little') / 256), f'tsb': current_primitive[10:12], 
                        f'u2': (int.from_bytes(current_primitive[12:13], byteorder='little') / 256), f'v2': (int.from_bytes(current_primitive[13:14], byteorder='little') / 256), f'pad_value0': current_primitive[14:16], 
                        f'u3': (int.from_bytes(current_primitive[16:17], byteorder='little') / 256), f'v3': (int.from_bytes(current_primitive[17:18], byteorder='little') / 256), f'pad_value1': current_primitive[18:20], 
                        f'normal0': int.from_bytes(current_primitive[20:22], byteorder='little'), f'vertex0': int.from_bytes(current_primitive[22:24], byteorder='little'), 
                        f'normal1': int.from_bytes(current_primitive[24:26], byteorder='little'), f'vertex1': int.from_bytes(current_primitive[26:28], byteorder='little'), 
                        f'normal2': int.from_bytes(current_primitive[28:30], byteorder='little'), f'vertex2': int.from_bytes(current_primitive[30:32], byteorder='little'), 
                        f'normal3': int.from_bytes(current_primitive[32:34], byteorder='little'), f'vertex3': int.from_bytes(current_primitive[34:36], byteorder='little')}
                        ilen = 8
                    
                    elif (texture_var == 'Texture_') and (shading_var == f'Flat_'):
                        decoded_data_in_primitive = {
                        f'u0': (int.from_bytes(current_primitive[4:5], byteorder='little') / 256), f'v0': (int.from_bytes(current_primitive[5:6], byteorder='little') / 256), f'cba': current_primitive[6:8], 
                        f'u1': (int.from_bytes(current_primitive[8:9], byteorder='little') / 256), f'v1': (int.from_bytes(current_primitive[9:10], byteorder='little') / 256), f'tsb': current_primitive[10:12], 
                        f'u2': (int.from_bytes(current_primitive[12:13], byteorder='little') / 256), f'v2': (int.from_bytes(current_primitive[13:14], byteorder='little') / 256), f'pad_value0': current_primitive[14:16], 
                        f'u3': (int.from_bytes(current_primitive[16:17], byteorder='little') / 256), f'v3': (int.from_bytes(current_primitive[17:18], byteorder='little') / 256), f'pad_value1': current_primitive[18:20], 
                        f'normal0': int.from_bytes(current_primitive[20:22], byteorder='little'), f'vertex0': int.from_bytes(current_primitive[22:24], byteorder='little'), 
                        f'vertex1': int.from_bytes(current_primitive[24:26], byteorder='little'), f'vertex2': int.from_bytes(current_primitive[26:28], byteorder='little'), 
                        f'vertex3': int.from_bytes(current_primitive[28:30], byteorder='little'), f'pad_value2': int.from_bytes(current_primitive[30:32], byteorder='little')}
                        ilen = 7
                
                else:
                    no_vertex_primitive_lsc = f'Not reading a Vertex Primitive Data (LSC)... exiting...'
                    error_vertex_lsc = QMessageBox.critical(None, 'CRITICAL ERROR!!', f'FATAL!!:\n{no_vertex_primitive_lsc}', QMessageBox.StandardButton.Ok)
                    exit()

            elif key_light_name == f'NLSC_':
                if vertex_var == f'3Vertex_':
                    if (texture_var == 'No-Texture_') and (shading_var == f'Gouraud_'):
                        decoded_data_in_primitive = {
                        f'r0': int.from_bytes(current_primitive[4:5], byteorder='little'), f'g0': int.from_bytes(current_primitive[5:6], byteorder='little'), f'b0': int.from_bytes(current_primitive[6:7], byteorder='little'), f'mode_val': current_primitive[7:8], 
                        f'r1': int.from_bytes(current_primitive[8:9], byteorder='little'), f'g1': int.from_bytes(current_primitive[9:10], byteorder='little'), f'b1': int.from_bytes(current_primitive[10:11], byteorder='little'), f'pad_val0': current_primitive[11:12], 
                        f'r2': int.from_bytes(current_primitive[12:13], byteorder='little'), f'g2': int.from_bytes(current_primitive[13:14], byteorder='little'), f'b2': int.from_bytes(current_primitive[14:15], byteorder='little'), f'pad_val1': current_primitive[15:16], 
                        f'vertex0': int.from_bytes(current_primitive[16:18], byteorder='little'), f'vertex1': int.from_bytes(current_primitive[18:20], byteorder='little'), 
                        f'vertex2': int.from_bytes(current_primitive[20:22], byteorder='little'), f'pad_value1': current_primitive[22:24]}
                        ilen = 5
                    
                    elif (texture_var == 'No-Texture_') and (shading_var == f'Flat_'):
                        decoded_data_in_primitive = {
                        f'r0': int.from_bytes(current_primitive[4:5], byteorder='little'), f'g0': int.from_bytes(current_primitive[5:6], byteorder='little'), f'b0': int.from_bytes(current_primitive[6:7], byteorder='little'), f'mode_val': current_primitive[7:8], 
                        f'vertex0': int.from_bytes(current_primitive[8:10], byteorder='little'), f'vertex1': int.from_bytes(current_primitive[10:12], byteorder='little'), 
                        f'vertex2': int.from_bytes(current_primitive[12:14], byteorder='little'), f'pad_val0': int.from_bytes(current_primitive[14:16], byteorder='little')}
                        ilen = 3
                    
                    elif (texture_var == 'Texture_') and (shading_var == f'Gouraud_'):
                        decoded_data_in_primitive = {
                        f'u0': (int.from_bytes(current_primitive[4:5], byteorder='little') / 256), f'v0': (int.from_bytes(current_primitive[5:6], byteorder='little') / 256), f'cba': current_primitive[6:8], 
                        f'u1': (int.from_bytes(current_primitive[8:9], byteorder='little') / 256), f'v1': (int.from_bytes(current_primitive[9:10], byteorder='little') / 256), f'tsb': current_primitive[10:12], 
                        f'u2': (int.from_bytes(current_primitive[12:13], byteorder='little') / 256), f'v2': (int.from_bytes(current_primitive[13:14], byteorder='little') / 256), f'pad_value0': current_primitive[14:16], 
                        f'r0': int.from_bytes(current_primitive[16:17], byteorder='little'), f'g0': int.from_bytes(current_primitive[17:18], byteorder='little'), f'b0': int.from_bytes(current_primitive[18:19], byteorder='little'), f'pad_val1': current_primitive[19:20], 
                        f'r1': int.from_bytes(current_primitive[20:21], byteorder='little'), f'g1': int.from_bytes(current_primitive[21:22], byteorder='little'), f'b1': int.from_bytes(current_primitive[22:23], byteorder='little'), f'pad_val2': current_primitive[23:24], 
                        f'r2': int.from_bytes(current_primitive[24:25], byteorder='little'), f'g2': int.from_bytes(current_primitive[25:26], byteorder='little'), f'b2': int.from_bytes(current_primitive[26:27], byteorder='little'), f'pad_val3': current_primitive[27:28],
                        f'vertex0': int.from_bytes(current_primitive[28:30], byteorder='little'), f'vertex1': int.from_bytes(current_primitive[30:32], byteorder='little'), 
                        f'vertex2': int.from_bytes(current_primitive[32:34], byteorder='little'), f'pad_val4': int.from_bytes(current_primitive[34:36], byteorder='little')}
                        ilen = 8
                    
                    elif (texture_var == 'Texture_') and (shading_var == f'Flat_'):
                        decoded_data_in_primitive = {
                        f'u0': (int.from_bytes(current_primitive[4:5], byteorder='little') / 256), f'v0': (int.from_bytes(current_primitive[5:6], byteorder='little') / 256), f'cba': current_primitive[6:8], 
                        f'u1': (int.from_bytes(current_primitive[8:9], byteorder='little') / 256), f'v1': (int.from_bytes(current_primitive[9:10], byteorder='little') / 256), f'tsb': current_primitive[10:12], 
                        f'u2': (int.from_bytes(current_primitive[12:13], byteorder='little') / 256), f'v2': (int.from_bytes(current_primitive[13:14], byteorder='little') / 256), f'pad_value0': current_primitive[14:16], 
                        f'r0': int.from_bytes(current_primitive[16:17], byteorder='little'), f'g0': int.from_bytes(current_primitive[17:18], byteorder='little'), f'b0': int.from_bytes(current_primitive[18:19], byteorder='little'), f'pad_val1': current_primitive[19:20], 
                        f'vertex0': int.from_bytes(current_primitive[20:22], byteorder='little'), f'vertex1': int.from_bytes(current_primitive[22:24], byteorder='little'), 
                        f'vertex2': int.from_bytes(current_primitive[24:26], byteorder='little'), f'pad_value2': int.from_bytes(current_primitive[26:28], byteorder='little')}
                        ilen = 6
                
                elif vertex_var == f'4Vertex_':
                    if (texture_var == 'No-Texture_') and (shading_var == f'Gouraud_'):
                        decoded_data_in_primitive = {
                        f'r0': int.from_bytes(current_primitive[4:5], byteorder='little'), f'g0': int.from_bytes(current_primitive[5:6], byteorder='little'), f'b0': int.from_bytes(current_primitive[6:7], byteorder='little'), f'mode_val': current_primitive[7:8], 
                        f'r1': int.from_bytes(current_primitive[8:9], byteorder='little'), f'g1': int.from_bytes(current_primitive[9:10], byteorder='little'), f'b1': int.from_bytes(current_primitive[10:11], byteorder='little'), f'pad_val0': current_primitive[11:12], 
                        f'r2': int.from_bytes(current_primitive[12:13], byteorder='little'), f'g2': int.from_bytes(current_primitive[13:14], byteorder='little'), f'b2': int.from_bytes(current_primitive[14:15], byteorder='little'), f'pad_val1': current_primitive[15:16], 
                        f'r3': int.from_bytes(current_primitive[16:17], byteorder='little'), f'g3': int.from_bytes(current_primitive[17:18], byteorder='little'), f'b3': int.from_bytes(current_primitive[18:19], byteorder='little'), f'pad_val2': current_primitive[19:20], 
                        f'vertex0': int.from_bytes(current_primitive[20:22], byteorder='little'), f'vertex1': int.from_bytes(current_primitive[22:24], byteorder='little'), 
                        f'vertex2': int.from_bytes(current_primitive[24:26], byteorder='little'), f'vertex3': current_primitive[26:28]}
                        ilen = 6
                    
                    elif (texture_var == 'No-Texture_') and (shading_var == f'Flat_'):
                        decoded_data_in_primitive = {
                        f'r0': int.from_bytes(current_primitive[4:5], byteorder='little'), f'g0': int.from_bytes(current_primitive[5:6], byteorder='little'), f'b0': int.from_bytes(current_primitive[6:7], byteorder='little'), f'mode_val': current_primitive[7:8], 
                        f'vertex0': int.from_bytes(current_primitive[8:10], byteorder='little'), f'vertex1': int.from_bytes(current_primitive[10:12], byteorder='little'), 
                        f'vertex2': int.from_bytes(current_primitive[12:14], byteorder='little'), f'vertex3': int.from_bytes(current_primitive[14:16], byteorder='little')}
                        ilen = 3
                    
                    elif (texture_var == 'Texture_') and (shading_var == f'Gouraud_'):
                        decoded_data_in_primitive = {
                        f'u0': (int.from_bytes(current_primitive[4:5], byteorder='little') / 256), f'v0': (int.from_bytes(current_primitive[5:6], byteorder='little') / 256), f'cba': current_primitive[6:8], 
                        f'u1': (int.from_bytes(current_primitive[8:9], byteorder='little') / 256), f'v1': (int.from_bytes(current_primitive[9:10], byteorder='little') / 256), f'tsb': current_primitive[10:12], 
                        f'u2': (int.from_bytes(current_primitive[12:13], byteorder='little') / 256), f'v2': (int.from_bytes(current_primitive[13:14], byteorder='little') / 256), f'pad_value0': current_primitive[14:16], 
                        f'u3': (int.from_bytes(current_primitive[16:17], byteorder='little') / 256), f'v3': (int.from_bytes(current_primitive[17:18], byteorder='little') / 256), f'pad_value1': current_primitive[18:20], 
                        f'r0': int.from_bytes(current_primitive[20:21], byteorder='little'), f'g0': int.from_bytes(current_primitive[21:22], byteorder='little'), f'b0': int.from_bytes(current_primitive[22:23], byteorder='little'), f'pad_val2': current_primitive[23:24], 
                        f'r1': int.from_bytes(current_primitive[24:25], byteorder='little'), f'g1': int.from_bytes(current_primitive[25:26], byteorder='little'), f'b1': int.from_bytes(current_primitive[26:27], byteorder='little'), f'pad_val3': current_primitive[27:28], 
                        f'r2': int.from_bytes(current_primitive[28:29], byteorder='little'), f'g2': int.from_bytes(current_primitive[29:30], byteorder='little'), f'b2': int.from_bytes(current_primitive[30:31], byteorder='little'), f'pad_val4': current_primitive[31:32], 
                        f'r3': int.from_bytes(current_primitive[32:33], byteorder='little'), f'g3': int.from_bytes(current_primitive[33:34], byteorder='little'), f'b3': int.from_bytes(current_primitive[34:35], byteorder='little'), f'pad_val5': current_primitive[35:36], 
                        f'vertex0': int.from_bytes(current_primitive[36:38], byteorder='little'), f'vertex1': int.from_bytes(current_primitive[38:40], byteorder='little'), 
                        f'vertex2': int.from_bytes(current_primitive[40:42], byteorder='little'), f'vertex3': int.from_bytes(current_primitive[42:44], byteorder='little')}
                        ilen = 10
                    
                    elif (texture_var == 'Texture_') and (shading_var == f'Flat_'):
                        decoded_data_in_primitive = {
                        f'u0': (int.from_bytes(current_primitive[4:5], byteorder='little') / 256), f'v0': (int.from_bytes(current_primitive[5:6], byteorder='little') / 256), f'cba': current_primitive[6:8], 
                        f'u1': (int.from_bytes(current_primitive[8:9], byteorder='little') / 256), f'v1': (int.from_bytes(current_primitive[9:10], byteorder='little') / 256), f'tsb': current_primitive[10:12], 
                        f'u2': (int.from_bytes(current_primitive[12:13], byteorder='little') / 256), f'v2': (int.from_bytes(current_primitive[13:14], byteorder='little') / 256), f'pad_value0': current_primitive[14:16], 
                        f'u3': (int.from_bytes(current_primitive[16:17], byteorder='little') / 256), f'v3': (int.from_bytes(current_primitive[17:18], byteorder='little') / 256), f'pad_value1': current_primitive[18:20], 
                        f'r0': int.from_bytes(current_primitive[20:21], byteorder='little'), f'g0': int.from_bytes(current_primitive[21:22], byteorder='little'), f'b0': int.from_bytes(current_primitive[22:23], byteorder='little'), f'pad_val2': current_primitive[23:24], 
                        f'vertex0': int.from_bytes(current_primitive[24:26], byteorder='little'), f'vertex1': int.from_bytes(current_primitive[26:28], byteorder='little'), 
                        f'vertex2': int.from_bytes(current_primitive[28:30], byteorder='little'), f'vertex3': int.from_bytes(current_primitive[30:32], byteorder='little')}
                        ilen = 7
                
                else:
                    no_vertex_primitive_nlsc = f'Not reading Vertex Primitive Data (NLSC)... exiting...'
                    error_vertex_nlsc = QMessageBox.critical(None, 'CRITICAL ERROR!!', f'FATAL!!:\n{no_vertex_primitive_nlsc}', QMessageBox.StandardButton.Ok)
                    exit()
            
            else:
                no_light_primitive= f'Not reading Primitive Data...\nObject Number: {current_obj_num}, Primitive Number: {this_primitive}, Current Packet Header: {primitive_packet_header}\nexiting...'
                no_defined_primitive = QMessageBox.critical(None, 'CRITICAL ERROR!!', f'FATAL!!:\n{no_light_primitive}', QMessageBox.StandardButton.Ok)
                exit()

            decoded_primitive[f'Prim_Num_{this_primitive}'].update({f'{prim_name_key}': decoded_data_in_primitive})
            primitive_dict.update(decoded_primitive)
            ilen_calc_next_header = (ilen * 4) + 4 # + 4 because it's the header of primitive itself
            next_primitive_in_array += ilen_calc_next_header
        return primitive_dict

class BinaryDataAnimation:
    def __init__(self, binary_data=dict, animation_type=str) -> None:
        self.binary_data = binary_data
        self.animation_type = animation_type
        self.animation_converted: dict = {}
        self.convert_animation()
    
    def convert_animation(self):
        if self.animation_type == 'SAF':
            saf_converted = self.convert_saf()
            self.animation_converted = saf_converted
        else:
            no_animation_converter = f'Animation Type: {self.animation_type}, have no Converter/Handler Implemented'
            error_no_conversion_animation = QMessageBox.critical(None, 'CRITICAL ERROR!!', f'FATAL!!:\n{no_animation_converter}', QMessageBox.StandardButton.Ok)
            exit()
    
    def convert_saf(self) -> dict:
        """Convert SAF data [Simple Animation File] into human readable data to be added to the model in the final conversion."""
        saf_animation_dict: dict = {}
        # First we need some information about the Animation Header (which is composed by a pair of 16Bit U_INT) first is the number of Objects and the Second is the total transformations done
        saf_objects = int.from_bytes(self.binary_data[0:2], 'little', signed=False)
        saf_transforms = int.from_bytes(self.binary_data[2:4], 'little', signed=False)
        # Now we get the complete Binary Data Block to be split later
        total_binary_block = self.binary_data[4:]
        # Then we split it into blocks
        length_each_block = saf_objects * 12 # 12 == 2 Bytes per each transform (rx,ry,rz,tx,ty,tz)
        # File size - Getting the length of the complete block, for further calculations
        block_size = len(total_binary_block)
        # Correlativity Objects/NumberFrames/Blocks
        coincidence = (block_size // length_each_block)

        if int(coincidence * 2) != (saf_transforms): # Multiply this coincidence, since transformations in SAF are split in ROT/LOC
            conversion_saf_error = f'There are no correlativity between Animation Frames and Blocks, Report this as Frame/Block not equal'
            conversion_saf_error_messsage = QMessageBox.critical(None, 'CRITICAL ERROR!!', f'FATAL!!:\n{conversion_saf_error}', QMessageBox.StandardButton.Ok)
            exit()
        
        transforms_split: dict[str, bytes] = {}
        saf_transforms_adjusted = saf_transforms // 2 # SAF Count both Transforms ROT/LOC, while the actual block is both combined
        start_block_read = 0
        for transform_block in range(0, saf_transforms_adjusted):
            this_block: bytes = total_binary_block[start_block_read : (start_block_read + length_each_block)]
            transforms_split.update({f'Transform_Number_{transform_block}': this_block})
            start_block_read += length_each_block
        
        saf_converted_dict: dict = {}
        for current_object in range(0, saf_objects):
            saf_converted_dict.update({f'Object_Number_{current_object}': {}})
        
        for this_transform in transforms_split:
            get_transform_block: bytes | Any = transforms_split.get(f'{this_transform}')
            next_object_block = 0
            for this_object in range(0, saf_objects):
                object_rot_trans = {
                    "Rx": float(int.from_bytes(get_transform_block[next_object_block : (next_object_block + 2)], 'little', signed=True) / round((4096/360), 12)),
                    "Ry": float(int.from_bytes(get_transform_block[(next_object_block + 2) : (next_object_block + 4)], 'little', signed=True) / round((4096/360), 12)),
                    "Rz": float(int.from_bytes(get_transform_block[(next_object_block + 4) : (next_object_block + 6)], 'little', signed=True) / round((4096/360), 12)),
                    "Tx": float(int.from_bytes(get_transform_block[(next_object_block + 6) : (next_object_block + 8)], 'little', signed=True) / 1000),
                    "Ty": float(int.from_bytes(get_transform_block[(next_object_block + 8) : (next_object_block + 10)], 'little', signed=True) / 1000),
                    "Tz": float(int.from_bytes(get_transform_block[(next_object_block + 10) : (next_object_block + 12)], 'little', signed=True) / 1000)}
                current_object_transform: dict = {f'{this_transform}': object_rot_trans}
                saf_converted_dict[f'Object_Number_{this_object}'].update(current_object_transform)
                next_object_block += 12
        saf_animation_dict = {'TotalTransforms': saf_transforms_adjusted, 'AnimationData': saf_converted_dict}
        return saf_animation_dict

class BinaryDataTexture:
    def __init__(self, binary_data=dict, type_of_texture=str) -> None:
        self.binary_data = binary_data
        self.type_of_texture = type_of_texture
        self.texture_converted: dict = {}
        self.convert_texture()
    
    def convert_texture(self):
        if self.type_of_texture == 'TIM':
            tim_file_decoded = self.convert_tim_file()
            self.texture_converted = tim_file_decoded
        elif self.type_of_texture == 'PXL':
            print('PXL FILE Not Implemented')
        elif self.type_of_texture == 'MCQ':
            mcq_file_decoded = self.convert_mcq_file()
            self.texture_converted = mcq_file_decoded
        else:
            no_texture_converter = f'Texture Type: {self.type_of_texture}, have no Converter/Handler Implemented'
            error_no_conversion_animation = QMessageBox.critical(None, 'CRITICAL ERROR!!', f'FATAL!!:\n{no_texture_converter}', QMessageBox.StandardButton.Ok)
            exit()
    
    def convert_tim_file(self) -> dict:
        tim_to_png: dict = {'SizeImg': {}, 'RGBA_Data': {}}

        tim_flag: dict = {'Pixel_Mode': '', 'is_CLUT': ''}
        tim_data: dict = {'CLUT': [], 'Pixel_Data': []}

        # READ TIM FLAGs
        flag_data = self.binary_data[4:8]
        flag_data_int = int.from_bytes(flag_data, byteorder='little', signed=False)
        flag_data_bin = bin(flag_data_int)
        split_pixeldata_check = int(flag_data_bin[3:], base=2)
        split_clut_check = int(flag_data_bin[2:3])
        
        if split_pixeldata_check == 0:
            tim_flag['Pixel_Mode'] = '4-bit CLUT'
        elif split_pixeldata_check == 1:
            tim_flag['Pixel_Mode'] = '8-bit CLUT'
        elif split_pixeldata_check == 2:
            tim_flag['Pixel_Mode'] = '16-bit Direct'
        elif split_pixeldata_check == 3:
            tim_flag['Pixel_Mode'] = '24-bit Direct'
        elif split_pixeldata_check == 4:
            tim_flag['Pixel_Mode'] = 'Mixed MODE'
        
        if split_clut_check == 1:
            tim_flag['is_CLUT'] = 'CLUT'
            read_clut_length = self.binary_data[8:12]
            clut_length = int.from_bytes(read_clut_length, byteorder='little', signed=False)
            tim_data_clut = self.binary_data[8:(clut_length + 8)]
            tim_data['CLUT'] = tim_data_clut
            tim_pixel_data = self.binary_data[(clut_length + 8):]
            tim_data['Pixel_Data'] = tim_pixel_data
            len_all_taken= len(tim_pixel_data) + len(tim_data_clut) + 8 # This 8 represent the header + flag
            len_all_file = len(self.binary_data)
            if len_all_taken != len_all_file:
                raise ValueError(f'Critical!!: Some Calculations in file length went wrong! Expected: {len_all_file}, Obtained: {len_all_taken}')
        else:
            tim_flag['is_CLUT'] = 'NO-CLUT'
            read_pixel_data_len = self.binary_data[8:12]
            pd_noclut_len_int = int.from_bytes(read_pixel_data_len, byteorder='little', signed=False)
            read_pd_noclut = self.binary_data[8: pd_noclut_len_int]
            tim_data['Pixel_Data'] = read_pd_noclut

        rgba_data, size_img = self.split_data(get_flags=tim_flag, get_tim_data=tim_data)
        tim_to_png = {'SizeImg': size_img, 'RGBA_Data': rgba_data}
        return tim_to_png
    
    def split_data(self, get_flags=dict, get_tim_data=dict) -> tuple[dict, dict]:
        rgba_data: dict = {}
        img_size: dict = {}
        get_clut_flag = get_flags.get('is_CLUT')
        get_pixel_mode = get_flags.get('Pixel_Mode')
        get_img_data = get_tim_data.get('Pixel_Data')
        get_clut = get_tim_data.get('CLUT')
        if get_clut_flag == 'CLUT':
            processed_clut = self.split_clut(clut_data=get_clut, type_clut=get_pixel_mode)
            processed_image_data, img_size_got = self.combine_image(image_data=get_img_data, clut_data=processed_clut, pixel_mode=get_pixel_mode)
            rgba_data = processed_image_data
            img_size = img_size_got
        else:
            raise ValueError(f'Critical!!: CLUTless TIM Type not supported at the moment')
        
        return rgba_data, img_size

    def split_clut(self, clut_data=bytes, type_clut=str) -> dict:
        split_clut = {}
        clut_data_itself = clut_data[12:]
        
        if type_clut == f'4-bit CLUT':
            total_clut_entries = len(clut_data_itself) // 32
            next_clut = 0
            clut_entry_num = 0
            for current_clut_entry in range(total_clut_entries):
                this_clut = clut_data_itself[next_clut:(next_clut + 32)]
                if this_clut != (b'\x00' * 32):
                    split_clut[f'CLUT_{clut_entry_num}'] = this_clut
                    clut_entry_num += 1
                next_clut += 32
        
        elif type_clut == f'8-bit CLUT':
            total_clut_entries = len(clut_data_itself) // 512
            next_clut = 0
            clut_entry_num = 0
            for current_clut_entry in range(total_clut_entries):
                this_clut = clut_data_itself[next_clut:(next_clut + 512)]
                if this_clut != (b'\x00' * 512):
                    split_clut[f'CLUT_{clut_entry_num}'] = this_clut
                    clut_entry_num += 1
                next_clut += 512
        else: # Should i elaborate more in the different types for TLoD?
            raise ValueError(f'Critical!!: {type_clut} not supported')

        return split_clut
    
    def combine_image(self, image_data=bytes, clut_data=dict, pixel_mode=str) -> tuple[dict, dict]:
        rgba_data_combined = {}
        img_header = image_data[0:12]
        width_image = int.from_bytes(img_header[8:10], byteorder='little', signed=False)
        height_image = int.from_bytes(img_header[10:12], byteorder='little', signed=False)
        
        # Size Factors
        if pixel_mode == f'4-bit CLUT':
            intended_width = width_image * 4
        elif pixel_mode == f'8-bit CLUT':
            intended_width = width_image * 2
        
        image_size = {'X': intended_width, 'Y': height_image}
        
        image_data_itself = image_data[12:]
        total_of_cluts = len(clut_data)
        unfolded_byte_pairs = []
        for current_pixel in image_data_itself: # EACH PIXEL from Pixel Data
            unfold_byte_1 = current_pixel & 15 # UNFOLD one PIXEL from Pixel Data
            unfold_byte_2 = current_pixel >> 4 # UNFOLD one PIXEL from Pixel Data
            both_unfold = [unfold_byte_1, unfold_byte_2]
            unfolded_byte_pairs.append(both_unfold)

        if pixel_mode == f'4-bit CLUT':
            # applying the 16bit to 32bit conversion before doing the CLUT selection... this is an awesome idea from Monoxide
            final_cluts = {}
            for clut_num in range(0, total_of_cluts):
                current_clut = clut_data.get(f'CLUT_{clut_num}')
                lenght_current_clut = len(current_clut) // 2
                start_pair = 0
                clut_converted = []
                for current_byte_number in range(0, lenght_current_clut):
                    current_byte = current_clut[start_pair : (start_pair + 2)]
                    convert_current_byte = int.from_bytes(current_byte, 'little')
                    rgba = b''.join(self.convert_5_to_8(byte_pair=convert_current_byte))
                    clut_converted.append(rgba)
                    start_pair += 2
                join_clut = b''.join(clut_converted)
                final_cluts[f'CLUT_{clut_num}'] = join_clut
            
            for clut_num in range(0, total_of_cluts): # IN RANGE OF CLUTS
                current_clut = final_cluts.get(f'CLUT_{clut_num}') # IN THIS CLUT
                current_rgba = [] # CURRENT RGBA OF THE IMAGE
                for current_pixel in unfolded_byte_pairs: # EACH PIXEL from Pixel Data
                    for byte in current_pixel: # EACH OF UNFOLD BYTE -> To apply the CLUT
                        byte_pixel = current_clut[(byte*4):(byte*4+4)] # THE BYTE INDICATE THE BYTE COLOR IN A PIXEL OF THE CLUT
                        current_rgba.append(byte_pixel) # APPEND THIS BYTE
                joined_rgba = b''.join(current_rgba) # JOIN THE PREVIOUS PROCESSED BYTES
                rgba_data_combined[f'IMAGE_{clut_num}'] = joined_rgba # ONCE ALL PROCESSED IS SENT TO THE FINAL IMAGE ARRAY
        
        elif pixel_mode == f'8-bit CLUT':
            for clut_num in range(0, total_of_cluts):
                current_clut = clut_data.get(f'CLUT_{clut_num}')
                current_rgba = []
                for current_pixel in image_data_itself:
                    byte_pixel = current_clut[(current_pixel*2):(current_pixel*2+2)]
                    byte_pixel_byte = int.from_bytes(byte_pixel, 'little')
                    rgba_8bit = b''.join(self.convert_5_to_8(byte_pair=byte_pixel_byte))
                    current_rgba.append(rgba_8bit)
                joined_rgba = b''.join(current_rgba)
                rgba_data_combined[f'IMAGE_{clut_num}'] = joined_rgba
        
        return rgba_data_combined, image_size
    
    def convert_5_to_8(self, byte_pair) -> tuple[bytes, bytes, bytes, bytes]:
        b_int = CONVERT_5_TO_8_BIT[(byte_pair >> 10) & 0b11111]
        g_int = CONVERT_5_TO_8_BIT[(byte_pair >> 5) & 0b11111]
        r_int = CONVERT_5_TO_8_BIT[byte_pair & 0b11111]
        a_int = byte_pair >> 15
        if b_int == 0 and g_int == 0 and r_int == 0:
            if a_int == 1:
                a_int = 255 
            else:
                a_int = 0
        else:
            if a_int == 0:
                a_int = 255 
            else:
                a_int = 127
        r = int.to_bytes(r_int, 1, 'big')
        g = int.to_bytes(g_int, 1, 'big')
        b = int.to_bytes(b_int, 1, 'big')
        a = int.to_bytes(a_int, 1, 'big')
        return r, g, b, a
    
    def convert_mcq_file(self) -> dict:
        mcq_to_png: dict = {}

        mcq_data: dict = {'CLUT_WIDTH': 0, 'Pixel_Data': [], 'X': 0, 'Y': 0}
        # READ MCQ FLAGs and split the data
        data_start_bin = self.binary_data[4:8]
        data_start = int.from_bytes(data_start_bin, byteorder='little', signed=False)
        mcq_data['Pixel_Data'] = self.binary_data[data_start:]
        mcq_data['X'] = int.from_bytes(self.binary_data[20:22], 'little', signed=False)
        mcq_data['Y'] = int.from_bytes(self.binary_data[22:24], 'little', signed=False)
        mcq_data['CLUT_WIDTH'] = int.from_bytes(self.binary_data[16:18], 'little', signed=False)

        mcq_processed_data = self.process_mcq_data(mcq_split_data=mcq_data)

        both_sizes = {'IntendedX': mcq_processed_data[1], 'IntendedY': mcq_processed_data[2],  'AlignX': mcq_processed_data[3], 'AlignY': mcq_processed_data[4]}
        mcq_to_png = {'SizeImg': both_sizes, 'RGBA_Data': mcq_processed_data[0]}

        return mcq_to_png
    
    def process_mcq_data(self, mcq_split_data=dict) -> tuple[bytes, int, int, int, int]:
        final_rgba: bytes = b''
        final_image_width: int = 0
        final_image_height: int = 0
        final_align_width: int = 0
        final_align_height: int = 0

        image_width = mcq_split_data.get('X')
        image_height = mcq_split_data.get('Y')
        clut_width = mcq_split_data.get('CLUT_WIDTH')
        mcq_pixel_data = mcq_split_data.get('Pixel_Data')
        mcq_preprocessed = self.preprocess_mcq(pixel_data=mcq_pixel_data, image_width=image_width, image_height=image_height, clut_width=clut_width)
        align_width = mcq_preprocessed[2]
        align_height = mcq_preprocessed[3]
        mcq_processed = self.combine_mcq(final_clut=mcq_preprocessed[0], image_data_rows=mcq_preprocessed[1])
        final_rgba = self.convert_5_to_8_mcq(byte_pixel_list=mcq_processed)
        final_image_width = image_width
        final_image_height = image_height
        final_align_width = align_width
        final_align_height = align_height

        return final_rgba, final_image_width, final_image_height, final_align_width, final_align_height

    def preprocess_mcq(self, pixel_data=bytes, image_width=int, image_height=int, clut_width=int) -> tuple[list, list, int, int]:
        final_clut: list = []
        image_data_rows: list = []
        # We need some alignments before start working, this side no matters if Y > X, since we need to work always as Y < X
        align_width = (image_width * image_height) // 256
        align_height = 256
        align_width = tile_count = align_width + (align_width % 16) if align_width > 16 else 16
        # In this block get the CLUTs and the Image Data
        clut_1 = []
        clut_2 = []
        clut_3 = []
        move_slice = 0
        for byte_range in range(0, 256):
            clut_1_get = pixel_data[move_slice:(move_slice + 32)]
            clut_1.append(clut_1_get)
            move_slice += 32
            if clut_width > 16:
                clut_2_get = pixel_data[move_slice:(move_slice + 32)]
                clut_2.append(clut_2_get)
                move_slice += 32
                if clut_width > 32:
                    clut_3_get = pixel_data[move_slice:(move_slice + 32)]
                    clut_3.append(clut_3_get)
                    move_slice += 32
            row = []
            for j in range(align_width // 16):
                r = pixel_data[move_slice: (move_slice + 8)]
                move_slice += 8
                if r == b'':
                    r = b'\x00' * 8
                row.append(r)
            image_data_rows.append(row)
        concatenate_clut = clut_1 + clut_2 + clut_3
        final_clut = concatenate_clut[:tile_count]

        return final_clut, image_data_rows, align_width, align_height

    def combine_mcq(self, final_clut=list, image_data_rows=list) -> list:
        byte_pixel_list: list = []
        # Now we do some operations over the rows of data
        row_data_combined = []
        offset_clut = 0
        for i, row in enumerate(image_data_rows):
            clut_index = 0

            if (i % 16 == 0) and (i > 0):
                offset_clut += 1

            for tile_row in row:
                current_clut = final_clut[clut_index + offset_clut]
                new_combined_row = b''
                for pixel in tile_row:
                    byte1 = pixel & 0x0f
                    byte2 = pixel >> 0x04
                    byte_pair1 = current_clut[byte1 * 2:byte1 * 2 + 2]
                    new_combined_row += byte_pair1
                    byte_pair2 = current_clut[byte2 * 2:byte2 * 2 + 2]
                    new_combined_row += byte_pair2
                row_data_combined.append(new_combined_row)
                clut_index += 16
        
        joined_data_combined = b''.join(row_data_combined)
        
        while len(joined_data_combined) != 0:
            get_this_join = joined_data_combined[:2]
            byte_pixel_list.append(get_this_join)
            joined_data_combined = joined_data_combined[2:]
        
        return byte_pixel_list

    def convert_5_to_8_mcq(self, byte_pixel_list=list) -> bytes:
        final_rgba: bytes = b''
        rgba_data = []
        for bytepixel in byte_pixel_list:
            bp = int.from_bytes(bytepixel, 'little')
            a = 0b11111111 if (bp >> 15 == 0) else 0b01111111
            b = ((bp >> 10) & 0b11111) << 3
            g = ((bp >> 5) & 0b11111) << 3
            r = (bp & 0b11111) << 3
            rgba = [int.to_bytes(x, 1, 'big') for x in (r, g, b, a)]
            rgba_data.extend(rgba)
        
        final_rgba = b''.join(rgba_data)
        return final_rgba