"""

Sprite File: This module will take the Sprite Objects Data, 
process it for generating the Particles

Copyright (C) 2024 DooMMetaL

"""

from deff_handlers import particle_mesh
from deff_handlers import particle_simulation

class Sprite:
    def __init__(self, sprite_binary=bytes, sprite_properties=dict, parent_transforms=dict, all_particles_properties=dict) -> None:
        """Take the Sprite Data to generate the Sprite Effects from scratch"""
        self.sprite_binary = sprite_binary
        self.sprite_properties = sprite_properties
        self.parent_transforms = parent_transforms
        self.all_particles_properties = all_particles_properties
        self.sprite_processed_data: dict = {}
        self.process_sprite()
    
    def process_sprite(self):
        final_sprite: dict = {}
        texture_properties: dict = {}

        get_sprite_offset = int.from_bytes(self.sprite_binary[8:12], byteorder='little', signed=False)
        sprite_data = self.sprite_binary[get_sprite_offset:]
        texture_u = int.from_bytes(sprite_data[0:2], byteorder='little', signed=False) / 256
        texture_v = int.from_bytes(sprite_data[2:4], byteorder='little', signed=False) / 256
        texture_width = int.from_bytes(sprite_data[4:6], byteorder='little', signed=False)
        texture_height = int.from_bytes(sprite_data[6:8], byteorder='little', signed=False)
        texture_clut_x = int.from_bytes(sprite_data[8:10], byteorder='little', signed=False)
        texture_clut_y = int.from_bytes(sprite_data[10:12], byteorder='little', signed=False)
        texture_properties: dict = {'U': texture_u, 'V': texture_v}

        # Generate meshes Objects for Particles
        quad_particles = particle_mesh.Quad(generate_particle_properties=self.sprite_properties, particle_texture=texture_properties)

        # Generate Animations for the generated particles
        particles_simulation = particle_simulation.Simulation(simulation_properties=self.sprite_properties, parent_transforms=self.parent_transforms)