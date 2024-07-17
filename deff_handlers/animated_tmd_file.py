"""

Animated TMD File: This module will take the TMD Object Data and Embedded Animations, 
process it

Most if not every part of the code will be based on the one found in: 
https://github.com/Legend-of-Dragoon-Modding/Severed-Chains
https://github.com/Legend-of-Dragoon-Modding/Severed-Chains/blob/main/src/main/java/legend/game/combat/deff/Lmb.java
https://github.com/Legend-of-Dragoon-Modding/Severed-Chains/blob/main/src/main/java/legend/game/combat/deff/LmbType0.java
https://github.com/Legend-of-Dragoon-Modding/Severed-Chains/blob/main/src/main/java/legend/game/combat/deff/DeffPart.java
https://github.com/Legend-of-Dragoon-Modding/Severed-Chains/blob/main/src/main/java/legend/game/combat/deff/Cmb.java
https://github.com/Legend-of-Dragoon-Modding/Severed-Chains/blob/main/src/main/java/legend/game/types/TmdAnimationFile.java

Copyright (C) 2024 Monoxide
-------------------------------------------------------------------------------------------------------------------------
Little or minor changes by:
Copyright (C) 2024 DooMMetaL

Asset DICT Format:
Output to Asunder file: bin_to_split = {'Format': str, 'Data': dict}

Debug Files DICT Format: --> This only passed one time
Debug: dict = {'TMDReport': Bool, 'PrimPerObj': Bool, 'PrimData': Bool}

"""

from deff_handlers import lmb_file, cmb_file, saf_file
from file_handlers import asunder_binary_data

class TmdEmbeddedAnimation:
    def __init__(self, animated_tmd_binary=bytes) -> None:
        """
        Split a TMD File from it's Embedded Animation, process them for collada conversion.\n
        NOTE: Since CMB and LMB have several file MAGIC checks, i will do some workarounds to avoid changing everything.\n
        Monoxide, sorry for this hacky solution."""
        self.animated_tmd_binary = animated_tmd_binary
        self.lmb_magic = b'\x4C\x4D\x42\x00'
        self.cmb_magic = b'\x43\x4D\x42\x20'
        self.saf_magic = b'\x0c\x00\x00\x00' # Maybe not needed at all STATUS: Confirmed
        self.processed_animated_tmd_animation: dict = {}
        self.processed_animated_tmd_model: dict = {}
        self.tmd_processor()
        self.animated_tmd_discriminator()
    
    def animated_tmd_discriminator(self):
        """
        i will be using the SC Discriminator algorithm to get which 
        Type of Animated TMD is.
        """
        # Animation Discriminator
        animation_data: dict = {}

        find_animated_tmd_magic_offset = int.from_bytes(self.animated_tmd_binary[20:24], byteorder='little', signed=False)
        find_animated_tmd_magic = self.animated_tmd_binary[find_animated_tmd_magic_offset:(find_animated_tmd_magic_offset + 4)]
        animation_file = self.animated_tmd_binary[find_animated_tmd_magic_offset:]
        if find_animated_tmd_magic == self.lmb_magic:
            build_full_lmb_file_bytes = b'\x00\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00' + animation_file
            this_lmb_data = lmb_file.Lmb(lmb_binary_data=build_full_lmb_file_bytes)
            lmb_dict = {'LMB': this_lmb_data}
            animation_data.update(lmb_dict)
        elif find_animated_tmd_magic == self.cmb_magic:
            this_cmb_data = cmb_file.Cmb(cmb_binary_data=animation_file)
            cmb_dict = {'CMB': this_cmb_data}
            animation_data.update(cmb_dict)
        else:
            this_saf_data = saf_file.Saf(saf_binary_data=animation_file)
            saf_dict = {'SAF': this_saf_data}
            animation_data.update(saf_dict)

        self.processed_animated_tmd_animation = animation_data
        
    def tmd_processor(self):
        """
        i will be using the SC Discriminator algorithm to get the TMD model
        """
        find_texture_offset = int.from_bytes(self.animated_tmd_binary[8:12], byteorder='little', signed=False)
        find_tmd_offset = int.from_bytes(self.animated_tmd_binary[12:16], byteorder='little', signed=False)
        find_animation_offset = int.from_bytes(self.animated_tmd_binary[20:24], byteorder='little', signed=False)

        """NOTE: For Texture Data written in the header i will continue doing the checks, since in a future i plan
        use it to make the link between model and texture"""
        texture_info: bytes = b''
        if find_texture_offset != find_tmd_offset:
            texture_info = b''
        else:
            texture_info = b''
        
        tmd_cc_container: bytes = b'' 
        if find_tmd_offset != find_animation_offset:
            tmd_cc_container = self.animated_tmd_binary[find_tmd_offset:find_animation_offset]
        else:
            tmd_cc_container = b''
        
        this_cc_model = {'Format': 'TMD_CContainer', 'Data': [tmd_cc_container]}
        convert_model = asunder_binary_data.Asset(bin_to_split=this_cc_model)
        self.processed_animated_tmd_model = convert_model.model_converted_data