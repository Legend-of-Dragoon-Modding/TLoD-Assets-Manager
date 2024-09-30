"""

Conversion Interfaces:
This module is in charge of manage and store the interface
between the GUI Windows and the Code for converting itself,
in other words it's a kind of 'handler'.

Copyright (C) 2024 DooMMetaL

"""
from file_handlers import asunder_binary_data, binary_to_dict, folder_handler, debug_files_writer
from gltf_handlers import gltf_compiler, gltf_converter
from texture_handlers import png_writer

class BattleConversionInterface():
    def __init__(self, list_convert=list, assets_battle_database=dict, conv_passive_anims=bool, conv_attack_anims=bool, conv_text=bool, 
                 sc_folder=str, tmd_report=bool, prim_report=bool, generate_primdata=bool, deploy_folder=str) -> None:
        self.selected_conversion_list = list_convert
        self.battle_models_database = assets_battle_database
        self.conv_passive_anims = conv_passive_anims
        self.conv_attack_anims = conv_attack_anims
        self.convert_textures = conv_text
        self.sc_folder = sc_folder
        self.tmd_report = tmd_report
        self.prim_report = prim_report
        self.generate_primdata = generate_primdata
        self.deploy_folder = deploy_folder
        self.write_gltf()

    def write_gltf(self) -> None:
        """
        Clean the Selected Items List to fit the following logic:
        Parent->Child (Model Object to Convert)
        SuperParent->Parent->Child (Model Object to Convert) ==> This is used in CutScenes and Characters list due to the nesting
        """
        model_data_and_info = self.get_current_model_data(selection=self.selected_conversion_list)
        gather_model_data = self.get_data_to_convert(model_data_info=model_data_and_info)
        convert_to_gltf = self.convert_to_gltf(model_final_dict=gather_model_data)

    def get_current_model_data(self, selection=list) -> tuple[dict, str, list]:
        """
        Get current Model Data:\n
        Will grab the Data needed, based on the self.selected_conversion_list [Selections made by user]\n
        list size. This because Characters and CutScenes need one step more,\n
        due to the Dictionary nesting needed.
        """
        """
        Example of difference:
        Battle -> Enemies -> Mantis
        CutScenes -> Urobolos Death -> Dart
        this also impact to the nesting in the Dictionary which contains the Data.
        """
        model_data_dict: dict = {}
        parent_name: str = ''
        nesting_folders: list = []
        if len(selection) == 2:
            parent_name = selection[0].replace(" ", "_")
            model_name = selection[1]
            models_complete_dict = self.battle_models_database.get(f'{parent_name}')
            model_data_dict = models_complete_dict.get(f'{model_name}')
            nesting_folders.append(parent_name)
            nesting_folders.append(model_name)
        elif len(selection) >= 3:
            parent_name = selection[0].replace(" ", "_").strip()
            subparent_name = selection[1]
            model_name = selection[2]
            models_complete_dict = self.battle_models_database.get(f'{parent_name}')
            models_sub_dict = models_complete_dict.get(f'{subparent_name}')
            model_data_dict = models_sub_dict.get(f'{model_name}')
            nesting_folders.append(parent_name)
            nesting_folders.append(subparent_name)
            nesting_folders.append(model_name)

        return model_data_dict, parent_name, nesting_folders
    
    def get_data_to_convert(self, model_data_info=tuple) -> dict:
        """
        Get Data to Convert:\n
        Will take the data from the current Model selected dictionary\n
        and extract all the requeried data from it.
        """
        
        model_data = model_data_info[0]
        model_parent = model_data_info[1]

        model_name: str = ''
        if len(model_data_info[2]) > 2:
            model_proper_name = model_data_info[2][-2]
            model_action_name = model_data_info[2][-1]
            model_name = f'{model_proper_name}_{model_action_name}'.replace('\'', '')
        else:
            model_name = model_data_info[2][-1].replace('\'', '')

        model_folder_nesting = str(model_data_info[2]).replace('[', '').replace(']', '').replace('\'', '').replace('"', '')
        final_model_dict: dict = {}

        folder_path = model_data.get(f'ModelFolder')
        file = model_data.get(f'ModelFile')
        passive_anim_path = model_data.get(f'PassiveFolder')
        passive_anim_files = str(model_data.get(f'PassiveFiles')).replace('"', '').replace('[', '').replace(']', '').split(', ')
        attack_anim_path = model_data.get(f'AttackFolder')
        attack_anim_files = str(model_data.get(f'AttackFiles')).replace('"', '').replace('[', '').replace(']', '').split(', ')
        texture_file = model_data.get(f'Textures')

        # I NEED TO DESENFUCK THE FUCKENING GOING ON
        sc_path: str = self.sc_folder
        if model_parent != 'Characters':
            if model_parent != 'CutScenes':
                sc_path = f'{self.sc_folder}\\SECT\\DRGN0.BIN\\'
            else:
                sc_path = f'{self.sc_folder}\\SECT\\DRGN0.BIN'
        else:
            sc_path = f'{sc_path}/'
                
        if folder_path == 'None': # Only needed for Animations which are in the root of DRGN0.BIN for example CutScenes animations that are considered as "Passive"
            folder_path = ''
        
        # Model File Path [STR]
        model_file_path = f'{sc_path}{folder_path}\\{file}'.replace('//', '/')

        # Model Passive Animations Path Setting
        current_passive_anim_path: str = ''
        if (model_parent == 'CutScenes') and (passive_anim_files != ['None']): # This handles cases in which the passive animation path is equal to the root of DRGN0.BIN, example: CutScenes
            current_passive_anim_path = f'{sc_path}'
        elif (passive_anim_path == 'None') and (passive_anim_files == ['None']):
            current_passive_anim_path = 'None'
        else: # This are the rest of passive animation paths
            current_passive_anim_path = f'{sc_path}{passive_anim_path}'
        
        # Model Attack Animations Path Setting
        current_attack_anim_path: str = ''
        if (model_parent == 'Characters') and (attack_anim_files != ['None']):
            current_attack_anim_path = f'{sc_path}/SECT/DRGN0.BIN/{attack_anim_path}'.replace('//', '/')
        elif (attack_anim_path == 'None') and (attack_anim_files == ['None']):
            current_attack_anim_path = 'None'
        else:
            current_attack_anim_path = f'{sc_path}{attack_anim_path}'
        
        # Texture Path Settings
        texture_path: str = ''
        if model_parent == 'CutScenes':
            texture_path = f'{self.sc_folder}\\SECT\\DRGN0.BIN\\'
        elif (model_parent == 'Bosses') or (model_parent == 'Enemies') or (model_parent == 'Tutorial'):
            texture_path = self.sc_folder
        else:
            texture_path = sc_path
        
        texture_file_path = f'{texture_path}/{texture_file}'.replace('//', '/')
        if texture_file == 'None':
            texture_file_path = ''
        
        # Here ends the FUCKENING
        file_model_specs = {'Format': 'TMD_CContainer', 'Path': model_file_path}
        passive_animation_specs = {'Format': 'SAF_CContainer', 'Path': current_passive_anim_path, 'Files': passive_anim_files}
        attack_animation_specs = {'Format': 'SAF_CContainer', 'Path': current_attack_anim_path, 'Files': attack_anim_files}
        texture_model_specs = {'Format': 'TIM', 'Path': texture_file_path}
        debug_files_dict = {'TMDReport': self.tmd_report, 'PrimPerObj': self.prim_report, 'PrimData': self.generate_primdata} # This is only pass one, even in batch

        final_model_dict = {'Name': model_name, 'Model': file_model_specs, 
                            'PassiveAnims': passive_animation_specs, 'AttackAnims': attack_animation_specs, 
                            'FolderNesting': model_folder_nesting, 'Texture': texture_model_specs, 
                            'Debug': debug_files_dict}

        return final_model_dict

    def convert_to_gltf(self, model_final_dict=dict) -> str:
        file_name = model_final_dict.get('Name')
        file_model_specs = model_final_dict.get('Model')
        passive_animation_specs = model_final_dict.get('PassiveAnims')
        attack_animation_specs = model_final_dict.get('AttackAnims')
        folder_nesting = model_final_dict.get('FolderNesting')
        texture_specs = model_final_dict.get('Texture')
        debug_options = model_final_dict.get('Debug')

        # Start Conversion
        # Binary Conversion to glTF Format
        file_model_bin = binary_to_dict.BinaryToDict(bin_file_to_dict=file_model_specs)
        processed_data_model = asunder_binary_data.Asset(bin_to_split=file_model_bin.bin_data_dict)

        # Get Animation Flags to know if Conversion needed
        animations_converted: dict | None = {}
        if (self.conv_passive_anims == True) and (passive_animation_specs.get('Path') != 'None'):
            passive_anims_bin = binary_to_dict.BinariesToDict(binaries_to_dict=passive_animation_specs)
            for this_anim in passive_anims_bin.binaries_data_dict:
                get_anim_data = passive_anims_bin.binaries_data_dict.get(f'{this_anim}')
                processed_data_anim = asunder_binary_data.Asset(bin_to_split=get_anim_data)
                animations_converted.update({f'Passive_{this_anim}': processed_data_anim.animation_converted_data})
        if (self.conv_attack_anims == True) and (attack_animation_specs.get('Path') != 'None'):
            attack_anims_bin = binary_to_dict.BinariesToDict(binaries_to_dict=attack_animation_specs)
            for this_attack_anim in attack_anims_bin.binaries_data_dict:
                get_attack_anim_data = attack_anims_bin.binaries_data_dict.get(f'{this_attack_anim}')
                processed_attack_data_anim = asunder_binary_data.Asset(bin_to_split=get_attack_anim_data)
                animations_converted.update({f'Attack_{this_attack_anim}': processed_attack_data_anim.animation_converted_data})
        if len(animations_converted) == 0:
            animations_converted = None

        # Process the TMD Model Data into glTF Format
        process_to_gltf = gltf_compiler.NewGltfModel(model_data=processed_data_model.model_converted_data, animation_data=animations_converted, file_name=file_name)
        
        # Writting Folders and Files
        new_folder = folder_handler.Folders(deploy_folder_path=self.deploy_folder, file_nesting=folder_nesting, file_name=file_name)
        convert_gltf = gltf_converter.gltfFile(gltf_to_convert=process_to_gltf.gltf_format, gltf_file_name=file_name, gltf_deploy_path=new_folder.new_file_name)
        debug_data = debug_files_writer.DebugData(converted_file_path=new_folder.new_file_name, debug_files_flag=debug_options, file_data=processed_data_model.model_converted_data)
        
        # Since Textures are the most expensive processing thing will be at the end of the processing
        if (self.convert_textures == True) and (texture_specs.get('Path') != ''):
            file_texture_bin = binary_to_dict.BinaryToDict(bin_file_to_dict=texture_specs)
            processed_data_texture = asunder_binary_data.Asset(bin_to_split=file_texture_bin.bin_data_dict)
            texture_file_nesting = f'{folder_nesting}, Textures'
            new_folder_textures = folder_handler.TextureFolder(deploy_folder_path=self.deploy_folder, file_nesting=texture_file_nesting, file_name=file_name)
            png_file_write = png_writer.PngFile(texture_data=processed_data_texture.texture_converted_data, file_deploy_path=new_folder_textures.new_file_name, texture_type='TIM')
        
        return file_name

class SubMapConversionInterface():
    def __init__(self, list_convert=list, assets_submap_database=dict, conv_passive_anims=bool, conv_attack_anims=bool, conv_text=bool, 
                 sc_folder=str, tmd_report=bool, prim_report=bool, generate_primdata=bool, deploy_folder=str) -> None:
        self.selected_conversion_list = list_convert
        self.assets_submap_database = assets_submap_database
        self.conv_passive_anims = conv_passive_anims
        self.conv_attack_anims = conv_attack_anims
        self.convert_textures = conv_text
        self.sc_folder = sc_folder
        self.tmd_report = tmd_report
        self.prim_report = prim_report
        self.generate_primdata = generate_primdata
        self.deploy_folder = deploy_folder
        self.write_gltf()

    def write_gltf(self) -> None:
        """
        Clean the Selected Items List to fit the following logic:
        Chapter -> SubMap -> Cut -> Type of Object -> Object

        Example of DRGN2x Nesting:
        DRGN21 -> Bale -> Barn -> Objects -> Dart
        this also impact to the nesting in the Dictionary which contains the Data,\n
        also impact to the nesting of converted files.
        """
        model_data_and_info = self.get_current_model_data(selection=self.selected_conversion_list)
        gather_model_data = self.get_data_to_convert(model_data_info=model_data_and_info)
        convert_to_gltf = self.convert_to_gltf(model_final_dict=gather_model_data)

    def get_current_model_data(self, selection=list) -> tuple[dict, str, list]:
        """
        Get current Model Data:\n
        Will grab the Data needed, based on the self.selected_conversion_list [Selections made by user].
        """
        model_data_dict: dict = {}
        parent_name: str = ''
        nesting_folders: list = []
        # Adjusting Names for conversion, since i search through the Dicts
        drgn2x_name = selection[0].replace(' ', '_')
        submap_name = selection[1].replace(' ', '_')
        cut_name = selection[2].replace(' ', '_')
        type_object_name = selection[3]
        object_name = selection[4]
        nesting_folders = [drgn2x_name, submap_name, cut_name, type_object_name, object_name]

        this_drgn2x = self.assets_submap_database.get(f'{drgn2x_name}')
        this_submap = this_drgn2x.get(f'{submap_name}')
        this_cut = this_submap.get(f'{cut_name}')
        this_object_type = this_cut.get(f'{type_object_name}')
        model_data_dict = this_object_type.get(f'{object_name}')

        return model_data_dict, parent_name, nesting_folders
    
    def get_data_to_convert(self, model_data_info=tuple) -> dict:
        """
        Get Data to Convert:\n
        Will take the data from the current Model selected dictionary\n
        and extract all the requeried data from it.
        """
        
        model_data = model_data_info[0]
        model_parent = model_data_info[1]
        model_nesting = model_data_info[2]

        # Model Name
        model_name = model_nesting[4]
        
        get_model_and_anim_folder = model_data.get('ModelAnimFolder').strip()
        get_model_file = model_data.get('ModelFile').strip()
        get_anim_files = model_data.get('AnimationFiles').strip()
        get_textures = model_data.get('Textures').strip()
        
        # Setting Model path
        model_full_path = f'{self.sc_folder}\\SECT\\{get_model_and_anim_folder}\\{get_model_file}'
        
        # Setting Animations path
        modelanims_half_path: str = ''
        model_anims_files_to_list: list = []
        if (get_anim_files == 'None') or (get_anim_files == '[None]'):
            modelanims_half_path = f'None'
            get_anim_files = f'None'
        else:
            model_anims_files_to_list = get_anim_files.replace('[', '').replace(']', '').strip().split(', ')
            modelanims_half_path = f'{self.sc_folder}\\SECT\\{get_model_and_anim_folder}'
        
        # Setting Texture path/s, if Object there is a single path, if Environment will have several paths
        texture_half_path = f'{self.sc_folder}\\SECT\\'
        textures_file_path: list = []
        if model_nesting[3] == 'Environment':
            split_folder_path = get_textures.split('[')
            folder_path = split_folder_path[0]
            texture_files = split_folder_path[1].replace('[', '').replace(']', '').strip().split(', ')
            texture_half_path = f'{self.sc_folder}\\SECT\\{folder_path}'
            for this_texture in texture_files:
                textures_file_path.append(this_texture)
        else:
            single_texture_file = f'{get_textures}'
            textures_file_path.append(single_texture_file)

        tmd_type: str = ''
        if (model_nesting[3] == 'Environment') or (model_name == '16 Treasures Containers'):
            tmd_type = 'TMD_Standard'
        else:
            tmd_type = 'TMD_CContainer'
        
        file_model_specs = {'Format': tmd_type, 'Path': model_full_path}
        passive_animation_specs = {'Format': 'SAF_CContainer', 'Path': modelanims_half_path, 'Files': model_anims_files_to_list}
        attack_animation_specs = {'Format': 'SAF_CContainer', 'Path': 'None', 'Files': 'None'}
        texture_model_specs = {'Format': 'TIM', 'Path': texture_half_path, 'Files': textures_file_path}
        debug_files_dict = {'TMDReport': self.tmd_report, 'PrimPerObj': self.prim_report, 'PrimData': self.generate_primdata} # This is only pass one, even in batch

        final_model_dict = {'Name': model_name, 'Model': file_model_specs, 
                            'PassiveAnims': passive_animation_specs, 'AttackAnims': attack_animation_specs, 
                            'FolderNesting': model_nesting, 'Texture': texture_model_specs, 
                            'Debug': debug_files_dict}

        return final_model_dict

    def convert_to_gltf(self, model_final_dict=dict) -> str:
        file_name = model_final_dict.get('Name')
        file_model_specs = model_final_dict.get('Model')
        passive_animation_specs = model_final_dict.get('PassiveAnims')
        folder_nesting = str(model_final_dict.get('FolderNesting')).replace('[', '').replace(']', '').replace('\'', '').strip()
        texture_specs = model_final_dict.get('Texture')
        debug_options = model_final_dict.get('Debug')

        # Start Conversion
        # Binary Conversion to glTF Format
        file_model_bin = binary_to_dict.BinaryToDict(bin_file_to_dict=file_model_specs)
        processed_data_model = asunder_binary_data.Asset(bin_to_split=file_model_bin.bin_data_dict)

        # Get Animation Flags to know if Conversion needed
        animations_converted: dict | None = {}
        if (self.conv_passive_anims == True) and (passive_animation_specs.get('Path') != 'None'):
            passive_anims_bin = binary_to_dict.BinariesToDict(binaries_to_dict=passive_animation_specs)
            for this_anim in passive_anims_bin.binaries_data_dict:
                get_anim_data = passive_anims_bin.binaries_data_dict.get(f'{this_anim}')
                processed_data_anim = asunder_binary_data.Asset(bin_to_split=get_anim_data)
                animations_converted.update({f'Passive_{this_anim}': processed_data_anim.animation_converted_data})

        if len(animations_converted) == 0:
            animations_converted = None

        # Process the TMD Model Data into glTF Format
        process_to_gltf = gltf_compiler.NewGltfModel(model_data=processed_data_model.model_converted_data, animation_data=animations_converted, file_name=file_name)
        
        # Writting Folders and Files
        new_folder = folder_handler.Folders(deploy_folder_path=self.deploy_folder, file_nesting=folder_nesting, file_name=file_name)
        convert_gltf = gltf_converter.gltfFile(gltf_to_convert=process_to_gltf.gltf_format, gltf_file_name=file_name, gltf_deploy_path=new_folder.new_file_name)
        debug_data = debug_files_writer.DebugData(converted_file_path=new_folder.new_file_name, debug_files_flag=debug_options, file_data=processed_data_model.model_converted_data)
        
        # Since Textures are the most expensive processing thing will be at the end of the processing
        if (self.convert_textures == True) and (texture_specs.get('Path') != ''):
            file_texture_bin = binary_to_dict.BinariesToDict(binaries_to_dict=texture_specs)
            for this_binary_texture in file_texture_bin.binaries_data_dict:
                get_this_bin_texture = file_texture_bin.binaries_data_dict.get(f'{this_binary_texture}')
                current_processed_texture = asunder_binary_data.Asset(bin_to_split=get_this_bin_texture)
                texture_file_nesting = f'{folder_nesting}, Textures'
                texture_file_name:str = ''
                if '/textures/' in this_binary_texture:
                    find_end = this_binary_texture.rfind(f'/textures/')
                    texture_file_name = f'{file_name}_{this_binary_texture[find_end + 10:]}'
                elif 'DRGN21.BIN/2' == this_binary_texture:
                    texture_file_name = f'{file_name.replace(' ', '_')}'
                else:
                    texture_file_name = f'{file_name}_{this_binary_texture}'
                new_folder_textures = folder_handler.TextureFolder(deploy_folder_path=self.deploy_folder, file_nesting=texture_file_nesting, file_name=texture_file_name)
                png_file_write = png_writer.PngFile(texture_data=current_processed_texture.texture_converted_data, file_deploy_path=new_folder_textures.new_file_name, texture_type='TIM')

        return file_name