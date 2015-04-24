
"""
runs all spinn front end common tests scripts
"""
import unittest

testmodules = ['external_device_model_tests.munich_motor_control',
               'external_device_model_tests.munich_motor_device',
               'external_device_model_tests.munich_retina_device',
               'external_device_model_tests.test_external_cochlea_device',
               'external_device_model_tests.test_external_fpga_retina_device',
               'external_device_model_tests.test_live_spike_recorder']

suite = unittest.TestSuite()

for t in testmodules:
    try:
        # If the module defines a suite() function, call it to get the suite.
        mod = __import__(t, globals(), locals(), ['suite'])
        suitefn = getattr(mod, 'suite')
        suite.addTest(suitefn())
    except (ImportError, AttributeError):
        # else, just load all the test cases from the module.
        suite.addTest(unittest.defaultTestLoader.loadTestsFromName(t))

unittest.TextTestRunner().run(suite)