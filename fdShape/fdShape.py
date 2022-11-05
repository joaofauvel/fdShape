from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

import fdSencode
from common import VertexType
from decoder import fdSdecode
from exceptions import NotWGS84Error, InvalidGeometryType

# Warning: *_file methods won't be work without fiona


class fdShapeTypes(Enum):
    CURVEDTRACK = 'CurvedTrack'
    BOUNDARY = 'Boundary'

@dataclass
class Vertex:
    x: float
    y: float

@dataclass
class Feature:
    vertices: list[Vertex]

class fdShape(ABC):
    def __init__(self, type: fdShapeTypes, features: list[Feature]) -> None:
        self.type = type
        self.features = features

class CurvedTrack(fdShape):
    def __init__(self, features: list[Feature], reference_x: int, reference_y: int) -> None:
        super().__init__(fdShapeTypes.CURVEDTRACK, features)
        # reference x and y defined as the first vertex of the first feature
        self.ref_x = reference_x
        self.ref_y = reference_y

    def vertex_count(self) -> int:
        return sum([len(feat.vertices) for feat in self.features])

    def to_wkt(self) -> str:
        wkt_features_list = ['wkt_geom\n']
        for feat in self.features:
            wkt_feat_list = [f'{vertex.x} {vertex.y}' for vertex in feat.vertices]
            wkt_feat = 'LineString ('+', '.join(wkt_feat_list)+')\n'
            wkt_features_list.append(wkt_feat)
        return ''.join(wkt_features_list)

    def to_file(self, path: str) -> None:
        # TODO: check file extension
        with open(path, 'w') as f:
            f.write(self.to_wkt())

    def to_fdShape(self, path: str, **kwargs) -> None:
        with open(path, 'wb') as f:
            f.write(self.to_bytes(**kwargs))

    def to_bytes(self, prefix_x = 0.0, prefix_y = 0.0, insert_duplicate_bytes = False) -> bytes:
        if not insert_duplicate_bytes:
            vertex_count = self.vertex_count()
        else:
            # vertex count + 1 duplicate byte per feature, except last one (that's how its encoded with GLC/Apex)
            vertex_count = self.vertex_count()+(len(self.features)-1)
        # adding 1 to the vertex count due to prefix vertex, which adds to the vertex count
        ba_list: list[bytes] = [fdSencode.encode_header(vertex_count+1, prefix_x, prefix_y)]
        for fid, feature in enumerate(self.features):
            for index, vertex in enumerate(feature.vertices):
                x = vertex.x-self.ref_x
                y = vertex.y-self.ref_y
                if index == 0:
                    ba_list.append(fdSencode.encode_vertex(VertexType.STARTVERTEX.value, x, y))
                    continue
                ba_list.append(fdSencode.encode_vertex(VertexType.LINEVERTEX.value, x, y))
                # if it's the last vertex in the feature
                if index == (len(feature.vertices)-1) and insert_duplicate_bytes:
                    # if it's not the last feature
                    if fid != (len(self.features)-1):
                        ba_list.append(fdSencode.encode_vertex(VertexType.LINEVERTEX.value, x, y))
        # insert end sequence for CurvedTrack
        ba_list.append(b'\x00\x00\x80\x3F')
        return b''.join(ba_list)
    
    @classmethod
    def from_file(cls, path: str, ref_x: float = None, ref_y: float = None, **kwargs) -> 'CurvedTrack':
        features = cls._collection2features(path, **kwargs)
        # reference x and y defined as the first vertex of the first feature
        ref_x = features[0].vertices[0].x if not ref_x else ref_x
        ref_y = features[0].vertices[0].y if not ref_y else ref_y
        return cls(features, ref_x, ref_y)
   
    @classmethod
    def from_fdShape(cls, path: str, ref_x: int, ref_y: int) -> 'CurvedTrack':
        fdsdecode = fdSdecode.from_file(path)
        # TODO: get refx and refy from spatial catalog, use refx and refy passed as args if not None. 
        #   Make refx and refy optional (arg: float = None)
        features = cls._fdsdecode2features(fdsdecode, ref_x, ref_y)
        return cls(features, ref_x, ref_y)

    @classmethod
    def from_fdsdecode(cls, fdsdecode: fdSdecode, ref_x: int, ref_y: int) -> 'CurvedTrack':
        features = cls._fdsdecode2features(fdsdecode, ref_x, ref_y)
        return cls(features, ref_x, ref_y)

    @staticmethod
    def _fdsdecode2features(fdsdecode: fdSdecode, ref_x: int, ref_y: int) -> list[Feature]:
        features = []
        first_vertex = fdsdecode.vertices[0]
        feat = [Vertex(ref_x+first_vertex.x, ref_y+first_vertex.y)]
        for vertex in fdsdecode.vertices[1:]:
            if vertex.type == VertexType.STARTVERTEX:
                features.append(Feature(feat))
                feat = []
            feat.append(Vertex(ref_x+vertex.x, ref_y+vertex.y))
        features.append(Feature(feat))
        return features

    @staticmethod
    def _collection2features(path: str, **kwargs) -> list[Feature]:
        import fiona
        with fiona.open(path, 'r', **kwargs) as c:
            if c.crs['init'] != 'epsg:4326':
                raise NotWGS84Error
            features = []
            for record in c:
                feature = record['geometry']
                if feature['type'] not in ['LineString', 'MultiLineString']:
                    raise InvalidGeometryType
                feature_geom = feature['coordinates']
                if feature['type'] == 'MultiLineString':
                    # Flatten multipart geometry to singlepart, since fdShape doesn't support multipart
                    # TODO: multipart into singlepart as different features
                    feature_geom = [v for part in feature['coordinates'] for v in part]
                vertices = [Vertex(*vertex) for vertex in feature_geom]
                features.append(Feature(vertices))
        return features

class Boundary(fdShape):
    def __init__(self, features: list[Feature]) -> None:
        super().__init__(fdShapeTypes.BOUNDARY, features)

def read_file(path: str, override_type: str = None) -> fdShape:
    pass

def to_file(fdShape: fdShape, path: str = '.') -> None:
    pass

if __name__ == '__main__':
    print(fdSencode.__doc__)
