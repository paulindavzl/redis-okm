import pytest

from redis_okm.models.getter_model import Getter
from redis_okm.core.connection import RedisConnect

from redis_okm_tests.conftest import TestModel


@pytest.fixture
def getter() -> Getter:
    models = []
    for i in range(5):
        model = TestModel(
            attr1="test"+str(i),
            attr2=i,
            attr3=1.5
        )
        RedisConnect.add(model)
        models.append(model)
    models.reverse()
    return Getter(models)


def test__getter__filter_by(getter: Getter):
    model = getter.filter_by(attr1="test3")
    models = getter.filter_by(attr3=1.5)
    invalid = getter.filter_by(attr1="test")

    assert isinstance(model, TestModel)
    assert isinstance(models, Getter)
    assert models.length == 5
    assert invalid is None


def test__getter__first(getter: Getter):
    model_default = getter.first()
    model_attr1 = getter.first("attr1")

    assert isinstance(model_default, TestModel)
    assert model_default.attr1 == "test4"
    assert isinstance(model_attr1, TestModel)
    assert model_attr1.attr1 == "test4"

    
def test__getter__last(getter: Getter):
    model_default = getter.last()
    model_attr1 = getter.last("attr1")

    assert isinstance(model_default, TestModel)
    assert model_default.attr1 == "test0"
    assert isinstance(model_attr1, TestModel)
    assert model_attr1.attr1 == "test0"