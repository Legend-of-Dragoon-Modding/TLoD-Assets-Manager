"""

Particle Simulation: This module contains various classes which are designed
to simulate the particle systems and bake Animations, keep in mind,
this Animations are not RETAIL, but i try to replicate the seen in TLoD DEFFs.

Copyright (C) 2024 DooMMetaL

"""
import math
from random import randint, uniform
from numpy import pi

class Simulation:
    def __init__(self, particle_name=str, simulation_type=str, start_frame=int, end_frame=int, precalculated_transforms=dict, count=int) -> None:
        """Simulate various kinds of Particles behaviors seen on TLoD"""
        self.particle_name = particle_name
        self.simulation_type = simulation_type
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.precalculated_transforms = precalculated_transforms
        self.count = count
        self.animation_baked: dict = {}
        self.simulate_system()
    
    def simulate_system(self) -> None:
        this_animation: dict = {}
        processing_animation = SimulationData(calculated_transforms=self.precalculated_transforms)
        """For keyframes in this case we need only 6, since we have 6 states, HidingStart/HidingStartEnd, StartShowing - EndShowing, HidingEnd/HidingEndEnd"""
        # keyframe_resolution: Quantity of keyframes in the total number of frames...
        keyframe_resolution = (self.end_frame - self.start_frame) // 2

        if self.simulation_type == 'ExplodeFrontUniform':
            explode_type_0_simulation = ExplosionFrontUniform(process_data=processing_animation.simulation_data_compiled, name=self.particle_name, 
                                                              count=self.count, keyframe_count=keyframe_resolution, 
                                                              frame_start=self.start_frame, frame_end=self.end_frame)
            
            this_animation.update(explode_type_0_simulation.generated_animation)
        
        elif self.simulation_type == 'ExplodeFrontNonUniform':
            explode_type_1 = ExplosionFrontNonUniform(process_data=processing_animation.simulation_data_compiled, name=self.particle_name, 
                                                      count=self.count, keyframe_count=keyframe_resolution, 
                                                      frame_start=self.start_frame, frame_end=self.end_frame)
            
            this_animation.update(explode_type_1.generated_animation)

        elif self.simulation_type == 'RevolvingLinearIncrement':
            revolving_type_0 = RevolvingLinearIncrement(process_data=processing_animation.simulation_data_compiled, name=self.particle_name, 
                                                        count=self.count, keyframe_count=keyframe_resolution, 
                                                        frame_start=self.start_frame, frame_end=self.end_frame)
            
            this_animation.update(revolving_type_0.generated_animation)

        elif self.simulation_type == 'Pulsation':
            pulsation_type_0 = PulsationScale(process_data=processing_animation.simulation_data_compiled, name=self.particle_name, 
                                              count=self.count, keyframe_count=keyframe_resolution, 
                                              frame_start=self.start_frame, frame_end=self.end_frame)

            this_animation.update(pulsation_type_0.generated_animation)

        elif self.simulation_type == 'Starburst':
            starburst = StarburstPosition(process_data=processing_animation.simulation_data_compiled, name=self.particle_name, 
                                          count=self.count, keyframe_count=keyframe_resolution, 
                                          frame_start=self.start_frame, frame_end=self.end_frame)

            this_animation.update(starburst.generated_animation)

        elif self.simulation_type == 'ExplodingSphere':
            exploding_sphere = SphereExplosion(process_data=processing_animation.simulation_data_compiled, name=self.particle_name, 
                                               count=self.count, keyframe_count=keyframe_resolution, 
                                               frame_start=self.start_frame, frame_end=self.end_frame)
            
            this_animation.update(exploding_sphere.generated_animation)

        else:
            print(f'FATAL ERROR: Simulation Type {self.simulation_type} not recognised!!')
            print(f'Report this Error as Simulation Type not recongnised, closing the tool...')
            exit()
                
        self.animation_baked = this_animation

class ExplosionFrontUniform:
    def __init__(self, process_data=dict, name=str, count=int, keyframe_count=int, frame_start=int, frame_end=int) -> None:
        """
        Expand Particles Front Uniform Emission:\n
        Particles are expanded evenly (Uniform emission) from the Center using a random Angle.\n
        In a kind of 2D Explosion
        """
        self.process_data = process_data
        self.name = name
        self.count = count
        self.keyframe_count = keyframe_count
        self.frame_start = frame_start
        self.frame_end = frame_end
        self.generated_animation: dict = {}
        self.simulate_explosion()
    
    def simulate_explosion(self) -> None:
        particle_initial_location = self.process_data.get(f'Location')
        particle_initial_rotation = self.process_data.get(f'Rotation')
        particle_initial_scale = self.process_data.get(f'Scale')

        particle_initial_location_x = particle_initial_location[0]
        particle_initial_location_y = particle_initial_location[1]
        particle_initial_location_z = particle_initial_location[2]

        particle_initial_rotation_x = particle_initial_rotation[0]
        particle_initial_rotation_y = particle_initial_rotation[1]
        particle_initial_rotation_z = particle_initial_rotation[2]

        particle_initial_scale_x = particle_initial_scale[0]
        particle_initial_scale_y = particle_initial_scale[1]
        particle_initial_scale_z = particle_initial_scale[2]

        # Set a starting Pseudo Random Number to the Angle of a travelling Particle for each particle
        generated_angles = Vector.generate_random_angles_2d(particle_count=self.count)

        distance_factor = 0.2 # I can use this to set different factor if needed in the future
        total_keyframes = self.keyframe_count + 4
        processed_particles: dict = {}
        for current_number_animations in range(0, 1):
            current_animation_name = f'{self.name}_Animation_{current_number_animations}'
            current_animation: dict = {}
            store_objects_animation: dict = {}
            for current_particle_number in range(0, self.count):
                get_particle_angle = generated_angles[current_particle_number]
                this_object_keyframes: dict = {}
                distance_travelled = 0.0
                for current_frame_number in range(0, total_keyframes):
                    values_xy = Vector.get_xy_vector(current_distance=distance_travelled, current_angle=get_particle_angle)
                    x = values_xy[0]
                    y = values_xy[1]
                    vector_x: float = 0.0
                    vector_y: float = 0.0
                    vector_z: float = 0.0
                    rotation_x: float = 0.0
                    rotation_y: float = 0.0
                    rotation_z: float = 0.0
                    scale_x: float = 0.0
                    scale_y: float = 0.0
                    scale_z: float = 0.0
                    if (current_frame_number <= 1) or (current_frame_number >= (total_keyframes - 2)):
                        rotation_x = rotation_y = rotation_z = 0.0
                        vector_x = vector_y = vector_z = 0.0
                        scale_x = scale_y = scale_z = 0.0
                    else:
                        vector_x = x * math.cos(get_particle_angle) + particle_initial_location_x # EYES ON THIS before was random_m which was the last number in the generation
                        vector_y = y * math.sin(get_particle_angle) + particle_initial_location_y # inverted sinX cosY
                        vector_z = particle_initial_location_z
                        rotation_x = particle_initial_rotation_x
                        rotation_y = particle_initial_rotation_y
                        rotation_z = particle_initial_rotation_z
                        scale_x = particle_initial_scale_x
                        scale_y = particle_initial_scale_y
                        scale_z = particle_initial_scale_z
                        distance_travelled += distance_factor
                    
                    rottransscale_dict = {"Rx": rotation_x, "Ry": rotation_y, "Rz": rotation_z, 
                                        "Tx": round(vector_x, 12), "Ty": round(vector_y, 12), "Tz": round(vector_z, 12), 
                                        "Sx": scale_x, "Sy": scale_y, "Sz": scale_z}
                    this_keyframe = {f'Keyframe_{current_frame_number}': rottransscale_dict}
                    this_object_keyframes.update(this_keyframe)
                this_object_compiled_keyframes = {f'{self.name}_{current_particle_number}': this_object_keyframes}
                store_objects_animation.update(this_object_compiled_keyframes)
            current_animation = {f'{current_animation_name}': {'TotalTransforms': total_keyframes, 'ObjectCount':self.count, 
                                                               'AnimationType': 'SIMULATION', 
                                                               'StartFrame': self.frame_start, 'EndFrame': self.frame_end, 
                                                               'AnimationsData': store_objects_animation}}
            processed_particles.update(current_animation)
        self.generated_animation = processed_particles

class ExplosionFrontNonUniform:
    def __init__(self, process_data=dict, name=str, count=int, keyframe_count=int, frame_start=int, frame_end=int) -> None:
        """
        Expand Particles Front Non-Uniform Emission:\n
        Particles are expanded unevenly (with a random factor emission) from the Center using a random Angle.\n
        If particle is set to Random the Acceleration will be changing doing a little final speed randomness.\n
        Particles are emitted from Center and expand until last frame is reach.
        """
        self.process_data = process_data
        self.name = name
        self.count = count
        self.keyframe_count = keyframe_count
        self.frame_start = frame_start
        self.frame_end = frame_end
        self.generated_animation: dict = {}
        self.simulate_explosion()
    
    def simulate_explosion(self) -> None:
        particle_location = self.process_data.get(f'Location')
        particle_rotation = self.process_data.get(f'Rotation')
        particle_scale = self.process_data.get(f'Scale')

        particle_initial_location_x = particle_location[0]
        particle_initial_location_y = particle_location[1]
        particle_initial_location_z = particle_location[2]

        particle_initial_rotation_x = particle_rotation[0]
        particle_initial_rotation_y = particle_rotation[1]
        particle_initial_rotation_z = particle_rotation[2]

        particle_initial_scale_x = particle_scale[0]
        particle_initial_scale_y = particle_scale[1]
        particle_initial_scale_z = particle_scale[2]

        # Set a starting Pseudo Random Number to the Angle of a travelling Particle for each particle
        generated_angles = Vector.generate_random_angles_2d(particle_count=self.count)

        # Calculate the movement of each frame for each particle and it's parent location, rotation and scale
        processed_particles: dict = {}
        distance_factor = 0.3 #I can use this to set different factor if needed in the future
        total_keyframes = self.keyframe_count + 4
        for current_number_animations in range(0, 1):
            current_animation_name = f'{self.name}_Animation_{current_number_animations}'
            current_animation: dict = {}
            store_objects_animation: dict = {}
            for current_particle_number in range(0, self.count):
                get_particle_angle = generated_angles[current_particle_number]
                this_object_keyframes: dict = {}
                distance_travelled = float(randint(a=1, b=2) / 2)
                for current_frame_number in range(0, total_keyframes):
                    values_xy = Vector.get_xy_vector(current_distance=distance_travelled, current_angle=get_particle_angle)
                    x = values_xy[0]
                    y = values_xy[1]
                    vector_x: float = 0.0
                    vector_y: float = 0.0
                    vector_z: float = 0.0
                    rotation_x: float = 0.0
                    rotation_y: float = 0.0
                    rotation_z: float = 0.0
                    scale_x: float = 0.0
                    scale_y: float = 0.0
                    scale_z: float = 0.0
                    if (current_frame_number <= 1) or (current_frame_number >= (total_keyframes - 2)):
                        rotation_x = rotation_y = rotation_z = 0.0
                        vector_x = vector_y = vector_z = 0.0
                        scale_x = scale_y = scale_z = 0.0
                    else:
                        vector_x = x * math.sin(get_particle_angle) + particle_initial_location_x
                        vector_y = y * math.cos(get_particle_angle) + particle_initial_location_y
                        vector_z = particle_initial_location_z
                        rotation_x = particle_initial_rotation_x
                        rotation_y = particle_initial_rotation_y
                        rotation_z = particle_initial_rotation_z
                        scale_x = particle_initial_scale_x
                        scale_y = particle_initial_scale_y
                        scale_z = particle_initial_scale_z
                        distance_travelled += distance_factor
                    
                    rottransscale_dict = {"Rx": rotation_x, "Ry": rotation_y, "Rz": rotation_z, 
                                        "Tx": vector_x, "Ty": vector_y, "Tz": vector_z, 
                                        "Sx": scale_x, "Sy": scale_y, "Sz": scale_z}
                    
                    this_keyframe = {f'Keyframe_{current_frame_number}': rottransscale_dict}
                    this_object_keyframes.update(this_keyframe)
                this_object_compiled_keyframes = {f'{self.name}_{current_particle_number}': this_object_keyframes}
                store_objects_animation.update(this_object_compiled_keyframes)
            
            current_animation = {f'{current_animation_name}': {'TotalTransforms': total_keyframes, 'ObjectCount':self.count, 
                                                               'AnimationType': 'SIMULATION', 
                                                               'StartFrame': self.frame_start, 'EndFrame': self.frame_end, 
                                                               'AnimationsData': store_objects_animation}}
            processed_particles.update(current_animation)
        self.generated_animation = processed_particles

class RevolvingLinearIncrement:
    def __init__(self, process_data=dict, name=str, count=int, keyframe_count=int, frame_start=int, frame_end=int) -> None:
        """
        Twister like Effect - Revolving Particles Linear Increment:\n
        Particles are emitted evenly from the start position in a Radius1 and 
        windwhirl until they reach the Final Frame. 
        
        Distance it's used as Y Value (Height)
        """
        self.process_data = process_data
        self.name = name
        self.count = count
        self.keyframe_count = keyframe_count
        self.frame_start = frame_start
        self.frame_end = frame_end
        self.generated_animation: dict = {}
        self.simulate_windwhirl()
    
    def simulate_windwhirl(self) -> None:
        particle_initial_location = self.process_data.get(f'Location')
        particle_initial_rotation = self.process_data.get(f'Rotation')
        particle_initial_scale = self.process_data.get(f'Scale')

        particle_initial_location_x = particle_initial_location[0]
        particle_initial_location_y = particle_initial_location[1]
        particle_initial_location_z = particle_initial_location[2]

        particle_initial_rotation_x = particle_initial_rotation[0]
        particle_initial_rotation_y = particle_initial_rotation[1]
        particle_initial_rotation_z = particle_initial_rotation[2]

        particle_initial_scale_x = particle_initial_scale[0]
        particle_initial_scale_y = particle_initial_scale[1]
        particle_initial_scale_z = particle_initial_scale[2]

        # Set a starting Pseudo Random Number to the Angle of a travelling Particle for each particle
        generated_angles = Vector.generate_random_angles_3d(particle_count=self.count)
        # Set a starting Pseudo Random Position for a starting Windwhirl
        inner_radius = 0.5 # I can use this to set different inner radius if needed in the future
        generated_positions  = Vector.generate_random_init_windwhirl(particle_count=self.count, generated_angles=generated_angles, inner_radius=inner_radius)
        distance_factor = 0.3 # I can use this to set different factor if needed in the future
        total_keyframes = self.keyframe_count + 4
        processed_particles: dict = {}
        for current_number_animations in range(0, 1):
            current_animation_name = f'{self.name}_Animation_{current_number_animations}'
            current_animation: dict = {}
            store_objects_animation: dict = {}
            for current_particle_number in range(0, self.count):
                this_particle_init = generated_positions.get(f'Particle_{current_particle_number}')
                this_object_keyframes: dict = {}
                distance_travelled = 0.0
                for current_frame_number in range(0, total_keyframes):
                    """X: Cos(Alpha), Z: Sen(Alpha), TAN: Sen(Alpha)/Cos(Alpha), in this case swap Y by Z because i do positioning as 2D graphic
                    instead of using a full 3D Matrix [sorry i'm lazy -.-"]"""
                    random_x_init = this_particle_init.get(f'X Start')
                    random_z_init = this_particle_init.get(f'Y Start')
                    get_rotation_y = Vector.set_object_rotation_y(current_angle=generated_angles[current_particle_number]) + particle_initial_rotation_y # for some reason this is the Z value?? + particle_initial_rotation[2]
                    vector_y: float = 0.0
                    rotation_x: float = 0.0
                    rotation_z: float = 0.0
                    scale_x: float = 0.0
                    scale_y: float = 0.0
                    scale_z: float = 0.0
                    if (current_frame_number <= 1) or (current_frame_number >= (total_keyframes - 2)):
                        rotation_x = rotation_z = get_rotation_y = 0.0
                        random_x = vector_y = random_z = 0.0
                        scale_x = scale_y = scale_z = 0.0
                    elif (current_frame_number == 2):
                        random_x = random_x_init + particle_initial_location_x
                        random_z = random_z_init + particle_initial_location_z
                        vector_y = particle_initial_location_y
                        rotation_x = particle_initial_rotation_x
                        rotation_z = particle_initial_rotation_z
                        scale_x = particle_initial_scale_x
                        scale_y = particle_initial_scale_y
                        scale_z = particle_initial_scale_z
                        distance_travelled += distance_factor
                    else:
                        random_x = random_x_init + math.cos(distance_travelled) + particle_initial_location_x
                        random_z = random_z_init + math.sin(distance_travelled) + particle_initial_location_z
                        vector_y = particle_initial_location_y
                        rotation_x = particle_initial_rotation_x
                        rotation_z = particle_initial_rotation_z
                        scale_x = particle_initial_scale_x
                        scale_y = particle_initial_scale_y
                        scale_z = particle_initial_scale_z
                        distance_travelled += distance_factor
                    
                    rottransscale_dict = {"Rx": rotation_x, "Ry": get_rotation_y, "Rz": rotation_z, 
                                        "Tx": random_x, "Ty": vector_y, "Tz": random_z, 
                                        "Sx": scale_x, "Sy": scale_y, "Sz": scale_z}
                    
                    this_keyframe: dict = {f'Keyframe_{current_frame_number}': rottransscale_dict}
                    this_object_keyframes.update(this_keyframe)
                this_object_compiled_keyframes = {f'{self.name}_{current_particle_number}': this_object_keyframes}
                store_objects_animation.update(this_object_compiled_keyframes)
            current_animation = {f'{current_animation_name}': {'TotalTransforms': total_keyframes, 'ObjectCount':self.count, 
                                                               'AnimationType': 'SIMULATION', 
                                                               'StartFrame': self.frame_start, 'EndFrame': self.frame_end, 
                                                               'AnimationsData': store_objects_animation}}
            processed_particles.update(current_animation)
        self.generated_animation = processed_particles

class PulsationScale:
    def __init__(self, process_data=dict, name=str, count=int, keyframe_count=int, frame_start=int, frame_end=int) -> None:
        """
        Heartbeat like Effect - Pulsation:\n
        Particles will Scale in their Axis evenly,
        until they reach the Final Frame.
        """
        self.process_data = process_data
        self.name = name
        self.count = count
        self.keyframe_count = keyframe_count
        self.frame_start = frame_start
        self.frame_end = frame_end
        self.generated_animation: dict = {}
        self.pulsation()
    
    def pulsation(self) -> None:
        particle_initial_location = self.process_data.get(f'Location')
        particle_initial_rotation = self.process_data.get(f'Rotation')
        particle_initial_scale = self.process_data.get(f'Scale')

        particle_initial_location_x = particle_initial_location[0]
        particle_initial_location_y = particle_initial_location[1]
        particle_initial_location_z = particle_initial_location[2]

        particle_initial_rotation_x = particle_initial_rotation[0]
        particle_initial_rotation_y = particle_initial_rotation[1]
        particle_initial_rotation_z = particle_initial_rotation[2]

        particle_initial_scale_x = particle_initial_scale[0]
        particle_initial_scale_y = particle_initial_scale[1]
        particle_initial_scale_z = particle_initial_scale[2]

        total_keyframes = self.keyframe_count + 4
        frames_adjusted: int = 0
        if total_keyframes % 2 == 0:
            frames_adjusted = total_keyframes + 2
        else:
            frames_adjusted = total_keyframes + 1
        
        pulsation_count = 2 # i can use this to set different counts if needed in the future
        pulsation_times = total_keyframes // pulsation_count # will be 2 pulses by the total of frames
        half_anim = total_keyframes // 2
        
        scale_factor = 2 #i can use this to set different counts if needed in the future
        max_scale_x = particle_initial_scale_x * scale_factor
        max_scale_y = particle_initial_scale_y * scale_factor
        max_scale_z = particle_initial_scale_z * scale_factor

        add_subtract_scale_x = max_scale_x / pulsation_times
        add_subtract_scale_y = max_scale_y / pulsation_times
        add_subtract_scale_z = max_scale_z / pulsation_times

        processed_particles: dict = {}
        for current_number_animations in range(0, 1):
            current_animation_name = f'{self.name}_Animation_{current_number_animations}'
            current_animation: dict = {}
            store_objects_animation: dict = {}
            last_value: list = [0.0, 0.0, 0.0]
            for current_particle_number in range(0, self.count):
                this_object_keyframes: dict = {}
                for this_keyframe_number in range(0, frames_adjusted):
                    vector_x: float = particle_initial_location_x
                    vector_y: float = particle_initial_location_y
                    vector_z: float = particle_initial_location_z
                    rotation_x: float = particle_initial_rotation_x
                    rotation_y: float = particle_initial_rotation_y
                    rotation_z: float = particle_initial_rotation_z
                    final_scale_x: float = 0.0
                    final_scale_y: float = 0.0
                    final_scale_z: float = 0.0
                    if (this_keyframe_number <= 1) or (this_keyframe_number >= (total_keyframes - 2)):
                        rotation_x = rotation_y = rotation_z = 0.0
                        vector_x = vector_y = vector_z = 0.0
                        final_scale_x = final_scale_y = final_scale_z = 0.0
                    elif (this_keyframe_number >= 2) and (this_keyframe_number <= half_anim):
                        final_scale_x = last_value[0] + add_subtract_scale_x
                        final_scale_y = last_value[1] + add_subtract_scale_y
                        final_scale_z = last_value[2] + add_subtract_scale_z
                    elif (this_keyframe_number > half_anim):
                        final_scale_x = last_value[0] - add_subtract_scale_x
                        final_scale_y = last_value[1] - add_subtract_scale_y
                        final_scale_z = last_value[2] - add_subtract_scale_z

                    rottransscale_dict = {"Rx": rotation_x, "Ry": rotation_y, "Rz": rotation_z, 
                                        "Tx": vector_x, "Ty": vector_y, "Tz": vector_z, 
                                        "Sx": final_scale_x, "Sy": final_scale_y, "Sz": final_scale_z}
                    
                    this_keyframe = {f'Keyframe_{this_keyframe_number}': rottransscale_dict}
                    this_object_keyframes.update(this_keyframe)
                    
                    if (this_keyframe_number >= 2) and (this_keyframe_number <= half_anim):
                        last_value = [(final_scale_x + add_subtract_scale_x), (final_scale_y + add_subtract_scale_y), (final_scale_z + add_subtract_scale_z)]
                    elif (this_keyframe_number > half_anim):
                        last_value = [final_scale_x, final_scale_y, final_scale_z]
            
                this_object_compiled_keyframes = {f'{self.name}_{current_particle_number}': this_object_keyframes}
                store_objects_animation.update(this_object_compiled_keyframes)
            
            current_animation = {f'{current_animation_name}': {'TotalTransforms': total_keyframes, 'ObjectCount':self.count, 
                                                               'AnimationType': 'SIMULATION', 
                                                               'StartFrame': self.frame_start, 'EndFrame': self.frame_end, 
                                                               'AnimationsData': store_objects_animation}}
            processed_particles.update(current_animation)
        
        self.generated_animation = processed_particles

class StarburstPosition:
    def __init__(self, process_data=dict, name=str, count=int, keyframe_count=int, frame_start=int, frame_end=int) -> None:
        """
        Starburst Position:\n
        Put every Triangle of Starburst in their position and Generate an animation of it.
        """
        self.process_data = process_data
        self.name = name
        self.count = count
        self.keyframe_count = keyframe_count
        self.frame_start = frame_start
        self.frame_end = frame_end
        self.generated_animation: dict = {}
        self.position_starburst()

    def position_starburst(self) -> None:
        particle_initial_location = self.process_data.get(f'Location')
        particle_initial_rotation = self.process_data.get(f'Rotation')
        particle_initial_scale = self.process_data.get(f'Scale')

        particle_initial_location_x = particle_initial_location[0]
        particle_initial_location_y = particle_initial_location[1]
        particle_initial_location_z = particle_initial_location[2]

        particle_initial_rotation_x = particle_initial_rotation[0]
        particle_initial_rotation_y = particle_initial_rotation[1]
        particle_initial_rotation_z = particle_initial_rotation[2]

        particle_initial_scale_x = particle_initial_scale[0]
        particle_initial_scale_y = particle_initial_scale[1]
        particle_initial_scale_z = particle_initial_scale[2]

        # Generate an Pseudo Random Angle to be the position of the Starburst Triangle
        generated_angles = Vector.generate_random_angles_2d(particle_count=self.count)

        total_keyframes = self.keyframe_count + 4
        processed_particles: dict = {}
        for current_number_animations in range(0, 1):
            current_animation_name = f'{self.name}_Animation_{current_number_animations}'
            current_animation: dict = {}
            store_objects_animation: dict = {}
            for current_particle_number in range(0, self.count):
                this_object_random_angle = generated_angles[current_particle_number]
                this_object_keyframes: dict = {}
                for current_frame_number in range(0, total_keyframes):
                    vector_x: float = particle_initial_location_x
                    vector_y: float = particle_initial_location_y
                    vector_z: float = particle_initial_location_z
                    rotation_x: float = particle_initial_rotation_x
                    rotation_y: float = particle_initial_rotation_y
                    rotation_z: float = particle_initial_rotation_z
                    scale_x: float = particle_initial_scale_x
                    scale_y: float = particle_initial_scale_y
                    scale_z: float = particle_initial_scale_z
                    if  (current_frame_number <= 1) or (current_frame_number >= (total_keyframes - 2)):
                        rotation_x = rotation_y = rotation_z = 0.0
                        vector_x = vector_y = vector_z = 0.0
                        scale_x = scale_y = scale_z = 0.0
                    else:
                        values_xy = Vector.get_xy_vector(current_distance=0.001, current_angle=this_object_random_angle)
                        # An eye on this vector_x and vector_y... using the last value of random_m when is not what was intended
                        vector_x = values_xy[0] * math.sin(this_object_random_angle) + particle_initial_location_x
                        vector_y = values_xy[1] * math.cos(this_object_random_angle) + particle_initial_location_y
                        rotation_z = particle_initial_rotation_z + (this_object_random_angle - 180)

                    rottransscale_dict = {"Rx": rotation_x, "Ry": rotation_y, "Rz": rotation_z, 
                                        "Tx": vector_x, "Ty": vector_y, "Tz": vector_z, 
                                        "Sx": scale_x, "Sy": scale_y, "Sz": scale_z}
                    
                    this_keyframe: dict = {f'Keyframe_{current_frame_number}': rottransscale_dict}
                    this_object_keyframes.update(this_keyframe)
                this_object_compiled_keyframes = {f'{self.name}_{current_particle_number}': this_object_keyframes}
                store_objects_animation.update(this_object_compiled_keyframes)
            
            current_animation = {f'{current_animation_name}': {'TotalTransforms': total_keyframes, 'ObjectCount':self.count, 
                                                               'AnimationType': 'SIMULATION', 
                                                               'StartFrame': self.frame_start, 'EndFrame': self.frame_end, 
                                                               'AnimationsData': store_objects_animation}}
            processed_particles.update(current_animation)
        self.generated_animation = processed_particles

class SphereExplosion:
    def __init__(self, process_data=dict, name=str, count=int, keyframe_count=int, frame_start=int, frame_end=int) -> None:
        """
        Explosion Particle Sphere: Generate a Uniform Particle Implosion using random points values to set the Origin, \n
        going from Outer Radius to Inner Radius
        """
        self.process_data = process_data
        self.name = name
        self.count = count
        self.keyframe_count = keyframe_count
        self.frame_start = frame_start
        self.frame_end = frame_end
        self.generated_animation: dict = {}
        self.sphere_explosion()
    
    def sphere_explosion(self) -> None:
        particle_initial_location = self.process_data.get(f'Location')
        particle_initial_rotation = self.process_data.get(f'Rotation')
        particle_initial_scale = self.process_data.get(f'Scale')

        particle_initial_location_x = particle_initial_location[0]
        particle_initial_location_y = particle_initial_location[1]
        particle_initial_location_z = particle_initial_location[2]

        particle_initial_rotation_x = particle_initial_rotation[0]
        particle_initial_rotation_y = particle_initial_rotation[1]
        particle_initial_rotation_z = particle_initial_rotation[2]

        particle_initial_scale_x = particle_initial_scale[0]
        particle_initial_scale_y = particle_initial_scale[1]
        particle_initial_scale_z = particle_initial_scale[2]

        this_generated_particles = Vector.generate_random_point_sphere(particle_count=self.count, inner_radius=360)

        distance_step = 0.2 # I can use this to set different factor if needed in the future
        distance_travelled = 0
        total_keyframes = self.keyframe_count + 4
        processed_particles: dict = {}
        for current_number_animations in range(0, 1):
            current_animation_name = f'{self.name}_Animation_{current_number_animations}'
            current_animation: dict = {}
            store_objects_animation: dict = {}
            for current_particle_number in range(0, self.count):
                get_random_data = this_generated_particles.get(f'{current_particle_number}')
                get_x = get_random_data.get('X')
                get_y = get_random_data.get('Y')
                get_z = get_random_data.get('Z')
                this_object_keyframes: dict = {}
                for current_frame_number in range(0, total_keyframes):
                    vector_x: float = 0.0
                    vector_y: float = 0.0
                    vector_z: float = 0.0
                    rotation_x: float = 0.0
                    rotation_y: float = 0.0
                    rotation_z: float = 0.0
                    scale_x: float = 0.0
                    scale_y: float = 0.0
                    scale_z: float = 0.0
                    if (current_frame_number <= 1) or (current_frame_number >= (total_keyframes - 2)):
                        rotation_x = rotation_y = rotation_z = 0.0
                        vector_x = vector_y = vector_z = 0.0
                        scale_x = scale_y = scale_z = 0.0
                    else:
                        rotation_x = particle_initial_rotation_x
                        rotation_y = particle_initial_rotation_y
                        rotation_z = particle_initial_rotation_z
                        vector_x = get_x + distance_travelled + particle_initial_location_x
                        vector_y = get_y + distance_travelled + particle_initial_location_y
                        vector_z = get_z + distance_travelled + particle_initial_location_z
                        scale_x = particle_initial_scale_x
                        scale_y = particle_initial_scale_y
                        scale_z = particle_initial_scale_z
                    
                    rottransscale_dict = {"Rx": rotation_x, "Ry": rotation_y, "Rz": rotation_z, 
                                        "Tx": vector_x, "Ty": vector_y, "Tz": vector_z, 
                                        "Sx": scale_x, "Sy": scale_y, "Sz": scale_z}
                    
                    this_keyframe = {f'Keyframe_{current_frame_number}': rottransscale_dict}
                    this_object_keyframes.update(this_keyframe)
                    distance_travelled += distance_step
                
                this_object_compiled_keyframes = {f'{self.name}_{current_particle_number}': this_object_keyframes}
                store_objects_animation.update(this_object_compiled_keyframes)
            
            current_animation = {f'{current_animation_name}': {'TotalTransforms': total_keyframes, 'ObjectCount':self.count, 
                                                               'AnimationType': 'SIMULATION', 
                                                               'StartFrame': self.frame_start, 'EndFrame': self.frame_end, 
                                                               'AnimationsData': store_objects_animation}}
            processed_particles.update(current_animation)
        
        self.generated_animation = processed_particles

class RevolvingNonLinerIncrement: # NOT IMPLEMENTED YET for some reason
    def __init__(self, process_data=dict) -> None:
        """
        Twister like Effect - Revolving Particles Non Linear Increment:\n
        Particles are emitted unevenly from the start position in a Radius1 and 
        windwhirl until they reach the Final Frame. 
        
        Distance it's used as Y Value (Height)
        """
        self.process_data = process_data
        self.generated_animation: dict = {}
    
    def simulate_random_windwhirl(self) -> None:
        frames = self.process_data.get(f'Frames')
        particle_count = self.process_data.get(f'Count')
        particle_initial_location = self.process_data.get(f'Location')
        particle_initial_rotation = self.process_data.get(f'Rotation')
        particle_initial_scale = self.process_data.get(f'Scale')

        outer_radius_factor = 2.0
        inner_radius_factor = 0.1
        outer_radius_calculation = (outer_radius_factor / frames)

        acceleration_start = 0.1
        acceleration_end = 2.5
        random_acceleration = acceleration_start
        random_acceleration_flag = True

        for current_frame in range(0, frames):
            random_angle = uniform(a=0.0, b=(math.pi * 2)) # Set a starting Pseudo Random Number to the Angle of a travelling Particle in the Inner Radius
            
            distance_travelled = 0.0
            random_x_init = math.cos(random_angle) * inner_radius_factor
            random_z_init = math.sin(random_angle) * inner_radius_factor
            get_rotation_y = Vector.set_object_rotation_y(current_angle=random_angle)
            new_r_angle = random_angle
            outer_radius_sum = 0
            for current_particle in range(0, particle_count):
                
                if random_acceleration_flag == True:
                    current_acceleration = uniform(random_acceleration, acceleration_end)
                else:
                    current_acceleration = 0

                if current_frame == 0:
                    random_x = random_x_init * (outer_radius_calculation)
                    random_z = random_z_init * (outer_radius_calculation)
                else:
                    random_x = math.cos(new_r_angle) * (outer_radius_sum)
                    random_z = math.sin(new_r_angle) * (outer_radius_sum)
                    get_rotation_y = Vector.set_object_rotation_y(current_angle=new_r_angle)

                rottransscale_dict = {"Rx": 0, "Ry": get_rotation_y, "Rz": 0, "Tx": round(random_x, 12), "Ty": round(distance_travelled, 12), "Tz": round(random_z, 12), "Sx": 1, "Sy": 1, "Sz": 1}
                new_r_angle += 0.1
                distance_travelled -= (0.05 * current_acceleration)
                outer_radius_sum += outer_radius_calculation

class Vector:
    def __init__(self) -> None:
        """
        Vector:
        This Class do some of the common Vector Manipulation.\n
        """
    
    @staticmethod
    def get_xy_vector(current_distance=float, current_angle=int) -> list: # Thanks to Monoxide for refactoring my code with a simple look of it! thanks a LOT!!
        """
        Get XY Vector:\n
        Take the Distance and Current Angle and do a calc.\n
        To Know the current X/Y Position of the Object during travelling.
        """
        values: list = []
        x = math.cos(current_angle) * current_distance
        y = math.sin(current_angle) * current_distance

        values = [x, y]
        return values
    
    @staticmethod
    def set_object_rotation_y(current_angle=float) -> float:
        """
        Set Object Rotation Y:\n
        Simply takes the Object rotation and make a 90 degree Rotation to get it facing something.
        """
        rotation_y = 180 - math.degrees(current_angle) - 90
        return rotation_y

    @staticmethod
    def generate_random_angles_2d(particle_count=int) -> list:
        """
        Generate Random Angles 2D:\n
        Generate a Pseudo Random Angle in Circle Shape Type.
        """
        start_angle: list = []
        for current_particle in range(0, particle_count):
            random_angle = randint(a=0, b=359)
            random_m = math.tan(random_angle)
            start_angle.append(random_m)
        return start_angle
    
    @staticmethod
    def generate_random_angles_3d(particle_count=int) -> list:
        """
        Generate Random Angles 3D:\n
        Generate a Pseudo Random Angle in Cylinder Volume Type.
        """
        start_angle: list = []
        for current_particle_random_angle in range(0, particle_count):
            random_angle = uniform(a=0.0, b=(math.pi * 2)) # Set a starting Pseudo Random Number to the Angle of a travelling Particle in the Inner Radius
            start_angle.append(random_angle)
        return start_angle

    @staticmethod
    def generate_random_init_windwhirl(particle_count=int, generated_angles=list, inner_radius=float) -> dict:
        generated_positions: dict = {}
        for current_particle_random_position in range(0, particle_count):
            this_x_initializer = math.cos(generated_angles[current_particle_random_position]) * inner_radius
            this_y_initializer = math.sin(generated_angles[current_particle_random_position]) * inner_radius
            this_particle_start = {f'Particle_{current_particle_random_position}': {'X Start': this_x_initializer, 'Y Start': this_y_initializer}}
            generated_positions.update(this_particle_start)
        
        return generated_positions

    @staticmethod
    def generate_random_point_sphere(particle_count=int, inner_radius=float) -> dict:
        """
        Generate Random Point Sphere:\n
        Generate a starting point for a particle,\n
        placed in a random position in a Sphere Volume, taking in account the inner radius.
        """
        normal_vector = 1000
        random_point_sphere: dict = {}
        for this_particle in range(0, particle_count):
            z_pos = uniform((-inner_radius / normal_vector), (inner_radius / normal_vector))
            phi = uniform((-pi / normal_vector), (pi / normal_vector))
            rxy = math.sqrt(1 - z_pos**2)
            x_pos = rxy * math.cos(phi)
            y_post = rxy * math.sin(phi)
            this_generated_positions = {'X': x_pos, 'Y': y_post, 'Z': z_pos}
            this_generated_particle_start = {f'{this_particle}': this_generated_positions}
            random_point_sphere.update(this_generated_particle_start)
        return random_point_sphere

class SimulationData:
    def __init__(self, calculated_transforms=dict) -> None:
        """
        Simulation Data:\n
        Generate the simulation Data Translation/Rotation/Scale.\n
        Also applying the Transforms relative to the Parent
        """
        self.calculated_transforms = calculated_transforms
        self.simulation_data_compiled: dict = {}
        self.compile_simulation_data()
    
    def compile_simulation_data(self) -> None:
        final_simulation_transforms: dict = {}
        translation = self.calculated_transforms.get('Translation')
        rotation = self.calculated_transforms.get('Rotation')
        scale = self.calculated_transforms.get('Scale')

        final_pos_x = float(translation[0]) / 1000
        final_pos_y = float(translation[1]) / 1000
        final_pos_z = float(translation[2]) / 1000

        final_rot_x = float(rotation[0]) / round((4096/360), 12)
        final_rot_y = float(rotation[1]) / round((4096/360), 12)
        final_rot_z = float(rotation[2]) / round((4096/360), 12)

        # Scale is divided by 4096 instead of 1000? 
        final_scale_x = float(scale[0]) / 4096
        final_scale_y = float(scale[1]) / 4096
        final_scale_z = float(scale[2]) / 4096

        final_simulation_transforms = {'Location': [final_pos_x, final_pos_y, final_pos_z], 
                                       'Rotation': [final_rot_x, final_rot_y, final_rot_z], 
                                       'Scale': [final_scale_x, final_scale_y, final_scale_z]}
        
        self.simulation_data_compiled = final_simulation_transforms