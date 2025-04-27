import re
import pytest

from redis_orm.models.getter_model import Getter

from redis_orm_tests.conftest import TestModel


@pytest.fixture
def getter() -> Getter:
    models = []
    for i in range(5):
        model = TestModel(
            attr1="test"+str(i),
            attr2=i,
            attr3=1.5
        )
        models.append(model)
    models.reverse()
    return Getter(models)


def test__exceptions__getter__init__type_error():
    expected = re.escape("get_returns must be a list! get_returns: 0 (int)")

    with pytest.raises(TypeError, match=expected):
        Getter(0)


def test__exceptions__getter__init__value_error():
    expected = re.escape("get_returns must not be empty!")

    with pytest.raises(ValueError, match=expected):
        Getter([])


def test__exceptions__getter__filter_by__attribute_error(getter: Getter):
    expected = re.escape("TestModel does not have invalid_attr attribute!")

    with pytest.raises(AttributeError, match=expected):
        getter.filter_by(invalid_attr="")


def test__exceptions__getter__first__type_error(getter: Getter):
    expected = re.escape("reference must be a str (string)! reference: 0 (int)")

    with pytest.raises(TypeError, match=expected):
        getter.first(0)

    
def test__exceptions__getter__first__attribute_error(getter: Getter):
    expected = re.escape("TestModel does not have the invalid_attr attribute!")

    with pytest.raises(AttributeError, match=expected):
        getter.first("invalid_attr")


def test__exceptions__getter__last__type_error(getter: Getter):
    expected = re.escape("reference must be a str (string)! reference: 0 (int)")

    with pytest.raises(TypeError, match=expected):
        getter.last(0)

    
def test__exceptions__getter__last__attribute_error(getter: Getter):
    expected = re.escape("TestModel does not have the invalid_attr attribute!")

    with pytest.raises(AttributeError, match=expected):
        getter.last("invalid_attr")
