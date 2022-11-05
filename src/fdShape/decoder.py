# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from common import VertexType


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class fdSdecode(KaitaiStruct):

    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.header = fdSdecode.FileHeader(self._io, self, self._root)
        self.vertices = []
        for i in range((self.header.number_of_vertices - 1)):
            self.vertices.append(fdSdecode.Vertex(self._io, self, self._root))

        self.endsequence = self._io.read_u4le()

    class FileHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.padding = self._io.read_bytes(16)
            self.file_code = self._io.read_bytes(4)
            if not self.file_code == b"\x01\x02\x00\x00":
                raise kaitaistruct.ValidationNotEqualError(b"\x01\x02\x00\x00", self.file_code, self._io, u"/types/file_header/seq/1")
            self.padding1 = self._io.read_bytes(36)
            self.number_of_vertices = self._io.read_u4le()
            self.padding2 = self._io.read_bytes(4)
            self.prefix_x = self._io.read_f8le()
            self.prefix_y = self._io.read_f8le()


    class Vertex(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.type = KaitaiStream.resolve_enum(VertexType, self._io.read_u4le())
            self.x = self._io.read_f8le()
            self.y = self._io.read_f8le()



