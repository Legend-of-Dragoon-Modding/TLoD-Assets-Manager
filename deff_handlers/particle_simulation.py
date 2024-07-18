"""

Particle Simulation: This module contains various classes which are designed
to simulate the particle systems and bake Animations, keep in mind,
this Animations are not RETAIL, but i try to replicate the seen in TLoD DEFFs.

Copyright (C) 2024 DooMMetaL

"""
import math
from random import randint, uniform, normalvariate

class Simulation:
    def __init__(self, simulation_properties=dict, parent_transforms=dict) -> None:
        """Simulate various kinds of Particles behaviors seen on TLoD"""
        self.simulation_properties = simulation_properties
        self.parent_transforms = parent_transforms
        self.animation_baked: dict = {}
        self.simulate_system()
    
    def simulate_system(self):
        this_animation: dict = {}
        # Position (Location), Rotation, Scale to the Parent will be calculated in the SimulationData!!
        processing_animation = SimulationData(process_particle_data=self.simulation_properties, parent_transforms=self.parent_transforms)

        simulation_type = self.simulation_properties.get(f'SimType')
        if simulation_type == 'ExplodeFrontUniform':
            explode_type_0_simulation = ExplosionFrontUniform(process_data=processing_animation.simulation_data_compiled)
        elif simulation_type == 'ExplodeFrontNonUniform':
            explode_type_1 = ExplosionFrontNonUniform(process_data=processing_animation.simulation_data_compiled)
        elif simulation_type == 'RevolvingLinearIncrement':
            revolving_type_0 = RevolvingLinearIncrement(process_data=processing_animation.simulation_data_compiled)
        elif simulation_type == 'Pulsation':
            pulsation_type_0 = PulsationScale(process_data=processing_animation.simulation_data_compiled)
        elif simulation_type == 'ExplosionByObject':
            """
            [I have a serious problem in here, since this simulation depends on the first Vertex positioning
            to be the placement for it, now, i have to take that value somehow] ????
            FUTURE ME - IM A LIAR AND A SERIOUS DUMB, EVERYTHING IS PASSED BY THE REL_LOC VALUE PFFF
            """
            pass
        elif simulation_type == 'ExplodingSphere':
            pass
        else:
            print(f'FATAL ERROR: Simulation Type {simulation_type} not recognised!!')
            print(f'Report this Error as Simulation Type not recongnised, closing the tool...')
            exit()

class ExplosionFrontUniform:
    def __init__(self, process_data=dict) -> None:
        """
        Expand Particles Front Uniform Emission:\n
        Particles are expanded evenly (Uniform emission) from the Center using a random Angle.\n
        If particle is set to Random the Acceleration will be changing doing a little final speed randomness.\n
        Particles are emitted from Center and expand until last frame is reach.
        """
        self.process_data = process_data
        self.generated_animation: dict = {}
        self.simulate_explosion()
    
    def simulate_explosion(self):
        frames = self.process_data.get(f'Frames')
        particle_count = self.process_data.get(f'Count')
        particle_initial_location = self.process_data.get(f'Location')
        particle_initial_rotation = self.process_data.get(f'Rotation')
        particle_initial_scale = self.process_data.get(f'Scale')

        # Set a starting Pseudo Random Number to the Angle of a travelling Particle for each particle
        generated_angles: list = []
        for current_particle in range(0, particle_count):
            random_angle = randint(a=0, b=359)
            random_m = math.tan(random_angle)
            generated_angles.append(random_m)

        distance_factor = 0.1 # TODO: I can use this to set different factor if needed in the future
        # Calculate the movement of each frame for each particle and it's parent location, rotation and scale
        processed_particles: dict = {}
        distance_travelled = 0.0
        for current_frame_number in range(0, frames):
            this_frame_dict: dict = {}
            for current_particle_number in range(0, particle_count):
                this_object_dict: dict = {}
                get_particle_angle = generated_angles[current_particle_number]
                values_xy = Vector.get_xy_vector(current_distance=distance_travelled, current_angle=get_particle_angle)
                x = values_xy[0]
                y = values_xy[1]
                vector_x = 0.0 + particle_initial_location[0]
                vector_y = 0.0 + particle_initial_location[1]
                vector_z = 0.0 + particle_initial_location[2]
                if current_frame_number != 0:
                    vector_x = x * math.sin(random_m) + particle_initial_location[0]
                    vector_y = y * math.cos(random_m) + particle_initial_location[1]
                    vector_z = 0.0 + particle_initial_location[1]
                
                rottransscale_dict = {"Rx": round(particle_initial_rotation[0], 12), "Ry": round(particle_initial_rotation[1], 12), "Rz": round(particle_initial_rotation[2], 12), 
                                      "Tx": round(vector_x, 12), "Ty": round(vector_y, 12), "Tz": round(vector_z, 12), 
                                      "Sx": round(particle_initial_scale[0], 12), "Sy": round(particle_initial_scale[1], 12), "Sz": round(particle_initial_scale[2], 12)}
                
                this_object_dict = {f'Particle_Number_{current_particle_number}': rottransscale_dict}
                this_frame_dict.update(this_object_dict)
            
            build_keyframe_dict: dict = {f'Frame_{current_frame_number}': this_frame_dict}
            distance_travelled += distance_factor
            processed_particles.update(build_keyframe_dict)
        
        self.generated_animation = processed_particles

class ExplosionFrontNonUniform:
    def __init__(self, process_data=dict) -> None:
        """
        Expand Particles Front Non-Uniform Emission:\n
        Particles are expanded unevenly (with a random factor emission) from the Center using a random Angle.\n
        If particle is set to Random the Acceleration will be changing doing a little final speed randomness.\n
        Particles are emitted from Center and expand until last frame is reach.
        """
        self.process_data = process_data
        self.generated_animation: dict = {}
        self.simulate_explosion()
    
    def simulate_explosion(self):
        frames = self.process_data.get(f'Frames')
        particle_count = self.process_data.get(f'Count')
        particle_initial_location = self.process_data.get(f'Location')
        particle_initial_rotation = self.process_data.get(f'Rotation')
        particle_initial_scale = self.process_data.get(f'Scale')

        distance_factor = 0.1 # TODO: I can use this to set different factor if needed in the future

        # Set a starting Pseudo Random Number to the Angle of a travelling Particle for each particle
        generated_angles: list = []
        for current_particle in range(0, particle_count):
            random_angle = randint(a=0, b=359)
            random_m = math.tan(random_angle)
            generated_angles.append(random_m)

        # Set a starting Pseudo Random Number to the frame in which the Simulation Starts
        generated_start_simulation: dict = {}
        for current_particle in range(0, particle_count):
            random_start = randint(a=0, b=frames)
            generated_start_simulation.update({f'Particle_{current_particle}': random_start})

        # Calculate the movement of each frame for each particle and it's parent location, rotation and scale
        processed_particles: dict = {}
        distance_travelled = 0.0
        for current_frame_number in range(0, frames):
            this_frame_dict: dict = {}
            for current_particle_number in range(0, particle_count):
                this_particle_starts = generated_start_simulation.get(f'Particle_{current_particle_number}')
                this_object_dict: dict = {}
                get_particle_angle = generated_angles[current_particle_number]
                values_xy = Vector.get_xy_vector(current_distance=distance_travelled, current_angle=get_particle_angle)
                x = values_xy[0]
                y = values_xy[1]
                vector_x = 0.0 + particle_initial_location[0]
                vector_y = 0.0 + particle_initial_location[1]
                vector_z = 0.0 + particle_initial_location[2]
                if (current_frame_number == 0) and (this_particle_starts == 0):
                    vector_x = 0.0 + particle_initial_location[0]
                    vector_y = 0.0 + particle_initial_location[1]
                    vector_z = 0.0 + particle_initial_location[2]
                    distance_travelled += distance_factor
                elif (current_frame_number >= 1) and (this_particle_starts >= current_frame_number):
                    vector_x = x * math.sin(random_m) + particle_initial_location[0]
                    vector_y = y * math.cos(random_m) + particle_initial_location[1]
                    vector_z = 0.0 + particle_initial_location[2]
                    distance_travelled += distance_factor
                
                rottransscale_dict = {"Rx": round(particle_initial_rotation[0], 12), "Ry": round(particle_initial_rotation[1], 12), "Rz": round(particle_initial_rotation[2], 12), 
                                      "Tx": round(vector_x, 12), "Ty": round(vector_y, 12), "Tz": round(vector_z, 12), 
                                      "Sx": round(particle_initial_scale[0], 12), "Sy": round(particle_initial_scale[0], 12), "Sz": round(particle_initial_scale[0], 12)}
                
                this_object_dict = {f'Particle_Number_{current_particle_number}': rottransscale_dict}
                this_frame_dict.update(this_object_dict)
            
            build_keyframe_dict: dict = {f'Frame_{current_frame_number}': this_frame_dict}
            processed_particles.update(build_keyframe_dict)
            if (current_frame_number == 0) and (this_particle_starts == 0):
                    distance_travelled += distance_factor
            elif (current_frame_number >= 1) and (this_particle_starts >= current_frame_number):
                distance_travelled += distance_factor
        self.generated_animation = processed_particles

class RevolvingLinearIncrement:
    def __init__(self, process_data=dict) -> None:
        """
        Twister like Effect - Revolving Particles Linear Increment:\n
        Particles are emitted evenly from the start position in a Radius1 and 
        windwhirl until they reach the Final Frame. 
        
        Distance it's used as Y Value (Height)
        """
        self.process_data = process_data
        self.generated_animation: dict = {}
        self.simulate_windwhirl()
    
    def simulate_windwhirl(self) -> None:
        
        frames = self.process_data.get(f'Frames')
        particle_count = self.process_data.get(f'Count')
        particle_initial_location = self.process_data.get(f'Location')
        particle_initial_rotation = self.process_data.get(f'Rotation')
        particle_initial_scale = self.process_data.get(f'Scale')

        distance_factor = 0.1 # TODO: I can use this to set different factor if needed in the future
        inner_radius = 0.01 # TODO: I can use this to set different inner radius if needed in the future

        # Set a starting Pseudo Random Number to the Angle of a travelling Particle for each particle
        generated_angles: list = []
        for current_particle_random_angle in range(0, particle_count):
            random_angle = uniform(a=0.0, b=(math.pi * 2)) # Set a starting Pseudo Random Number to the Angle of a travelling Particle in the Inner Radius
            generated_angles.append(random_angle)
        
        generated_positions: dict = {}
        for current_particle_random_position in range(0, particle_count):
            this_x_initializer = math.cos(generated_angles[current_particle_random_position]) * inner_radius
            this_y_initializer = math.sin(generated_angles[current_particle_random_position]) * inner_radius
            this_particle_start = {f'Particle_{current_particle_random_position}': {'X Start': this_x_initializer, 'Y Start': this_y_initializer}}
            generated_positions.update(this_particle_start)

        # Calculate the movement of each frame for each particle and it's parent location, rotation and scale
        processed_particles: dict = {}
        distance_travelled = 0.0
        for current_frame in range(0, frames):
            """X: Cos(Alpha), Z: Sen(Alpha), TAN: Sen(Alpha)/Cos(Alpha), in this case swap Y by Z because i do positioning as 2D graphic
            instead of using a full 3D Matrix [sorry i'm lazy -.-"]"""
            this_frame_dict: dict = {}
            for current_particle in range(0, particle_count):
                this_particle_init = generated_positions.get(f'Particle_{current_particle}')
                random_x_init = this_particle_init.get(f'X Start')
                random_z_init = this_particle_init.get(f'Y Start')
                get_rotation_y = Vector.set_object_rotation_y(current_angle=generated_angles[current_particle]) + particle_initial_rotation[2]
                if current_frame == 0:
                    random_x = random_x_init + particle_initial_location[0]
                    random_z = random_z_init + particle_initial_location[2]
                elif current_frame >= 1 and (current_frame <= (frames // 2)):
                    random_x = random_x_init + math.cos(distance_travelled) + particle_initial_location[0]
                    random_z = random_z_init + math.sin(distance_travelled) + particle_initial_location[2]
                elif (current_frame >= (frames // 2)):
                    random_x = random_x_init + math.cos(distance_travelled) + particle_initial_location[0]
                    random_z = random_z_init + math.sin(distance_travelled) + particle_initial_location[2]

                rottransscale_dict = {"Rx": round(particle_initial_rotation[0], 12), "Ry": round(get_rotation_y, 12), "Rz": round(particle_initial_rotation[2], 12), 
                                      "Tx": round(random_x, 12), "Ty": round(particle_initial_location[1], 12), "Tz": round(random_z, 12), 
                                      "Sx": round(particle_initial_scale[0], 12), "Sy": round(particle_initial_scale[1], 12), "Sz": round(particle_initial_scale[2], 12)}
                
                this_object_dict = {f'Particle_Number_{current_particle}': rottransscale_dict}
                this_frame_dict.update(this_object_dict)

            build_keyframe_dict: dict = {f'Frame_{current_frame}': this_frame_dict}
            processed_particles.update(build_keyframe_dict)
            distance_travelled += distance_factor

        self.generated_animation = processed_particles

class RevolvingNonLinerIncrement:
    def __init__(self, process_data=dict) -> None:
        #TODO: NEED TO CHECK AND REFACTOR THE CODE TO MATCH KEYFRAME->OBJECT
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

class PulsationScale:
    def __init__(self, process_data=dict) -> None:
        """
        Heartbeat like Effect - Pulsation:\n
        Particles will Scale in their Axis evenly,
        until they reach the Final Frame.
        """
        self.process_data = process_data
        self.generated_animation: dict = {}
        self.pulsation()
    
    def pulsation(self):
        frames = self.process_data.get(f'Frames')
        particle_count = self.process_data.get(f'Count')
        particle_initial_location = self.process_data.get(f'Location')
        particle_initial_rotation = self.process_data.get(f'Rotation')
        particle_initial_scale = self.process_data.get(f'Scale')

        frames_adjusted: int = 0
        if frames % 2 == 0:
            frames_adjusted = frames + 2
        else:
            frames_adjusted = frames + 1
        
        pulsation_count = 2 # TODO i can use this to set different counts if needed in the future
        pulsation_times = frames // pulsation_count # will be 2 pulses by the total of frames

        half_anim = frames // 2
        
        scale_factor = 2 # TODO i can use this to set different counts if needed in the future
        max_scale_x = particle_initial_scale[0] * scale_factor
        max_scale_y = particle_initial_scale[1] * scale_factor
        max_scale_z = particle_initial_scale[2] * scale_factor

        add_subtract_scale_x = max_scale_x / pulsation_times
        add_subtract_scale_y = max_scale_y / pulsation_times
        add_subtract_scale_z = max_scale_z / pulsation_times

        processed_particles: dict = {}
        particle_scale_x: float = particle_initial_scale[0]
        particle_scale_y: float = particle_initial_scale[1]
        particle_scale_z: float = particle_initial_scale[2]
        last_value: list = [0.0, 0.0, 0.0]
        for current_frame in range(0, frames_adjusted):
            final_scale_x: float = 0.0
            final_scale_y: float = 0.0
            final_scale_z: float = 0.0
            this_keyframe: dict = {}
            for current_particle in range(0, particle_count):
                """I will leave the debug prints, since i'm not sure that this algorithm will do the trick always"""
                if current_frame == 0 :
                    final_scale_x = particle_scale_x
                    final_scale_y = particle_scale_y
                    final_scale_z = particle_scale_z
                    #print(current_frame, 'starting', final_scale_x, final_scale_y, final_scale_z)

                elif (current_frame >= 1) and (current_frame <= half_anim):
                    final_scale_x = last_value[0] + add_subtract_scale_x
                    final_scale_y = last_value[1] + add_subtract_scale_y
                    final_scale_z = last_value[2] + add_subtract_scale_z
                    #print(current_frame, 'advancing', final_scale_x, final_scale_y, final_scale_z)
                elif (current_frame > half_anim):
                    final_scale_x = last_value[0] - add_subtract_scale_x
                    final_scale_y = last_value[1] - add_subtract_scale_y
                    final_scale_z = last_value[2] - add_subtract_scale_z
                    #print(current_frame, 'backwarding', final_scale_x, final_scale_y, final_scale_z)
                
                rottransscale_dict = {"Rx": round(particle_initial_rotation[0], 12), "Ry":round(particle_initial_rotation[1], 12), "Rz": round(particle_initial_rotation[2], 12), 
                                      "Tx": round(particle_initial_location[0], 12), "Ty": round(particle_initial_location[1], 12), "Tz": round(particle_initial_location[2], 12), 
                                      "Sx": round(final_scale_x, 12), "Sy": round(final_scale_y, 12), "Sz": round(final_scale_z, 12)}
                
                this_object_dict = {f'Particle_Number_{current_particle}': rottransscale_dict}
                this_keyframe.update(this_object_dict)
            
            if current_frame == 0:
                last_value = [(final_scale_x + add_subtract_scale_x), (final_scale_y + add_subtract_scale_y), (final_scale_z + add_subtract_scale_z)]
            elif current_frame >= 1:
                last_value = [final_scale_x, final_scale_y, final_scale_z]

            build_keyframe_dict: dict = {f'Frame_{current_frame}': this_keyframe}
            processed_particles.update(build_keyframe_dict)
        
        self.generated_animation = processed_particles

class SphereExplosion:
    def __init__(self, process_data=dict) -> None:
        #TODO: NEED TO CHECK AND REFACTOR THE CODE TO MATCH KEYFRAME->OBJECT
        """
        Explosion Particle Sphere: Generate a Uniform Particle Implosion using random points values to set the Origin, \n
        going from Outer Radius to Inner Radius"""
        self.process_data = process_data
        self.generated_animation: dict = {}
        self.sphere_explosion()
    
    def sphere_explosion(self) -> None:
        processed_particles: dict = {}

        frames = self.process_data.get(f'Frames')
        particle_count = self.process_data.get(f'Count')
        particle_initial_location = self.process_data.get(f'Location')
        particle_initial_rotation = self.process_data.get(f'Rotation')
        particle_initial_scale = self.process_data.get(f'Scale')

        outer_radius_factor = 2.0 # TODO: I can use this to set different factor if needed in the future
        inner_radius_factor = 0.5 # TODO: I can use this to set different factor if needed in the future

        distance_step = (outer_radius_factor - inner_radius_factor) / frames
        for current_frame in range(0, frames):

            #SETTING RANDOM POINT FOR X, Y, Z to generate the starting point of the particle
            random_x = normalvariate()
            random_y = normalvariate()
            random_z = normalvariate()

            normalize_value = 1 / math.sqrt(math.pow(random_x, 2) + math.pow(random_y, 2) + math.pow(random_z, 2))
            normalized_x = random_x * normalize_value
            normalized_y = random_y * normalize_value
            normalized_z = random_z * normalize_value

            distance_travelled = inner_radius_factor
            rotation_degrees = 0.0
            for current_object in range(0, particle_count):
                final_x = normalized_x * distance_travelled
                final_y = normalized_y * distance_travelled
                final_z = normalized_z * distance_travelled

                rot_x = uniform(rotation_degrees, ((rotation_degrees + 1) * 2))
                rot_y = uniform(rotation_degrees, ((rotation_degrees + 1) * 2))
                rot_z = uniform(rotation_degrees, ((rotation_degrees + 1) * 2))

                rottransscale_dict = {"Rx": rot_x, "Ry": rot_y, "Rz": rot_z, "Tx": round(final_x, 12), "Ty": round(final_y, 12), "Tz": round(final_z, 12), "Sx": 1, "Sy": 1, "Sz": 1}
                distance_travelled += distance_step
                rotation_degrees += 11.25

class Vector:
    def __init__(self) -> None:
        """Vector Manipulation"""
    
    @staticmethod
    def get_xy_vector(current_distance=float, current_angle=int) -> list: # Thanks to Monoxide for refactoring my code with a simple look of it! thanks a LOT!!
        values: list = []
        x = math.cos(current_angle) * current_distance
        y = math.sin(current_angle) * current_distance

        values = [x, y]
        return values
    
    @staticmethod
    def get_xyz_vector(current_distance=float, current_angle=int) -> list: # TODO why i have this method written??
        values = []
        return values
    
    @staticmethod
    def set_object_rotation_y(current_angle=int):
        rotation_y = 180 - math.degrees(current_angle) - 90
        return rotation_y

class SimulationData:
    def __init__(self, process_particle_data=dict, parent_transforms=dict) -> None:
        self.process_particle_data = process_particle_data
        self.parent_transforms = parent_transforms
        self.simulation_data_compiled: dict = {}
        self.compile_simulation_data()
    
    def compile_simulation_data(self):
        final_simulation_transforms: dict = {}

        simulation_type = self.process_particle_data.get(f'SimType')
        simulation_lifespan_frames = self.process_particle_data.get(f'lifespan')
        simulation_particle_count = self.process_particle_data.get(f'count')

        parent_effect = self.process_particle_data.get(f'parent')
        parent_effect_transforms = self.parent_transforms.get(f'{parent_effect}')
        parent_rel_pos = parent_effect_transforms.get(f'rel_pos')
        parent_rel_rot = parent_effect_transforms.get(f'rel_rot')
        parent_rel_scale = parent_effect_transforms.get(f'rel_scale')

        simulation_pos = self.process_particle_data.get(f'rel_pos')
        simulation_rot = self.process_particle_data.get(f'rel_rot')
        simulation_scale = self.process_particle_data.get(f'rel_scale')

        final_pos_x = float(parent_rel_pos[0] + simulation_pos[0]) / 1000
        final_pos_y = float(parent_rel_pos[1] + simulation_pos[1]) / 1000
        final_pos_z = float(parent_rel_pos[2] + simulation_pos[2]) / 1000

        final_rot_x = float(parent_rel_rot[0] + simulation_rot[0]) / round((4096/360), 12)
        final_rot_y = float(parent_rel_rot[1] + simulation_rot[1]) / round((4096/360), 12)
        final_rot_z = float(parent_rel_rot[2] + simulation_rot[2]) / round((4096/360), 12)

        final_scale_x = float(parent_rel_scale[0] + simulation_scale[0]) / 1000
        final_scale_y = float(parent_rel_scale[1] + simulation_scale[1]) / 1000
        final_scale_z = float(parent_rel_scale[2] + simulation_scale[2]) / 1000

        final_simulation_transforms = {'SimType': simulation_type, 'Frames': simulation_lifespan_frames, 'Count': simulation_particle_count, 
                                       'Location': [final_pos_x, final_pos_y, final_pos_z], 
                                       'Rotation': [final_rot_x, final_rot_y, final_rot_z], 
                                       'Scale': [final_scale_x, final_scale_y, final_scale_z]}
        self.simulation_data_compiled = final_simulation_transforms