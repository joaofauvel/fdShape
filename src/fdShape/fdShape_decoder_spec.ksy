meta:
  id: fdshape
  title: John Deere fdShape
  file-extension: fdShape
  endian: le
seq:
  - id: header
    type: file_header
  - id: vertices
    type: vertex
    repeat: expr
    repeat-expr: header.number_of_vertices-1
  - id: endsequence
    type: u4
types:
  file_header:
    seq:
      - id: padding
        size: 16
      - id: file_code
        contents: [0x01, 0x02, 0x00, 0x00]
      - id: padding1
        size: 36
      - id: number_of_vertices
        type: u4
      - id: padding2
        size: 4
      - id: prefix_x
        type: f8
      - id: prefix_y
        type: f8
  vertex:
    seq:
      - id: type
        type: u4
        enum: vertextype
      - id: x
        type: f8
      - id: y
        type: f8
enums:
  vertextype:
    0x4479F99A: startvertex
    0x3F800000: linevertex
    0x00000000: polyvertex
    