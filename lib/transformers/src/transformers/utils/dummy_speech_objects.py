# This file is autogenerated by the command `make fix-copies`, do not edit.
from ..utils import DummyObject, requires_backends


class ASTFeatureExtractor(metaclass=DummyObject):
    _backends = ["speech"]

    def __init__(self, *args, **kwargs):
        requires_backends(self, ["speech"])


class MCTCTFeatureExtractor(metaclass=DummyObject):
    _backends = ["speech"]

    def __init__(self, *args, **kwargs):
        requires_backends(self, ["speech"])


class Speech2TextFeatureExtractor(metaclass=DummyObject):
    _backends = ["speech"]

    def __init__(self, *args, **kwargs):
        requires_backends(self, ["speech"])


class SpeechT5FeatureExtractor(metaclass=DummyObject):
    _backends = ["speech"]

    def __init__(self, *args, **kwargs):
        requires_backends(self, ["speech"])


class TvltFeatureExtractor(metaclass=DummyObject):
    _backends = ["speech"]

    def __init__(self, *args, **kwargs):
        requires_backends(self, ["speech"])
