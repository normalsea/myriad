#!/usr/bin/python3
"""
TODO: Docstring
"""

from myriad_utils import enforce_annotations, TypeEnforcer
from myriad_mako_wrapper import MakoFileTemplate

import myriad_types


HEADER_FILE_TEMPLATE = """

## Add include guards
<% include_guard = object_name.upper() + "_H" %>
#ifndef ${include_guard}
#define ${include_guard}

## Add library includes
% for lib in lib_includes:
#include <${lib}>
% endfor

## Add local includes
% for lib in local_includes:
#include "${lib}"
% endfor

## Declare typedefs
<%
for fun in functions:
    if fun.gen_typedef is not None:
        context.write(f.stringify_typedef())
%>

## Struct forward declarations
struct ${class_name};
struct ${object_name};

## Module variables
<%
for m_var in module_vars:
    context.write("extern "+m_var.stringify_decl()+";")
%>

## Print methods forward declarations
<%
for fun in functions:
    if fun.is_global:
        context.write("extern "+f.stringify_decl()+";")
%>

extern int initCUDAObjects();

extern void* myriad_new(const void* _class, ...);

extern const void* myriad_class_of(const void* _self);

extern size_t myriad_size_of(const void* self);

extern int myriad_is_a(const void* _self, const struct MyriadClass* m_class);

extern int myriad_is_of(const void* _self, const struct MyriadClass* m_class);

// Delegators

extern void* myriad_ctor(void* _self, va_list* app);

extern int myriad_dtor(void* _self);

extern void* myriad_cudafy(void* _self, int clobber);

extern void myriad_decudafy(void* _self, void* cuda_self);

extern const void* myriad_super(const void* _self);

extern void* super_ctor(const void* _class, void* _self, va_list* app);

extern int super_dtor(const void* _class, void* _self);

extern void* super_cudafy(const void* _class, void* _self, int clobber);

extern void super_decudafy(const void* _class, void* _self, void* cuda_self);

struct MyriadObject
{
    const struct MyriadClass* m_class; //! Object's class/description
};

struct MyriadClass
{
    const struct MyriadObject _;
    const struct MyriadClass* super;
    const struct MyriadClass* device_class;
    size_t size;
    ctor_t my_ctor;
    dtor_t my_dtor;
    cudafy_t my_cudafy;
    de_cudafy_t my_decudafy;
};

#endif

"""


# pylint: disable=R0902
class MyriadModule(object, metaclass=TypeEnforcer):
    """
    Represents an independent Myriad module (e.g. MyriadObject)
    """

    DEFAULT_LIB_INCLUDES = {"stdlib.h", "stdio.h", "assert.h",
                            "stddef.h", "stdarg.h", "stdint.h"}

    DEFAULT_CUDA_INCLUDES = {"cuda_runtime.h", "cuda_runtime_api.h"}

    def __init__(self,
                 object_name: str,
                 class_name: str=None,
                 cuda: bool=False,
                 lib_includes: set=None):
        """Initializes a module"""

        # Set CUDA support status
        self.cuda = cuda

        # Set internal names for classes
        self.object_name = object_name
        if class_name is None:
            self.class_name = object_name + "Class"
        else:
            self.class_name = class_name

        # TODO: Initialize functions/methods/delegators
        self.functions = set()

        # Initialize module global variables
        self.module_vars = set()
        self.initialize_module_vars()

        # Initialize standard library imports, by default with fail-safes
        self.lib_includes = lib_includes
        if self.lib_includes is None:
            self.lib_includes = MyriadModule.DEFAULT_LIB_INCLUDES

        # TODO: Initialize local header imports
        self.local_includes = set()

        # Initialize C header template
        self.header_template = None
        self.initialize_header_template()

    def initialize_module_vars(self,
                               mvars: set=None,
                               strict: bool=False,
                               override: bool=False):
        """
        Initializes module variables with defaults + args.

        Note: strict and override are mutually exclusive.

        Keyword arguments:
        mvars -- set of variables to be registered
        strict -- if True, raises an error if a collision occurs when joining.
        override -- if True, overrides existing variables.
        """

        if strict is True and override is True:
            raise ValueError("Flags strict and override cannot both be True.")

        v_obj = myriad_types.MyriadScalar(self.object_name,
                                          myriad_types.MyriadCType.m_void,
                                          True,
                                          quals=["const"])
        self.module_vars.add(v_obj)
        v_cls = myriad_types.MyriadScalar(self.class_name,
                                          myriad_types.MyriadCType.m_void,
                                          True,
                                          quals=["const"])
        self.module_vars.add(v_cls)

        # TODO: Make "override"/"strict" modes check for existance better.
        if mvars is not None:
            for mvar in mvars:
                if mvar in self.module_vars:
                    if strict:
                        raise ValueError("Cannot add duplicate variable.")
                    elif override:
                        self.module_vars.discard(mvar)
                self.module_vars.add(mvar)

    def initialize_header_template(self, context_dict: dict=None):
        """ Initializes internal Mako template for C header file """
        if context_dict is None:
            context_dict = vars(self)
        self.header_template = MakoFileTemplate(self.object_name+".h",
                                                HEADER_FILE_TEMPLATE,
                                                context_dict)

    def render_header_template(self, printout: bool=False):
        """ Renders the header file template """

        # Reset buffer if necessary
        if self.header_template.buffer is not '':
            self.header_template.reset_buffer()

        self.header_template.render()

        if printout:
            print(self.header_template.buffer)
        else:
            self.header_template.render_to_file()

    # TODO: Implement register_global_variable
    def register_module_variable(self, var: myriad_types.MyriadScalar):
        pass


def main():
    """ Creates a template and renders it using a Mako context """
    m_object = MyriadModule("MyriadObject", "MyriadClass")
    m_object.render_header_template(printout=True)

if __name__ == "__main__":
    main()
