import os
import re
import pytest 

from redis_okm.tools import RedisConnect, Settings, RedisModel
from redis_okm.exceptions.connection_exceptions import *

from redis_okm_tests.conftest import TestModel


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
    settings.set_config(retry_on_timeout=False, timeout=0.1)
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
    expected1 = re.escape("TestModel: Use an instance of the model or provide an identifier.")

    with pytest.raises(RedisConnectNoIdentifierException, match=expected1):
        RedisConnect.exists(TestModel)

    expected2 = re.escape("TestModel: Use an instance of the model or provide an identifier.")

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

    
def test__exceptions__redis_connect__foreign_key_exception():
    RedisConnect.add(TestModel(attr1="test", attr2=0, attr3=0))

    class TestFK(RedisModel):
        __testing__ = True
        __db__ = "tests"
        __action__ = {"reference": "restrict"}

        tid: int
        reference: TestModel

    expected1 = re.escape("TestModel: It was not possible to delete the model because it is a reference to another record (TestFK - tid: 0 - reference)!")
    with pytest.raises(RedisConnectForeignKeyException, match=expected1):
        RedisConnect.add(TestFK(reference="test"))
        RedisConnect.delete(TestModel, "test")

    expected2 = re.escape("TestFK2: Foreign key action is invalid (reference: a - tid: 0)!")
    with pytest.raises(RedisConnectForeignKeyException, match=expected2):
        class TestFK2(RedisModel):
            __tablename__ = "testing"
            __testing__ = True
            __db__ = "tests"
            __action__ = {"reference": "a"}

            tid: int
            reference: TestModel

        RedisConnect.add(TestFK2(reference="test"))
        RedisConnect.delete(TestModel, "test")
    
    expected3 = re.escape('TestFK: Foreign key "reference" (TestModel) with ID "test" has no record!')
    with pytest.raises(RedisConnectForeignKeyException, match=expected3):
        RedisConnect.delete(TestFK, 0, True)
        RedisConnect.delete(TestFK2, 0, True)
        test3 = TestFK(reference="test")
        RedisConnect.delete(TestModel, "test")
        RedisConnect.add(test3)

    expected4 = re.escape("TestFK3: The connection information (HOST, PORT and PASSWORD) of the reference model (TestModel) and the referenced model (TestFK3) must be the same. Differences: HOST")
    with pytest.raises(RedisConnectForeignKeyException, match=expected4):
        sett = Settings("test_error.json")
        sett.set_config(host="error")

        class TestFK3(RedisModel):
            __testing__ = True
            __db__ = "tests"
            __action__ = {"referenced": "cascade"}

            tid: int
            referenced: TestModel

        RedisConnect.add(TestModel(attr1="test", attr2=0, attr3=0))

        test2 = TestFK3(referenced="test")
        test2.__settings__ = sett

        RedisConnect.add(test2)

        if os.path.exists("test_error.json"):
            os.remove("test_error.json")

    if os.path.exists("test_error.json"):
        os.remove("test_error.json")


def test__exceptions__redis_connect__type_value_exception():
    class TestModel2(RedisModel):
        __db__ = "tests"
        __testing__ = True

        id: int
        attr1: dict = ["error"]

    model = TestModel2()

    expected = re.escape('TestModel2: Divergence in the type of the attribute "attr1". expected: "dict" - received: "list"')
    with pytest.raises(RedisConnectTypeValueException, match=expected):
        RedisConnect.add(model)


def test__exceptions__redis_connect__get_on_corrupt__exception():
    expected = re.escape('on_corrupt must be "flag", "skip" or "ignore"! on_corrupt: "raise"')

    with pytest.raises(RedisConnectGetOnCorruptException, match=expected):
        RedisConnect.get(TestModel, on_corrupt="raise")