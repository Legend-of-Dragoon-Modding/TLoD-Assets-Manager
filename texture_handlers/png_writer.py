"""

PNG Writer:
This module will take the Processed Texture Data\n
and convert it into PNG format.
--------------------------------------------------------------------------------------------------------------
Input Data: Texture Processed DICT.
--------------------------------------------------------------------------------------------------------------
:RETURN: -> None; FILE WRITE ON DISK
--------------------------------------------------------------------------------------------------------------
Copyright (C) 2024 DooMMetaL

"""
from PIL import Image

class PngFile:
    def __init__(self, texture_data=dict, file_deploy_path=str, texture_type=str) -> None:
        self.texture_data = texture_data
        self.file_deploy_path = file_deploy_path
        self.texture_type = texture_type
        self.write_png_file()
    
    def write_png_file(self) -> None:
        if self.texture_type == 'TIM':
            self.write_tim_to_png()
        elif self.texture_type == 'PXL':
            print('PXL FILE')
        elif self.texture_type == 'MCQ':
            self.write_mcq_to_png()
    
    def write_tim_to_png(self) -> None:
        rgba_data = self.texture_data.get('RGBA_Data')
        size_img = self.texture_data.get('SizeImg')
        size_w = size_img.get('X')
        size_h = size_img.get('Y')
        total_files = len(rgba_data)
        for current_file in range(0, total_files):
            complete_path = self.file_deploy_path + f'_{current_file}.png'
            this_file = rgba_data.get(f'IMAGE_{current_file}')
            img = Image.frombytes('RGBA', (size_w, size_h), this_file)
            img.save(complete_path, format='png')
    
    def write_mcq_to_png(self) -> None:
        rgba_data = self.texture_data.get('RGBA_Data')
        all_sizes = self.texture_data.get('SizeImg')
        standard_size_width = all_sizes.get('IntendedX')
        standard_size_height = all_sizes.get('IntendedY')
        align_size_width = all_sizes.get('AlignX')
        align_size_height = all_sizes.get('AlignY')
        complete_path = self.file_deploy_path + f'_MCQ.png'

        if standard_size_height == 256:
            img = Image.frombytes('RGBA', (standard_size_width, standard_size_height), rgba_data)
            img.save(complete_path, format='png')
        else:
            img = Image.frombytes('RGBA', (align_size_width, align_size_height), rgba_data)
            unshuffled_img = Image.new('RGBA', (standard_size_width, standard_size_height), None)
            img_tile_list = []
            for x in range(0, align_size_width, 16):
                for y in range(0, align_size_height, 16):
                    img_tile_list.append(img.crop((x, y, x+16, y+16)))
            for x in range(0, standard_size_width, 16):
                for y in range(0, standard_size_height, 16):
                    tile = img_tile_list.pop(0)
                    unshuffled_img.paste(tile, (x, y, x+16, y+16))
            unshuffled_img.save(complete_path, format='png')

if __name__ == '__main__':
    new_png = PngFile(texture_data={}, file_deploy_path='', texture_type='TIM')