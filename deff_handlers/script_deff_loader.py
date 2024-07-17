"""

Script DEFF Loader: This module will load the data from the Custom Script 
to sort for the processing

Copyright (C) 2024 DooMMetaL

"""

class DeffScript:
    def __init__(self, deff_sequence=dict, deff_name=str, deff_parent=str) -> None:
        self.deff_sequence = deff_sequence
        self.deff_name = deff_name
        self.deff_parent = deff_parent
        self.deff_path: str = f''
        self.deff_anim_frames: str = f''
        self.sequenced_deff: dict = {} # The sequenced DEFF is the final form of a DEFF Dictionary to be later converted
        """This lines of code were written in the Argentina Independence Day!!
        ===============================
        |||||||||||||||||||||||||||||||
        ===============================
                      ***
                     *****
                      ***
        ===============================
        |||||||||||||||||||||||||||||||
        ===============================
        Viva la libertad CARAJO!!!"""
        self.script_sequence_loader()
    
    def script_sequence_loader(self) -> None:
        """This will load the Sequence got from the Rebuild file and sort it into it's final form, keep an eye
        that i extract some data from the nested dictionary, i do this way because it's easy to track errors
        from the rebuild files instead of doing from the code"""
        deff_sorted_sequence = self.sort_deff(deff_seq=self.deff_sequence)

        self.sequenced_deff = {'Parent': self.deff_parent, 'Name': self.deff_name, 'DEFF File Path': self.deff_path,
                               'Textures Path': self.deff_sequence.get(f'Textures'), 
                               'Extra Textures Flag': self.deff_sequence.get(f'Extra Textures Flag'), 'Extra Textures Folder': self.deff_sequence.get(f'Extra Textures Folder'), 
                               'Rebuild Sequence': deff_sorted_sequence}
    
    def sort_deff(self, deff_seq=dict) -> dict:
        """DEFF Sequences have a Super Parent, which is 'Main', then each Object [3D Model or Particle] is attach to this Super Parent
        or to another Object which is child of, to sort this i will create first a dict containing all the parents, and after that,
        code will be sorting the objects depending on the inheritances. This will keep the inheritance to do the relative location/rotation/scale
        calculations"""
        deff_new_sequence: dict = {}
        get_old_sequence = deff_seq.get(f'Rebuild Sequence')
        self.deff_path = get_old_sequence.get(f'DEFF Path')
        self.deff_anim_frames = get_old_sequence.get(f'DEFF Anim Frames')
        old_anim_sequence_data = get_old_sequence.get(f'DEFF Anim Seq')

        sequence_number = 0
        deff_new_sequence: dict = {}
        for anim_sequence in old_anim_sequence_data:
            deff_new_sequence.update({f'{sequence_number}': {f'{anim_sequence}': old_anim_sequence_data.get(f'{anim_sequence}')}})
            sequence_number += 1
        
        return deff_new_sequence
