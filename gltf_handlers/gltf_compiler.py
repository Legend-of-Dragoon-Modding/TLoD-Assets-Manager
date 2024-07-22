"""

glTF Compiler: this module will take the converted data,
and re-arrage for later being converted into glTF Files.

Copyright (C) 2024 DooMMetaL

"""

class NewModel:
    def __init__(self, model_data=dict, animation_data=dict | None) -> None:
        self.model_data = model_data
        self.animation_data = animation_data
        self.gltf_format: dict = {}
        self.model_arrager()
    
    def model_arrager(self) -> None:
        gltf_data: dict = {}

        tmd_model_data = self.model_data.get(f'Converted_Data')
        print(tmd_model_data)
    
    def quad_to_tri(self):
        """
        Quad to Tri:\n
        Convert a Primitive Quadrilatera intro a Triangle\n
        since glTF format won't support Quads in their Primitives structure
        """
        pass