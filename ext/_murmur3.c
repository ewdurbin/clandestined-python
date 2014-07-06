#include <Python.h>

#include <stdint.h>
#include <string.h>

// MurmurHash3 was written by Austin Appleby, and is placed in the public
// domain. The author hereby disclaims copyright to this source code.

uint32_t murmur3_32(const char *key, uint32_t len, uint32_t seed) {
    static const uint32_t c1 = 0xcc9e2d51;
    static const uint32_t c2 = 0x1b873593;
    static const uint32_t r1 = 15;
    static const uint32_t r2 = 13;
    static const uint32_t m = 5;
    static const uint32_t n = 0xe6546b64;
 
    uint32_t hash = seed;
 
    const int nblocks = len / 4;
    const uint32_t *blocks = (const uint32_t *) key;
    int i;
    for (i = 0; i < nblocks; i++) {
        uint32_t k = blocks[i];
        k *= c1;
        k = (k << r1) | (k >> (32 - r1));
        k *= c2;
 
        hash ^= k;
        hash = ((hash << r2) | (hash >> (32 - r2))) * m + n;
    }
 
    const uint8_t *tail = (const uint8_t *) (key + nblocks * 4);
    uint32_t k1 = 0;
 
    switch (len & 3) {
    case 3:
        k1 ^= tail[2] << 16;
    case 2:
        k1 ^= tail[1] << 8;
    case 1:
        k1 ^= tail[0];
 
        k1 *= c1;
        k1 = (k1 << r1) | (k1 >> (32 - r1));
        k1 *= c2;
        hash ^= k1;
    }
 
    hash ^= len;
    hash ^= (hash >> 16);
    hash *= 0x85ebca6b;
    hash ^= (hash >> 13);
    hash *= 0xc2b2ae35;
    hash ^= (hash >> 16);
 
    return hash;
}

static char module_docstring[] =
    "This module provides an interface for calculating murmur3_32 hashes with C.";
static char murmur3_32_docstring[] =
    "Calculate the murmur3_32 hash for a given string.";

static PyObject *clandestine_murmur3_32(PyObject *self, PyObject *args);
 
static PyMethodDef module_methods[] = {
    {"murmur3_32", clandestine_murmur3_32, METH_VARARGS, murmur3_32_docstring},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC init_murmur3(void)
{
    PyObject *m = Py_InitModule3("_murmur3", module_methods, module_docstring);
    if (m == NULL){
        return;
    }
}

static PyObject *clandestine_murmur3_32(PyObject *self, PyObject *args)
{
    const char *key;
    uint32_t len;
    uint32_t seed = 0;

    if (!PyArg_ParseTuple(args, "s#|i", &key, &len, &seed)) {
        return NULL;
    }

    uint32_t value = murmur3_32(key, len, seed);
 
    PyObject *ret = Py_BuildValue("k", value);
    return ret;
}
