"""

Animated TMD File: 
This module will receive the AnimatedTMD Object Dict and process it.

AnimatedTMD Dict:
FILE - FILETYPE - TEXTURES - ANIM FILES - PARENT - FRAME START - FRAME END - PARTICLE TYPE - COUNT - SIMULATION TYPE - LIFESPAN

animated_tmd_dict: dict = {'File': None, 'Filetype': None, 'Texture': None, 'Anim Files': None, 'Parent': None, 
'Frame Start': None, 'Frame End': None, 'Particle Type': None, 'Count': None, 'Simulation Type': None, 'Lifespan': None, 
'Script Animation': None}

Asset DICT Format:
Output to Asunder file: bin_to_split = {'Format': str, 'Data': dict}

Debug Files DICT Format: --> This only passed one time
Debug: dict = {'TMDReport': Bool, 'PrimPerObj': Bool, 'PrimData': Bool}
-------------------------------------------------------------------------------------------------------------------------
Copyright (C) 2025 DooMMetaL

"""

from deff_handlers import lmb_file, cmb_file, saf_file
from file_handlers import asunder_binary_data

class TmdAnimatedFile:
    def __init__(self, animated_tmd_data=dict, path_to_file=str) -> None:
        """
        Split a TMD File from it's Animation, also adds the Extra Anims if required,\n
        Finally process them for glTF conversion.\n
        """
        self.animated_tmd_data = animated_tmd_data
        self.path_to_file = path_to_file
        self.saf_magic = b'\x0C\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        self.lmb_magic = b'\x4C\x4D\x42\x00'
        self.cmb_magic = b'\x43\x4D\x42\x20'
        self.processed_animated_tmd: dict = {}
        self.animated_tmd_process()
        
    def animated_tmd_process(self):
        """
        Animated TMD Process:\n
        In here i will split the Animated TMD into Model and Animation in separated chunks.\n
        Also will adding the Extra Animations if present.
        After conversion all the data will be contained in self.processed_animated_tmd dict.
        """
        get_animated_tmd_file_path = self.animated_tmd_data.get('File')
        get_animated_tmd_name = self.animated_tmd_data.get('Name')
        get_animated_tmd_type = self.animated_tmd_data.get('Filetype')
        get_animated_tmd_extra_anims = self.animated_tmd_data.get('Anim Files')
        get_animated_tmd_frame_start = self.animated_tmd_data.get('Frame Start')
        get_animated_tmd_frame_end = self.animated_tmd_data.get('Frame End')
        get_animated_tmd_parent = self.animated_tmd_data.get('Parent')

        complete_file_path = f'{self.path_to_file}{get_animated_tmd_file_path}'.replace('/', '\\').replace('\\\\', '\\')
        animated_tmd_binary: bytes = b''
        try:
            with open(complete_file_path, 'rb') as binary_file:
                animated_tmd_binary = binary_file.read()
                binary_file.close()
        except FileNotFoundError:
            anim_tmd_file_error = f'File: {complete_file_path} - Do NOT EXIST!!!.\nClosing Tool to avoid further errors...'
            print(anim_tmd_file_error)
            exit()

        find_tmd_offset = int.from_bytes(animated_tmd_binary[12:16], byteorder='little', signed=False)
        find_animation_offset = int.from_bytes(animated_tmd_binary[20:24], byteorder='little', signed=False)

        model_binary = animated_tmd_binary[find_tmd_offset:find_animation_offset]
        animation_binary = animated_tmd_binary[find_animation_offset:]
        this_cc_model = {'Format': 'TMD_CContainer', 'Data': [model_binary]}
        convert_model = asunder_binary_data.Asset(bin_to_split=this_cc_model)

        animations_converted: dict = {}
        # Numeration for Animations would be 0 {Reserved for Embedded Animation}, 1 and so on for Extra Animations
        if get_animated_tmd_extra_anims == ['NONE']:
            # Converting right now; We'll Do it LIVE... We'll Do it LIVE!!! ...f**k**g thing suxx!! for more context: yu.tube =fXZj4Wy58Pk
            find_animation_type = get_animated_tmd_type.find('-')
            animation_type = get_animated_tmd_type[(find_animation_type + 1):]
            if animation_type == 'LMB':
                animation_type = 'LMB0'
            
            animation_name = f'{get_animated_tmd_name}_Animation_0'
            single_animation_converted = self.animation_convert(animation_data=animation_binary, anim_type=animation_type, anim_name=animation_name)
            animations_converted.update(single_animation_converted)
        
        else:
            # TODO: When the times comes, CHECK THIS SHIT
            find_animation_type = get_animated_tmd_type.find('-')
            animation_type = get_animated_tmd_type[(find_animation_type + 1):]
            if animation_type == 'LMB':
                animation_type = 'LMB0'
            animation_name_0 = f'{get_animated_tmd_name}_Animation_0'
            embedded_animation_convert = self.animation_convert(animation_data=animation_binary, anim_type=animation_type, anim_name=animation_name_0)
            animations_converted.update(embedded_animation_convert)
            total_extra_animations = len(get_animated_tmd_extra_anims)
            for current_extra_animation in range(0, total_extra_animations):
                current_animation_file = get_animated_tmd_extra_anims[current_extra_animation]
                complete_extra_anim_file_path = f'{self.path_to_file}{current_animation_file}'.replace('/', '\\').replace('\\\\', '\\')
                animation_binary_file: bytes = b''
                try:
                    with open(complete_extra_anim_file_path, 'rb') as anim_binary_file:
                        animation_binary_file = anim_binary_file.read()
                        anim_binary_file.close()
                except FileNotFoundError:
                    animation_file_error = f'File: {complete_extra_anim_file_path} - Do NOT EXIST!!!.\nClosing Tool to avoid further errors...'
                    print(animation_file_error)
                    exit()

                get_animation_binary_and_type = self.standalone_animation(binary_file=animation_binary_file, file_path=complete_extra_anim_file_path)
                animation_data_standalone = get_animation_binary_and_type[0]
                animation_type_standalone = get_animation_binary_and_type[1]
                # Since Animation slot 0 is reserved for the Embedded Animation, the first standalone animation would be using 1 and so on
                animation_name_extra = f'{get_animated_tmd_name}_Animation_{current_extra_animation + 1}'
                converted_data_extra = self.animation_convert(animation_data=animation_data_standalone, anim_type=animation_type_standalone, anim_name=animation_name_extra)
                animations_converted.update(converted_data_extra)
        
        this_animated_tmd_final = {'Model': convert_model.model_converted_data, 'Animations': animations_converted, 
                                   'Frame Start': get_animated_tmd_frame_start, 'Frame End': get_animated_tmd_frame_end, 
                                   'Parent': get_animated_tmd_parent, 'Name': get_animated_tmd_name}
        
        self.processed_animated_tmd = this_animated_tmd_final
    
    def standalone_animation(self, binary_file=bytes, file_path=str) -> tuple[bytes, str]:
        """
        Standalone Animation:\n
        This Function will check the Type of Animation from this Animation file.\n
        Will return the Animation Binary (from the Animation Header start) and the File Type. 
        """
        animation_binary: bytes = b''
        animation_type: str = ''
        # This is a little random, but actually i didn't find some of these headers that get the magic beyond 40 bytes or more
        get_animation_saf = binary_file[0:40].find(self.saf_magic)
        get_animation_cmb = binary_file[0:40].find(self.cmb_magic)
        get_animation_lmb = binary_file[0:40].find(self.lmb_magic)
        
        if get_animation_saf != -1:
            saf_pointer = int.from_bytes(binary_file[8:12], 'little', signed=False)
            animation_type = 'SAF'
            animation_binary = binary_file[saf_pointer:]
        elif get_animation_cmb != -1:
            cmb_pointer = int.from_bytes(binary_file[8:12], 'little', signed=False)
            animation_type = 'CMB'
            animation_binary = binary_file[cmb_pointer:]
        elif get_animation_lmb != -1:
            lmb_pointer = int.from_bytes(binary_file[8:12], 'little', signed=False)
            lmb_type = int.from_bytes(binary_file[4:8], 'little', signed=False)
            if lmb_type == 0:
                animation_type = 'LMB0'
            elif lmb_type == 1:
                animation_type = 'LMB1'
            elif lmb_type == 2:
                animation_type = 'LMB2'
            else:
                lmb_animation_error = f'ERROR - File: {file_path}, Unsupported LMB Type: {lmb_type}.\nClosing tool to avoid further errors...'
                print(lmb_animation_error)
                exit()
            animation_binary = binary_file[lmb_pointer:]
        else:
            animation_type_not_found_error = f'CRITICAL ERROR - File: {file_path}, Animation Type not found!!.\nClosing tool to avoid further errors...'
            print(animation_type_not_found_error)
            exit()

        return animation_binary, animation_type

    def animation_convert(self, animation_data=bytes, anim_type=str, anim_name=str) -> dict:
        """
        Animation Convert:\n
        Depending on the Animation Type, will be the result.\n
        Animation Types are:\n
        AnimatedTMD-SAF; AnimatedTMD-CMB; AnimatedTMD-LMB; {Embedded}\n
        SAF; CMB; LMB0; LMB1; LMB2. {Extra Animations - Standalone files}
        """
        # Animation Discriminator
        animation_data_converted: dict = {}
        # I need to refactor all LMB
        # TODO: LMBType1; LMBType2;
        # The conversion sorting is Objects->KeyframeN

        if anim_type == 'SAF':
            processed_saf = saf_file.Saf(saf_binary_data=animation_data, model_name=anim_name)
            animation_data_converted = processed_saf.processed_saf
        elif anim_type == 'CMB':
            process_cmb = cmb_file.Cmb(cmb_binary_data=animation_data, model_name=anim_name)
            animation_data_converted = process_cmb.processed_cmb
        elif (anim_type == 'LMB0') or (anim_type == 'LMB1') or (anim_type == 'LMB2'):
            processed_lmb = lmb_file.Lmb(lmb_binary_data=animation_data, lmb_type=anim_type, model_name=anim_name)
            animation_data_converted = processed_lmb.processed_lmb

        return animation_data_converted