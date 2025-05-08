import os
import re
import pytest 

from redis_okm.core.connection import RedisConnect
from redis_okm.exceptions.connection_exceptions import *

from redis_okm_tests.conftest import TestModel, Settings


def test__exceptions__redis_connect__settings_instance_exception():
    expected1 = re.escape("settings must be an instance of Settings! senttings_handler: str")

    with pytest.raises(RedisConnectionSettingsInstanceException, match=expected1):
        RedisConnect._connect(use_model=False, settings="settings")

    expected2 = re.escape("For a named db enter an instance of Settings!")
    with pytest.raises(RedisConnectionSettingsInstanceException, match=expected2):
        RedisConnect.count("tests", "")


def test__exceptions__redis_connect__connection_failed_exception():
    path = "test.json"
    expected = re.escape("Unable to connect to Redis database: Error 10061 connecting to localhost:6379. Nenhuma conexão pôde ser feita porque a máquina de destino as recusou ativamente.")

    settings = Settings(path)
    with pytest.raises(RedisConnectConnectionFailedException, match=expected):
        RedisConnect._connect(use_model=False, settings=settings, db="tests")

    if os.path.exists(path):
        os.remove(path)


def test__exceptions__redis_connect__model_instance_exception():
    expected = re.escape("The model must be instantiated to be added to the database!")

    with pytest.raises(RedisConnectionModelInstanceException, match=expected):
        RedisConnect.add(TestModel)


def test__exceptions__redis_connect__already_registered_exception():
    model = TestModel(attr1="test", attr2=0, attr3=0)
    RedisConnect.add(model)

    expected = re.escape("This attr1 (test) already exists in the database!")

    with pytest.raises(RedisConnectionAlreadyRegisteredException, match=expected):
        RedisConnect.add(model)


def test__exceptions__redis_connect__no_identifier_exception():
    expected1 = re.escape("Use an instance of the model (TestModel) or provide an identifier.")

    with pytest.raises(RedisConnectNoIdentifierException, match=expected1):
        RedisConnect.exists(TestModel)

    expected2 = re.escape("Use an instance of the model (TestModel) or provide an identifier.")

    with pytest.raises(RedisConnectNoIdentifierException, match=expected2):
        RedisConnect.delete(TestModel)


def test__exceptions__redis_connect__no_records_exception():
    model = TestModel(attr1="test", attr2=0, attr3=0)
    expected = re.escape("This attr1 (test) does not exist in the database!")

    with pytest.raises(RedisConnectNoRecordsException, match=expected):
        RedisConnect.delete(model)


def test__exceptions__redis_connect__invalid_expire_exception():
    model = TestModel(attr1="test", attr2=0, attr3=0)
    model.__expire__ = "test"
    expected = re.escape('expire must be convertible to float! expire: "test"')

    with pytest.raises(RedisConnectInvalidExpireException, match=expected):
        RedisConnect.add(model)