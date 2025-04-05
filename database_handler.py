"""

Database Handler:
Handle Database file, pre-processing before GUI Start
There are Four Database Types:
Battle, DEFF, SubMap, Textures Only, World Map.

Copyright (C) 2025 DooMMetaL

"""
import os
from collections import Counter
import random
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
        self.full_database: dict = {'Battle': {}, 'DEFF': {}, 'SubMaps': {}, 'Textures Only': {}, 'World Map': {}}
        self.process_csv_file()
    
    def process_csv_file(self) -> None:
        """
        Process CSV Files format for TLoD Assets Manager
        """
        check_databases_path = os.walk(self.database_path)

        main_folder_databases: list[str] = []
        deff_folder_databases: list[str] = []
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
                elif 'SubMaps' in each_database_full_path:
                    submap_folder_databases.append(each_database_full_path)
                elif 'Textures_Only' in each_database_full_path:
                    texture_only_folder_databases.append(each_database_full_path)
                elif 'World_Map' in each_database_full_path:
                    world_map_folder_databases.append(each_database_full_path)
        
        # FINAL STRUCTURE -> {'Battle_Stages': {}, 'Bosses': {}, 'Characters': {}, 'CutScenes': {}, 'Enemies': {}, 'Tutorial': {}}
        battle_dict = self.process_file_from_folder(file_path_list=main_folder_databases, file_path_type='Battle')
        # FINAL STRUCTURE -> {'South Serdio': {}, 'North Serdio': {}, 'Tiberoa': {}, 'Illisa Bay': {}, 'Mille Seseau': {}, 'Gloriano': {}, 'Death Frontier Desert': {}, 'World Map Complete': {}, 'Mini Dart': {}, 'Queen Fury': {}, 'Coolon': {}, 'Teleportation Glow': {}}
        # NOTE: The texture nesting from World Maps will be handled in the Converter directly
        world_map_dict = self.process_file_from_folder(file_path_list=world_map_folder_databases, file_path_type='WorldMap')
        # FINAL STRUCTURE -> {'DRGN21': {}, 'DRGN22': {}, 'DRGN23': {}, 'DRGN24': {}}
        submaps_dict = self.process_database_from_submap(file_path_list=submap_folder_databases)
        # FINAL STRUCTURE -> {'Menu_Textures': {}, 'Skyboxes': {}, 'THE_END': {}, 'WorldMap_Thumbnails': {}, 'WorldMap_GUI': {}}
        texture_only_dict = self.process_database_from_textonly(file_path_list=texture_only_folder_databases)
        # FINAL STRUCTURE -> {'Bosses': {}, 'CutScenes': {}, 'Dragoon': {}, 'Enemies': {}, 'General': {}, 'Magic and Special Attacks': {}}
        deff_dict = self.process_file_from_folder_deff(file_path_list=deff_folder_databases)

        self.full_database = {'Battle': battle_dict, 'DEFF': deff_dict, 'SubMaps': submaps_dict, 'Textures Only': texture_only_dict, 'World Map': world_map_dict}
    
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
                    self.database_not_empty(check_data=csv_data, database_path=simple_path)
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
                {'Battle': {'Characters': {'Dart_Normal': {'idle': ModelFolder': 'path', 'ModelFile': 'n', 'PassiveFolder': 'path', 'PassiveFiles': 'files', 'AttackFolder': 'path', 'AttackFiles': 'files', 'texture': 'file'}}}}"""
                csv_nested_read: list[str] = []
                with open(nested_path, 'r') as csv_nested_file:
                    # First i read the Custom CSV with a '!' as delimiter for Texture and main data (Since i don't like the idea of repeating the texture data over and over)
                    csv_read = csv.reader(csv_nested_file)
                    for csv_data in csv_read:
                        self.database_not_empty(check_data=csv_data, database_path=nested_path)
                        object_name_nested = csv_data[0]
                        object_dict_nested = self.csv_data_to_dict(csv_row=csv_data)
                        data_dict_nested: dict = {f'{object_name_nested}': object_dict_nested}
                        this_inner_dict_nested[f'{nested_subparent_name}'].update(data_dict_nested)
                    database_to_process['Characters'].update(this_inner_dict_nested)
                    csv_nested_file.close()

            elif nested_parent_name == 'CutScenes':
                this_inner_dict_nested_2: dict = {f'{nested_subparent_name}': {}}
                # This is the Character Models/Animations data
                with open(nested_path, 'r') as csv_file_nested:
                    csv_read_nested = csv.reader(csv_file_nested)
                    for csv_data_nested in csv_read_nested:
                        self.database_not_empty(check_data=csv_data_nested, database_path=nested_path)
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
                                self.database_not_empty(check_data=csv_data, database_path=this_cut_path_environment)
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
                                self.database_not_empty(check_data=csv_data, database_path=this_cut_path_objects)
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
    
    def process_database_from_textonly(self, file_path_list=list[str]) -> dict:
        texture_only_dict: dict = {'Menu_Textures': {}, 'Skyboxes': {}, 'THE_END': {}, 'WorldMap_GUI': {}, 'WorldMap_Thumbnails': {}}
        
        for current_textonly_database in file_path_list:
            find_last_slash = current_textonly_database.rfind(f'\\')
            find_csv_extension = current_textonly_database.find(f'.csv')
            texture_only_parent_name = current_textonly_database[(find_last_slash + 1):find_csv_extension].strip()
            
            with open(current_textonly_database, 'r') as csv_file:
                csv_read = csv.reader(csv_file)
                for csv_data in csv_read:
                    self.database_not_empty(check_data=csv_data, database_path=current_textonly_database)
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

        for deff_file in file_path_list:
            if 'Bosses' in deff_file:
                pass
            elif 'CutScenes' in deff_file:
                pass
            elif 'Dragoon_Characters' in deff_file:
                if '-Objects' not in deff_file:
                    # Here i filter Sequence CSV of Objects from the Sequence, since the sequence file would be loaded only when a DEFF is selected
                    # The Object Loader would be in a separated Class
                    dragoon_sequence = self.rebuild_deff_sequence(deff_file)
                    deff_database_files['Dragoon'].update(dragoon_sequence)
            elif 'Enemies' in deff_file:
                pass
            elif 'General' in deff_file:
                pass
            elif 'Magic_and_Special_Attacks' in deff_file:
                pass

        return deff_database_files
    
    def rebuild_deff_sequence(self, rebuild_file_path=str) -> dict:
        """
        Rebuild DEFF Sequence:\n
        Pretty much as the name says, rebuilds a DEFF Sequence, based on CSV files,\n
        which acts as a kind of script file, but human readable.\n
        Since much of this files are written by hand could contain some errors.
        """
        
        """
        First understanding that getting Data from the Script files is not an easy task, even people like Monoxide, TheFlyingZamboni, Zychronix, Icarus, struggles a lot
        to simply follow up whats going on (and seriously i'm not even closer to their understanding about this files), 
        this because the Script Files are not necessarily 'linear'. So getting the exact frame in which an effect start or end is very complex at best (impossible in other words).
        What i do in this files is comparing some timing/frame data from the Scripts Versus a 15~20~24 FPS Recording (in which i dump each frame into images) and checking
        frame by frame when a effect start to appear or end (disappear).
        Also will using as support value VSyncDivider, which will dictate in how to place the Keyframes in the timeline, but is the Frame Rate dictated to be run by the Engine.
        For the rest of Data I just follow what file is loading.
        For sake of easy reading and maintainance I opted to split the "Script" into two concepts.
        First Concept is "Sequecence File", Sequence file is a csv which contains:
        --------------------------------------------------
        Name - Objects Folder - Texture Folder - Total Frames - VSyncDivider - Extra Texture Folder - AnimatedTMDBool - StaticTMDBool - ParticleBool
        {Extra Texture Folder is the general folders in which this DEFF Stores it's Extra Textures}
        {AnimatedTMDBool - StaticTMDBool - ParticleBool: This way i can trace prior if creating folders is needed, also avoid Conversion if in General do not exist this kind of Objects inside THIS DEFF}
        0_DEFFObject0
        1_DEFFObject1
        n_DEFFObjectn
        --------------------------------------------------
        Second concept is "DEFF Object Properties File", DEFF Object Properties File have the same name as referred in Sequence File, 
        So for example we say the last DEFFObject is the n_DEFFObjectn, and the name of the file would be "n_DEFFObjectn.csv"
        This files contains the properties of the Object itself and have General Properties and Script Animation.
        Objects could be: AnimatedTMD, StaticTMD, Particles.
        --------------------------------------------------
        """
        rebuild_file: dict = {}

        raw_rebuild_file: list = []
        try:
            with open(rebuild_file_path, 'r') as csv_script:
                csv_file = csv.reader(csv_script)
                for csv_data in csv_file:
                    self.database_not_empty(check_data=csv_data, database_path=rebuild_file_path)
                    raw_rebuild_file.append(csv_data)
                csv_script.close()
        except RuntimeError:
            deff_db_error = f'{rebuild_file_path}\nCannot be loaded, check if the file exist\nExiting tool to avoid further errors...'
            error_deff_csv_loading = QMessageBox.critical(None, 'CRITICAL ERROR!!', deff_db_error, QMessageBox.StandardButton.Ok)
            exit()
        
        row_count = len(raw_rebuild_file)

        deff_name:str = ''
        deff_sequence_number_as_str: str = ''

        deff_sequence: dict = {'Name': None, 'Folder': None, 'Texture Folder': None, 'Total Frames': None, 'VSyncDivider': None, 
                               'Extra Textures': None, 'Sequence': None, 'Sequence Folder': None, 
                               'AnimatedTMDBool': None, 'StaticTMDBool': None, 'ParticleBool': None}
        
        sequence: list = []
        for this_row_number in range(0, row_count):
            this_row = raw_rebuild_file[this_row_number]
            if this_row_number == 0:
                deff_name = this_row[0] # The name to generate the last Dict, so once you packed in the nested dict don't get replaced
                deff_sequence_number_as_str = this_row[1]
                deff_sequence['Name'] = this_row[0]
                deff_sequence['Folder'] = this_row[1]
                deff_sequence['Texture Folder'] = this_row[2]
                deff_sequence['Total Frames'] = this_row[3]
                deff_sequence['VSyncDivider'] = StringIntegerList.convert_integer(convert_int=this_row[4])
                deff_sequence['Extra Textures'] = this_row[5]
                deff_sequence['AnimatedTMDBool'] = this_row[6]
                deff_sequence['StaticTMDBool'] = this_row[7]
                deff_sequence['ParticleBool'] = this_row[8]
            else:
                add_this_sequence = this_row[0]
                sequence.append(add_this_sequence)
        deff_sequence['Sequence'] = sequence

        # Now i need to setup the Sequence Folder
        find_last_slash_from_path = rebuild_file_path.rfind('\\')
        database_clear_path = rebuild_file_path[0:find_last_slash_from_path]
        find_first_slash_from_sequence_number = deff_sequence_number_as_str.find('/')
        sequence_number_clear = deff_sequence_number_as_str[0:find_first_slash_from_sequence_number]
        
        # Now we join both Strings to get the actual Sequence Folder
        joined_sequence_path = f'{database_clear_path}\\{sequence_number_clear}-Objects\\'
        deff_sequence['Sequence Folder'] = joined_sequence_path

        rebuild_file = {f'{deff_name}': deff_sequence}

        return rebuild_file

    def database_not_empty(self, check_data=list, database_path=str):
        """
        Database Not Empty:\n
        Check if a Database is not empty.\n
        in case of an Empty Database, must crash.
        """
        if len(check_data) == 0:
            database_is_empty = f'Database: {database_path}, have Empty Data.\nCheck if Database is placed as intended or have some data in it.\nExiting tool to avoid further errors...'
            error_database_type = QMessageBox.critical(None, 'CRITICAL ERROR!!', database_is_empty, QMessageBox.StandardButton.Ok)
            exit()

class DeffObjectDatabase:
    def __init__(self, current_object, sequence_folder=str) -> dict:
        """DEFF Object Database: Holds properties of each object from the current DEFF"""
        self.current_object = current_object
        self.sequence_folder = sequence_folder
        self.current_object_dict: dict = {}
        self.process_object_csv()

    def process_object_csv(self) -> None:
        """
        Process Object CSV:\n
        Will process the csv file, which is created in this way:\n
        General Properties: Are the properties which are spread across all the Object Sequence, no matter the timing of it.\n
        ===============================================================================================================================\n
        FILE - FILETYPE - TEXTURES - ANIM FILES - PARENT - FRAME START - FRAME END - PARTICLE TYPE - COUNT - SIMULATION TYPE - LIFESPAN
        ===============================================================================================================================\n
        NOTE: Textures could be more than 1, will depend on the Extra Textures folder if != to NONE
        After will be the Scripting Animation: This properties are changing across Object Sequences, sometimes in DEFF Devs changed Position, Rotation, Translation, etc.\n
        Script Animation Types included: Relative Position, Relative Rotation, Relative Scale, Relative Color.
        First will come the Script Animation Header telling How Many Script Animations are in this Object Sequence:\n
        =================\n
        ScriptAnimation N {Where N is a Unsigned Integer | NONE}
        =================\n
        Then start the Scripted Animations Types in this fashion:\n
        ==========================================================\n
        ScriptAnimationType{Name} - Parent{Name} - Property{Value}\n
        ==========================================================
        Working in this way, if some of the properties is variable, is taken as a Script Animation.
        Anyway, Script Animation would be apply only If we are re-creating the whole sequence, at the moment that is work in progress.
        """
        current_object_csv_path = f'{self.sequence_folder}{self.current_object}.csv'

        raw_objects_data_dict: dict = {}
        try:
            with open(current_object_csv_path, 'r') as csv_file:
                csv_read = csv.reader(csv_file)
                next(csv_read) # Here we jump the very first row, since is not needed
                raw_current_object: list = []
                for current_row in csv_read:
                    this_row: list = []
                    for current_column in current_row:
                        if current_column != '': # Here i take out the "blank" spaces from csv file
                            this_row.append(current_column)
                    raw_current_object.append(this_row)
                this_object_dict = {f'{self.current_object}': raw_current_object}
                raw_objects_data_dict.update(this_object_dict)
                csv_file.close()
        
        except RuntimeError:
            deff_db_error = f'{current_object_csv_path}\nCannot be loaded, check if the file exist\nExiting tool to avoid further errors...'
            print(f'CRITICAL ERROR!!! - {deff_db_error}')
            exit()
        
        current_object_dict: dict = {'Name': None, 'File': None, 'Filetype': None, 'Texture': None, 'ExtraTextures': None, 'Anim Files': None, 'Parent': None, 'Frame Start': None, 'Frame End': None, 'Particle Type': None, 'Count': None, 'Simulation Type': None, 'Lifespan': None, 'Script Animation': None}
        for current_object_name in raw_objects_data_dict:
            current_object_list = raw_objects_data_dict.get(f'{current_object_name}')
            current_object_dict['Name'] = current_object_name

            general_properties_row = current_object_list[0]
            current_object_dict['File'] = general_properties_row[0]
            current_object_dict['Filetype'] = general_properties_row[1]
            if 'EXTRA:' not in general_properties_row[2]:
                current_object_dict['Texture'] = general_properties_row[2].split(', ')
            else:
                #TODO: Check that Extra Textures only loaded with now 'Base' Textures with it, in case that this happens, redirect the base textures to 'Texture' Key
                find_extra = general_properties_row[2].find('EXTRA:')
                extra_texture_files = general_properties_row[2]
                extra_texture_files_isolated = extra_texture_files[(find_extra + 6):].split(', ')
                current_object_dict['Texture'] = ['EXTRA']
                current_object_dict['ExtraTextures'] = extra_texture_files_isolated
            current_object_dict['Anim Files'] = general_properties_row[3].split(', ')
            current_object_dict['Parent'] = general_properties_row[4]
            current_object_dict['Frame Start'] = StringIntegerList.convert_integer(convert_int=general_properties_row[5])
            current_object_dict['Frame End'] = StringIntegerList.convert_integer(convert_int=general_properties_row[6])
            current_object_dict['Particle Type'] = general_properties_row[7]
            current_object_dict['Count'] = StringIntegerList.transform_string_to_int(int_string=general_properties_row[8])
            current_object_dict['Simulation Type'] = general_properties_row[9]
            current_object_dict['Lifespan'] = general_properties_row[10]

            script_animation_properties = current_object_list[1]
            script_animation_number = StringIntegerList.convert_integer(convert_int=script_animation_properties[1])

            script_animation_rows = current_object_list[2:]

            if len(script_animation_rows) != script_animation_number:
                script_animation_error_msg = f'File: {current_object_name}, had a Script Animation Number discrepancy.\nExpected: {script_animation_number} - Obtained: {len(script_animation_rows)}\nClosing tool to avoid further errors...'
                error_script_anim_number = QMessageBox.critical(None, 'CRITICAL ERROR!!', script_animation_error_msg, QMessageBox.StandardButton.Ok)
                print(script_animation_error_msg)
                exit()

            script_animations_dict: dict = {}
            for current_script_animation_number in range(0, script_animation_number):
                current_script_animation = script_animation_rows[current_script_animation_number]
                this_script_animation = {f'ScriptAnimation_{current_script_animation_number}': current_script_animation}
                script_animations_dict.update(this_script_animation)
            
            script_animation_array: dict = {'ScriptAnimNumber': script_animation_number, 'ScriptAnimData': script_animations_dict}
            current_object_dict['Script Animation'] = script_animation_array
        
        self.current_object_dict = current_object_dict
            

class StringIntegerList:
    def __init__(self) -> None:
        self.self = StringIntegerList

    @staticmethod
    def transform_string_to_list(list_string=str) -> list:
        """
        Take a format '[0x00000000, 0x00000000, 0x00000000]' and convert it into a List of Integers
        """
        string_to_list: list = []
        
        split_string = list_string.split(', ')
        
        for integer_string in split_string:
            if integer_string != 'RAND':
                new_int = int(integer_string, 0)
                check_int = StringIntegerList.check_sign(check_int=new_int)
                string_to_list.append(check_int)
            else:
                pass
        return string_to_list
    
    @staticmethod
    def transform_string_to_int(int_string=str) -> int:
        """
        Take a format '{0x00000000}' and convert it into a Integer
        """
        string_to_int: int = 0
        if 'RANDOM' in int_string:
            new_string = int_string.replace('RANDOM', '').replace('(', '').replace(')', '')
            split_numbers = new_string.split(',')
            number_a = int(split_numbers[0])
            number_b = int(split_numbers[1])
            string_to_int = random.randint(number_a, number_b)
        else:
            new_int = int(int_string, 0)
            check_int = StringIntegerList.check_sign(check_int=new_int)
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
    
    @staticmethod
    def convert_integer(convert_int=str) -> int:
        """
        Convert Integer:\n
        String data is converted into Integer.
        """
        final_int = int(convert_int)

        return final_int