"""

CMB File: This module will take the LMB Object Data, process it and get it ready to be applied to a model

Most if not every part of the code will be based on the one found in: 
https://github.com/Legend-of-Dragoon-Modding/Severed-Chains
https://github.com/Legend-of-Dragoon-Modding/Severed-Chains/blob/main/src/main/java/legend/game/combat/deff/Cmb.java

Copyright (C) 2024 Monoxide
-------------------------------------------------------------------------------------------------------------------------
Little or minor changes by:
Copyright (C) 2024 DooMMetaL

"""

class Cmb:
    def __init__(self, cmb_binary_data=bytes, model_name=str) -> None:
        self.cmb_binary_data = cmb_binary_data
        self.model_name = model_name
        self.processed_cmb: dict = {}
        self.cmb_object_count: int = 0
        self.process_cmb()
    
    def process_cmb(self):
        """
        Process CMB:\n
        Process CMB Animation Data into glTF Suitable Format.
        """
        cmb_file_size = int.from_bytes(self.cmb_binary_data[8:12], byteorder='little', signed=False)
        self.cmb_object_count = int.from_bytes(self.cmb_binary_data[12:14], 'little', signed=False)
        cmb_transforms_count = int.from_bytes(self.cmb_binary_data[14:16], 'little', signed=False)
        
        transform_count_calc = cmb_transforms_count - 1
        get_cmb_transforms_data = self.get_cmb_transform_data(cmb_binary=self.cmb_binary_data)
        get_cmb_subtransform_data = self.get_cmb_subtransform_data(cmb_binary=self.cmb_binary_data, transforms_number=transform_count_calc)
        final_cmb_data = self.combine_transforms_cmb(transformation_count=cmb_transforms_count, 
                                                     base_transforms=get_cmb_transforms_data, sub_transforms=get_cmb_subtransform_data)
        
        self.processed_cmb = final_cmb_data
    
    def get_cmb_transform_data(self, cmb_binary=bytes) -> dict:
        """
        Get CMB Transform Data:\n
        This method take the Base Transform Data,\n
        later in the processing this data is used as kind of Delta Value\n
        for calculating the "In Current Frame" Object Rotation and Translation.
        """
        base_transforms: dict = {}
        for model_object_number in range(0, self.cmb_object_count):
            this_object_transform: dict = {}
            current_start_slice = 16 + (model_object_number * 12)
            current_end_slice = current_start_slice + 12
            this_base_transforms_binary = cmb_binary[current_start_slice:current_end_slice]
            this_base_transforms_converted = self.convert_cmb_transform(transform_data=this_base_transforms_binary)
            this_object_transform = {f'{self.model_name}_{model_object_number}': this_base_transforms_converted}
            base_transforms.update(this_object_transform)
        return base_transforms
    
    def get_cmb_subtransform_data(self, cmb_binary=bytes, transforms_number=int) -> dict:
        """
        Get CMB SubTransform Data:\n
        Take the SubTransform Data and Convert it,\n
        later to be used with the Base Transform Data.\n
        The Calculation is Done in Hierachy of "Current Transform" -> "Current Object".
        """
        final_subtransforms: dict = {}
        base_address = 16 + (self.cmb_object_count * 12)
        for current_object in range(0, self.cmb_object_count):
            this_object_subtransforms: dict = {}
            for current_subtransform_number in range(0, transforms_number):
                current_start_slice = base_address + (((current_subtransform_number * self.cmb_object_count) + current_object) * 8)
                current_end_slice = current_start_slice + 8
                current_cmb_transform = cmb_binary[current_start_slice:current_end_slice]
                convert_this_transforms = self.convert_cmb_subtransform(subtransform_data=current_cmb_transform)
                current_object_subtransform = {f'SubTransform_{current_subtransform_number}': convert_this_transforms}
                this_object_subtransforms.update(current_object_subtransform)
            object_subtransforms_dict = {f'{current_object}': this_object_subtransforms}
            final_subtransforms.update(object_subtransforms_dict)
        return final_subtransforms

    def convert_cmb_transform(self, transform_data=bytes) -> dict:
        """
        Convert CMB Transform:\n
        Take the Binary data from the Transforms and convert them\n
        into human readable values.
        """
        final_transform: dict = {"Rx": float(int.from_bytes(transform_data[0:2], 'little', signed=True) / round((4096/360), 12)), 
                                 "Ry": float(int.from_bytes(transform_data[2:4], 'little', signed=True) / round((4096/360), 12)), 
                                 "Rz": float(int.from_bytes(transform_data[4:6], 'little', signed=True) / round((4096/360), 12)), 
                                 "Tx": float(int.from_bytes(transform_data[6:8], 'little', signed=True) / 1000), 
                                 "Ty": float(int.from_bytes(transform_data[8:10], 'little', signed=True) / 1000), 
                                 "Tz": float(int.from_bytes(transform_data[10:12], 'little', signed=True) / 1000)}
        
        return final_transform
    
    def convert_cmb_subtransform(self, subtransform_data=bytes) -> dict:
        """
        Convert CMB SubTransform:\n
        Take the Binary data from the SubTransforms and convert them\n
        into human readable values.
        """
        final_subtransforms: dict = {}

        rotation_scalar = 1 << int.from_bytes(subtransform_data[0:1], byteorder='little', signed=True)
        rotation_bvec_x = int.from_bytes(subtransform_data[1:2], byteorder='little', signed=True) * rotation_scalar
        rotation_bvec_y = int.from_bytes(subtransform_data[2:3], byteorder='little', signed=True) * rotation_scalar
        rotation_bvec_z = int.from_bytes(subtransform_data[3:4], byteorder='little', signed=True) * rotation_scalar

        translation_scalar = 1 << int.from_bytes(subtransform_data[4:5], byteorder='little', signed=True)
        translation_bvec_x = int.from_bytes(subtransform_data[5:6], byteorder='little', signed=True) * translation_scalar
        translation_bvec_y = int.from_bytes(subtransform_data[6:7], byteorder='little', signed=True) * translation_scalar
        translation_bvec_z = int.from_bytes(subtransform_data[7:8], byteorder='little', signed=True) * translation_scalar

        final_subtransforms = {"SubRx": float(rotation_bvec_x) / round((4096/360), 12), 
                               "SubRy": float(rotation_bvec_y) / round((4096/360), 12), 
                               "SubRz": float(rotation_bvec_z) / round((4096/360), 12), 
                               "SubTx": float(translation_bvec_x / 1000), 
                               "SubTy": float(translation_bvec_y / 1000), 
                               "SubTz": float(translation_bvec_z / 1000)}
        return final_subtransforms
    
    def combine_transforms_cmb(self, transformation_count=int, base_transforms=dict, sub_transforms=dict) -> dict:
        """
        Combine Transforms CMB:\n
        Combine the Base Transforms and the SubTransforms per Keyframe\n
        (the resultant is the Actual Transformation).\n
        """
        cmb_animation: dict = {}
        store_objects_animation: dict = {}
        for current_object_number in range(0, self.cmb_object_count):
            this_object_keyframes: dict = {}
            for current_keyframe_number in range(0, transformation_count):
                get_this_0_frame_transform = base_transforms.get(f'{self.model_name}_{current_object_number}')
                if current_keyframe_number == 0:
                    this_rx = get_this_0_frame_transform.get(f'Rx')
                    this_ry = get_this_0_frame_transform.get(f'Ry')
                    this_rz = get_this_0_frame_transform.get(f'Rz')
                    this_tx = get_this_0_frame_transform.get(f'Tx')
                    this_ty = get_this_0_frame_transform.get(f'Ty')
                    this_tz = get_this_0_frame_transform.get(f'Tz')
                    cmb_transforms = {'Rx': this_rx, 'Ry': this_ry, 'Rz': this_rz, 
                                        'Tx': this_tx, 'Ty': this_ty, 'Tz': this_tz, 
                                        'Sx': 1.0, 'Sy': 1.0, 'Sz': 1.0}
                    keyframe = {f'Keyframe_{current_keyframe_number}': cmb_transforms}
                    continue_animating = {f'{self.model_name}_{current_object_number}': cmb_transforms}
                    this_object_keyframes.update(keyframe)
                    base_transforms.update(continue_animating)
                else:
                    get_this_frame = sub_transforms.get(f'{current_object_number}')
                    get_this_object_subtransform = get_this_frame.get(f'SubTransform_{current_keyframe_number - 1}')
                    final_rx = get_this_object_subtransform.get(f'SubRx') + get_this_0_frame_transform.get(f'Rx')
                    final_ry = get_this_object_subtransform.get(f'SubRy') + get_this_0_frame_transform.get(f'Ry')
                    final_rz = get_this_object_subtransform.get(f'SubRz') + get_this_0_frame_transform.get(f'Rz')
                    final_tx = get_this_object_subtransform.get(f'SubTx') + get_this_0_frame_transform.get(f'Tx')
                    final_ty = get_this_object_subtransform.get(f'SubTy') + get_this_0_frame_transform.get(f'Ty')
                    final_tz = get_this_object_subtransform.get(f'SubTz') + get_this_0_frame_transform.get(f'Tz')
                    cmb_transforms = {'Rx': final_rx, 'Ry': final_ry, 'Rz': final_rz, 
                                        'Tx': final_tx, 'Ty': final_ty, 'Tz': final_tz, 
                                        'Sx': 1.0, 'Sy': 1.0, 'Sz': 1.0}
                    keyframe = {f'Keyframe_{current_keyframe_number}': cmb_transforms}
                    this_object_keyframes.update(keyframe)
                    continue_animating = {f'{self.model_name}_{current_object_number}': cmb_transforms}
                    base_transforms.update(continue_animating)
            this_object_compiled_keyframes = {f'{self.model_name}_Object_{current_object_number}': this_object_keyframes}
            store_objects_animation.update(this_object_compiled_keyframes)
        
        cmb_animation = {f'{self.model_name}': {'TotalTransforms': transformation_count, 'ObjectCount':self.cmb_object_count, 
                                                            'AnimationType': 'CMB', 'AnimationsData': store_objects_animation}}
        
        return cmb_animation