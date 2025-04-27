import re
import pytest

from redis_orm.models import BaseModel


def test__exceptions__base_model__attribute_error__no_db():
    class TestModel(BaseModel):
        __test__ = False

        attr1: str
        attr2: int

    expected = re.escape("Specify the database using __db__ when structuring the model")
    with pytest.raises(AttributeError, match=expected):
        TestModel()


def test__exceptions__base_model__attribute_error__invalid_attribute():
    class TestModel(BaseModel):
        __test__ = False
        __db__ = "tests"

        attr1: str
        attr2: int

    expected = re.escape('TestModel does not have "attr3" attribute!')
    with pytest.raises(AttributeError, match=expected):
        TestModel(attr3="error")


def test__exceptions__base_model__value_error():
    class TestModel(BaseModel):
        __test__ = False
        __db__ = "tests"

        attr1: str
        attr2: int

    expected = re.escape("attr2 expected a possible int value, but received a str (impossible) value!")
    with pytest.raises(ValueError, match=expected):
        TestModel(attr2="impossible")


def test__exceptions__base_model__attribute_error__attr_not_null():
    class TestModel(BaseModel):
        __test__ = False
        __db__ = "tests"
        __idname__ = "testID"

        attr1: str

    expected = re.escape("attr1 must receive a value!")
    with pytest.raises(AttributeError, match=expected):
        TestModel()
    