"""

SAF File: This module will take the SAF Animation Data, process it and get it ready to be applied to a model

Most if not every part of the code will be based on the one found in: 
https://github.com/Legend-of-Dragoon-Modding/Severed-Chains
https://github.com/Legend-of-Dragoon-Modding/Severed-Chains/blob/main/src/main/java/legend/game/types/TmdAnimationFile.java

Copyright (C) 2024 Monoxide
-------------------------------------------------------------------------------------------------------------------------
Little or minor changes by:
Copyright (C) 2024 DooMMetaL

"""

class Saf:
    def __init__(self, saf_binary_data=bytes) -> None:
        """SAF Decoder and Processor, in a future will handle the creation of SAF files if needed"""
        self.saf_binary_data = saf_binary_data
        self.processed_saf: dict = {}
        self.process_saf()
    
    def process_saf(self):
        number_objects = int.from_bytes(self.saf_binary_data[12:14], byteorder='little', signed=False)
        total_frames = int.from_bytes(self.saf_binary_data[14:16], byteorder='little', signed=False)

        keyframe_count = total_frames / 2

        accumulative_transforms: dict = {}
        for current_frame in range(0, keyframe_count):
            current_frame_transforms: dict = {}
            for current_model_object in range(0, number_objects):
                current_object_transforms: dict = {}
                offset_to_transforms_start = 16 + ((current_frame * number_objects) + current_model_object) * 12
                offset_to_transforms_end = offset_to_transforms_start + 12
                get_transform_binary = self.saf_binary_data[offset_to_transforms_start:offset_to_transforms_end]
                this_transforms_converted = self.convert_saf_transforms(transform_data=get_transform_binary)
                current_object_transforms = {f'Object_Number_{current_model_object}': this_transforms_converted}
                current_frame_transforms.update(current_object_transforms)
            final_object_transforms: dict = {f'Frame_{current_frame}': current_frame_transforms}
            accumulative_transforms.update(final_object_transforms)
    
    def convert_saf_transforms(self, transform_data=bytes) -> dict:
        final_transform: dict = {"Rx": float(int.from_bytes(transform_data[0:2], 'little', signed=True) / round((4096/360), 12)), 
                                 "Ry": float(int.from_bytes(transform_data[2:4], 'little', signed=True) / round((4096/360), 12)), 
                                 "Rz": float(int.from_bytes(transform_data[4:6], 'little', signed=True) / round((4096/360), 12)), 
                                 "Tx": float(int.from_bytes(transform_data[6:8], 'little', signed=True) / 1000), 
                                 "Ty": float(int.from_bytes(transform_data[8:10], 'little', signed=True) / 1000), 
                                 "Tz": float(int.from_bytes(transform_data[10:12], 'little', signed=True) / 1000)}
        return final_transform