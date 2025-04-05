"""

Generated Particles:
This module will handle the different Generated Particles.
Difference with the Particle Files is actually that, 
This Particles have no file which guide the creation.
-----------------------------------------------------------
Copyright (C) 2024 DooMMetaL

"""

from deff_handlers import particle_mesh

class GeneratedParticle:
    def __init__(self, name=str, type=str, count=str, transforms=dict, relative_scale_color=dict):
        """
        Generated Particle:\n
        A particle created and based on the type and count.\n
        This particles are generated on the fly, but also have no data written in files, except Script Files.
        """
        self.name = name
        self.type = type
        self.count = count
        self.transforms = transforms
        self.relative_scale_color = relative_scale_color
        self.particles_generated: dict = {}
        self.generate_particle()
    
    def generate_particle(self) -> None:
        """
        Generate Particle:\n
        This will select the type of particle which have to be created,\n
        At the end of the work, the particle will be fully created.
        """
        created_particle: dict = {}

        particle_properties = self.create_particle_properties()
        if self.type == 'Starburst':
            created_starburst = StarBurst(starburst_properties=particle_properties)
            created_particle = created_starburst.starburst_generated
        
        self.particles_generated = created_particle
    
    def create_particle_properties(self) -> dict:
        """
        Create Particle Properties:\n
        Pretty much self explanatory, just take the data needed and feed as Particle Properties.
        """
        final_particle: dict = {}
        rel_color_r = self.relative_scale_color[0] / 256
        rel_color_g = self.relative_scale_color[1] / 256
        rel_color_b = self.relative_scale_color[2] / 256
        relative_color = [rel_color_r, rel_color_g, rel_color_b]

        transform_translation = self.transforms.get('Translation')
        transform_rotation = self.transforms.get('Rotation')
        transform_scale = self.transforms.get('Scale')

        translation_x = round(float(transform_translation[0] / 1000), 12)
        translation_y = round(float(transform_translation[1] / 1000), 12)
        translation_z = round(float(transform_translation[2] / 1000), 12)

        rotation_x = round(float( transform_rotation[0] / (4096/360)), 12)
        rotation_y = round(float( transform_rotation[1] / (4096/360)), 12)
        rotation_z = round(float( transform_rotation[2] / (4096/360)), 12)

        # ATM i will leave the scale as it is
        scale_x = transform_scale[0] #round(float(transform_scale[0] / 4096), 12)
        scale_y = transform_scale[1] #round(float(transform_scale[1] / 4096), 12)
        scale_z = transform_scale[2] #round(float(transform_scale[2] / 4096), 12)

        transforms_final = {'Translation': [translation_x, translation_y, translation_z], 
                            'Rotation': [rotation_x, rotation_y, rotation_z], 
                            'Scale': [scale_x, scale_y, scale_z]}

        final_particle = {'Name': self.name, 'Count': self.count, 'RelativeColor': relative_color, 'Transforms': transforms_final}

        return final_particle

class StarBurst:
    def __init__(self, starburst_properties=dict) -> None:
        """
        StarBurst:\n
        A classic 'Impact' special effect of Starburst... like in additions and some manga...\n
        add some dynamism.
        """
        self.starburst_properties = starburst_properties
        self.starburst_generated: dict = {}
        self.create_starburst()
    
    def create_starburst(self) -> None:
        create_starburst = particle_mesh.Triangle(properties=self.starburst_properties)
        self.starburst_generated = create_starburst.generated_particles
    


class Rays:
    def __init__(self, name=str, count=str, transforms=dict):
        """
        Rays:\n
        A classic Ray that make electricity effects.
        """
        self.name = name
        self.type = type
        self.count = count
        self.transforms = transforms