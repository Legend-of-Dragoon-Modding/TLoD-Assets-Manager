import sys
import time
from PyQt6.QtWidgets import QApplication
from file_handlers import binary_to_dict, asunder_binary_data, fill_animations, folder_handler, debug_files_writer
from dae_handlers import collada_compiler, collada_writer
from texture_handlers import png_writer

app = QApplication(sys.argv)

"""AT THE MOMENT CC CONTAINED MODEL AND ANIMS; STANDARD TMD; TIM ARE WORKING AS EXPECTED"""

"""
Asset DICT Format:
Asset: dict = {'Format': AssetFormat-str, 'Path': OriginFilePath-str, 'Name': 'FileFantasyName'-str, 'isAnimated': Bool [Only for Models], 'isTextured': Bool [Only for Models], 'isOnlyTexture': Bool [Only for OnlyTexture Files]}

Debug Files DICT Format: --> This only passed one time
Debug: dict = {'TMDReport': Bool, 'PrimPerObj': Bool, 'PrimData': Bool}

Deploy Files DICT Format: --> i'm not sure if better doing this previously
Deploy: dicr = {'MainFolderPath': DeployPath-str, 'ModelNesting': SubFolderToCreate-str, 'TextureNesting': SubFolderToCreate-str}

"""
# Parameters that i have to pass to make this shit to work
file_model = {'Format': 'TMD_CContainer', 'Path': 'C:\\Users\\Axel\\Desktop\\Bin_Test_Tool\\tmd_ccontainer\\32', 'Name': 'Dart', 'isAnimated': True, 'isTextured': True}
file_animation = {'Format': 'SAF_CContainer', 'Path': 'C:\\Users\\Axel\\Desktop\\Bin_Test_Tool\\tmd_ccontainer\\0'}
file_texture = {'Format': 'TIM', 'Path': 'C:\\Users\\Axel\\Desktop\\Bin_Test_Tool\\tmd_ccontainer\\combat', 'Name': 'Dart'}
debug_files_dict = {'TMDReport': True, 'PrimPerObj': True, 'PrimData': True} # This is only pass one, even in batch
model_origin_path = file_model.get(f'Path')
file_name_model = file_model.get('Name')
file_name_texture = file_texture.get('Name')
file_type_texture = file_texture.get('Format')
is_animated_param = file_model.get('isAnimated')
is_texture_param = file_model.get('isTextured')
#--------------------------------------------------------------------------------------------------------------------------------------------------------------#
start = time.time()
contain_file_model = binary_to_dict.BinaryToDict(bin_file_to_dict=file_model)
processed_data_model = asunder_binary_data.Asset(bin_to_split=contain_file_model.bin_data_dict)

#HERE I CHECK IF ANIMATION WILL BE CONVERTED
processed_data_animation: asunder_binary_data.Asset | fill_animations.EmptyAnimation
if is_animated_param == True:
    contain_file_animation = binary_to_dict.BinaryToDict(bin_file_to_dict=file_animation)

    processed_data_animation = asunder_binary_data.Asset(bin_to_split=contain_file_animation.bin_data_dict)
else:
    processed_data_animation = fill_animations.EmptyAnimation(object_table=processed_data_model.model_converted_data)
#----------> END ANIMATION CHECK

new_folder = folder_handler.Folders(deploy_folder_path=f'C:\\Users\\Axel\\Desktop\\TMD_DUMP\\', file_nesting='CC_Container, Animation', file_name=file_name_model)
debug_data = debug_files_writer.DebugData(converted_file_path=new_folder.new_file_name, debug_files_flag=debug_files_dict, file_data=processed_data_model.model_converted_data)

collada_compile = collada_compiler.ColladaFileFormat(processed_model_data=processed_data_model.model_converted_data)
collada_file_write = collada_writer.ColladaFile(collada_compiled_file=collada_compile.compiled_collada_data, total_objects=collada_compile.total_objects, total_primitives=collada_compile.total_primitives , animation_data=processed_data_animation.animation_converted_data, deploy_file_path=new_folder.new_file_name, origin_file_path=model_origin_path)
end = time.time()
#HERE I CHECK IF TEXTURE WILL BE CONVERTED
if is_texture_param == True:
    #print(f'Execution time on Model Convert:', (end-start) * 10**3, 'ms')
    start_texture = time.time()
    contain_file_texture = binary_to_dict.BinaryToDict(bin_file_to_dict=file_texture)
    processed_data_texture = asunder_binary_data.Asset(bin_to_split=contain_file_texture.bin_data_dict)
    new_folder_text = folder_handler.Folders(deploy_folder_path=f'C:\\Users\\Axel\\Desktop\\TMD_DUMP\\', file_nesting='CC_Container, Animation, Texture', file_name=file_name_texture)
    png_file_write = png_writer.PngFile(texture_data=processed_data_texture.texture_converted_data, file_deploy_path=new_folder_text.new_file_name, texture_type=file_type_texture)
    end_texture = time.time()
    #print(f'Execution time on Texture Convert:', (end_texture-start_texture) * 10**3, 'ms')