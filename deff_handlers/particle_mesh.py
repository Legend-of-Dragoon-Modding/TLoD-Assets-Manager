"""

Particle Mesh: This module contains and generate the particles mesh
for the different types used in TLoD Effect:
Quadilateral, Triangles, Rays and "Lines"
About Lines, i will handle them as very stretched Quads because
working with Curves and Lines in Blender is really a mess

Copyright (C) 2024 DooMMetaL

"""

class Quad:
    def __init__(self, particle_properties=dict) -> None:
        """
        Quad: Create the Quads used as particles in Particle Files
        """
        self.particle_properties = particle_properties
        self.generated_particles: dict = {}
        self.generate_quad()
    
    def generate_quad(self):
        """
        Generate Quad:\n
        Generate a Quad Particle for the given Effect
        """
        particle_name = self.particle_properties.get('Name')
        particle_count = self.particle_properties.get('Count')
        particle_texture_properties = self.particle_properties.get('TextureProperties')
        main_u = particle_texture_properties.get('U') - 2
        main_v = particle_texture_properties.get('V')
        main_u_negate = main_u - main_u
        main_v_negate = main_v - main_v
        particle_relative_color = self.particle_properties.get('RelativeColor')
        particle_scale_factor = self.particle_properties.get('ScaleFactor')

        scale_factor = particle_scale_factor / 2
        relative_color_r = particle_relative_color[0] / 256
        relative_color_g = particle_relative_color[1] / 256
        relative_color_b = particle_relative_color[2] / 256

        this_particle_created: dict = {}
        for creation in range(0, particle_count):
            this_particle: dict = {}
            particle_new_name = f'{particle_name}_{creation}'

            vertex = {'Vertex_Number_0': {'VecX': (-1 * scale_factor), 'VecY': (1 * scale_factor), 'VecZ': 0.000}, 
                        'Vertex_Number_1': {'VecX': (1 * scale_factor), 'VecY': (1 * scale_factor), 'VecZ': 0.000},
                        'Vertex_Number_2': {'VecX': (1 * scale_factor), 'VecY': (-1 * scale_factor), 'VecZ': 0.000}, 
                        'Vertex_Number_3': {'VecX': (-1* scale_factor), 'VecY': (-1* scale_factor), 'VecZ': 0.000}}
            
            normal = {'Normal_Number_0': {'VecX': 0, 'VecY': 0, 'VecZ': 1}, 
                        'Normal_Number_1': {'VecX': 0, 'VecY': 0, 'VecZ': 1}, 
                        'Normal_Number_2': {'VecX': 0, 'VecY': 0, 'VecZ': 1}, 
                        'Normal_Number_3': {'VecX': 0, 'VecY': 0, 'VecZ': 1}}

            primitives_num_0 = {'LSC_4Vertex_Gouraud_Texture_Solid_No-Translucent': {f'r0': relative_color_r, f'g0': relative_color_g, f'b0': relative_color_b, f'mode_val': b'\x00\x00', 
                                                                               f'u0': main_u, 'v0': main_v, f'u1': main_u, 'v1': main_v_negate, 
                                                                               f'u2': main_u_negate, 'v2': main_v, f'u3': main_u_negate, 'v3': main_v_negate, 
                                                                               f'normal0': 0, f'vertex0': 3, 
                                                                               f'normal1': 1, f'vertex1': 0, 
                                                                               f'normal2': 2, f'vertex2': 2, 
                                                                               f'normal3': 3, f'vertex3': 1}}
            
            primitives = {'Prim_Num_0': primitives_num_0}
            this_particle = {f'{particle_new_name}': {'Vertex': vertex, 'Normal': normal, 'Primitives': primitives}}
            this_particle_created.update(this_particle)
        
        particle_finished = {'Format': 'TMD_CContainer', 'Data_Table': None, 'Converted_Data': this_particle_created}
        
        self.generated_particles = particle_finished

class Triangle:
    def __init__(self, properties=dict) -> None:
        """
        Generate Triangle:\n
        Create a triangle Mesh, with given parameters
        """
        self.properties = properties
        self.generated_particles: dict = {}
        self.generate_triangles()
    
    def generate_triangles(self) -> None:
        name = self.properties.get('Name')
        count = self.properties.get('Count')
        relative_color = self.properties.get('RelativeColor')

        this_particles_created: dict = {}

        for this_particle_number in range(0, count):
            this_particle: dict = {}
            particle_new_name = f'{name}_{this_particle_number}'
            
            vertex = {'Vertex_Number_0': {'VecX': -0.5, 'VecY': 0.5, 'VecZ': 0.000}, 
                        'Vertex_Number_1': {'VecX': 0.5, 'VecY': 0.5, 'VecZ': 0.000},
                        'Vertex_Number_2': {'VecX': 0.5, 'VecY': -0.5, 'VecZ': 0.000}}
            
            normal = {'Normal_Number_0': {'VecX': 0, 'VecY': 0, 'VecZ': 1}, 
                        'Normal_Number_1': {'VecX': 0, 'VecY': 0, 'VecZ': 1}, 
                        'Normal_Number_2': {'VecX': 0, 'VecY': 0, 'VecZ': 1}}

            primitives_num_0 = { 'LSC_3Vertex_Gradation_No-Texture_No-Translucent': {
                f'r0': relative_color[0], f'g0': relative_color[1], f'b0': relative_color[2], f'mode_val': b'\x00\x00', 
                f'r1': relative_color[0], f'g1': relative_color[1], f'b1': relative_color[2], f'pad0': b'\x00\x00', 
                f'r2': relative_color[0], f'g2': relative_color[1], f'b2': relative_color[2], f'pad1': b'\x00\x00', 
                f'normal0': 0, f'vertex0': 0, 
                f'normal1': 1, f'vertex1': 1, 
                f'normal2': 2, f'vertex2': 2,}}
            
            primitives = {'Prim_Num_0': primitives_num_0}
            this_particle = {f'{particle_new_name}': {'Vertex': vertex, 'Normal': normal, 'Primitives': primitives}}
            this_particles_created.update(this_particle)
        
        particle_finished = {'Format': 'TMD_CContainer', 'Data_Table': None, 'Converted_Data': this_particles_created}
        
        self.generated_particles = particle_finished
