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
    
class TextureOnlyConversionInterface():
    def __init__(self, list_convert=list, texture_assets_database=dict, sc_folder=str, deploy_folder=str) -> None:
        self.selected_conversion_list = list_convert
        self.texture_assets_database = texture_assets_database
        self.sc_folder = sc_folder
        self.deploy_folder = deploy_folder
        self.write_texture()

    def write_texture(self) -> None:
        """
        Clean the Selected Items List to fit the following logic:
        Parent->Child (Model Object to Convert)
        SuperParent->Parent->Child (Model Object to Convert) ==> This is used in CutScenes and Characters list due to the nesting
        """
        texture_data = self.get_textures_data_and_info(selection=self.selected_conversion_list)
        convert_to_png = self.convert_to_png(texture_final_dict=texture_data)

    def get_textures_data_and_info(self, selection=list) -> tuple[dict, str, list]:
        """
        Get current Texture Data:\n
        Will grab the Data needed, based on the self.selected_conversion_list [Selections made by user]\n
        Example of Nesting:
        Menu Textures -> Ending Credits
        this also impact to the nesting in the Dictionary which contains the Data.
        """
        texture_data_dict: dict = {}
        nesting_folders: list = []

        parent_name = selection[0].replace(' ', '_')
        texture_group_name = selection[1]

        """
        Asset Storage: [Type of Storages] Single-File or FOLDER.
        If Single-File (just work with a single TIM File)
        If FOLDER (Is a folder with a lot of Texture Files)
        """
        get_texture_parent = self.texture_assets_database.get(f'{parent_name}')
        get_texture_pack = get_texture_parent.get(f'{texture_group_name}')
        get_textures_folder = get_texture_pack.get('TextureFolder')
        get_asset_storage = get_texture_pack.get('AssetStorage')
        get_textures_file = get_texture_pack.get('Textures')

        texture_type: str = ''
        if parent_name == 'Skyboxes':
            texture_type = 'MCQ'
        else:
            texture_type = 'TIM'
        
        nesting_folders = f'{parent_name}, {texture_group_name}'

        texture_model_specs: dict = {}
        if get_asset_storage == 'Single-File':
            clean_file_name = get_textures_file.replace('[', '').replace(']', '').replace('\'', '').strip()
            file_list = [clean_file_name]
            if get_textures_folder == clean_file_name: # This are the files placed in Root DRGN0.BIN
                textures_path = f'{self.sc_folder}\\SECT\\DRGN0.BIN'
                texture_model_specs = {'Format': texture_type, 'Path': textures_path, 'Files': file_list}
            else: # This seems to be only the Skyboxes MCQ lol
                textures_path = f'{self.sc_folder}\\SECT\\DRGN0.BIN\\{get_textures_folder}'
                texture_model_specs = {'Format': texture_type, 'Path': textures_path, 'Files': file_list}      
        else:
            texture_files = get_textures_file.replace('[', '').replace(']', '').replace('\'', '').strip().split(', ')
            textures_path = f'{self.sc_folder}\\SECT\\DRGN0.BIN\\{get_textures_folder}'
            texture_model_specs = {'Format': texture_type, 'Path': textures_path, 'Files': texture_files}
        
        texture_data_dict = {'Name': texture_group_name, 'FolderNesting': nesting_folders, 'Texture': texture_model_specs}
        
        return texture_data_dict

    def convert_to_png(self, texture_final_dict=dict) -> str:
        file_name = texture_final_dict.get('Name')
        folder_nesting = texture_final_dict.get('FolderNesting')
        texture_specs = texture_final_dict.get('Texture')

        # Start Conversion
        # Binary to PNG file
        texture_list_to_convert = texture_specs.get('Files')
        texture_path = texture_specs.get('Path')
        texture_format = texture_specs.get('Format')
        for current_texture in texture_list_to_convert:
            current_path = f'{texture_path}\\{current_texture}'
            texture_dict = {f'Format': texture_format, 'Path': current_path}
            if (current_texture == '6666') or (current_texture == '6665'):
                get_embedded_tims = self.handle_embedded_tims(file_path=current_path, file_name=current_texture)
                for this_embedded_tim in get_embedded_tims:
                    this_embedded_tim_data = get_embedded_tims.get(f'{this_embedded_tim}')
                    processed_data_texture = asunder_binary_data.Asset(bin_to_split=this_embedded_tim_data)
                    new_nesting = f'{folder_nesting}, {current_texture}'
                    new_folder_textures = folder_handler.TextureFolder(deploy_folder_path=self.deploy_folder, file_nesting=new_nesting, file_name=file_name)
                    png_file_write = png_writer.PngFile(texture_data=processed_data_texture.texture_converted_data, file_deploy_path=new_folder_textures.new_file_name, texture_type=texture_format)
            else:
                file_texture_bin = binary_to_dict.BinaryToDict(bin_file_to_dict=texture_dict)
                processed_data_texture = asunder_binary_data.Asset(bin_to_split=file_texture_bin.bin_data_dict)
                new_nesting = f'{folder_nesting}, {current_texture}'
                new_folder_textures = folder_handler.TextureFolder(deploy_folder_path=self.deploy_folder, file_nesting=new_nesting, file_name=file_name)
                png_file_write = png_writer.PngFile(texture_data=processed_data_texture.texture_converted_data, file_deploy_path=new_folder_textures.new_file_name, texture_type=texture_format)
        
        return file_name
    
    def handle_embedded_tims(self, file_path=str, file_name=str) -> dict:
        """
        Handle Embedded TIMs:\n
        This is a special handling for very few Textures which for some reason\n
        had a single file and inside are full of TIM files.\n
        At the moment files 6665 and 6666, inside DRGN0.bin
        """
        tims_embedded: dict = {}

        if file_name == '6666':
            with open(file_path, 'rb') as embedded_tims:
                read_all_tims = embedded_tims.read()
                this_tim = read_all_tims[57116:]
                this_data = {'Format': 'TIM', 'Data': [this_tim]}
                tims_embedded.update({f'EmbeddedTim': this_data})
                embedded_tims.close()
        
        elif file_name == '6665':
            with open(file_path, 'rb') as embedded_tims:
                read_all_tims = embedded_tims.read()                
                tim_bin_0 = read_all_tims[0 : 25088]
                this_data_0 = {'Format': 'TIM', 'Data': [tim_bin_0]}
                tims_embedded.update({f'EmbeddedTim0': this_data_0})

                tim_bin_1 = read_all_tims[25088 : 33760]
                this_data_1 = {'Format': 'TIM', 'Data': [tim_bin_1]}
                tims_embedded.update({f'EmbeddedTim1': this_data_1})

                tim_bin_2 = read_all_tims[33760 : 66656]
                this_data_2 = {'Format': 'TIM', 'Data': [tim_bin_2]}
                tims_embedded.update({f'EmbeddedTim2': this_data_2})
                embedded_tims.close()
        
        return tims_embedded

class WorldMapConversionInterface():
    def __init__(self, list_convert=list, assets_worldmap_database=dict, conv_anims=bool, conv_text=bool, 
                 sc_folder=str, tmd_report=bool, prim_report=bool, generate_primdata=bool, deploy_folder=str) -> None:
        self.selected_conversion_list = list_convert
        self.assets_worldmap_database = assets_worldmap_database
        self.conv_anims = conv_anims
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

        parent_name = selection[0].replace(' ', '_')
        model_name = selection[1]
        models_complete_dict = self.assets_worldmap_database.get(f'{parent_name}')
        model_data_dict = models_complete_dict.get(f'{model_name}')
        nesting_folders.append(parent_name)
        nesting_folders.append(model_name)

        return model_data_dict, nesting_folders
    
    def get_data_to_convert(self, model_data_info=tuple) -> dict:
        """
        Get Data to Convert:\n
        Will take the data from the current Model selected dictionary\n
        and extract all the requeried data from it.
        """
        
        model_data = model_data_info[0]
        nesting_folder = model_data_info[1]
        model_name = nesting_folder[1]

        model_folder_nesting = str(nesting_folder).replace('[', '').replace(']', '').replace('\'', '').replace('"', '')
        final_model_dict: dict = {}

        folder_path = model_data.get(f'ModelFolder')
        model_file = model_data.get(f'ModelFile')
        anim_path = model_data.get(f'PassiveFolder')
        animation_files = str(model_data.get(f'PassiveFiles')).replace('"', '').replace('[', '').replace(']', '').split(', ')
        texture_file = model_data.get(f'Textures')
        
        # SC Folder Path to Model File
        model_full_path: str = ''
        tmd_type: str = ''
        if folder_path == 'DRGN0.BIN':
            model_full_path = f'{self.sc_folder}\\SECT\\DRGN0.BIN\\{model_file}'
            tmd_type = 'TMD_Standard'
        else:
            model_full_path = f'{self.sc_folder}\\SECT\\DRGN0.BIN\\{folder_path}\\{model_file}'
            tmd_type = 'TMD_CContainer'
        
        # SC Folder path to Model Anims
        animation_full_path: str = ''
        if anim_path != 'None':
            animation_full_path = f'{self.sc_folder}\\SECT\\DRGN0.BIN\\{anim_path}'
        else:
            animation_full_path = 'None'
            animation_files = []
        
        # Texture Path Settings
        texture_files: list = []
        textures_full_path: list = []
        split_folder_from_file = texture_file.split('[')
        texture_folder = split_folder_from_file[0]
        texture_files = split_folder_from_file[1].replace('[', '').replace(']', '').strip().split(',')

        for this_texture in texture_files:
            this_texture_full_path = f'{self.sc_folder}\\SECT\\DRGN0.BIN\\{texture_folder}\\{this_texture}'
            textures_full_path.append(this_texture_full_path)
        
        file_model_specs = {'Format': tmd_type, 'Path': model_full_path}
        animation_specs = {'Format': 'SAF_CContainer', 'Path': animation_full_path, 'Files': animation_files}
        texture_model_specs = {'Format': 'TIM', 'Path': textures_full_path}
        debug_files_dict = {'TMDReport': self.tmd_report, 'PrimPerObj': self.prim_report, 'PrimData': self.generate_primdata}
        
        final_model_dict = {'Name': model_name, 'Model': file_model_specs, 
                            'Anims': animation_specs, 
                            'FolderNesting': model_folder_nesting, 'Texture': texture_model_specs, 
                            'Debug': debug_files_dict}

        return final_model_dict

    def convert_to_gltf(self, model_final_dict=dict) -> str:
        file_name = model_final_dict.get('Name')
        file_model_specs = model_final_dict.get('Model')
        animation_specs = model_final_dict.get('Anims')
        folder_nesting = model_final_dict.get('FolderNesting')
        texture_specs = model_final_dict.get('Texture')
        debug_options = model_final_dict.get('Debug')

        # Start Conversion
        # Binary Conversion to glTF Format
        file_model_bin = binary_to_dict.BinaryToDict(bin_file_to_dict=file_model_specs)
        processed_data_model = asunder_binary_data.Asset(bin_to_split=file_model_bin.bin_data_dict)

        # Get Animation Flags to know if Conversion needed
        animations_converted: dict | None = {}
        if (self.conv_anims == True) and (animation_specs.get('Path') != 'None'):
            passive_anims_bin = binary_to_dict.BinariesToDict(binaries_to_dict=animation_specs)
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
            format = texture_specs.get(f'Format')
            texture_files = texture_specs.get(f'Path')
            for this_texture_path in texture_files:
                texture_name_end = this_texture_path.rfind('\\')
                texture_name = this_texture_path[texture_name_end + 1:]
                single_texture_spec = {'Format': format, 'Path': this_texture_path}
                file_texture_bin = binary_to_dict.BinaryToDict(bin_file_to_dict=single_texture_spec)
                processed_data_texture = asunder_binary_data.Asset(bin_to_split=file_texture_bin.bin_data_dict)
                texture_file_nesting = f'{folder_nesting}, Textures, {texture_name}'
                new_folder_textures = folder_handler.TextureFolder(deploy_folder_path=self.deploy_folder, file_nesting=texture_file_nesting, file_name=file_name)
                png_file_write = png_writer.PngFile(texture_data=processed_data_texture.texture_converted_data, file_deploy_path=new_folder_textures.new_file_name, texture_type=format)
        
        return file_name