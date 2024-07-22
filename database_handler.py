"""

Database Handler:
Handle Database file, pre-processing before GUI Start
There are Four Database Types:
Battle, DEFF, Misc, SubMap, Textures Only, World Map.

Copyright (C) 2024 DooMMetaL

"""
import os
from collections import Counter
import csv
from PyQt6.QtWidgets import QMessageBox

class DatabaseHandler:
    def __init__(self, database_path=str) -> None:
        """Database Handler will work on all the Database Files\n
        will take all them which are under /Databases/ Folder\n
        and create necessary dicts for easy navigation in the treeview in the tool
        """
        self.self = DatabaseHandler
        self.database_path = database_path
        self.full_database: dict = {'Battle': {}, 'DEFF': {}, 'Misc': {}, 'SubMaps': {}, 'Textures Only': {}, 'World Map': {}}
        self.process_csv_file()
    
    def process_csv_file(self) -> None:
        """
        Process CSV Files format for TLoD Assets Manager
        """
        check_databases_path = os.walk(self.database_path)

        main_folder_databases: list[str] = []
        deff_folder_databases: list[str] = []
        misc_folder_databases: list[str] = []
        submap_folder_databases: list[str] = []
        texture_only_folder_databases: list[str] = []
        world_map_folder_databases: list[str] = []
        
        for folder, subfolder, database_files in check_databases_path:
            for database_file in database_files:
                each_database_full_path = f'{folder}\\{database_file}'
                if 'Battle' in each_database_full_path:
                    main_folder_databases.append(each_database_full_path)
                elif 'DEFF' in each_database_full_path:
                    deff_folder_databases.append(each_database_full_path)
                elif 'Misc' in each_database_full_path:
                    misc_folder_databases.append(each_database_full_path)
                elif 'SubMaps' in each_database_full_path:
                    submap_folder_databases.append(each_database_full_path)
                elif 'Textures_Only' in each_database_full_path:
                    texture_only_folder_databases.append(each_database_full_path)
                elif 'World_Map' in each_database_full_path:
                    world_map_folder_databases.append(each_database_full_path)                
                else:
                    error_database_type = QMessageBox.critical(None, 'CRITICAL ERROR!!', f'FATAL!!:\nNot recognized Database Type: {each_database_full_path}, \nPlease, report this error', QMessageBox.StandardButton.Ok)
                    raise RuntimeError()
        
        # FINAL STRUCTURE -> {'Battle_Stages': {}, 'Bosses': {}, 'Characters': {}, 'CutScenes': {}, 'Enemies': {}, 'Tutorial': {}}
        battle_dict = self.process_file_from_folder(file_path_list=main_folder_databases, file_path_type='Battle')
        # FINAL STRUCTURE -> {'Logo': {}}
        misc_dict = self.process_file_from_folder(file_path_list=misc_folder_databases, file_path_type='Misc')
        # FINAL STRUCTURE -> {'South Serdio': {}, 'North Serdio': {}, 'Tiberoa': {}, 'Illisa Bay': {}, 'Mille Seseau': {}, 'Gloriano': {}, 'Death Frontier Desert': {}, 'World Map Complete': {}, 'Mini Dart': {}, 'Queen Fury': {}, 'Coolon': {}, 'Teleportation Glow': {}}
        # NOTE: The texture nesting from World Maps will be handled in the Converter directly
        world_map_dict = self.process_file_from_folder(file_path_list=world_map_folder_databases, file_path_type='WorldMap')
        # FINAL STRUCTURE -> {'DRGN21': {}, 'DRGN22': {}, 'DRGN23': {}, 'DRGN24': {}}
        submaps_dict = self.process_database_from_submap(file_path_list=submap_folder_databases)
        # FINAL STRUCTURE -> {'Menu_Textures': {}, 'Skyboxes': {}, 'THE_END': {}, 'WorldMap_Thumbnails': {}, 'WorldMap_GUI': {}}
        texture_only_dict = self.process_database_from_textonly(file_path_list=texture_only_folder_databases)
        # FINAL STRUCTURE -> {'Bosses': {}, 'CutScenes': {}, 'Dragoon': {}, 'Enemies': {}, 'General': {}, 'Magic and Special Attacks': {}}
        deff_dict = self.process_file_from_folder_deff(file_path_list=deff_folder_databases)

        self.full_database = {'Battle': battle_dict, 'DEFF': deff_dict, 'Misc': misc_dict, 'SubMaps': submaps_dict, 'Textures Only': texture_only_dict, 'World Map': world_map_dict}
    
    def process_file_from_folder(self, file_path_list=list[str], file_path_type=str) -> dict:
        """
        Process a Database File from a folder, using a list of files obtained
        :params: file_path_list -> List of Database Files
        process_file_from_folder() -> dict: a processed csv file into a Python Dictionary
        """
        if file_path_type == 'Battle':
            database_to_process: dict = {'Characters': {}, 'CutScenes': {}}
            database_file_path: str = ''
        else:
            database_to_process: dict = {}
            database_file_path: str = ''

        cleaned_file_path: list = []

        for file_path in file_path_list:
            clear_file_path = file_path.find('\\Databases\\')
            new_path = file_path[(clear_file_path + 1):]
            cleaned_file_path.append(new_path)

        # First gather all the file list and split them based in the nesting inside the folders
        simple_nest_path: list[tuple] = []
        double_nest_path: list[tuple] = []
        for database_file_path in cleaned_file_path:
            split_file_path = database_file_path.split('\\')
            get_parent_name: str = ''
            get_child_name: str = ''

            # if length_this_path equal to 3 == Simple Nesting ; if length_this_path equal to 4 == Double Nesting
            length_this_path = len(split_file_path)
            if length_this_path == 3:
                get_parent_name = split_file_path[2].replace('.csv', '')
                this_path_data_simple = get_parent_name, database_file_path
                simple_nest_path.append(this_path_data_simple)

            elif length_this_path == 4: # This are Characters and CutScenes Databases, which also had a sligthy different format from the others CSV
                get_parent_name = split_file_path[2]
                get_child_name = split_file_path[3].replace('.csv', '').replace('_', ' ')
                this_path_data_double = get_parent_name, get_child_name, database_file_path
                double_nest_path.append(this_path_data_double)
            else:
                error_database_len = QMessageBox.critical(None, 'CRITICAL ERROR!!', f'FATAL!!:\nUnexpected lenght for Database File Path,\n{database_file_path} \nPlease, report this error', QMessageBox.StandardButton.Ok)
                raise RuntimeError()
        
        # Then process each database file to be added to the database_to_process
        for simple_path_tuple in simple_nest_path:
            simple_parent_name: str = simple_path_tuple[0]
            simple_path: str = simple_path_tuple[1]
            this_inner_dict: dict = {f'{simple_parent_name}': {}}

            with open(simple_path, 'r') as csv_file:
                csv_read = csv.reader(csv_file)
                for csv_data in csv_read:
                    object_name = csv_data[0]
                    object_dict = self.csv_data_to_dict(csv_row=csv_data)
                    data_dict: dict = {f'{object_name}': object_dict}
                    this_inner_dict[f'{simple_parent_name}'].update(data_dict)
                csv_file.close()
            database_to_process.update(this_inner_dict)
        
        for nested_path_tuple in double_nest_path:
            nested_parent_name: str = nested_path_tuple[0] # This is the Folder Name
            nested_subparent_name: str = nested_path_tuple[1] # This is the File Name
            nested_path: str = nested_path_tuple[2] # This is the path to the file

            if nested_parent_name == 'Characters':
                this_inner_dict_nested: dict = {f'{nested_subparent_name}': {}}
                """example of how this Dict how to looks like
                {'Battle': {'Characters': {'Dart_Normal': {'idle': ModelFolder': 'path', 'ModelFile': 'n', 'PassiveFolder': 'path', 'PassiveFiles': 'files', 'AttackFolder': 'path', 'AttackFiles': 'files'}}}}"""
                csv_nested_read: list[str] = []
                with open(nested_path, 'r') as csv_nested_file:
                    # First i read the Custom CSV with a '!' as delimiter for Texture and main data (Since i don't like the idea of repeating the texture data over and over)
                    read_custom_csv = csv_nested_file.read()
                    # Split the total read in two chunks: Texture Data (to be used just one per dict) and the rest of data
                    csv_nested_read = self.handle_special_csv(custom_csv=read_custom_csv)
                    csv_nested_file.close()
                
                # Set a single Texture for all the Models/Animations
                texture_action_and_path = csv_nested_read[0].split(',')
                texture_path = texture_action_and_path[1]
                this_inner_dict_nested[f'{nested_subparent_name}'].update({'Texture': texture_path})
                
                # This is the Character Models/Animations data
                rest_of_csv = csv_nested_read[1].strip().split('\n')
                for csv_single_row_data in rest_of_csv:
                    manipulate_row = csv_single_row_data.replace(', ', '-')
                    split_this_row = manipulate_row.split(',')
                    action_name = split_this_row[0]
                    model_path = split_this_row[1]
                    model_file = split_this_row[2]
                    passive_path = split_this_row[3]
                    passive_files = split_this_row[4].replace('-', ', ')
                    attack_path = split_this_row[5]
                    attack_files = split_this_row[6].replace('-', ', ')

                    object_dict_inner = {f'{action_name}':  {'ModelFolder': model_path, 'ModelFile': model_file, 
                                         'PassiveFolder': passive_path, 'PassiveFiles': passive_files, 
                                            'AttackFolder': attack_path, 'AttackFiles': attack_files}}
                    this_inner_dict_nested[f'{nested_subparent_name}'].update(object_dict_inner)
                database_to_process['Characters'].update(this_inner_dict_nested)

            elif nested_parent_name == 'CutScenes':
                this_inner_dict_nested_2: dict = {f'{nested_subparent_name}': {}}
                # This is the Character Models/Animations data
                with open(nested_path, 'r') as csv_file_nested:
                    csv_read_nested = csv.reader(csv_file_nested)
                    for csv_data_nested in csv_read_nested:
                        object_name_nested = csv_data_nested[0]
                        object_dict_nested = self.csv_data_to_dict(csv_row=csv_data_nested)
                        data_dict_nested: dict = {f'{object_name_nested}': object_dict_nested}
                        this_inner_dict_nested_2[f'{nested_subparent_name}'].update(data_dict_nested)
                database_to_process['CutScenes'].update(this_inner_dict_nested_2)

        return database_to_process

    def csv_data_to_dict(self, csv_row=list) -> dict:
        """
        CSV data to dict\n
        :params: csv_row -> a single ROW from the csv data which is currently iterated\n
        csv_data_to_dict() -> Dictionary with the data already compiled\n
        as a Single Object
        """
        object_dict: dict = {}
        model_folder = csv_row[1]
        model_file = csv_row[2]
        passive_folder = csv_row[3]
        passive_files = csv_row[4]
        attack_folder = csv_row[5]
        attack_files = csv_row[6]
        texture_files = csv_row[7]

        object_dict = {'ModelFolder': model_folder, 'ModelFile': model_file, 
                        'PassiveFolder': passive_folder, 'PassiveFiles': passive_files, 
                        'AttackFolder': attack_folder, 'AttackFiles': attack_files, 
                        'Textures': texture_files}
        
        return object_dict

    def process_database_from_submap(self, file_path_list=list[str]) -> dict:
        submaps_total: dict = {'DRGN21': {}, 'DRGN22': {}, 'DRGN23': {}, 'DRGN24': {}}
        
        # Here i clean the SubMap-Cut from Environment and Objects files to just having one path (not repeated)
        clear_path_list = []
        for submaps_in_list in file_path_list:
            get_folder_path_only = submaps_in_list.rfind(f'\\')
            folder_path_clean = submaps_in_list[0:get_folder_path_only]
            if folder_path_clean not in clear_path_list:
                clear_path_list.append(folder_path_clean)
        # Here i take the clean path list and transform into a nested dict to get the correct nesting in the final dict
        nested_paths: dict = {}
        for this_drgn_disk in submaps_total:
            submap_repetitions: list = []
            submap_path: list = []
            for this_current_path in clear_path_list:
                if this_drgn_disk in this_current_path:
                    find_submap_name_start = this_current_path.find(f'\\{this_drgn_disk}')
                    find_submap_name_end = this_current_path.rfind(f'\\')
                    current_submap_name = this_current_path[(find_submap_name_start + 8) :find_submap_name_end] # \\DRGN2x\\ always is a 8 length string
                    submap_repetitions.append(current_submap_name)
                    submap_path.append(this_current_path)
            # I count the ocurrences because of YES
            count_submap_repetitions = dict(Counter(submap_repetitions))
            # Sorting and matching the SubMap with it cuts
            submap_dict: dict = {}
            for this_submap in count_submap_repetitions:
                current_cuts: list = []
                for submap_cut_path in submap_path:
                    this_submap_full_string = f'\\{this_submap}\\'
                    if (this_submap_full_string in submap_cut_path) and (this_drgn_disk in submap_cut_path):
                        current_cuts.append(submap_cut_path)
                gather_data_into_dict = {f'{this_submap}': current_cuts}
                submap_dict.update(gather_data_into_dict)
            gather_submap_data_into_dict = {f'{this_drgn_disk}': submap_dict}
            nested_paths.update(gather_submap_data_into_dict)
        
        for this_drgn2x in nested_paths:
            get_submaps = nested_paths.get(f'{this_drgn2x}')
            final_disk_dict: dict = {f'{this_drgn2x}': {}}
            for this_current_submap in get_submaps:
                final_submap_dict: dict = {f'{this_current_submap}': {}}
                get_cut_paths = get_submaps.get(f'{this_current_submap}')
                for this_cut_path in get_cut_paths:
                    find_cut_name = this_cut_path.rfind(f'\\')
                    cut_name = this_cut_path[find_cut_name + 1:]
                    cut_data: dict = {}
                    this_cut_path_environment = f'{this_cut_path}\\Environment.csv'
                    this_cut_path_objects = f'{this_cut_path}\\Objects.csv'
                    if os.path.isfile(this_cut_path_environment):
                        with open(this_cut_path_environment, 'r') as csv_file:
                            csv_read = csv.reader(csv_file)
                            for csv_data in csv_read:
                                object_name = csv_data[0]
                                object_dict = self.csvsubmap_data_to_dict(csv_row=csv_data)
                                data_dict: dict = {f'{object_name}': object_dict}
                                cut_data.update({f'Environment': data_dict})
                            csv_file.close()
                    if os.path.isfile(this_cut_path_objects):
                        with open(this_cut_path_objects, 'r') as csv_file:
                            csv_read = csv.reader(csv_file)
                            objects_dict: dict = {}
                            for csv_data in csv_read:
                                object_name = csv_data[0]
                                object_dict = self.csvsubmap_data_to_dict(csv_row=csv_data)
                                data_dict: dict = {f'{object_name}': object_dict}
                                objects_dict.update(data_dict)
                            csv_file.close()
                            cut_data.update({f'Objects': objects_dict})
                    final_submap_dict[f'{this_current_submap}'].update({f'{cut_name}': cut_data})
                final_disk_dict[f'{this_drgn2x}'].update(final_submap_dict)
            submaps_total.update(final_disk_dict)
        
        # This is the nesting example to get a nice view in the treeview
        """for disk in submaps_total:
            get_submap = submaps_total.get(f'{disk}')
            for current_submap in get_submap:
                get_cuts = get_submap.get(f'{current_submap}')
                for current_cut in get_cuts:
                    get_data = get_cuts.get(f'{current_cut}')
                    for this_data in get_data:
                        print(this_data)"""
        
        return submaps_total
    
    def csvsubmap_data_to_dict(self, csv_row=list) -> dict:
        """
        CSV data to dict\n
        :params: csv_row -> a single ROW from the csv data which is currently iterated\n
        csvsubmap_data_to_dict() -> Dictionary with the data already compiled\n
        as a Single Object
        """
        object_dict: dict = {}
        model_anim_folder = csv_row[1]
        model_file = csv_row[2]
        animation_files = csv_row[3]
        texture_files = csv_row[4]

        object_dict = {'ModelAnimFolder': model_anim_folder, 'ModelFile': model_file, 
                        'AnimationFiles': animation_files, 'Textures': texture_files}
        
        return object_dict

    def handle_special_csv(self, custom_csv=str) -> list[str]:
        special_csv: list[str] = []
        special_csv = custom_csv.split('!')
        return special_csv
    
    def process_database_from_textonly(self, file_path_list=list[str]) -> dict:
        texture_only_dict: dict = {'Menu_Textures': {}, 'Skyboxes': {}, 'THE_END': {}, 'WorldMap_GUI': {}, 'WorldMap_Thumbnails': {}}
        
        for current_textonly_database in file_path_list:
            find_last_slash = current_textonly_database.rfind(f'\\')
            find_csv_extension = current_textonly_database.find(f'.csv')
            texture_only_parent_name = current_textonly_database[(find_last_slash + 1):find_csv_extension].strip()
            
            with open(current_textonly_database, 'r') as csv_file:
                csv_read = csv.reader(csv_file)
                for csv_data in csv_read:
                    object_name = csv_data[0]
                    object_dict = self.csvtextonly_data_to_dict(csv_row=csv_data)
                    data_dict: dict = {f'{object_name}': object_dict}
                    texture_only_dict[f'{texture_only_parent_name}'].update(data_dict)        
        return texture_only_dict
    
    def csvtextonly_data_to_dict(self, csv_row=list) -> dict:
        """
        CSV data to dict\n
        :params: csv_row -> a single ROW from the csv data which is currently iterated\n
        csvtextonly_data_to_dict() -> Dictionary with the data already compiled\n
        as a Single Object
        """
        object_dict: dict = {}
        texture_folder = csv_row[1]
        folder_or_singlefile = csv_row[2]
        texture_files = csv_row[3]

        object_dict = {'TextureFolder': texture_folder, 'AssetStorage': folder_or_singlefile, 'Textures': texture_files}
        
        return object_dict
    
    def process_file_from_folder_deff(self, file_path_list=list[str]) -> dict:
        deff_database_files: dict = {'Bosses': {}, 'CutScenes': {}, 'Dragoon': {}, 'Enemies': {}, 'General': {}, 'Magic_and_Special_Attacks': {}}

        root_files: list = []
        rebuild_files: list = []
        for list_of_deff_files in file_path_list:
            if 'Rebuilding_Script' in list_of_deff_files:
                rebuild_files.append(list_of_deff_files)
            else:
                root_files.append(list_of_deff_files)
        
        for root_database_file in root_files:
            find_name_end_slash = root_database_file.rfind('\\')
            find_name_end = root_database_file.find('.csv')
            root_name = root_database_file[(find_name_end_slash + 1): find_name_end]
            
            database_data: dict = {}
            for rebuild_file in rebuild_files:
                if root_name in rebuild_file:
                    find_start_drgn_number = rebuild_file.rfind('\\')
                    rebuild_file_name = rebuild_file[find_start_drgn_number + 1:]
                    find_underscore_number = rebuild_file_name.find('_')
                    deff_drgn_number = rebuild_file_name[:find_underscore_number]
                    
                    with open(root_database_file, 'r') as root_csv:
                        csv_read = csv.reader(root_csv)
                        for csv_data in csv_read:
                            if deff_drgn_number == csv_data[2]:
                                drgn_deff_name = csv_data[0]
                                drgn_deff_texture = csv_data[1]
                                drgn_deff_file = csv_data[2]
                                drgn_deff_extra_textures_flag = csv_data[3]
                                drgn_deff_extra_textures_folder = csv_data[4]
                                rebuild_dict = self.rebuild_file_builder(rebuild_file_path=rebuild_file)
                                compiled_deff_data = {f'{drgn_deff_name}': {'Textures': drgn_deff_texture, 'File Path': drgn_deff_file, 
                                                      'Extra Textures Flag': drgn_deff_extra_textures_flag, 'Extra Textures Folder': drgn_deff_extra_textures_folder, 
                                                      'Rebuild Sequence': rebuild_dict}}
                                database_data.update(compiled_deff_data)
                        root_csv.close()
            deff_database_files[f'{root_name}'].update(database_data)

        return deff_database_files
    
    def rebuild_file_builder(self, rebuild_file_path=str) -> dict:
        rebuild_file: dict = {}

        raw_rebuild_file: list = []
        with open(rebuild_file_path, 'r') as script_rebuild_file:
            read_rebuild_file = script_rebuild_file.readlines()
            for text_string in read_rebuild_file:
                if text_string != f'\n':
                    raw_rebuild_file.append(text_string)
            script_rebuild_file.close()
        
        deff_name: str = f''
        deff_path: str = f''
        deff_animation_frames: str = f''
        deff_sequence: dict = {}

        transform_this_to_list_int = ['rel_pos', 'rel_rot', 'rel_scale', 'rel_col', 'rel_scale_color', 'scale_factor']
        transform_this_to_int = ['set_z', 'lifespan', 'count']

        for rebuild_text_string in raw_rebuild_file:
            rebuild_text_string_clean = rebuild_text_string.strip()
            if 'deff_name' in rebuild_text_string_clean:
                deff_name = rebuild_text_string_clean.replace(f'deff_name: ', '')
            elif 'deff_path' in rebuild_text_string_clean:
                deff_path = rebuild_text_string_clean.replace(f'deff_path: ', '')
            elif 'deff_animation_frames' in rebuild_text_string_clean:
                deff_animation_frames = rebuild_text_string_clean.replace(f'deff_animation_frames: ', '')
            else:
                split_rebuild_string = rebuild_text_string_clean.split(':')
                object_or_action = split_rebuild_string[0]
                split_properties = split_rebuild_string[1].split('-')
                sequence_properties: dict = {}
                for sequence_property in split_properties:
                    if "(" in sequence_property:
                        sequence_property_clean = sequence_property.strip()
                        find_name_start = sequence_property_clean.find('(')
                        find_name_end = sequence_property_clean.find(')')
                        name_property = sequence_property_clean[:find_name_start]
                        property_data_string = sequence_property_clean[find_name_start + 1: find_name_end]
                        sequence_properties.update({f'{name_property}': property_data_string})
                    elif "{" in sequence_property:
                        sequence_property_clean = sequence_property.strip()
                        find_name_start = sequence_property_clean.find('{')
                        find_name_end = sequence_property_clean.find('}')
                        name_property = sequence_property_clean[:find_name_start]
                        property_data_to_int = sequence_property_clean[find_name_start + 1: find_name_end]
                        property_data_int = StringInteger.transform_string_to_int(int_string=property_data_to_int)
                        sequence_properties.update({f'{name_property}': property_data_int})
                    elif "[" in sequence_property:
                        sequence_property_clean = sequence_property.strip()
                        find_name_start = sequence_property_clean.find('[')
                        find_name_end = sequence_property_clean.find(']')
                        name_property = sequence_property_clean[:find_name_start]
                        property_data_string_to_list = sequence_property_clean[find_name_start + 1: find_name_end]
                        property_data_list = StringInteger.transform_string_to_list(list_string=property_data_string_to_list)
                        sequence_properties.update({f'{name_property}': property_data_list})

                deff_sequence.update({f'{object_or_action}': sequence_properties})
        
        rebuild_file = {f'DEFF Name': deff_name, 'DEFF Path': deff_path, 'DEFF Anim Frames': deff_animation_frames, 'DEFF Anim Seq': deff_sequence}
        return rebuild_file

class StringInteger:
    def __init__(self) -> None:
        self.self = StringInteger

    @staticmethod
    def transform_string_to_list(list_string=str) -> list:
        """
        Take a format '[0x00000000, 0x00000000, 0x00000000]' and convert it into a List of Integers
        """
        string_to_list: list = []
        split_string = list_string.split(', ')
        
        for integer_string in split_string:
            new_int = int(integer_string, 0)
            check_int = StringInteger.check_sign(check_int=new_int)
            string_to_list.append(check_int)
        return string_to_list
    
    @staticmethod
    def transform_string_to_int(int_string=str) -> int:
        """
        Take a format '{0x00000000}' and convert it into a Integer
        """
        string_to_int: int = 0
        new_int = int(int_string, 0)
        check_int = StringInteger.check_sign(check_int=new_int)
        string_to_int = check_int

        return string_to_int
    
    @staticmethod
    def check_sign(check_int=int) -> int:
        """Check the sign of a integer converted from a string"""
        """
        Thanks to amarchiori in this Question solving at
        https://stackoverflow.com/questions/6727875/hex-string-to-signed-int-in-python
        """
        this_int: int = 0
        if (check_int & 0x8000) == 0x8000:
            this_int = -((check_int ^ 0xffffffff) + 1)
        else:
            this_int = check_int
        
        return this_int