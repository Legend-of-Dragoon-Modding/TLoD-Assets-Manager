"""
-------------------------------------------------------------
Folder Handler:
This module will work on anything related to Folders
manipulation.
-------------------------------------------------------------
INPUT:
dump_folder_path (Path in which files will be deployed).
file_nesting (Subdirectories to be created).
file_name (Final name to been given to the converted file).
-------------------------------------------------------------
OUTPUT:
Folders tree created on disk.
-------------------------------------------------------------

Copyright (C) 2024 DooMMetaL

"""
import os
from PyQt6.QtWidgets import QMessageBox

class Folders:
    def __init__(self, deploy_folder_path=str, file_nesting=str, file_name=str) -> None:
        self.deploy_folder_path = deploy_folder_path
        self.file_name = file_name
        self.file_nesting = file_nesting
        self.new_file_name: str = ''
        self.new_deploy_path: str = ''
        self.create_folders()
    
    def create_folders(self):
        nesting_to_file = self.file_nesting.replace(", ", "\\").strip()
        self.new_file_name = f'{self.deploy_folder_path}\\{nesting_to_file}\\{self.file_name}'
        search_last_slash = self.new_file_name.rfind('\\')
        self.new_deploy_path = self.new_file_name[0:search_last_slash]
        
        try:
            os.makedirs(self.new_deploy_path, exist_ok=True)
        except OSError:
            error_folder = f'Can\'t be created, permission denied'
            error_folder_creation = QMessageBox.critical(None, 'CRITICAL SYSTEM ERROR!!', f'Folder: {self.deploy_folder_path}\n{error_folder}', QMessageBox.StandardButton.Ok)
            exit()

class TextureFolder:
    def __init__(self, deploy_folder_path=str, file_nesting=str, file_name=str) -> None:
        self.deploy_folder_path = deploy_folder_path
        self.file_name = file_name
        self.file_nesting = file_nesting
        self.new_file_name: str = ''
        self.new_deploy_path: str = ''
        self.create_folders()

    def create_folders(self):
        nesting_to_file = self.file_nesting.replace(", ", "\\").strip()
        self.new_file_name = f'{self.deploy_folder_path}\\{nesting_to_file}\\{self.file_name}'
        search_last_slash = self.new_file_name.rfind('\\')
        self.new_deploy_path = self.new_file_name[0:search_last_slash]

        try:
            os.makedirs(self.new_deploy_path, exist_ok=True)
        except OSError:
            error_folder = f'Can\'t be created, permission denied'
            error_folder_creation = QMessageBox.critical(None, 'CRITICAL SYSTEM ERROR!!', f'Folder: {self.deploy_folder_path}\n{error_folder}', QMessageBox.StandardButton.Ok)
            exit()