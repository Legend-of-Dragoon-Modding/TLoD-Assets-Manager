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
    def __init__(self, cmb_binary_data=bytes) -> None:
        """Cmb Decoder and Processor, in a future will handle the creation of CMB files if needed"""
        self.cmb_binary_data = cmb_binary_data
        self.cmb_magic = b'\x43\x4D\x42\x20'
        self.processed_cmb: dict = {}
        self.process_cmb()
    
    def process_cmb(self):
        get_cmb_header = self.cmb_binary_data[0:4]
        self.check_if_cmb(cmb_data=get_cmb_header)
        cmb_file_size = int.from_bytes(self.cmb_binary_data[8:12], byteorder='little', signed=False) # Not used at all lol
        cmb_object_count = int.from_bytes(self.cmb_binary_data[12:14], 'little', signed=False)
        cmb_frames_count = int.from_bytes(self.cmb_binary_data[14:16], 'little', signed=False)

        base_transforms: dict = {}
        for model_object_number in range(0, cmb_object_count):
            this_object_transform: dict = {}
            current_transform_offset_start = 16 + (model_object_number * 12)
            current_transform_offset_end = current_transform_offset_start + 12
            this_base_transforms_binary = self.cmb_binary_data[current_transform_offset_start:current_transform_offset_end]
            this_base_transforms_converted = self.convert_cmb_transform(transform_data=this_base_transforms_binary)
            this_object_transform = {f'Object_Number_{model_object_number}': this_base_transforms_converted}
            base_transforms.update(this_object_transform)

        accumulative_transforms_offset = 16 + (cmb_object_count * 12)
        accumulative_keyframe_count = cmb_frames_count - 1
        accumulative_transforms: dict = {}
        for current_frame in range(0, accumulative_keyframe_count):
            current_frame_transforms: dict = {}
            for current_model_object in range(0, cmb_object_count):
                current_object_transforms: dict = {}
                offset_to_subtransforms_start = accumulative_transforms_offset + (current_frame * cmb_object_count + current_model_object) * 8
                offset_to_subtransforms_end = offset_to_subtransforms_start + 8
                get_subtransform_binary = self.cmb_binary_data[offset_to_subtransforms_start:offset_to_subtransforms_end]
                this_subtransforms_converted = self.convert_cmb_subtransform(subtransform_data=get_subtransform_binary)
                current_object_transforms = {f'Object_Number_{current_model_object}': this_subtransforms_converted}
                current_frame_transforms.update(current_object_transforms)
            final_object_transforms: dict = {f'This_Frame_{current_frame + 1}': current_frame_transforms}
            accumulative_transforms.update(final_object_transforms)
        
        combined_transforms = self.combine_transforms_cmb(frame_count=cmb_frames_count, object_count=cmb_object_count, 
                                                          base_transforms=base_transforms, sub_transforms=accumulative_transforms)
        
        self.processed_cmb = combined_transforms

    def check_if_cmb(self, cmb_data=bytes):
        if cmb_data != self.cmb_magic:
            print(f'This is not an CMB File: {cmb_data}')
            print(f'Report this as NOT CMB File!')
            exit()
    
    def convert_cmb_transform(self, transform_data=bytes) -> dict:
        final_transform: dict = {"Rx": float(int.from_bytes(transform_data[0:2], 'little', signed=True) / round((4096/360), 12)), 
                                 "Ry": float(int.from_bytes(transform_data[2:4], 'little', signed=True) / round((4096/360), 12)), 
                                 "Rz": float(int.from_bytes(transform_data[4:6], 'little', signed=True) / round((4096/360), 12)), 
                                 "Tx": float(int.from_bytes(transform_data[6:8], 'little', signed=True) / 1000), 
                                 "Ty": float(int.from_bytes(transform_data[8:10], 'little', signed=True) / 1000), 
                                 "Tz": float(int.from_bytes(transform_data[10:12], 'little', signed=True) / 1000)}
        return final_transform
    
    def convert_cmb_subtransform(self, subtransform_data=bytes) -> dict:
        final_subtransforms: dict = {}

        rotation_scalar = 1 << int.from_bytes(subtransform_data[0:1], byteorder='little', signed=False)
        rotation_bvec_x = int.from_bytes(subtransform_data[1:2], byteorder='little', signed=False) * rotation_scalar
        rotation_bvec_y = int.from_bytes(subtransform_data[2:3], byteorder='little', signed=False) * rotation_scalar
        rotation_bvec_z = int.from_bytes(subtransform_data[3:4], byteorder='little', signed=False) * rotation_scalar

        translation_scalar = 1 << int.from_bytes(subtransform_data[4:5], byteorder='little', signed=False)
        translation_bvec_x = int.from_bytes(subtransform_data[5:6], byteorder='little', signed=False) * translation_scalar
        translation_bvec_y = int.from_bytes(subtransform_data[6:7], byteorder='little', signed=False) * translation_scalar
        translation_bvec_z = int.from_bytes(subtransform_data[7:8], byteorder='little', signed=False) * translation_scalar

        final_subtransforms = {"SubRx": float(rotation_bvec_x) / round((4096/360), 12), 
                               "SubRy": float(rotation_bvec_y) / round((4096/360), 12), 
                               "SubRz": float(rotation_bvec_z) / round((4096/360), 12), 
                               "SubTx": float(translation_bvec_x / 1000), 
                               "SubTy": float(translation_bvec_y / 1000), 
                               "SubTz": float(translation_bvec_z / 1000)}

        return final_subtransforms
    
    def combine_transforms_cmb(self, frame_count=int, object_count=int, base_transforms=dict, sub_transforms=dict) -> dict:
        final_combined_transforms: dict = {}

        for current_frame in range(0, frame_count):
            if current_frame == 0:
                frame_0_cmb = {f'Frame_0': base_transforms}
                final_combined_transforms.update(frame_0_cmb)
            else:
                get_this_frame = sub_transforms.get(f'This_Frame_{current_frame}')
                final_frame_transforms: dict = {}
                this_frame_transforms: dict = {}
                for current_object in range(0, object_count):
                    # TODO it's really needed to update the transformations?, lets check it out
                    this_object_transforms: dict = {}
                    get_this_object_subtransform = get_this_frame.get(f'Object_Number_{current_object}')
                    get_this_0_frame_transform = base_transforms.get(f'Object_Number_{current_object}')

                    final_rx = get_this_object_subtransform.get(f'SubRx') + get_this_0_frame_transform.get(f'Rx')
                    final_ry = get_this_object_subtransform.get(f'SubRy') + get_this_0_frame_transform.get(f'Ry')
                    final_rz = get_this_object_subtransform.get(f'SubRz') + get_this_0_frame_transform.get(f'Rz')
                    final_tx = get_this_object_subtransform.get(f'SubTx') + get_this_0_frame_transform.get(f'Tx')
                    final_ty = get_this_object_subtransform.get(f'SubTy') + get_this_0_frame_transform.get(f'Tx')
                    final_tz = get_this_object_subtransform.get(f'SubTz') + get_this_0_frame_transform.get(f'Tx')

                    final_transforms: dict = {"Rx": final_rx, "Ry": final_ry, "Rz": final_rz, 
                                              "Tx": final_tx, "Ty": final_ty, "Tz": final_tz}
                    this_object_transforms = {f'Object_Number_{current_object}': final_transforms}
                    this_frame_transforms.update(this_object_transforms)
                
                final_frame_transforms = {f'Frame_{current_frame}': this_frame_transforms}
                final_combined_transforms.update(final_frame_transforms)
        return final_combined_transforms