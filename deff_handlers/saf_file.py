"""

SAF File: This module will take the SAF Animation Data, process it and get it ready to be applied to a model

Most if not every part of the code will be based on the one found in: 
https://github.com/Legend-of-Dragoon-Modding/Severed-Chains
https://github.com/Legend-of-Dragoon-Modding/Severed-Chains/blob/main/src/main/java/legend/game/types/TmdAnimationFile.java

Copyright (C) 2025 Monoxide
-------------------------------------------------------------------------------------------------------------------------
Little or minor changes by:
Copyright (C) 2025 DooMMetaL

"""

class Saf:
    def __init__(self, saf_binary_data=bytes, model_name=str) -> None:
        self.saf_binary_data = saf_binary_data
        self.model_name = model_name
        self.processed_saf: dict = {}
        self.process_saf()
    
    def process_saf(self):
        """
        Process SAF:\n
        Process SAF File into glTF Suitable Format.
        """
        saf_animation: dict = {}

        number_objects = int.from_bytes(self.saf_binary_data[12:14], byteorder='little', signed=False)
        total_transforms = int.from_bytes(self.saf_binary_data[14:16], byteorder='little', signed=False)

        transforms_count = total_transforms // 2

        saf_converted_dict: dict = {}
        for this_object in range(0, number_objects):
            saf_converted_dict.update({f'{self.model_name}_Object_{this_object}': {}})

        for current_frame in range(0, transforms_count):
            for current_model_object in range(0, number_objects):
                offset_to_transforms_start = 16 + ((current_frame * number_objects) + current_model_object) * 12
                offset_to_transforms_end = offset_to_transforms_start + 12
                get_transform_binary = self.saf_binary_data[offset_to_transforms_start:offset_to_transforms_end]
                this_transforms_converted = self.convert_saf_transforms(transform_data=get_transform_binary)
                current_keyframe = {f'Keyframe_{current_frame}': this_transforms_converted}
                saf_converted_dict[f'{self.model_name}_Object_{current_model_object}'].update(current_keyframe)

        saf_animation = {f'{self.model_name}': {'TotalTransforms': transforms_count, 'ObjectCount': number_objects, 
                                                            'AnimationType': 'SAF', 'AnimationsData': saf_converted_dict}}
        
        self.processed_saf = saf_animation
    
    def convert_saf_transforms(self, transform_data=bytes) -> dict:
        final_transform: dict = {"Rx": float(int.from_bytes(transform_data[0:2], 'little', signed=True) / round((4096/360), 12)), 
                                 "Ry": float(int.from_bytes(transform_data[2:4], 'little', signed=True) / round((4096/360), 12)), 
                                 "Rz": float(int.from_bytes(transform_data[4:6], 'little', signed=True) / round((4096/360), 12)), 
                                 "Tx": float(int.from_bytes(transform_data[6:8], 'little', signed=True) / 1000), 
                                 "Ty": float(int.from_bytes(transform_data[8:10], 'little', signed=True) / 1000), 
                                 "Tz": float(int.from_bytes(transform_data[10:12], 'little', signed=True) / 1000)}
        return final_transform