"""

glTF Converter: Convert the model from human readable
to glTF (JSON) [Descriptor] and glTF (Binary Blob) [Buffers]
using the pygltflib or Py glTF Lib which is available at:
https://pypi.org/project/pygltflib/ 
--> Copyright (C) 2018, 2023 Luke Miller

-------------------------------------------------------------------------

code which is not part of pygltflib:
Copyright (C) 2024 DooMMetaL

-------------------------------------------------------------------------

DEVELOPER NOTE: since i'm new at this format expect a lot of non expected
behaviors and code stupidity //SORRY

"""
from pygltflib import *

class gltfFile:
    def __init__(self, gltf_to_convert=dict, gltf_file_name=str, gltf_deploy_path=str) -> None:
        """
        glTF Converter: Convert the model from human readable\n
        to glTF (JSON) [Descriptor] and (Binary Buffer)\n
        using the pygltflib.
        """
        self.gltf_to_convert = gltf_to_convert
        self.gltf_file_name = gltf_file_name
        self.gltf_deploy_path = gltf_deploy_path
        self.convert_gltf()
    
    def convert_gltf(self) -> None:
        """This writes the glTF file and the Binary Buffer file"""
        total_objects_gltf = self.gltf_to_convert.get('ObjectsNumber')
        meshes_gltf = self.gltf_to_convert.get('Meshes')
        binary_buffers_gltf = self.gltf_to_convert.get('Buffers')
        accessors_data_gltf = self.gltf_to_convert.get('Accessors')
        buffersview_gltf = self.gltf_to_convert.get('BufferViews')
        buffer_gltf_total_size = self.gltf_to_convert.get('BufferSizeTotal')
        animation_data = self.gltf_to_convert.get('Animations')
        
        # Setup an empty glTF File
        gltf_file = GLTF2()

        # Setup Asset
        gltf_file.asset.generator = f'TLoD Assets Converter ALPHA 0.1'
        gltf_file.asset.version = f'2.0'
        gltf_file.extensionsUsed = [f'KHR_materials_specular', f'KHR_materials_ior']
        gltf_file.scene = 0
        
        # Setup an Scene
        gltf_scene = Scene()
        gltf_scene.name = 'Scene'
        for this_node in range(0, total_objects_gltf):
            gltf_scene.nodes.append(this_node)
        gltf_file.scenes.append(gltf_scene)
        
        # Setup Nodes
        for this_node_number in range(0, total_objects_gltf):
            gltf_nodes = Node()
            gltf_nodes.mesh = this_node_number
            gltf_nodes.name =  f'{self.gltf_file_name}_ObjNum_{this_node_number}'
            gltf_file.nodes.append(gltf_nodes)

        # Setup Materials - HERE WE ARE IMPLEMENTING VERY BASIC MATERIALS (In future i hope implementing specific materials for each objects)
        for this_object_material in range(0, total_objects_gltf):
            material_gltf = Material()
            material_gltf.doubleSided = True
            material_gltf.extensions = {'KHR_materials_specular': {'specularFactor': 0}, 
                                        'KHR_materials_ior': {'ior': 1.0}}
            material_gltf.name = f'{self.gltf_file_name}_ObjNum_{this_object_material}'
            pbr_settings = PbrMetallicRoughness()
            pbr_settings.baseColorFactor = [0.800000011920929, 0.800000011920929, 0.800000011920929, 1]
            pbr_settings.metallicFactor = 0.0
            pbr_settings.roughnessFactor = 1.0
            material_gltf.pbrMetallicRoughness = pbr_settings
            material_gltf.alphaCutoff = None
            gltf_file.materials.append(material_gltf)

        # Setup Meshes (for each node, since TLoD use object by object Animation) -> And Primitives
        # Maybe i could add a single mesh and each primitives block is represented by an object? who knows
        current_mesh_number = 0
        for this_gltf_mesh in meshes_gltf:
            get_this_object = meshes_gltf.get(f'{this_gltf_mesh}')
            get_this_primitive_attributes = get_this_object.get('attributes')
            gltf_mesh = Mesh()
            gltf_mesh.name = f'{self.gltf_file_name}_ObjNum_{current_mesh_number}'
            gltf_primitive = Primitive()
            gltf_primitive.attributes.POSITION = get_this_primitive_attributes.get('POSITION')
            gltf_primitive.attributes.NORMAL = get_this_primitive_attributes.get('NORMAL')
            gltf_primitive.attributes.TEXCOORD_0 = get_this_primitive_attributes.get('TEXCOORD_0')
            gltf_primitive.attributes.COLOR_0 = get_this_primitive_attributes.get('COLOR_0')
            gltf_primitive.attributes.COLOR_1 = get_this_primitive_attributes.get('COLOR_1')
            gltf_primitive.indices = get_this_object.get('indices')
            gltf_primitive.material = get_this_object.get('material')
            gltf_mesh.primitives.append(gltf_primitive)
            gltf_file.meshes.append(gltf_mesh)
            current_mesh_number += 1
        
        # Setup Accessors
        # POSITION=VEC3 ; NORMAL=VEC3 ; NORMAL=VEC2 ; COLOR_0=VEC4 ; COLOR_1=VEC4 ; index=SCALAR
        for this_object in accessors_data_gltf:
            current_accessors_arrays = accessors_data_gltf.get(f'{this_object}')
            for this_accessor in current_accessors_arrays:
                accessor_gltf = Accessor()
                get_accessor_data = current_accessors_arrays.get(f'{this_accessor}')
                accessor_gltf.bufferView = get_accessor_data.get('bufferView')
                accessor_gltf.componentType = get_accessor_data.get('componentType')
                accessor_gltf.count = get_accessor_data.get('count')
                accessor_gltf.type = get_accessor_data.get('type')
                if get_accessor_data.get('type') == 'VEC4':
                    accessor_gltf.normalized = True
                if get_accessor_data.get('VertexRange') != None:
                    get_vertex_range = get_accessor_data.get('VertexRange')
                    get_maximums = get_vertex_range.get('Maximum')
                    get_minimums = get_vertex_range.get('Minimum')
                    maximum_list = [get_maximums.get('XMax'), get_maximums.get('YMax'), get_maximums.get('ZMax')]
                    minimum_list = [get_minimums.get('XMin'), get_minimums.get('YMin'), get_minimums.get('ZMin')]
                    accessor_gltf.max = maximum_list
                    accessor_gltf.min = minimum_list
                gltf_file.accessors.append(accessor_gltf)
        
        if animation_data != None:
            for animation_name in animation_data:
                this_animation = animation_data.get(f'{animation_name}')
                this_animation_accessors = this_animation.get('AnimAccessors')
                for this_accessor_anim in this_animation_accessors:
                    gltf_anim_accessor = Accessor()
                    anim_accessor = this_animation_accessors.get(f'{this_accessor_anim}')
                    gltf_anim_accessor.bufferView = anim_accessor.get('BufferView')
                    gltf_anim_accessor.componentType = anim_accessor.get('ComponentType')
                    gltf_anim_accessor.count = anim_accessor.get('Count')
                    gltf_anim_accessor.type = anim_accessor.get('Type')
                    if (anim_accessor.get('Min') != None) and (anim_accessor.get('Max') != None):
                        gltf_anim_accessor.min = [anim_accessor.get('Min')]
                        gltf_anim_accessor.max = [anim_accessor.get('Max')]
                    gltf_file.accessors.append(gltf_anim_accessor)

        # Setup BufferViews
        for this_object in buffersview_gltf:
            this_bufferviews_in_object = buffersview_gltf.get(f'{this_object}')
            for this_bufferview_data in this_bufferviews_in_object:
                buffer_view = this_bufferviews_in_object.get(f'{this_bufferview_data}')
                this_bufferview_gltf = BufferView()
                this_bufferview_gltf.buffer = buffer_view.get(f'buffer')
                this_bufferview_gltf.byteLength = buffer_view.get(f'byteLength')
                this_bufferview_gltf.byteOffset = buffer_view.get(f'byteOffset')
                this_bufferview_gltf.target = buffer_view.get(f'target')
                gltf_file.bufferViews.append(this_bufferview_gltf)
        
        if animation_data != None:
            for animation_name in animation_data:
                this_animation = animation_data.get(f'{animation_name}')
                this_animation_bufferviews = this_animation.get('AnimBuffersView')
                for this_bufferview in this_animation_bufferviews:
                    bufferview_data = this_animation_bufferviews.get(f'{this_bufferview}')
                    anim_bufferview_gltf = BufferView()
                    anim_bufferview_gltf.buffer = bufferview_data.get(f'buffer')
                    anim_bufferview_gltf.byteLength = bufferview_data.get(f'byteLength')
                    anim_bufferview_gltf.byteOffset = bufferview_data.get(f'byteOffset')
                    gltf_file.bufferViews.append(anim_bufferview_gltf)

        # Setup Animation Array
        if animation_data != None:
            for animation_name in animation_data:
                this_animation = animation_data.get(f'{animation_name}')
                animation_links = this_animation.get('AnimLinks')
                gltf_animation = Animation()
                anim_name = animation_links.get('Name')
                anim_channels = animation_links.get('Channels')
                anim_samplers = animation_links.get('Samplers')
                
                gltf_animation.name = anim_name
                
                for channel_name in anim_channels:
                    gltf_anim_channel = AnimationChannel()
                    channel = anim_channels.get(f'{channel_name}')
                    gltf_anim_channel.sampler = channel.get('Sampler')
                    gltf_anim_channel_target = AnimationChannelTarget()
                    gltf_anim_channel_target.node = channel.get('Node')
                    gltf_anim_channel_target.path = channel.get('Path')
                    gltf_anim_channel.target = gltf_anim_channel_target
                    gltf_animation.channels.append(gltf_anim_channel)

                for sampler_name in anim_samplers:
                    gltf_anim_sampler = AnimationSampler()
                    sampler = anim_samplers.get(f'{sampler_name}')
                    gltf_anim_sampler.input = sampler.get('Input')
                    gltf_anim_sampler.interpolation = sampler.get('Interpolation')
                    gltf_anim_sampler.output = sampler.get('output')
                    gltf_animation.samplers.append(gltf_anim_sampler)

                gltf_file.animations.append(gltf_animation)

        # Creating Binary Buffers in GLB Binary Format
        binary_file_name = f'{self.gltf_file_name}_buffers.bin'
        buffer_glb_gltf = Buffer()
        buffer_glb_gltf.byteLength = buffer_gltf_total_size
        buffer_glb_gltf.uri = binary_file_name
        gltf_file.buffers.append(buffer_glb_gltf)

        gltf_file.save_json(f'{self.gltf_deploy_path}.gltf')

        buffer_data_total: list = []
        for current_object_buffer in binary_buffers_gltf:
            get_buffer_data = binary_buffers_gltf.get(f'{current_object_buffer}')
            buffer_data_total.append(get_buffer_data)
        
        if animation_data != None:
            for animation_name in animation_data:
                this_animation = animation_data.get(f'{animation_name}')
                animation_buffers = this_animation.get('AnimBuffers')
                this_buffer = animation_buffers.get('Buffers')
                for this_buffer_sort in this_buffer:
                    get_data = this_buffer.get(f'{this_buffer_sort}')
                    for bufferdata in get_data:
                        if bufferdata == 'KeyframeData':
                            get_keyframe_data = get_data.get('KeyframeData')
                            buffer_data_total.append(get_keyframe_data)
                        elif bufferdata != 'KeyframeData':
                            this_object_data = get_data.get(f'{bufferdata}')
                            denest_translation = this_object_data.get('Translation')
                            denest_rotation = this_object_data.get('Rotation')
                            denest_scale = this_object_data.get('Scale')
                            this_translation_data = denest_translation.get('TransData')
                            this_rotation_data = denest_rotation.get('RotData')
                            this_scale_data = denest_scale.get('ScaleData')
                            buffer_data_total.append(this_translation_data)
                            buffer_data_total.append(this_rotation_data)
                            buffer_data_total.append(this_scale_data)
        
        final_buffer_data = b''.join(buffer_data_total)

        with open(f'{self.gltf_deploy_path}_buffers.bin', 'wb') as gltf_binary_buffer:
            gltf_binary_buffer.write(final_buffer_data)
            gltf_binary_buffer.close()
