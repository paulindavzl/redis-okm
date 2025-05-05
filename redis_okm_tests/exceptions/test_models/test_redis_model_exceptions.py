import re
import pytest

from redis_okm.models import RedisModel
from redis_okm.exceptions.redis_model_exceptions import *


def test__exceptions__redis_model__id_exception():
    class TestModel(RedisModel):
        __test__ = False

        attr1: str
        attr2: int

    expected = re.escape("Specify the database using __db__ when structuring the model")
    with pytest.raises(RedisModelDBException, match=expected):
        TestModel()


def test__exceptions__redis_model__attribute_exception():
    class TestModel(RedisModel):
        __test__ = False
        __db__ = "tests"

        attr1: str
        attr2: int

    expected = re.escape('TestModel does not have "attr3" attribute!')
    with pytest.raises(RedisModelAttributeException, match=expected):
        TestModel(attr3="error")


def test__exceptions__redis_model__type_value_exception():
    class TestModel(RedisModel):
        __test__ = False
        __db__ = "tests"

        attr1: str
        attr2: int

    expected = re.escape("attr2 expected a possible int value, but received a str (impossible) value!")
    with pytest.raises(RedisModelTypeValueException, match=expected):
        TestModel(attr2="impossible")


def test__exceptions__redis_model__no_value_exception():
    class TestModel(RedisModel):
        __test__ = False
        __db__ = "tests"
        __idname__ = "testID"

        attr1: str

    expected = re.escape("attr1 must receive a value!")
    with pytest.raises(RedisModelNoValueException, match=expected):
        TestModel()
    