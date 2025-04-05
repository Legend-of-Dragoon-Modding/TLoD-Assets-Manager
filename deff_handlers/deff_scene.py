"""

DEFF Scene: This module will route the conversion depending on FLAGs
from the GUI Selected, if Complete Scene ENABLED, will convert everything in
a single glTF file, else, will convert selected Objects into split folders.
This Folders are: AnimatedTMD, StaticTMD, Particles.

Copyright (C) 2025 DooMMetaL
"""

from file_handlers import folder_handler, binary_to_dict, asunder_binary_data
from database_handler import DeffObjectDatabase
from deff_handlers import animated_tmd_file, deff_object_compile_gltf, deff_gltf_writer, static_tmd_file, cloned_tmd_file
from texture_handlers import png_writer

class DeffScene:
    def __init__(self, scene_flag=bool, convert_particles=bool, convert_textures=bool, data_to_convert=dict, selected_parent=str, sc_folder=str, deploy_folder=str):
        self.scene_flag = scene_flag
        self.convert_particles = convert_particles
        self.convert_textures = convert_textures
        self.data_to_convert = data_to_convert
        self.selected_parent = selected_parent
        self.sc_folder = sc_folder
        self.deploy_folder = deploy_folder
        self.scene_selector()

    def scene_selector(self):
        if self.scene_flag == True:
            self.convert_scene_complete()
        else:
            self.convert_each_object()
    
    def convert_scene_complete(self):
        # HERE LIES THE CODE FOR COMPLETE SCENE CONVERSION
        pass

    def convert_each_object(self) -> bool:
        # Getting General DEFF Properties
        deff_name = self.data_to_convert.get('Name')
        objects_path = self.data_to_convert.get('Folder')
        textures_path = self.data_to_convert.get('Texture Folder')
        total_frames = self.data_to_convert.get('Total Frames')
        vsync_divider = self.data_to_convert.get('VSyncDivider')
        extra_textures = self.data_to_convert.get('Extra Textures')
        animated_tmd_bool = self.data_to_convert.get('AnimatedTMDBool')
        static_tmd_bool = self.data_to_convert.get('StaticTMDBool')
        particle_bool = self.data_to_convert.get('ParticleBool')
        deff_sequence = self.data_to_convert.get('Sequence')
        deff_sequence_folder = self.data_to_convert.get('Sequence Folder')

        object_to_convert_file_path = f'{self.sc_folder}\\{objects_path}'

        change_deff_name = deff_name.replace(' ', '_')
        
        for current_deff_object_name in deff_sequence:
            current_object_database = DeffObjectDatabase(current_object=current_deff_object_name, sequence_folder=deff_sequence_folder)
            current_object_dict = current_object_database.current_object_dict
            # Get File Type and Textures Path from Current Object
            get_object_type = current_object_dict.get(f'Filetype')
            get_object_extra_textures = current_object_dict.get(f'ExtraTextures')
            
            get_object_textures_path = current_object_dict.get(f'Texture') # This is a list, since could be more than 1 Texture per Object
            exist_texture_bool: bool = False
            if get_object_textures_path != ['NONE']:
                exist_texture_bool = True

            animated_tmd_types = ['AnimatedTMD-CMB', 'AnimatedTMD-SAF', 'AnimatedTMD-LMB']
            if (get_object_type in animated_tmd_types) and (animated_tmd_bool != 'False'):
                # Create Main Deploy Folders for AnimatedTMD
                animated_tmd_nesting = ['DEFF', self.selected_parent, change_deff_name, 'AnimatedTMD', current_deff_object_name]
                animated_tmd_folders = self.create_folders(file_nesting=animated_tmd_nesting, deff_textures_path=textures_path, obj_textures_path=get_object_textures_path)
                animated_tmd_deploy_folder = animated_tmd_folders[0]
                animated_tmd_texture_folder = animated_tmd_folders[1]
                animated_tmd_converted = animated_tmd_file.TmdAnimatedFile(animated_tmd_data=current_object_dict, path_to_file=object_to_convert_file_path)
                animated_tmd_compiled = deff_object_compile_gltf.NewGltfDeffObject(data_to_convert=animated_tmd_converted.processed_animated_tmd, vsync_divider=vsync_divider)
                write_gltf = deff_gltf_writer.gltfFile(gltf_to_convert=animated_tmd_compiled.gltf_format, gltf_deploy_path=animated_tmd_deploy_folder)
                if (exist_texture_bool == True) and (self.convert_textures != False):
                    convert_texture = self.convert_and_write_textures(text_folder=textures_path, text_files=get_object_textures_path, 
                                                                      deploy_folder=animated_tmd_texture_folder, 
                                                                      extra_textures_folder=extra_textures, extra_texture_files=get_object_extra_textures)
            
            elif (get_object_type == 'ClonedTMD') and (animated_tmd_bool != 'False'):
                # For Cloned TMD i do the assumption that all of them are Animated, that's why i put them into AnimatedTMD Folder
                cloned_tmd_nesting = ['DEFF', self.selected_parent, change_deff_name, 'AnimatedTMD', current_deff_object_name]
                cloned_tmd_folders = self.create_folders(file_nesting=cloned_tmd_nesting, deff_textures_path=textures_path, obj_textures_path=get_object_textures_path)
                cloned_tmd_deploy_folder = cloned_tmd_folders[0]
                cloned_tmd_texture_folder = cloned_tmd_folders[1]
                cloned_tmd_converted = cloned_tmd_file.TmdClonedFile(cloned_tmd_data=current_object_dict, path_to_file=object_to_convert_file_path, sc_folder=self.sc_folder)
                cloned_tmd_compiled = deff_object_compile_gltf.NewGltfDeffObject(data_to_convert=cloned_tmd_converted.processed_animated_tmd, vsync_divider=vsync_divider)
                write_gltf = deff_gltf_writer.gltfFile(gltf_to_convert=cloned_tmd_compiled.gltf_format, gltf_deploy_path=cloned_tmd_deploy_folder)
                if (exist_texture_bool == True) and (self.convert_textures != False):
                    convert_texture = self.convert_and_write_textures(text_folder='', text_files=get_object_textures_path, 
                                                                      deploy_folder=cloned_tmd_texture_folder, 
                                                                      extra_textures_folder=extra_textures, extra_texture_files=get_object_extra_textures)
                
            elif (get_object_type == 'StaticTMD') and (static_tmd_bool != 'False'):
                # Create Main Deploy Folders for StaticTMD
                static_tmd_nesting = ['DEFF', self.selected_parent, change_deff_name, 'StaticTMD', current_deff_object_name]
                static_tmd_folders = self.create_folders(file_nesting=static_tmd_nesting, deff_textures_path=textures_path, obj_textures_path=get_object_textures_path)
                static_tmd_deploy_folder = static_tmd_folders[0]
                static_tmd_texture_folder = static_tmd_folders[1]
                static_tmd_converted = static_tmd_file.StaticTmd(static_tmd_dict=current_object_dict, path_to_file=object_to_convert_file_path)
                static_tmd_compiled = deff_object_compile_gltf.NewGltfDeffObject(data_to_convert=static_tmd_converted.processed_static_tmd_model, vsync_divider=vsync_divider)
                write_gltf = deff_gltf_writer.gltfFile(gltf_to_convert=static_tmd_compiled.gltf_format, gltf_deploy_path=static_tmd_deploy_folder)
                if (exist_texture_bool == True) and (self.convert_textures != False):
                    convert_texture = self.convert_and_write_textures(text_folder=textures_path, text_files=get_object_textures_path, 
                                                                      deploy_folder=static_tmd_texture_folder, 
                                                                      extra_textures_folder=extra_textures, extra_texture_files=get_object_extra_textures)
            
            elif (self.convert_particles == True) and (particle_bool != 'False'):
                # Create Main Deploy Folders for Particles
                particles_nesting = ['DEFF', self.selected_parent, change_deff_name, 'Particles', current_deff_object_name]
                particles_folders = self.create_folders(file_nesting=particles_nesting, deff_textures_path=textures_path, obj_textures_path=get_object_textures_path)
                particles_deploy_folder = particles_folders[0]
                particles_texture_folder = particles_folders[1]
    
    def create_folders(self, file_nesting=list, deff_textures_path=str, obj_textures_path=list) -> tuple[str, str]:
        """
        Create Folders:\n
        Will procede in creation of folders On-Demand,\n
        In cases in which no object is converted, this gone to be ignored.
        """
        object_dump_path: str = ''
        create_object_folder = folder_handler.DeffFolders(deploy_folder_path=self.deploy_folder, file_nesting=file_nesting)
        object_dump_path = create_object_folder.new_deploy_path
        
        texture_dump_path: str = ''
        if (self.convert_textures == True) and (deff_textures_path != 'NONE') and (obj_textures_path != ['NONE']):
            texture_object_nesting = ['Textures']
            texture_folder = folder_handler.DeffFolders(deploy_folder_path=object_dump_path, file_nesting=texture_object_nesting)
            texture_dump_path = texture_folder.new_deploy_path.replace('\\\\', '\\') # Sorry this a very shitty solution ¯\_(ツ)_/¯
        
        return object_dump_path, texture_dump_path
    
    def convert_and_write_textures(self, text_folder=str, text_files=list, deploy_folder=str, extra_textures_folder=list, extra_texture_files=list) -> None:
        """
        Convert Textures:\n
        Convert and Write into PNG Files the TLoD Textures.\n
        Must exist a Texture in the database and selected to convert by the user, to Convert them.
        """
        if text_files != ['EXTRA']:
            retry_sc_folder = self.sc_folder
            if 'CLONED' in text_files[0]:
                self.sc_folder = self.sc_folder.replace('SECT\\DRGN0.BIN', '')
                new_files = []
                for current_texture_file in text_files:
                    change_path = current_texture_file.replace('CLONED:', '')
                    new_files.append(change_path)
                text_files = new_files
            texture_folder_full_path = f'{self.sc_folder}{text_folder}'.replace('/', '\\').replace('\\\\', '\\').replace('\\\\\\', '\\')
            textures_initial_dict = {'Format': 'TIM', 'Path': texture_folder_full_path, 'Files': text_files}
            textures_to_dict = binary_to_dict.BinariesToDict(binaries_to_dict=textures_initial_dict)
            for current_texture_name in textures_to_dict.binaries_data_dict:
                new_texture_name = current_texture_name
                if len(current_texture_name) > 3:
                    take_extra_positions = new_texture_name.rfind('\\')
                    new_texture_name = new_texture_name[(take_extra_positions + 1):]
                current_texture_dict = textures_to_dict.binaries_data_dict.get(f'{current_texture_name}')
                convert_texture_rgba = asunder_binary_data.Asset(bin_to_split=current_texture_dict)
                current_rgba_texture = convert_texture_rgba.texture_converted_data
                deploy_texture_full = f'{deploy_folder}\\{new_texture_name}'
                write_texture = png_writer.PngFile(texture_data=current_rgba_texture, file_deploy_path=deploy_texture_full, texture_type='TIM')
            self.sc_folder = retry_sc_folder
        else:
            extra_texture_folder_full_path = f'{self.sc_folder}{extra_textures_folder}'.replace('/', '\\').replace('\\\\', '\\').replace('\\\\\\', '\\')
            extra_textures_initial_dict = {'Format': 'TIM', 'Path': extra_texture_folder_full_path, 'Files': extra_texture_files}
            extra_textures_to_dict = binary_to_dict.BinariesToDict(binaries_to_dict=extra_textures_initial_dict)
            for current_extra_texture in extra_textures_to_dict.binaries_data_dict:
                new_extra_texture_name = f'extra_{current_extra_texture}'
                current_extra_texture_dict = extra_textures_to_dict.binaries_data_dict.get(f'{current_extra_texture}')
                convert_extratexture_rgba = asunder_binary_data.Asset(bin_to_split=current_extra_texture_dict)
                current_extra_rgba_texture = convert_extratexture_rgba.texture_converted_data
                deploy_extra_texture_full = f'{deploy_folder}{new_extra_texture_name}'
                write_texture = png_writer.PngFile(texture_data=current_extra_rgba_texture, file_deploy_path=deploy_extra_texture_full, texture_type='TIM')