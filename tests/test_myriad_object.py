"""
..module:: test_myriad_object
    :platform: Linux
    :synopsis: Testing for inheriting from MyriadObject

.. moduleauthor:: Pedro Rittner <pr273@cornell.edu>
"""

import unittest

from myriad_testing import set_external_loggers, MyriadTestCase

from context import myriad
from myriad import myriad_types as mtypes
from myriad import myriad_metaclass as mclass
from myriad import myriad_object as mobject


@set_external_loggers("TestMyriadMetaclass", mobject.LOG, mclass.LOG)
class TestMyriadMetaclass(MyriadTestCase):
    """
    Tests MyriadMetaclass functionality 'standalone'
    """

    def test_create_blank_class(self):
        """ Testing if creating a blank metaclass works """
        class BlankObj(mobject.MyriadObject):
            """ Blank test class """
            pass
        # Test for the existence expected members
        self.assertTrue("obj_struct" in BlankObj.__dict__)
        self.assertTrue("myriad_obj_vars" in BlankObj.__dict__)
        # TODO: Add more checks for other members
        # Check if names are as we expect them
        self.assertTrue("obj_name" in BlankObj.__dict__)
        self.assertEqual(BlankObj.__dict__["obj_name"], "BlankObj")
        self.assertTrue("cls_name" in BlankObj.__dict__)
        self.assertEqual(BlankObj.__dict__["cls_name"], "BlankObjClass")

    def test_create_variable_only_class(self):
        """ Testing if creating a variable-only metaclass works """
        class VarOnlyObj(mobject.MyriadObject):
            capacitance = mtypes.MDouble
            vm = mtypes.MyriadTimeseriesVector
        result_str = VarOnlyObj.__dict__["obj_struct"].stringify_decl()
        expected_result = """
        struct VarOnlyObj
        {
            const struct MyriadObject _;
            double capacitance;
            double vm[SIMUL_LEN];
        }
        """
        self.assertTrimStrEquals(result_str, expected_result)

    def test_create_methods_class(self):
        """ Testing if creating Myriad classes with methods works """
        class MethodsObj(mobject.MyriadObject):
            @mclass.myriad_method
            def do_stuff(self):
                return 0
        # Test whether a myriad method was created
        self.assertIn("myriad_methods", MethodsObj.__dict__)
        self.assertIn("do_stuff", MethodsObj.__dict__["myriad_methods"])

    def test_verbatim_methods(self):
        """ Testing if creating Myriad classes with verbatim methods work"""
        class VerbatimObj(mobject.MyriadObject):
            @mclass.myriad_method_verbatim
            def do_verbatim_stuff(self):
                """return;"""
        self.assertIsNotNone(
            VerbatimObj.__dict__["myriad_methods"]["do_verbatim_stuff"])

    def test_myriad_blank_init(self):
        """ Testing creating empty Myriad objects """
        class InstanceObject(mobject.MyriadObject):
            pass
        inst = InstanceObject()
        self.assertIsNotNone(inst)

    def test_myriad_init(self):
        """ Testing creating a non-empty Myriad object """
        class InstanceObject(mobject.MyriadObject):
            dummy = mtypes.MDouble
        inst = InstanceObject(dummy=3.0)
        self.assertIsNotNone(inst)
        self.assertTrue(hasattr(inst, "dummy"))
        self.assertEqual(getattr(inst, "dummy"), 3.0)

    def test_myriad_invalid_init(self):
        """ Testing creating Myriad object with invalid constructor calls """
        class InstanceObject(mobject.MyriadObject):
            dummy = mtypes.MDouble
        inst = None
        # No arguments - should fail
        try:
            inst = InstanceObject()
        except ValueError:
            pass
        self.assertIsNone(inst)
        # Incorrect argument - should fail
        try:
            inst = InstanceObject(bar="LOL")
        except ValueError:
            pass
        self.assertIsNone(inst)
        # Incorrect argument type - should fail
        try:
            inst = InstanceObject(value=1.0)
        except ValueError:
            pass
        self.assertIsNone(inst)


@set_external_loggers("TestMyriadRendering", mobject.LOG, mclass.LOG)
class TestMyriadRendering(MyriadTestCase):
    """
    Tests rendering of objects inheriting from MyriadObject
    """

    def test_template_instantiation(self):
        """ Testing if template rendering produces files """
        class RenderObj(mobject.MyriadObject):
            pass
        RenderObj.render_templates()
        self.assertFilesExist(RenderObj)
        # self.cleanupFiles(RenderObj)

    def test_render_variable_only_class(self):
        """ Testing if rendering a variable-only class works """
        class VarOnlyObj(mobject.MyriadObject):
            capacitance = mtypes.MDouble
        VarOnlyObj.render_templates()
        self.assertFilesExist(VarOnlyObj)
        # self.cleanupFiles(VarOnlyObj)

    def test_render_timeseries_class(self):
        """ Testing if rendering a timeseries-containing class works"""
        class TimeseriesObj(mobject.MyriadObject):
            capacitance = mtypes.MDouble
            vm = mtypes.MyriadTimeseriesVector
        TimeseriesObj.render_templates()
        self.assertFilesExist(TimeseriesObj)
        # self.cleanupFiles(TimeseriesObj)


if __name__ == '__main__':
    unittest.main()
