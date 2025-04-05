"""

Particle File: This module will take the Particle Data, 
process it for generating the Particles.
-------------------------------------------------------------------------------------------------------------------------
Copyright (C) 2024 DooMMetaL

"""
from deff_handlers import particle_mesh

class ParticleFile:
    def __init__(self, particle_path=str, particle_count=int, particle_name=str, relative_color=list, scale_factor=int) -> None:
        """
        Particle File: Take the Particle File Data to create a package of Particles for the given Effect.
        """
        self.particle_path = particle_path
        self.particle_count = particle_count
        self.particle_name = particle_name
        self.relative_color = relative_color
        self.scale_factor = scale_factor
        self.generated_particle: dict = {}
        self.handle_particle_file()
    
    def handle_particle_file(self) -> None:
        binary_particle_file = self.get_particle_file_data()
        created_particle_data = self.create_particle_data(particle_binary=binary_particle_file)
        create_particle_model_data = particle_mesh.Quad(particle_properties=created_particle_data)

        self.generated_particle = create_particle_model_data.generated_particles

    def get_particle_file_data(self) -> bytes:
        """
        Get Particle File Data:\n
        Take the file Path and Open the Particle File as a Binary Stream.
        """
        particle_file_binary: bytes = b''
        with open(self.particle_path, 'rb') as particle_file:
            particle_file_binary = particle_file.read()
            particle_file.close()

        return particle_file_binary

    def create_particle_data(self, particle_binary=bytes) -> dict:
        """
        Create Particle Data:\n
        Take the Data from the Particle File and Sort it to Generate a Particle.
        """
        final_particle: dict = {}
        get_particle_offset = int.from_bytes(particle_binary[8:12], byteorder='little', signed=False)
        particle_data = particle_binary[get_particle_offset:]

        texture_u = int.from_bytes(particle_data[0:2], byteorder='little', signed=False) / 256
        texture_v = int.from_bytes(particle_data[2:4], byteorder='little', signed=False) / 256
        texture_width = int.from_bytes(particle_data[4:6], byteorder='little', signed=False)
        texture_height = int.from_bytes(particle_data[6:8], byteorder='little', signed=False)
        texture_clut_x = int.from_bytes(particle_data[8:10], byteorder='little', signed=False)
        texture_clut_y = int.from_bytes(particle_data[10:12], byteorder='little', signed=False)
        
        texture_properties: dict = {'U': texture_u, 'V': texture_v, 'TexWidth': texture_width, 'TextHeight': texture_height, 
                                    'TexCLUT_X': texture_clut_x, 'TexCLUT_Y': texture_clut_y}
        
        final_particle = {'Name': self.particle_name, 'Count': self.particle_count, 'TextureProperties': texture_properties, 'RelativeColor': self.relative_color, 'ScaleFactor': self.scale_factor}

        return final_particle
        
