import re
import pytest

from redis_okm.models.getter_model import Getter
from redis_okm.exceptions.getter_model_exceptions import *

from redis_okm_tests.conftest import TestModel, RedisModel


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


def test__exceptions__getter___not_list_model_exception():
    expected = re.escape("get_returns must be a list! get_returns: 0 (int)")

    with pytest.raises(GetterNotListModelsException, match=expected):
        Getter(0)


def test__exceptions__getter__not_redis_model_exception():
    class Model:
        pass

    model = Model()

    expected = re.escape("All models passed to Getter must be a class that inherits from RedisModel. Model does not inherit RedisModel!")

    with pytest.raises(GetterNotRedisModelException, match=expected):
        Getter([model])


def test__exceptions__getter__different_models_exception():
    class Model(RedisModel):
        __db__ = "tests"

        attr1: str

    test_model = TestModel(
        attr1="test",
        attr2=0,
        attr3=1.5
    )

    model = Model(
        attr1="test"
    )

    expected = re.escape("All models passed to Getter must be of the same type/class (TestModel). Model != TestModel")

    with pytest.raises(GetterDifferentModelsException, match=expected):
        Getter([test_model, model])


def test__exceptions__getter__filter_by__attribute_exception(getter: Getter):
    expected = re.escape("TestModel does not have invalid_attr attribute!")

    with pytest.raises(GetterAttributeException, match=expected):
        getter.filter_by(invalid_attr="")


def test__exceptions__getter__first__reference_type_exception(getter: Getter):
    expected = re.escape("reference must be a str (string)! reference: 0 (int)")

    with pytest.raises(GetterReferenceTypeException, match=expected):
        getter.first(0)

    
def test__exceptions__getter__first__attribute_exception(getter: Getter):
    expected = re.escape("TestModel does not have the invalid_attr attribute!")

    with pytest.raises(GetterAttributeException, match=expected):
        getter.first("invalid_attr")


def test__exceptions__getter__last__reference_type_exception(getter: Getter):
    expected = re.escape("reference must be a str (string)! reference: 0 (int)")

    with pytest.raises(GetterReferenceTypeException, match=expected):
        getter.last(0)

    
def test__exceptions__getter__last__attribute_exception(getter: Getter):
    expected = re.escape("TestModel does not have the invalid_attr attribute!")

    with pytest.raises(GetterAttributeException, match=expected):
        getter.last("invalid_attr")


def test__exceptions__getter__filter_by__condition_type_exception(getter: Getter):
    expected = re.escape('The "attr3" condition must be a possible float. attr3: "test_error" (str)')

    with pytest.raises(GetterConditionTypeException, match=expected):
        getter.filter_by(attr3="test_error")


def test__exceptions__getter__corruption_exception():
    expected = re.escape("TestModel: The information in this record (attr1: test) is corrupt!")
    test = TestModel(attr1="test", attr2=0, attr3=0)
    test.__status__ = False
    gett = Getter([test])

    with pytest.raises(GetterCorruptionException, match=expected):
        gett.filter_by(attr1="test")

    with pytest.raises(GetterCorruptionException, match=expected):
        gett.first()

    with pytest.raises(GetterCorruptionException, match=expected):
        gett.last()
