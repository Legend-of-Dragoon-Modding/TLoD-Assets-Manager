"""

Animated TMD File: This module will take the TMD Object Data and Embedded Animations, 
process it

Most if not every part of the code will be based on the one found in: 
https://github.com/Legend-of-Dragoon-Modding/Severed-Chains
https://github.com/Legend-of-Dragoon-Modding/Severed-Chains/blob/main/src/main/java/legend/game/combat/deff/DeffPart.java

Copyright (C) 2024 Monoxide
-------------------------------------------------------------------------------------------------------------------------
Little or minor changes by:
Copyright (C) 2024 DooMMetaL

Asset DICT Format:
Output to Asunder file: bin_to_split = {'Format': str, 'Data': dict}

Debug Files DICT Format: --> This only passed one time
Debug: dict = {'TMDReport': Bool, 'PrimPerObj': Bool, 'PrimData': Bool}

"""

from file_handlers import asunder_binary_data

class StaticTmd:
    def __init__(self, static_tmd_binary=bytes) -> None:
        """
        Just a TMD Conversion handler for Static TMD.
        """
        self.static_tmd_binary = static_tmd_binary
        self.processed_static_tmd_model: dict = {}
        self.tmd_subfile_1: dict = {}
        self.tmd_subfile_2: dict = {}
        self.tmd_processor()
    
    def tmd_processor(self):
        """
        i will be using the SC Discriminator algorithm to get the TMD model
        """
        find_texture_offset = int.from_bytes(self.static_tmd_binary[8:12], byteorder='little', signed=False)
        find_tmd_offset = int.from_bytes(self.static_tmd_binary[12:16], byteorder='little', signed=False)
        find_animation_offset = int.from_bytes(self.static_tmd_binary[20:24], byteorder='little', signed=False)

        """NOTE: For Texture Data written in the header i will continue doing the checks, since in a future i plan
        use it to make the link between model and texture"""
        texture_info: bytes = b''
        if find_texture_offset != find_tmd_offset:
            texture_info = b''
        else:
            texture_info = b''
        
        tmd_cc_container: bytes = b''
        if (find_tmd_offset != find_animation_offset):
            tmd_cc_container = self.get_cc_container_files(cc_binary_data=self.static_tmd_binary[find_tmd_offset:])
        else:
            tmd_cc_container = b''
        
        self.processed_static_tmd_model = tmd_cc_container
    
    def get_cc_container_files(self, cc_binary_data=bytes) -> dict:
        final_cc_tmd_model: dict = {}
        read_offset_04_subfiles = int.from_bytes(cc_binary_data[4:8], byteorder='little', signed=False)
        read_offset_08_subfiles = int.from_bytes(cc_binary_data[4:8], byteorder='little', signed=False)
        """NOTE: Offset 0x04 and Offset 0x08 written in the header i will continue doing the checks, since in a future i plan
        use it to links those files to the TMD"""
        if read_offset_04_subfiles != 0:
            pass
        else:
            pass

        if read_offset_08_subfiles != 0:
            pass
        else:
            pass
        this_cc_model = {'Format': 'TMD_CContainer', 'Data': [cc_binary_data]}
        this_cc_model_converted = asunder_binary_data.Asset(bin_to_split=this_cc_model)
        final_cc_tmd_model = this_cc_model_converted.model_converted_data
        return final_cc_tmd_model