"""

LMB File: This module will take the LMB Object Data, process it and get it ready to be applied to a model

Most if not every part of the code will be based on the one found in: 
https://github.com/Legend-of-Dragoon-Modding/Severed-Chains
https://github.com/Legend-of-Dragoon-Modding/Severed-Chains/blob/main/src/main/java/legend/game/combat/deff/Lmb.java
https://github.com/Legend-of-Dragoon-Modding/Severed-Chains/blob/main/src/main/java/legend/game/combat/deff/LmbType0.java
https://github.com/Legend-of-Dragoon-Modding/Severed-Chains/blob/main/src/main/java/legend/game/combat/deff/LmbType1.java
https://github.com/Legend-of-Dragoon-Modding/Severed-Chains/blob/main/src/main/java/legend/game/combat/deff/LmbType2.java

Copyright (C) 2024 Monoxide
-------------------------------------------------------------------------------------------------------------------------
Little or minor changes by:
Copyright (C) 2024 DooMMetaL

"""

class Lmb:
    def __init__(self, lmb_binary_data=bytes) -> None:
        """TODO: AT THE MOMENT THIS CODE WILL NOT DECODED FULLY THE LMB, RATHER IS JUST GETTING THE DATA IN GOOD SHAPE
        WILL FINISH THIS CODE WHEN I START TO CONVERT DEFF WITH LMB AS STANDALONE FILES"""
        self.lmb_binary_data = lmb_binary_data
        self.lmb_magic = b'\x4C\x4D\x42\x00'
        self.processed_lmb: dict = {}
        self.lmb_type_discriminator()
    
    def lmb_type_discriminator(self) -> None:
        """
        I will be using the SC Discriminator algorithm to get which 
        Type of LMB is and after split into parts
        """
        final_lmb_data: dict = {}

        lmb_type = self.lmb_binary_data[4:8]
        lmb_offset = self.lmb_binary_data[8:12]
        this_lmb_type = int.from_bytes(lmb_type, byteorder='little', signed=False)
        this_lmb_offset = int.from_bytes(lmb_offset, byteorder='little', signed=False)
        this_lmb_data = self.lmb_binary_data[this_lmb_offset:]
        
        self.check_if_lmb(lmb_data=this_lmb_data[0:4])
        self.lmb_object_count = self.object_count(lmb_data=this_lmb_data[4:8])

        if this_lmb_type == 0:
            lmb_type_0_processed = self.process_lmb_type_0(lmb_data=this_lmb_data)
            final_lmb_data = {'LMB_Type_0': None}
        elif this_lmb_type == 1:
            lmb_type_1_processed = self.process_lmb_type_1(lmb_data=this_lmb_data)
            final_lmb_data = {'LMB_Type_1': None}
        elif this_lmb_type == 2:
            lmb_type_2_processed = self.process_lmb_type_2(lmb_data=this_lmb_data)
            final_lmb_data = {'LMB_Type_2': None}
        else:
            print(f'LMB Type: {this_lmb_type}, not supported')
            print(f'Report this error as LMB Type not supported with the path to the file...')
            exit()

        self.processed_lmb = final_lmb_data
    
    def check_if_lmb(self, lmb_data=bytes):
        if lmb_data != self.lmb_magic:
            print(f'This is not an LMB File: {lmb_data}')
            print(f'Report this as NOT LMB File!')
            exit()
    
    def object_count(self, lmb_data=bytes) -> int:
        object_count: int = 0
        object_count = int.from_bytes(lmb_data, byteorder='little', signed=False)
        return object_count

    def process_lmb_type_0(self, lmb_data=bytes) -> dict:
        lmb_type_0_transforms: dict = {}

        lmb_type_0_transforms_gather: dict = {}
        for object_number in range(0, self.lmb_object_count):
            slice_data_start = 8 + (object_number * 12)
            slice_data_end = slice_data_start + 12
            inner_slice = lmb_data[slice_data_start:slice_data_end]
            number_of_transforms: int = int.from_bytes(inner_slice[4:8], byteorder='little', signed=False)
            offset_to_transforms: int = int.from_bytes(inner_slice[8:12], byteorder='little', signed=False)
            
            transforms: dict = {}
            for current_number_transform in range(0, number_of_transforms):
                current_offset_transform_start = offset_to_transforms + (current_number_transform * 20)
                current_offset_transform_end = current_offset_transform_start + 20
                this_binary_transform_data = lmb_data[current_offset_transform_start:current_offset_transform_end]
                current_transform_converted = self.convert_lmb_transform(transform_data=this_binary_transform_data)
                transform_dict: dict = {f'Transform_{current_number_transform}': current_transform_converted}
                transforms.update(transform_dict)

            object_transforms: dict = {f'LMB_Object_{object_number}': {'Number Transforms': number_of_transforms, 'Transforms': transforms}}
            lmb_type_0_transforms_gather.update(object_transforms)
        
        lmb_type_0_transforms = {f'LMB Type 0': lmb_type_0_transforms_gather}
        return lmb_type_0_transforms
    
    def process_lmb_type_1(self, lmb_data=bytes) -> dict:
        lmb_type_1_transforms: dict = {}

        get_data_bytes_calc_08 = int.to_bytes(lmb_data[8:10], byteorder='little', signed=False)
        get_keyframes_count_0a = int.to_bytes(lmb_data[10:12], byteorder='little', signed=False)
        get_subtable_offset = int.to_bytes(lmb_data[12:16], byteorder='little', signed=False)
        get_base_transforms_offset = int.to_bytes(lmb_data[16:20], byteorder='little', signed=False)
        get_incremental_transforms_offset = int.to_bytes(lmb_data[20:24], byteorder='little', signed=False)

        get_subtable_transforms_types = self.subtable_transforms_types(table_data=lmb_data, subtable_offset=get_subtable_offset)
        get_base_transforms = self.base_transforms(base_transform_data=lmb_data, base_transform_offset=get_base_transforms_offset)
        get_incremental_transforms = self.incremental_transforms_lmb_type_1(incr_transform_data=lmb_data, incr_transform_offset=get_incremental_transforms_offset, 
                                                                 keyframes_count=get_keyframes_count_0a, data_byte_calc=get_data_bytes_calc_08)
        
        lmb_type_1_gather_transforms: dict = {f'SubTable Transforms Types': get_subtable_transforms_types,
                                            f'Base Transforms': get_base_transforms,
                                            f'Incremental Transforms': get_incremental_transforms}
        
        lmb_type_1_transforms = {'LMB Type 1': {f'Transforms Data': lmb_type_1_gather_transforms, 'Keyframes': get_keyframes_count_0a}}
        return lmb_type_1_transforms
    
    def process_lmb_type_2(self, lmb_data=bytes) -> dict:
        lmb_type_2_transforms: dict = {}

        get_data_bytes_calc_08 = int.to_bytes(lmb_data[8:10], byteorder='little', signed=False)
        get_keyframes_count_0a = int.to_bytes(lmb_data[10:12], byteorder='little', signed=False)
        get_subtable_offset = int.to_bytes(lmb_data[12:16], byteorder='little', signed=False)
        get_base_transforms_offset = int.to_bytes(lmb_data[16:20], byteorder='little', signed=False)
        get_incremental_transforms_offset = int.to_bytes(lmb_data[20:24], byteorder='little', signed=False)

        get_subtable_transforms_types = self.subtable_transforms_types(table_data=lmb_data, subtable_offset=get_subtable_offset)
        get_base_transforms = self.base_transforms(base_transform_data=lmb_data, base_transform_offset=get_base_transforms_offset)
        get_incremental_transforms = self.incremental_transforms_lmb_type_2(incr_transform_data=lmb_data, incr_transform_offset=get_incremental_transforms_offset, 
                                                                 keyframes_count=get_keyframes_count_0a, data_byte_calc=get_data_bytes_calc_08)
        
        lmb_type_1_gather_transforms: dict = {f'SubTable Transforms Types': get_subtable_transforms_types,
                                            f'Base Transforms': get_base_transforms,
                                            f'Incremental Transforms': get_incremental_transforms}
        
        lmb_type_2_transforms = {'LMB Type 2': {f'Transforms Data': lmb_type_1_gather_transforms, 'Keyframes': get_keyframes_count_0a}}

        return lmb_type_2_transforms
    
    def subtable_transforms_types(self, table_data=bytes, subtable_offset=int) -> dict:
        final_subtable: dict = {}

        types_slice = 0
        for object_number in range(0, self.lmb_object_count):
            this_subtable: dict = {}
            this_type_data = table_data[(subtable_offset + types_slice) : (subtable_offset + types_slice + 4)]
            transform_type = int.from_bytes(this_type_data[0:2], byteorder='little', signed=False)
            transform_flags = int.from_bytes(this_type_data[2:3], byteorder='little', signed=False)
            this_subtable = {f'Transform_Type-Flag_{object_number}': {f'Type': transform_type, f'Flags': transform_flags}}
            final_subtable.update(this_subtable)

            types_slice += 4

        return final_subtable

    def base_transforms(self, base_transform_data=bytes, base_transform_offset=int) -> dict:
        final_base_transforms: dict = {}

        for object_number in range(0, self.lmb_object_count):
            this_base_transform: dict = {}
            current_base_transform_offset_start = base_transform_offset + (object_number * 14)
            current_base_transform_offset_end = current_base_transform_offset_start + 14
            base_transform_binary = base_transform_data[current_base_transform_offset_start:current_base_transform_offset_end]
            base_transform_converted = self.convert_lmb_transform(transform_data=base_transform_binary)
            this_base_transform = {f'Base_Transformation_{object_number}': base_transform_converted}
            final_base_transforms.update(this_base_transform)

        return final_base_transforms

    def incremental_transforms_lmb_type_1(self, incr_transform_data=bytes, incr_transform_offset=int, keyframes_count=int, data_byte_calc=int) -> dict:
        final_incremental_transforms: dict = {}
        array_calculation = data_byte_calc * (keyframes_count - 1) / 2

        for current_position in range(0, array_calculation):
            this_incremental_transform: dict = {}
            incremental_offset_start = incr_transform_offset + (current_position * 2)
            incremental_offset_end = incremental_offset_start + 2
            incremental_transform = int.from_bytes(incr_transform_data[incremental_offset_start:incremental_offset_end], byteorder='little', signed=False)
            this_incremental_transform = {f'Incremental_Transform_{current_position}': incremental_transform}
            final_incremental_transforms.update(this_incremental_transform)

        return final_incremental_transforms
    
    def incremental_transforms_lmb_type_2(self, incr_transform_data=bytes, incr_transform_offset=int, keyframes_count=int, data_byte_calc=int) -> dict:
        final_incremental_transforms: dict = {}
        array_calculation = data_byte_calc * (keyframes_count - 1)

        for current_position in range(0, array_calculation):
            this_incremental_transform: dict = {}
            incremental_offset_start = incr_transform_offset + current_position
            incremental_offset_end = incremental_offset_start + 1
            incremental_transform = int.from_bytes(incr_transform_data[incremental_offset_start:incremental_offset_end], byteorder='little', signed=False)
            this_incremental_transform = {f'Incremental_Transform_{current_position}': incremental_transform}
            final_incremental_transforms.update(this_incremental_transform)

        return final_incremental_transforms

    def convert_lmb_transform(self, transform_data=bytes) -> dict:
        final_transform: dict = {"Sx": float(int.from_bytes(transform_data[0:2], 'little', signed=False) / 4096), 
                                 "Sy": float(int.from_bytes(transform_data[2:4], 'little', signed=False) / 4096), 
                                 "Sz": float(int.from_bytes(transform_data[4:6], 'little', signed=False) / 4096),
                                 "Tx": float(int.from_bytes(transform_data[6:8], 'little', signed=True) / 1000), 
                                 "Ty": float(int.from_bytes(transform_data[8:10], 'little', signed=True) / 1000), 
                                 "Tz": float(int.from_bytes(transform_data[10:12], 'little', signed=True) / 1000), 
                                 "Rx": float(int.from_bytes(transform_data[12:14], 'little', signed=True) / round((4096/360), 12)), 
                                 "Ry": float(int.from_bytes(transform_data[14:16], 'little', signed=True) / round((4096/360), 12)), 
                                 "Rz": float(int.from_bytes(transform_data[16:18], 'little', signed=True) / round((4096/360), 12)), 
                                 "PadLmb": transform_data[18:20]}
        return final_transform

    def combine_lmb_type_0(self):
        """ NOT NEEDED?? """
        pass

    def combine_process_lmb_type_1(self):
        pass
    
    def combine_process_lmb_type_2(self):
        pass
