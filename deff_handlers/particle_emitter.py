"""

Particle Emitter: A Class in charge of "simulate" a Particle Emitter,
Doing this way to keep everything kind of "sorted".

Copyright (C) 2025 DooMMetaL
"""

class ParticleEmitter:
    """Just A Base Name -not actually an emitter- Here we do some of Particle Calculations and Selections"""
    def __init__(self, behavior_type=int, count=int, type_id=int, transform_scalar=int, emitter_scalar=int, velocity_scalar=int, inner_stuff=int, parent=str):
        self.behavior_type = behavior_type
        self.count = count
        self.type_id = type_id
        self.transform_scalar = transform_scalar
        self.emitter_scalar = emitter_scalar
        self.velocity_scalar = velocity_scalar
        self.inner_stuff = inner_stuff
        self.parent = parent
        self.particle_data: dict = {}
    
    def create_particle_system(self):
        if self.inner_stuff & 0xff == 0:
            pass

        if self.inner_stuff & 0xff00 == 0:
            pass

        if self.inner_stuff & 0xff0000 == 0:
            pass

        render_type = self.type_id >> 20

        try:
            if render_type == 0:
                # QUAD
                pass
            elif render_type == 1:
                # TMD Particle
                pass
            elif render_type == 2:
                # Line Particle
                pass
            elif render_type == 3:
                # Pixel Particle
                pass
            elif render_type == 4:
                # Definitely not a Line Particle
                pass
            elif render_type == 5:
                # Void Particle
                pass
        except ValueError:
            print(f'Particle of Type: {render_type}, INVALID PARTICLE TYPE')
            print(f'Closing tool to avoid further errors')
            exit()
        
