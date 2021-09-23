""" Drift detection algorithms. """
import inspect
import sys

import alibi_detect.cd as alibi_drifts

drift_detection_algorithms = ['KSDrift',
                              'AverageDriftDetection', 'AveragePerDay']

# TODO: implement all detection algorithms.
class DriftDetectionAlgorithmsMixin:
    '''
    A DriftDetection algorithms Mixin class
    contains helper function to setup and 
    retrive detection algorithms modules.

    '''

    def get_drift(self, name):
        ''' a method to retrive algorithm function
        from name.
        '''
        _built_in_drift_detecition = {}
        _built_in_clsmembers = inspect.getmembers(
            sys.modules[__name__], inspect.isclass)
        for n, a in _built_in_clsmembers:
            _built_in_drift_detecition[n] = a

        if name not in _built_in_drift_detecition.keys():
            return getattr(alibi_drifts, name)
        return _built_in_drift_detecition[name]
