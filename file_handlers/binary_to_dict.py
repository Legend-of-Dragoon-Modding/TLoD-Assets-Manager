"""

Binary to Dictionary:
This module will take any of the known Binary files
in TLoD and contain into Dictionary format
--------------------------------------------------------------------------------------------------------------
Input file: bin_file_to_dict = {'Format': str, 'Path': dict}
Format: TMD_Standard, TMD_CContainer, TMD_DEFF, SAF_CContainer, SAF_DEFF, CMB, LMB, TIM.
Path: File data path.
Embedded: FLAG used to know if the file have Embedded Animation data in it.
isDEFF: FLAG used to determine if the file is part of a DEFF or not.
--------------------------------------------------------------------------------------------------------------
:RETURN: -> self.bin_data_dict = {'Format': str, 'Data': dict}
DICT --> 'Data': [BINARY_DATA]
--------------------------------------------------------------------------------------------------------------
Copyright (C) 2024 DooMMetaL

"""
from PyQt6.QtWidgets import QMessageBox

class BinaryToDict:
    """Binary to Dict, take a Binary File to Open and deploy it into a Dict"""
    def __init__(self, bin_file_to_dict=dict) -> None:
        self.bin_file_to_dict = bin_file_to_dict
        self.bin_data_dict: dict = {'Format': '', 'Data': []}
        self.build_dict_from_bin()
    
    def build_dict_from_bin(self) -> None:
        file_format: str = self.bin_file_to_dict.get('Format')
        file_path: str = self.bin_file_to_dict.get('Path')

        file_read_to_split: list = []
        try:
            with open(file_path, 'rb') as binary_file_stream:
                binary_file_read = binary_file_stream.read()
                file_read_to_split.append(binary_file_read)
                binary_file_stream.close()
        except:
            error_cannot_open_file = QMessageBox.critical(None, 'CRITICAL ERROR!!', f'File: {file_path} not found!, check if SC Files folder is correct or deployed files are ok!!', QMessageBox.StandardButton.Ok)
            exit(1)
        
        self.bin_data_dict.update({'Format': file_format, 'Data': file_read_to_split})