"""

Particle Mesh: This module contains and generate the particles mesh
for the different types used in TLoD Effect:
Quadilateral, Triangles, Rays and "Lines"
About Lines, i will handle them as very stretched Quads because
working with Curves and Lines in Blender is really a mess

Copyright (C) 2024 DooMMetaL

"""

class Quad:
    def __init__(self, generate_particle_properties=dict, particle_texture=dict) -> None:
        self.generate_particle_properties = generate_particle_properties
        self.particle_texture = particle_texture
        self.generated_particles: dict = {}
        self.generate_quad()
    
    def generate_quad(self):
        particle_name = self.generate_particle_properties.get('name')
        particle_count = self.generate_particle_properties.get('count')
        relative_color = self.generate_particle_properties.get('rel_col')
        scale_factor = self.generate_particle_properties.get('scale_factor')

        main_u = self.particle_texture.get('U') - 2
        main_v = self.particle_texture.get('V')
        main_u_negate = main_u - main_u
        main_v_negate = main_v - main_v


        scale_factor = scale_factor / 1000
        relative_color_r = relative_color[0] / 256
        relative_color_g = relative_color[1] / 256
        relative_color_b = relative_color[2] / 256

        this_particle_objects: dict = {}
        for creation in range(0, particle_count):
            this_particle: dict = {}
            particle_new_name = f'Particle_{particle_name}_{creation}'
            vertices = [[(-50 * scale_factor), (50 * scale_factor), 0], [(50 * scale_factor), (50 * scale_factor), 0], [(50 * scale_factor), (-50 * scale_factor), 0], [(-50 * scale_factor), (-50 * scale_factor), 0]]
            normals = [[0, 0, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1]]
            primitives = [{
                f'r0': relative_color_r, f'g0': relative_color_g, f'b0': relative_color_b, f'mode_val': b'\x00\x00', 
                f'u0': main_u, 'v0': main_v, f'u1': main_u, 'v1': main_v_negate, 
                f'u2': main_u_negate, 'v2': main_v, f'u3': main_u_negate, 'v3': main_v_negate, 
                f'normal0': 0, f'vertex0': 3, 
                f'normal1': 1, f'vertex1': 0, 
                f'normal2': 2, f'vertex2': 2,
                f'normal3': 3, f'vertex3': 1}]
            
            this_particle = {f'{particle_new_name}': {'Vertices': vertices, 'Normals': normals, 'Primitives': primitives}}
            this_particle_objects.update(this_particle)
        
        self.generated_particles = this_particle_objects