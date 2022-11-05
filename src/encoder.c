#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdio.h>
#include <stdint.h>


enum FileType {
    FDSHAPE = 0x0201,
};

enum VertexType {
    STARTVERTEX = 0x4479F99A,
    LINEVERTEX = 0x3F800000,
    POLYVERTEX = 0x00000000,
};

static uint8_t padding1_data[16] = {
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
};

static uint8_t padding2_data[36] = {
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00
};

static uint8_t padding3_data[4] = {
        0x00, 0x00, 0x00, 0x00
};

struct FileHeader {
    uint8_t padding1[16];
    enum FileType type;
    uint8_t padding2[36];
    uint32_t size;
    uint8_t padding3[4];
    double prefix_x, prefix_y;
};

#pragma pack(push, 1)
struct Vertex {
    enum VertexType type;
    double x, y;
};
#pragma pack(pop)

PyObject *encode_vertex(PyObject *self, PyObject *args) {
    uint32_t vertex_type;
    double x;
    double y;
    int bufsize = sizeof(struct Vertex);
    if (!PyArg_ParseTuple(args, "Idd", &vertex_type, &x, &y)) {
        return NULL;
    }
    struct Vertex vertex = {.type = vertex_type, x, y};
    PyObject *bufferobj = Py_BuildValue("y#", &vertex, (Py_ssize_t)bufsize);
    return bufferobj;
}

PyObject *encode_header(PyObject *self, PyObject *args) {
    uint32_t size;
    double prefix_x;
    double prefix_y;
    int bufsize = sizeof(struct FileHeader);
    if (!PyArg_ParseTuple(args, "Idd", &size, &prefix_x, &prefix_y)) {
        return NULL;
    }
    struct FileHeader header = {
        .type = FDSHAPE,
        .size = size,
        .prefix_x = prefix_x,
        .prefix_y = prefix_y,
    };
    memcpy(&header.padding1, padding1_data, sizeof(header.padding1));
    memcpy(&header.padding2, padding2_data, sizeof(header.padding2));
    memcpy(&header.padding3, padding3_data, sizeof(header.padding3));
    PyObject *bufferobj = Py_BuildValue("y#", &header, (Py_ssize_t)bufsize);
    return bufferobj;
}

static PyMethodDef fdSencodeMethods[] = {
    {"encode_header", encode_header, METH_VARARGS, "Encode an fdShape header. Returns bytes"},
    {"encode_vertex", encode_vertex, METH_VARARGS, "Encode an fdShape vertex. Returns bytes"},
    {NULL, NULL, 0, NULL},
};

static struct PyModuleDef fdSencode = {
    PyModuleDef_HEAD_INIT,
    "fdSencode",   /* name of module */
    "fdShape file encoder module", /* module documentation, may be NULL */
    -1,
    fdSencodeMethods
};

PyMODINIT_FUNC PyInit_fdSencode(void) {
    return PyModule_Create(&fdSencode);
}
