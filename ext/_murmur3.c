#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <stdint.h>
#include <string.h>

#ifdef PYPY_VERSION
#define COMPILING_IN_PYPY 1
#define COMPILING_IN_CPYTHON 0
#else
#define COMPILING_IN_PYPY 0
#define COMPILING_IN_CPYTHON 1
#endif
// MurmurHash3 was written by Austin Appleby, and is placed in the public
// domain. The author hereby disclaims copyright to this source code.

uint32_t murmur3_32(const char *key, Py_ssize_t len, uint32_t seed) {
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

static PyObject *clandestined_murmur3_32(PyObject *self, PyObject *args);
 
static PyMethodDef module_methods[] = {
    {"murmur3_32", clandestined_murmur3_32, METH_VARARGS, murmur3_32_docstring},
    {NULL, NULL, 0, NULL}
};

struct module_state {
    PyObject *error;
};

#if COMPILING_IN_CPYTHON && PY_MAJOR_VERSION >= 3
#define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))
#else
#define GETSTATE(m) (&_state)
static struct module_state _state;
#endif

#if PY_MAJOR_VERSION >= 3
static int module_traverse(PyObject *m, visitproc visit, void *arg) {
    Py_VISIT(GETSTATE(m)->error);
    return 0;
}

static int module_clear(PyObject *m) {
    Py_CLEAR(GETSTATE(m)->error);
    return 0;
}

static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "_murmur3",
        module_docstring,
        sizeof(struct module_state),
        module_methods,
        NULL,
        module_traverse,
        module_clear,
        NULL
};

#define INITERROR return NULL
#else
#define INITERROR return
#endif

#if PY_MAJOR_VERSION >= 3
PyObject * PyInit__murmur3(void)
{
    PyObject *m = PyModule_Create(&moduledef);
#else
PyMODINIT_FUNC init_murmur3(void)
{
    PyObject *m = Py_InitModule3("_murmur3", module_methods, module_docstring);
#endif

    if (m == NULL){
        INITERROR;
    }
    struct module_state *st = GETSTATE(m);

    st->error = PyErr_NewException("_murmur3.Error", NULL, NULL);
    if (st->error == NULL) {
        Py_DECREF(m);
        INITERROR;
    }

#if PY_MAJOR_VERSION >= 3
    return m;
#endif
}

static PyObject *clandestined_murmur3_32(PyObject *self, PyObject *args)
{
    const char *key;
    Py_ssize_t len;
    uint32_t seed = 0;

    if (!PyArg_ParseTuple(args, "s#|i", &key, &len, &seed)) {
        return NULL;
    }

    uint32_t value = murmur3_32(key, len, seed);
 
    PyObject *ret = Py_BuildValue("k", value);
    return ret;
}
