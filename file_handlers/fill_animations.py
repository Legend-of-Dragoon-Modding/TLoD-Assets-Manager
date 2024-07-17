"""

Fill Animations:
This module will take an Object table and generates
a single frame animation with 0 data in it to fill
in specific cases in which animations are not loaded or used
in models, cases such: World Maps or TLoD Menu Logo
--------------------------------------------------------------------------------------------------------------
Input file: object_table = {}
--------------------------------------------------------------------------------------------------------------
:RETURN: -> self.animation_converted_data = {}
DICT --> 'Data': [BINARY_DATA]
--------------------------------------------------------------------------------------------------------------
Copyright (C) 2024 DooMMetaL

"""

class EmptyAnimation:
    def __init__(self, object_table=dict) -> None:
        self.object_table = object_table
        self.animation_converted_data: dict = {}
        self.fill_with_empy_animation()
    
    def fill_with_empy_animation(self) -> None:
        get_number_of_objects = len(self.object_table.get(f'Data_Table'))
        self.animation_converted_data = {'TotalTransforms': 2, 'AnimationData': {}}

        for this_object in range(0, get_number_of_objects):
            for transform in range(0, 1):
                object_rot_trans = {"Rx": 0.0, "Ry": 0.0, "Rz": 0.0, "Tx": 0.0, "Ty": 0.0, "Tz": 0.0}
                current_object_transform: dict = {f'Transform_Number_{transform}': object_rot_trans}
                self.animation_converted_data['AnimationData'][f'Object_Number_{this_object}'] = current_object_transform