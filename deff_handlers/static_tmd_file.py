"""

StaticTMD:
Take a Static TMD (a TMD Model with no animation) and convert it
Asset DICT Format:
Output to Asunder file: bin_to_split = {'Format': str, 'Data': dict}

Debug Files DICT Format: --> This only passed one time
Debug: dict = {'TMDReport': Bool, 'PrimPerObj': Bool, 'PrimData': Bool}
-------------------------------------------------------------------------------------------------------------------------
Copyright (C) 2024 DooMMetaL

"""

from file_handlers import asunder_binary_data, binary_to_dict

class StaticTmd:
    def __init__(self, static_tmd_dict=dict, path_to_file=str) -> None:
        """
        TMD Conversion handler for Static TMD Type.
        """
        self.static_tmd_dict = static_tmd_dict
        self.path_to_file = path_to_file
        self.processed_static_tmd_model: dict = {}
        self.static_model_object_count: int = 0
        self.static_tmd_processor()
    
    def static_tmd_processor(self):
        """
        Static TMD Processor:\n
        Take the TMD Path and Convert data into glTF Suitable format.
        """
        get_static_tmd_file_path = self.static_tmd_dict.get('File')
        get_static_tmd_name = self.static_tmd_dict.get('Name')
        get_static_tmd_frame_start = self.static_tmd_dict.get('Frame Start')
        get_static_tmd_frame_end = self.static_tmd_dict.get('Frame End')
        get_static_tmd_parent = self.static_tmd_dict.get('Parent')

        complete_static_tmd_path = f'{self.path_to_file}{get_static_tmd_file_path}'.replace('/', '\\').replace('\\\\', '\\')
        this_cc_model_dict = {'Format': 'TMD_CContainer', 'Path': complete_static_tmd_path}
        this_cc_model_binary = binary_to_dict.BinaryToDict(bin_file_to_dict=this_cc_model_dict)
        adjusted_cc_model_binary = self.adjust_tmd_address(original_model_dict=this_cc_model_binary.bin_data_dict)
        this_cc_model_converted = asunder_binary_data.Asset(bin_to_split=adjusted_cc_model_binary)

        # Create a 'fake' Animation just for holding the keyframes... anyhow in here i will be applying the Scripted Animation in the future
        fake_transforms = {'Translation': [0.0, 0.0, 0.0], 'Rotation': [0.0, 0.0, 0.0], 'Scale': [1.0, 1.0, 1.0]}
        static_animation = GeneratedAnimation(name=get_static_tmd_name, object_count=self.static_model_object_count, 
                                              transforms=fake_transforms, 
                                              start_frame=get_static_tmd_frame_start, end_frame=get_static_tmd_frame_end)

        this_static_tmd_final = {'Model': this_cc_model_converted.model_converted_data, 'Animations': static_animation.static_anim, 
                                   'Frame Start': get_static_tmd_frame_start, 'Frame End': get_static_tmd_frame_end, 
                                   'Parent': get_static_tmd_parent, 'Name': get_static_tmd_name}
        
        self.processed_static_tmd_model = this_static_tmd_final
    
    def adjust_tmd_address(self, original_model_dict=dict) -> dict:
        """
        Adjust TMD Address:\n
        As you might know, TMDs inside DEFF have a more extensive header,\n
        so to avoid reading unnecessary data, just make a check,\n
        sliding to the correct CContainer TMD Position.
        """
        new_model_dict: dict = {}
        this_model_type = original_model_dict.get('Format')
        this_model_old_binary_holder = original_model_dict.get('Data')

        c_container_start:int = 0
        this_model_old_binary = this_model_old_binary_holder[0]
        check_embedded_header_1 = int.from_bytes(this_model_old_binary[8:12], 'little', signed=False)
        check_embedded_header_2 = int.from_bytes(this_model_old_binary[12:20], 'little', signed=False)

        if check_embedded_header_1 != check_embedded_header_2:
            c_container_start = check_embedded_header_2
        else:
            c_container_start = check_embedded_header_2
        
        new_model_binary = [this_model_old_binary[c_container_start:]]
        new_model_dict = {'Format': this_model_type, 'Data': new_model_binary}
        # Get number of Objects
        self.static_model_object_count = int.from_bytes(new_model_binary[0][20:24], 'little', signed=False)
        
        return new_model_dict

class GeneratedAnimation:
    def __init__(self, name=str, object_count=int, transforms=dict, start_frame=int, end_frame=int):
        """
        Generated Animation:\n
        Will create a "fake" animation for Static TMD Models.\n
        Since it's way more easy to manage if every Model in glTF have it's own animation.
        """
        self.name = name
        self.object_count = object_count
        self.transforms = transforms
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.static_anim: dict = {}
        self.generate_static_anim()
    
    def generate_static_anim(self) -> None:
        translation = self.transforms.get('Translation')
        rotation = self.transforms.get('Rotation')
        scale = self.transforms.get('Scale')

        tx = round(float(translation[0] / 1000))
        ty = round(float(translation[1] / 1000))
        tz = round(float(translation[2] / 1000))

        rx = float(rotation[0]) / round((4096/360), 12)
        ry = float(rotation[1]) / round((4096/360), 12)
        rz = float(rotation[2]) / round((4096/360), 12)

        # Scale is divided by 4096 instead of 1000? // no, is not hahaha
        sx = float(scale[0]) #/ 4096
        sy = float(scale[1]) #/ 4096
        sz = float(scale[2]) #/ 4096

        total_frames = self.end_frame - self.start_frame
        
        static_animations: dict = {}

        store_objects_animation: dict = {}
        for current_object_number in range(0, self.object_count):
            this_object_keyframes: dict = {}
            #TODO: atm we are filling the keyframes just with the same placement... in the future here will be creating the Scripted Animation Keyframes
            for this_keyframe_number in range(0, total_frames):
                this_keyframe_transforms = {'Tx': tx, 'Ty': ty, 'Tz': tz, 'Rx': rx, 'Ry': ry, 'Rz':rz, 'Sx': sx, 'Sy': sy, 'Sz': sz}
                keyframe = {f'Keyframe_{this_keyframe_number}': this_keyframe_transforms}
                this_object_keyframes.update(keyframe)
            this_object_compiled_keyframes = {f'{self.name}_{current_object_number}': this_object_keyframes}
            store_objects_animation.update(this_object_compiled_keyframes)
        this_static_animation = {f'{self.name}': {'TotalTransforms': total_frames, 'ObjectCount':self.object_count, 
                                                            'AnimationType': 'STATIC', 
                                                            'StartFrame': self.start_frame, 'EndFrame': self.end_frame, 
                                                            'AnimationsData': store_objects_animation}}
        static_animations.update(this_static_animation)
        self.static_anim = static_animations
