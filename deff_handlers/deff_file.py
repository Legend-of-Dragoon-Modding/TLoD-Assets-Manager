"""

DEFF Rebuild: This module will take the data from the sequenced rebuild Dict
and process it for the final conversion, also will create a file in which will
be used for loading the scene into Blender
-------------------------------------------------------------------------------------------------------------------------
Copyright (C) 2024 DooMMetaL

"""
from deff_handlers import deff_gltf_writer, deff_object_compile_gltf, static_tmd_file, animated_tmd_file, particle_file, particle_simulation, generated_particles
from file_handlers import folder_handler

class DeffFile:
    def __init__(self, data_to_convert=dict, convert_textures=bool, convert_particles=bool, sc_folder=str, deploy_folder=str, selected_names=str) -> None:
        self.data_to_convert = data_to_convert
        self.convert_textures = convert_textures
        self.convert_particles = convert_particles
        self.sc_folder = sc_folder
        self.deploy_folder = deploy_folder
        self.selected_names = selected_names
        self.conformed_deff: dict = {}
        self.convert_deff()
    
    def convert_deff(self) -> None:
        """
        Convert DEFF:\n
        This takes the data from the sequence and checks for the files and if everything is ok,\n
        will convert them into glTF suitable format
        """
        deff_name = self.data_to_convert.get(f'DEFF Name')
        deff_path = self.data_to_convert.get(f'Objects Path')
        deff_textures_path = self.data_to_convert.get(f'Textures Path')
        deff_total_frames = self.data_to_convert.get(f'Total Frames')
        deff_extra_tims = self.data_to_convert.get(f'Extra TIMs') # TODO: NOT IMPLEMENTED YET
        deff_sequence = self.data_to_convert.get(f'Sequence')

        total_objects_in_deff = len(deff_sequence)

        change_deff_name = deff_name.replace(' ', '_')
        change_selected_names = f'DEFF, {self.selected_names}, {change_deff_name}'
        new_folders = folder_handler.Folders(deploy_folder_path=self.deploy_folder, file_nesting=change_selected_names, file_name=change_deff_name)
        

        # First we get all the Parents properties, to know where to get some position/rotation/scale data
        # This step is important to keep referenced distances from parent objects in the DEFF creation
        parent_data: dict = {'Main': {'InitPosition': [0, 0, 0], 'InitRotation': [0, 0, 0], 'InitScale': [1, 1, 1]}}
        for this_model_numeration_init in range(0, total_objects_in_deff):
            model_name_sequenced_init = f'{this_model_numeration_init}'
            this_model_init = deff_sequence.get(f'{model_name_sequenced_init}')
            this_model_init_parent = this_model_init.get('Parent')
            if this_model_init_parent != 'Main':
                for parent_numeration in range(0, total_objects_in_deff):
                    parent_location = f'{parent_numeration}'
                    this_model_looking_parent = deff_sequence.get(f'{parent_location}')
                    name_parent = this_model_looking_parent.get('Name')
                    if this_model_init_parent == name_parent:
                        parent_position = this_model_looking_parent.get('RelativePosition')
                        parent_rotation = this_model_looking_parent.get('RelativeRotation')
                        parent_scale = this_model_looking_parent.get('RelativeScale')
                        parent_data_init = {f'{name_parent}': {'InitPosition': parent_position, 'InitRotation': parent_rotation, 'InitScale': parent_scale}}
                        parent_data.update(parent_data_init)
    
        model_data: dict = {}
        texture_data: dict = {}
        for this_model_numeration in range(0, total_objects_in_deff):
            model_name_sequenced = f'{this_model_numeration}'
            this_model = deff_sequence.get(f'{model_name_sequenced}')
            # Basic Model Properties
            this_model_name = this_model.get('Name')#
            this_model_parent = this_model.get('Parent')#
            this_model_file = this_model.get('File')#
            this_model_file_type = this_model.get('FileType')#
            this_model_texture = this_model.get('Texture')#
            # Animation Properties
            this_model_anim_files = this_model.get('AnimFiles')# TODO: NOT IMPLEMENTED YET
            this_model_frame_start = this_model.get('FrameStart')#
            this_model_frame_end = this_model.get('FrameEnd')#
            # "If This Model is a Particle" Properties
            this_model_count = this_model.get('Count')#
            this_model_particle_type = this_model.get('ParticleType')# NOT USED ATM
            this_model_simulation_type = this_model.get('SimulationType')#
            this_model_lifespan = this_model.get('Lifespan')# NOT USED ATM
            # Transforms and Color Properties
            this_model_relative_position = this_model.get('RelativePosition')#
            this_model_relative_rotation = this_model.get('RelativeRotation')#
            this_model_relative_scale = this_model.get('RelativeScale')#
            this_model_relative_color = this_model.get('RelativeColor')#
            this_model_relative_scale_color = this_model.get('RelativeScaleColor')# This is like Relative Color or what? let's check it out ;)
            this_model_scale_factor = this_model.get('ScaleFactor')#
            
            """
            Here i will calculate the relative position, rotation and scale to parent
            Taking in account the initial Parent position is 0, 0, 0
            """
            current_parent_data = parent_data.get(f'{this_model_parent}')
            current_position = current_parent_data.get(f'InitPosition')
            current_rotation = current_parent_data.get(f'InitRotation')
            current_scale = current_parent_data.get(f'InitScale')

            new_position = self.calculate_relative_position(parent_position=current_position, relative_position=this_model_relative_position)
            new_rotation = self.calculate_relative_rotation(parent_rotation=current_rotation, relative_rotation=this_model_relative_rotation)
            new_scale = self.calculate_relative_scale(parent_scale=current_scale, relative_scale=this_model_relative_scale)
            # Precalculated Transforms take the LOC/ROT/SCALE Data which is already calculated taking in account the Parent
            pre_calculated_transforms = {'Translation': new_position, 'Rotation': new_rotation, 'Scale': new_scale}

            """
            File Type Discriminator, there are various types of files and will be processed depending on this type
            take in account that exist various file types:
            StaticTMD, AnimatedTMD-SAF, AnimatedTMD-CMB, AnimatedTMD-LMB0, ParticleFile, GeneratedParticle,
            SAF, CMB, LMB0, LMB1, LMB2. -> This last if not embedded are processed in AnimatedTMD with an special option
            ----------------------------------------------------------------------------------------------------------------------------------
            NOTE: Developer note, AnimatedTMD actually are Models with Embedded Animation in the same file container, since
            SC Lead Developer Monoxide said that he won't change that name from SC Code i'll keep it.
            Surely original devs did this to save a little processing time. Embedding short animations into the same file, to later load
            the rest of the animation files if needed.
            ----------------------------------------------------------------------------------------------------------------------------------
            """
            # TODO: ADD AnimatedTMD-SAF, general add to any AnimatedTMD support for multiple files Animation
            # TODO: Implement AnimatedTMD-SAF
            # TODO: check if some options in to-do list for particle_simulation.py could be used.
            model_path = self.sc_folder + deff_path + this_model_file
            current_processed_model: dict = {}

            if this_model_file_type == 'StaticTMD':
                static_model = static_tmd_file.StaticTmd(static_tmd_path=model_path)
                """
                # Static Models also need an "Animation", what i gone to do here is simple... take a total of 6 Keyframes used and fill the data with its static data
                # Keyframes: 0 to 1 will be all Transforms == 0.
                # Keyframes: 2 to 3 will be the Translation/Rotation/Scale of the StaticTmd Model.
                # Keyframes: 4 to 5 will be all Transforms == 0.
                # Because Blender need to be locked at least two consecutive Keyframes to detect that object have a determined Transform.
                # If transform data changes from Frame to Frame Blender will animate them.
                """
                static_model_animation = static_tmd_file.GeneratedAnimation(name=this_model_name, 
                                                                            object_count=static_model.static_model_object_count, 
                                                                            transforms=pre_calculated_transforms, 
                                                                            start_frame=this_model_frame_start, end_frame=this_model_frame_end)
                
                static_model_converted = {f'{this_model_name}': {'ModelData': static_model.processed_static_tmd_model, 'ModelAnimation': static_model_animation.static_anim}}
                current_processed_model.update(static_model_converted)
                
            elif this_model_file_type == 'AnimatedTMD-SAF':
                print('NOT IMPLEMENTED YET')

            elif this_model_file_type == 'AnimatedTMD-CMB':
                animated_model_cmb = animated_tmd_file.TmdEmbeddedAnimation(animated_tmd_path=model_path, anim_type='CMB', 
                                                                            model_name=this_model_name, 
                                                                            start_frame=this_model_frame_start, end_frame=this_model_frame_end)
                
                model_processed_cmb = animated_model_cmb.processed_animated_tmd_model
                animation_processed_cmb = animated_model_cmb.processed_animated_tmd_animation
                final_cmb_dict = {f'{this_model_name}': {'ModelData': model_processed_cmb, 'ModelAnimation': animation_processed_cmb}}
                current_processed_model.update(final_cmb_dict)

            elif this_model_file_type == 'AnimatedTMD-LMB0':
                animated_model_lmb0 = animated_tmd_file.TmdEmbeddedAnimation(animated_tmd_path=model_path, anim_type='LMB', 
                                                                             model_name=this_model_name, 
                                                                             start_frame=this_model_frame_start, end_frame=this_model_frame_end)
                
                model_processed_lmb = animated_model_lmb0.processed_animated_tmd_model
                animation_processed_lmb = animated_model_lmb0.processed_animated_tmd_animation
                final_lmb_dict = {f'{this_model_name}': {'ModelData': model_processed_lmb, 'ModelAnimation': animation_processed_lmb}}
                current_processed_model.update(final_lmb_dict)

            elif (this_model_file_type == 'ParticleFile') and (self.convert_particles == True):
                """
                # Pretty Much as done for Static Models, the difference is Keyframes are not Static, but always have 2 Keyframes at start with Transforms set at 0
                # At the end the same, will be two Keyframes with transforms set at 0.
                # Keyframes: N0 to N1 will be all Transforms == 0.
                # Keyframes: AnimatedStart to AnimatedEnd will be the Translation/Rotation/Scale of the StaticTmd Model.
                # Keyframes: NEnd-1 to NEnd will be all Transforms == 0.
                # Because Blender need to be locked at least two consecutive Keyframes to detect that object have a determined Transform.
                # If transform data changes from Frame to Frame Blender will animate them.
                """
                animated_particle_file = particle_file.ParticleFile(particle_path=model_path, particle_count=this_model_count, particle_name=this_model_name, 
                                                                    relative_color=this_model_relative_color, scale_factor=this_model_scale_factor)
                
                get_particle_get_simulation = particle_simulation.Simulation(particle_name=this_model_name, 
                                                                             simulation_type=this_model_simulation_type, 
                                                                             precalculated_transforms=pre_calculated_transforms, 
                                                                             start_frame=this_model_frame_start, 
                                                                             end_frame=this_model_frame_end, 
                                                                             count=this_model_count)
                
                final_particlefile_dict = {f'{this_model_name}': {'ModelData': animated_particle_file.generated_particle, 'ModelAnimation': get_particle_get_simulation.animation_baked}}
                current_processed_model.update(final_particlefile_dict)
                
            elif (this_model_file_type == 'GeneratedParticle') and (self.convert_particles == True):
                """
                # Pretty Much as done for Static Models, the difference is Keyframes are not Static, but always have 2 Keyframes at start with Transforms set at 0
                # At the end the same, will be two Keyframes with transforms set at 0.
                # Keyframes: N0 to N1 will be all Transforms == 0.
                # Keyframes: AnimatedStart to AnimatedEnd will be the Translation/Rotation/Scale of the StaticTmd Model.
                # Keyframes: NEnd-1 to NEnd will be all Transforms == 0.
                # Because Blender need to be locked at least two consecutive Keyframes to detect that object have a determined Transform.
                # If transform data changes from Frame to Frame Blender will animate them.
                """
                particle_generated = generated_particles.GeneratedParticle(name=this_model_name, type=this_model_simulation_type, count=this_model_count, 
                                                                           transforms=pre_calculated_transforms, relative_scale_color=this_model_relative_scale_color)
                
                particle_generate_animation = particle_simulation.Simulation(particle_name=this_model_name, 
                                                                             simulation_type=this_model_simulation_type, 
                                                                             precalculated_transforms=pre_calculated_transforms, 
                                                                             start_frame=this_model_frame_start, 
                                                                             end_frame=this_model_frame_end, 
                                                                             count=this_model_count)
                
                final_generatedparticle_dict = {f'{this_model_name}': {'ModelData': particle_generated.particles_generated, 'ModelAnimation': particle_generate_animation.animation_baked}}
                current_processed_model.update(final_generatedparticle_dict)

            else:
                print(f'ERROR-FILETYPE: {this_model_file_type}, not recognized, closing tool to prevent further errors...')
                exit()
            
            model_data.update(current_processed_model)
    
        # Here start the Readable Format into glTF
        new_deff_gltf = deff_object_compile_gltf.NewGltfDeff(deff_name=change_deff_name, data_to_convert=model_data, deff_total_frames=deff_total_frames)
        for this_gltf_key_name in new_deff_gltf.gltf_format:
            this_gltf_to_convert = new_deff_gltf.gltf_format.get(f'{this_gltf_key_name}')
            gltf_converted = deff_gltf_writer.gltfFile(gltf_to_convert=this_gltf_to_convert, gltf_file_name=change_deff_name, gltf_deploy_path=new_folders.new_deploy_path)

        # Here start the Texture Conversion
        if this_model_texture != 'NONE':
                texture_folder_creation_name = this_model_name + f'_texture' # TODO: add this to the final folder for texture conversion
                texture_path = f'{self.sc_folder}{deff_textures_path}{this_model_texture}'
                texture_output_properties = {'FileNesting': f'{change_selected_names}, {this_model_name}', 'TextureFolderOutput': texture_folder_creation_name}
                texture_properties = {f'{this_model_name}': {'Name': this_model_name, 'TexturePath': texture_path, 'TextureOutputPathProperties': texture_output_properties}}
                texture_data.update(texture_properties)


    def calculate_relative_position(self, parent_position=list, relative_position=list) -> list:
        """
        Calculate Relative Position:\n
        Will calculate Model Position based in the current Parent Position\n
        Simple equation ParentDistance + ModelRelative = CurrentPosition.
        """
        final_position: list = []
        final_position_x = parent_position[0] + relative_position[0]
        final_position_y = parent_position[1] + relative_position[1]
        final_position_z = parent_position[2] + relative_position[2]

        final_position = [final_position_x, final_position_y, final_position_z]

        return final_position

    def calculate_relative_rotation(self, parent_rotation=list, relative_rotation=list) -> list:
        """
        Calculate Relative Rotation:\n
        Will calculate Model Rotation based in the current Parent Rotation\n
        """
        final_rotation: list = []
        final_rotation_x = parent_rotation[0] + relative_rotation[0]
        final_rotation_y = parent_rotation[1] + relative_rotation[1]
        final_rotation_z = parent_rotation[2] + relative_rotation[2]

        final_rotation = [final_rotation_x, final_rotation_y, final_rotation_z]

        return final_rotation

    def calculate_relative_scale(self, parent_scale=list, relative_scale=list) -> list:
        """
        Calculate Relative Scale:\n
        Will calculate Model Scale based in the current Parent Scale\n
        so if the Scale of the Parent is 1 and the Model size is 0.1 and it's Relative Scale is 0.1\n
        final Model size is 0.01.\n
        Anyhow this is good when you need to scale all the objects in group.
        """
        final_scale: list = []
        final_scale_x = parent_scale[0] * relative_scale[0]
        final_scale_y = parent_scale[1] * relative_scale[1]
        final_scale_z = parent_scale[2] * relative_scale[2]

        final_scale = [final_scale_x, final_scale_y, final_scale_z]

        return final_scale