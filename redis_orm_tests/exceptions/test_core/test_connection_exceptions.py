import re
import pytest

from redis_orm.core.connection import RedisConnect

from redis_orm_tests.conftest import TestModel, settings_test


def test__exceptions__redis_connect__connect__type_error():
    expected = re.escape("settings must be an instance of Settings! senttings_handler: str")

    with pytest.raises(TypeError, match=expected):
        RedisConnect._connect(use_model=False, settings="settings")


def test__exceptions__redis_connect__connect__connection_error():
    expected = re.escape("Unable to connect to Redis database: Error 10061 connecting to localhost:6379. Nenhuma conexão pôde ser feita porque a máquina de destino as recusou ativamente.")

    settings_test.set_config(testing=False)
    with pytest.raises(ConnectionError, match=expected):
        RedisConnect._connect(use_model=False, settings=settings_test, db="tests")

    settings_test.set_config(testing=True)



def test__exceptions__redis_connect__add__type_error():
    expected = re.escape("The model must be instantiated to be added to the database!")

    with pytest.raises(TypeError, match=expected):
        RedisConnect.add(TestModel)


def test__exceptions__redis_connect__add__value_error():
    model = TestModel(attr1="test", attr2=0, attr3=0)
    RedisConnect.add(model)

    expected = re.escape("This attr1 (test) already exists in the database!")

    with pytest.raises(ValueError, match=expected):
        RedisConnect.add(model)


def test__exceptions__redis_connect__exists__value_error():
    expected = re.escape("Use an instance of the model (TestModel) or provide an identifier.")

    with pytest.raises(ValueError, match=expected):
        RedisConnect.exists(TestModel)


def test__exceptions__redis_connect__delete__value_error__no_identify():
    expected = re.escape("Use an instance of the model (TestModel) or provide an identifier.")

    with pytest.raises(ValueError, match=expected):
        RedisConnect.delete(TestModel)


def test__exceptions__redis_connect__delete__value_error__non_existent():
    model = TestModel(attr1="test", attr2=0, attr3=0)
    expected = re.escape("This attr1 (test) does not exist in the database!")

    with pytest.raises(ValueError, match=expected):
        RedisConnect.delete(model)