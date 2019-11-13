import os
import sys
from compas_fofin.datastructures import Cablenet
from compas_rhino.artists import MeshArtist
from compas.datastructures import Mesh
from compas.geometry import add_vectors
from compas.geometry import scale_vector
from compas.datastructures import mesh_flip_cycles
import compas.geometry as cg 


HERE = os.path.dirname(__file__)

FILE_I = os.path.join(HERE, 'data', 'cablenet.json')
FILE_O = os.path.join(HERE, 'data', 'blocks.json')
cablenet = Cablenet.from_json(FILE_I)
mesh_flip_cycles(cablenet)

# ==============================================================================
# Parameters
# ==============================================================================

OFFSET = 0.0500

# ==============================================================================
# Make block
# ==============================================================================
blocks = []


all_vertices = []
all_faces = []


for fkey in cablenet.faces():
#fkey = cablenet.get_any_face()
    vertices = cablenet.face_vertices(fkey)
    points = cablenet.get_vertices_attributes("xyz", keys=vertices)
    
    polygon = cg. Polygon(points)
    offset_polygon = cg.offset_polygon(points, OFFSET)
    
    normals= [cablenet.vertex_normal(key) for key in vertices]
    
    bottom = offset_polygon[:]
    top = []
    for point, normal in zip(offset_polygon, normals):
        xyz = add_vectors(point, scale_vector(normal, OFFSET))
        top.append(xyz)
    vertices= bottom+top
    faces = [[0, 3, 2, 1], [4, 5, 6, 7], [4, 0, 1, 5], [2, 6, 5, 1], [6, 2, 3, 7], [0, 4, 7, 3]]
    block = Mesh.from_vertices_and_faces(vertices, faces)
    blocks.append(block)
    
    
    all_vertices.extend(vertices)
    k = fkey * 8
    faces_ = [[0+k, 3+k, 2+k, 1+k],[4+k, 5+k, 6+k, 7+k], [4+k, 0+k, 1+k, 5+k], [2+k, 6+k, 5+k, 1+k], [6+k, 2+k, 3+k, 7+k], [0+k, 4+k, 7+k, 3+k]]
    all_faces.extend(faces_)

b = Cablenet.from_vertices_and_faces(all_vertices, all_faces)
# ==============================================================================
# Visualize
# ==============================================================================

#artist = MeshArtist(block, layer="Boxes::Test")
#artist.clear_layer()
#artist.draw_faces(join_faces=True,color=(0,255,255))
#artist.draw_vertexlabels()


for i,block in enumerate(blocks):
    artist = MeshArtist(block, layer="Boxes::Test")
    if i == 0:
        artist.clear_layer()
    artist.draw_faces(join_faces=True,color=(0,255,255))

artist_2 = MeshArtist(b, layer="Boxes::Group")
artist_2.clear_layer()
artist_2.draw_faces(join_faces=True,color=(0,255,255))

b.to_json(FILE_O)