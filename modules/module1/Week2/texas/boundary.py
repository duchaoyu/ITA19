import os
from compas_fofin.datastructures import Cablenet
from compas_rhino.artists import MeshArtist
from compas_rhino.artists import FrameArtist
from compas_rhino.artists import PointArtist
from compas.datastructures import Mesh
from compas.geometry import add_vectors
from compas.geometry import scale_vector
from compas.geometry import Frame
from compas.geometry import Point
from compas.geometry import Box
from compas.geometry import Transformation
from compas.geometry import transform_points
from compas.geometry import cross_vectors
from compas.geometry import subtract_vectors
from compas.geometry import bounding_box_xy
from compas.geometry import offset_polygon
from compas.geometry import intersection_line_plane
import compas.geometry as cg

# ==============================================================================
# Create a proxy for PCA
# ==============================================================================

from compas.rpc import Proxy
numerical = Proxy("compas.numerical")
pca_numpy = numerical.pca_numpy

# ==============================================================================
# Construct a cablenet
# ==============================================================================

HERE = os.path.dirname(__file__)
FILE_I = os.path.join(HERE, 'data', 'cablenet.json')

cablenet = Cablenet.from_json(FILE_I)

# ==============================================================================
# Parameters
# ==============================================================================

OFFSET = 0.200
PADDING = 0.020

# ==============================================================================
# Vertices on SOUTH
# ==============================================================================

SOUTH = list(cablenet.vertices_where({"constraint": "SOUTH"}))
boundary = list(cablenet.vertices_on_boundary(ordered=True))
SOUTH = [key for key in boundary if key in SOUTH]
print SOUTH

# ==============================================================================
# Boundary plane
# ==============================================================================

a = cablenet.vertex_coordinates(SOUTH[0])
b = cablenet.vertex_coordinates(SOUTH[-1])

xaxis = subtract_vectors(b, a)
yaxis = [0, 0, 1.0]
zaxis = cross_vectors(xaxis, yaxis)
xaxis = cross_vectors(yaxis, zaxis)

frame = Frame([0,0,0], xaxis, yaxis)
point = add_vectors(a, scale_vector(frame.zaxis, OFFSET))
normal = frame.zaxis
plane = cg.Plane(point, normal)

# ==============================================================================
# Intersections
# ==============================================================================

intersections = []

for key in SOUTH:
    a = cablenet.vertex_coordinates(key)
    r = cablenet.residual(key)
    b = add_vectors(a, r)
    x = intersection_line_plane((a,b), plane)

    intersections.append(Point(*x))



# ==============================================================================
# Bounding boxes
# ==============================================================================
beam_num = len(intersections) // 6
print(beam_num)

all_vertices = []
all_faces = []

for i in range(beam_num):
    points = intersections[(i*6):((i+1)*6)]
    
    origin, axes, values = pca_numpy([list(point) for point in points])
    
    frame_1 = Frame(origin, axes[0], axes[1])
    
    x = Transformation.from_frame_to_frame(frame_1, Frame.worldXY())
    points2 = transform_points(points, x)
    bbox = bounding_box_xy(points2)
    bbox = offset_polygon(bbox, -PADDING)
    bbox = transform_points(bbox, x.inverse())
    all_vertices.extend(bbox)
    all_faces.append([i*4, i*4+1, i*4+2, i*4+3])

bbox = Mesh.from_vertices_and_faces(all_vertices, all_faces)


# ==============================================================================
# Visualization
# ==============================================================================

artist = FrameArtist(frame, layer="SOUTH::Frame", scale=0.3)
artist.clear_layer()
artist.draw()

artist = FrameArtist(frame_1, layer="SOUTH::Frame_1", scale=0.3)
artist.clear_layer()
artist.draw()

artist = MeshArtist(bbox, layer= "SOUTH::Bbox1")
artist.clear_layer()
artist.draw_faces(join_faces=True,color=(0,255,255))

PointArtist.draw_collection(intersections, layer="SOUTH::intersections", clear=True)
