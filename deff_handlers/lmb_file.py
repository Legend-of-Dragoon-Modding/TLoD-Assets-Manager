"""

LMB File: This module will take the LMB Object Data, process it and get it ready to be applied to a model

Most if not every part of the code will be based on the one found in: 
https://github.com/Legend-of-Dragoon-Modding/Severed-Chains
https://github.com/Legend-of-Dragoon-Modding/Severed-Chains/blob/main/src/main/java/legend/game/combat/deff/Lmb.java
https://github.com/Legend-of-Dragoon-Modding/Severed-Chains/blob/main/src/main/java/legend/game/combat/deff/LmbType0.java
https://github.com/Legend-of-Dragoon-Modding/Severed-Chains/blob/main/src/main/java/legend/game/combat/deff/LmbType1.java
https://github.com/Legend-of-Dragoon-Modding/Severed-Chains/blob/main/src/main/java/legend/game/combat/deff/LmbType2.java

Copyright (C) 2025 Monoxide
-------------------------------------------------------------------------------------------------------------------------
Little or minor changes by:
Copyright (C) 2025 DooMMetaL

"""

class Lmb:
    def __init__(self, lmb_binary_data=bytes, lmb_type=str, model_name=str) -> None:
        self.lmb_binary_data = lmb_binary_data
        self.lmb_type = lmb_type
        self.model_name = model_name
        self.processed_lmb: dict = {}
        self.lmb_object_count: int = 0
        self.lmb_transforms_count: list = []
        self.lmb_type_discriminator()
    
    def lmb_type_discriminator(self) -> None:
        """
        LMB Type Discriminator:\n
        Depending on the LMB Type {LMB0, LMB1, LMB2} will process the Animation into glTF Suitable Format.
        """
        self.lmb_object_count = int.from_bytes(self.lmb_binary_data[4:8], byteorder='little', signed=False)

        if self.lmb_type == 'LMB0':
            lmb_get_keyframes_data_table = self.get_lmb0_keyframes_per_object_table(lmb_data=self.lmb_binary_data)
            lmb_get_transform_data = self.conform_lmb0_transforms(keyframes_table=lmb_get_keyframes_data_table, lmb_data=self.lmb_binary_data)
            self.processed_lmb = lmb_get_transform_data
        elif self.lmb_type == 'LMB1':
            print('LMB Type 1 not Implemented Yet')
            exit()
        elif self.lmb_type == 'LMB2':
            print('LMB Type 2 not Implemented Yet')
            exit()

    def get_lmb0_keyframes_per_object_table(self, lmb_data=bytes) -> dict:
        """
        Get LMB0 Transforms per Object Table:\n
        Get LMB_Type_0 Transform Table reference per Object.
        """
        # TODO: CHECK THIS SHIT!!!!!
        part_animation_table: dict = {}
        current_offset = 8
        for current_object in range(0, self.lmb_object_count):
            this_reference_table = lmb_data[current_offset:(current_offset + 12)]
            flag_00 = int.from_bytes(this_reference_table[0:2], 'little', signed=False)
            transform_count = int.from_bytes(this_reference_table[4:8], 'little', signed=False)
            transform_table_offset = int.from_bytes(this_reference_table[8:12], 'little', signed=False)
            this_object_table = {f'{current_object}': {f'flag_00': flag_00, 'TransformCount': transform_count, 'TableTransformOffset': transform_table_offset}}
            part_animation_table.update(this_object_table)
            self.lmb_transforms_count.append(transform_count)
            current_offset += 12
        
        return part_animation_table
    
    def conform_lmb0_transforms(self, keyframes_table=dict, lmb_data=bytes) -> dict:
        """
        Conform LMB0 Transform Data:\n
        Take LMB Data and conform it's Transforms.
        """
        lmb_animation: dict = {}
        store_objects_animation: dict = {}
        for current_object_table in keyframes_table:
            get_table = keyframes_table.get(f'{current_object_table}')
            get_flags = get_table.get(f'flag_00') # Actually not used at all here, because tell to Engine if need to Render Particles... but we keep it
            transform_count = get_table.get(f'TransformCount')
            transform_table_pointer = get_table.get(f'TableTransformOffset')

            current_object_transforms: dict = {}
            current_pointer = transform_table_pointer
            for current_transform_number in range(0, transform_count):
                current_transform_binary_block = lmb_data[current_pointer:(current_pointer + 20)]
                current_transform_processed = self.each_transforms(transfrom_block=current_transform_binary_block)
                this_transform = {f'Keyframe_{current_transform_number}': current_transform_processed}
                current_object_transforms.update(this_transform)
                current_pointer += 20
            
            this_object_transforms = {f'{self.model_name}_Object_{current_object_table}': current_object_transforms}
            store_objects_animation.update(this_object_transforms)
        
        get_len_transforms = len(self.lmb_transforms_count)
        sum_all_transforms = sum(self.lmb_transforms_count)
        total_transforms = sum_all_transforms // get_len_transforms
        
        lmb_animation = {f'{self.model_name}': {'TotalTransforms': total_transforms, 'ObjectCount':self.lmb_object_count, 
                                                            'AnimationType': 'LMB0', 'AnimationsData': store_objects_animation}}

        return lmb_animation
    
    def each_transforms(self, transfrom_block=bytes) -> dict:
        """
        Each Transforms:\n
        Take the data from the current Transforms and Convert them.
        """
        new_transforms: dict = {}
        read_scale = self.convert_svec_scale(transfrom_block[0:6])
        read_translation = self.convert_svec_translation(binary_vec=transfrom_block[6:12])
        read_rotation = self.convert_svec_rotation(binary_vec=transfrom_block[12:18])
        #read_pad = transfrom_block[18:20] NOT NEEDED
        new_transforms = {'Tx': read_translation[0], 'Ty': read_translation[1], 'Tz': read_translation[2], 
                          'Rx': read_rotation[0], 'Ry': read_rotation[1], 'Rz': read_rotation[2], 
                          'Sx': read_scale[0], 'Sy': read_scale[1], 'Sz': read_scale[2]}
        return new_transforms
    
    # Conversion of Vectors
    def convert_svec_scale(self, binary_vec=bytes) -> tuple[float, float, float]:
        """
        Convert SVec Scale:\n
        Take Binary block and convert into Scale values.
        """
        scale_x = float(int.from_bytes(binary_vec[0:2], 'little', signed=False) / 4096)
        scale_y = float(int.from_bytes(binary_vec[2:4], 'little', signed=False) / 4096)
        scale_z = float(int.from_bytes(binary_vec[4:6], 'little', signed=False) / 4096)
        return scale_x, scale_y, scale_z

    def convert_svec_translation(self, binary_vec=bytes) -> tuple[float, float, float]:
        """
        Convert SVec Translation:\n
        Take Binary block and convert into Translation values.
        """
        translation_x = float(int.from_bytes(binary_vec[0:2], 'little', signed=True) / 1000)
        translation_y = float(int.from_bytes(binary_vec[2:4], 'little', signed=True) / 1000)
        translation_z = float(int.from_bytes(binary_vec[4:6], 'little', signed=True) / 1000)
        return translation_x, translation_y, translation_z

    def convert_svec_rotation(self, binary_vec=bytes) -> tuple[float, float, float]:
        """
        Convert SVec Rotation:\n
        Take Binary block and convert into Rotation values.
        """
        rotation_x = float(int.from_bytes(binary_vec[0:2], 'little', signed=True) / round((4096/360), 12))
        rotation_y = float(int.from_bytes(binary_vec[2:4], 'little', signed=True) / round((4096/360), 12))
        rotation_z = float(int.from_bytes(binary_vec[4:6], 'little', signed=True) / round((4096/360), 12))
        return rotation_x, rotation_y, rotation_z