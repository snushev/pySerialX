import pytest
from pySerialX.serialx_jit_interpreter import SerialXInterpreter


def test_encode_set_bool_values():
    # 1. Python bool True -> JIT 'sb led 1'
    assert SerialXInterpreter._encode_set(["set", "bool", "led", True]) == "sb led 1"

    # 2. Python bool False -> JIT 'sb led 0'
    assert SerialXInterpreter._encode_set(["set", "bool", "led", False]) == "sb led 0"

    # 3. String 'true' / '1' -> JIT 'sb led 1'
    assert SerialXInterpreter._encode_set(["set", "bool", "led", "true"]) == "sb led 1"
    assert SerialXInterpreter._encode_set(["set", "bool", "led", "1"]) == "sb led 1"

    # 4. String 'false' / '0' -> JIT 'sb led 0'
    assert SerialXInterpreter._encode_set(["set", "bool", "led", "false"]) == "sb led 0"
    assert SerialXInterpreter._encode_set(["set", "bool", "led", "0"]) == "sb led 0"


def test_encode_set_bool_invalid():
    # Invalid value
    assert SerialXInterpreter._encode_set(["set", "bool", "led", "invalid"]) is None
