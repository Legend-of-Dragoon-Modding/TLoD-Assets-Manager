"""

DEFF Rebuild: This module will take the data from the sequenced rebuild Dict
and process it for the final conversion, also will create a file in which will
be used for loading the scene into Blender

Copyright (C) 2024 DooMMetaL

DEFF Discriminator Algorithm directly based on the code found in:
https://github.com/Legend-of-Dragoon-Modding/Severed-Chains
https://github.com/Legend-of-Dragoon-Modding/Severed-Chains/blob/main/src/main/java/legend/game/combat/deff/DeffPart.java

Copyright (C) 2024 Monoxide

"""
from deff_handlers import lmb_file, animated_tmd_file, static_tmd_file, sprite_file, cmb_file
from gltf_handlers import NewGltfModel

class DeffFile:
    def __init__(self, deff_sequence=dict, sc_folder=str) -> None:
        self.deff_sequence = deff_sequence
        self.sc_folder = sc_folder + f'/SECT/DRGN0.BIN/'
        self.parent_folder = self.deff_sequence.get(f'Parent')
        self.deff_name = self.deff_sequence.get(f'Name')
        self.deff_file_path = self.sc_folder + self.deff_sequence.get(f'DEFF File Path') # Need to pass as argument the sc_default_folder
        self.deff_textures_path = self.deff_sequence.get(f'Textures Path')
        self.deff_extra_textures_flag = self.deff_sequence.get(f'Extra Textures Flag') # Need to check if extra textures are loaded, if not, the deff_extra_textures_folder will be not run
        self.deff_extra_textures_folder = self.deff_sequence.get(f'Extra Textures Folder')
        #self.dae_deff: dict = {}
        self.convert_deff()
    
    def convert_deff(self) -> None:
        """This takes the data from the sequence and checks for the files and if everything is ok, will convert them into DAE suitable format"""
        deff_sequence = self.deff_sequence.get(f'Rebuild Sequence') # Need to sort the Objects depending on the inheritance this way Main->SubObj->ifSubSubObj

        deff_parents: list = []
        for current_sequence in deff_sequence:
            get_this_seq = deff_sequence.get(f'{current_sequence}')
            for this_object in get_this_seq:
                this_object_properties = get_this_seq.get(f'{this_object}')
                get_parent = this_object_properties.get(f'parent')
                if get_parent != None:
                    deff_parents.append(get_parent)
        
        deff_parents_clean = []
        for current_parent in deff_parents:
            if current_parent not in deff_parents_clean:
                deff_parents_clean.append(current_parent)
        
        self.deff_parents_position: dict = {}
        for parent_deff in deff_parents_clean:
            if parent_deff == 'Main':
                main_parent = {'Main': {'rel_pos': [0, 0, 0], 'rel_rot': [0, 0, 0], 'rel_scale':[0, 0, 0]}}
                self.deff_parents_position.update(main_parent)
            else:
                for current_sequence in deff_sequence:
                    get_this_seq = deff_sequence.get(f'{current_sequence}')
                    for this_object in get_this_seq:
                        this_object_properties = get_this_seq.get(f'{this_object}')
                        get_object_name = this_object_properties.get(f'name')
                        if get_object_name == parent_deff:
                            get_rel_pos = this_object_properties.get(f'rel_pos')
                            get_rel_rot = this_object_properties.get(f'rel_rot')
                            get_rel_scale = this_object_properties.get(f'rel_scale')
                            this_parent = {f'{get_object_name}': {'rel_pos': get_rel_pos, 'rel_rot': get_rel_rot, 'rel_scale':get_rel_scale}}
                            self.deff_parents_position.update(this_parent)

        deff_storage: dict = {}
        for this_sequence in deff_sequence:
            get_data_sequence = deff_sequence.get(f'{this_sequence}')
            for get_data in get_data_sequence:
                get_properties = get_data_sequence.get(f'{get_data}')
                get_file_path = get_properties.get(f'file')
                if get_file_path != None:
                    self.deff_file_complete = self.deff_file_path + get_file_path
                    this_deff_file = self.deff_part_discriminator(deff_data_file_path=self.deff_file_complete, deff_properties=get_properties, parent_transforms=self.deff_parents_position, all_properties=deff_sequence)
                else:
                    # in here lies the startburst effects, rays and lines
                    pass
                    #print('this is a totally generated particle')
    
    def deff_part_discriminator(self, deff_data_file_path=str, deff_properties=dict, parent_transforms=dict, all_properties=dict) -> dict:
        """
        main_model Model Type is a 3D Model with embedded Animations
        static_model Model Type is a 3D Model with no Animations
        animated_model Model Type is a 3D Model with embedded Animations
        """
        final_deff_data: dict = {}
        
        deff_file_store: bytes = b''
        with open(deff_data_file_path, 'rb') as deff_file_bin:
            deff_file_store = deff_file_bin.read()
            deff_file_bin.close()

        """HERE i will use the DEFF Discriminator from SC and doing the check directly over the files"""
        """
        Explaning a little bit of how flags works:
        FLAG 0 is used for LMB Files which are standalone file
        FLAG 1 and 2 are used for TMD Files [Optimised/Unoptimised] which have embedded Animation Data
        FLAG 3 is used for Static TMD Files
        FLAG 4 is used for Sprites
        FLAG 5 is used for CMB and SAF Files which are standalone file"""
        get_deff_flags = deff_file_store[0:4]
        flags_to_int = int.from_bytes(get_deff_flags, byteorder='little', signed=False)
        check_flags = flags_to_int >> 24
        if check_flags == 0:
            final_deff_data_lmb = lmb_file.Lmb(lmb_binary_data=deff_file_store)
        elif (check_flags == 1) or (check_flags == 2):
            final_deff_data_animated_tmd = animated_tmd_file.TmdEmbeddedAnimation(animated_tmd_binary=deff_file_store)
        elif check_flags == 3:
            final_deff_static_tmd = static_tmd_file.StaticTmd(static_tmd_binary=deff_file_store)
            convert_static_tmd = NewGltfModel(model_data=final_deff_static_tmd.processed_static_tmd_model, animation_data=None)
        elif check_flags == 4:
            """TODO: inside the DEFF properties i need to write the type of simulation of particle by hand ¯\\_(ツ)_/¯"""
            final_sprite = sprite_file.Sprite(sprite_binary=deff_file_store, sprite_properties=deff_properties, parent_transforms=parent_transforms, all_particles_properties=all_properties)
        elif check_flags == 5:
            final_deff_data_cmb = cmb_file.Cmb(cmb_binary_data=deff_file_store)
        else:
            print(f'{deff_data_file_path} is not a valid DEFF file, this will be ignored...')
            print(f'Report this error as DEFF File not recognised with the path to the file...')

        return final_deff_data