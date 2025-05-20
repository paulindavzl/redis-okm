import re
import pytest

from redis_okm.models import RedisModel
from redis_okm.exceptions.redis_model_exceptions import *


def test__exceptions__redis_model__id_exception():
    expected = re.escape("Specify the database using __db__ when structuring the model")
    with pytest.raises(RedisModelDBException, match=expected):
        class TestModel(RedisModel):
            __test__ = False

            attr1: str
            attr2: int


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
    class TestModel1(RedisModel):
        __test__ = False
        __db__ = "tests"

        attr1: str
        attr2: int

    expected1 = re.escape("TestModel1: attr2 expected a possible int value, but received a str (impossible) value!")
    with pytest.raises(RedisModelTypeValueException, match=expected1):
        TestModel1(attr2="impossible")

    expected2 = re.escape("TestModel2: The attr1 must be of type int (integer) or str (string). attr1: float")
    with pytest.raises(RedisModelTypeValueException, match=expected2):
        class TestModel2(RedisModel):
            __test__ = False
            __db__ = "tests"

            attr1: float
            attr2: str

    
def test__exceptions__redis_model__no_value_exception():
    class TestModel(RedisModel):
        __test__ = False
        __db__ = "tests"
        __idname__ = "testID"

        attr1: str

    expected = re.escape("attr1 must receive a value!")
    with pytest.raises(RedisModelNoValueException, match=expected):
        TestModel()
    

def test__exceptions__redis_model__invalid_nomeclature_exception():
    expected = re.escape('TestModel: Cannot set attributes that start and end with "__" (__error__)!')
    with  pytest.raises(RedisModelInvalidNomenclatureException, match=expected):
        class TestModel(RedisModel):
            __error__: str


def test__exceptions__redis_model__foreign_key_exception():
    expected1 = re.escape("TestModel: __action__ must be dict. __action__: error (str)")
    with pytest.raises(RedisModelForeignKeyException, match=expected1):
        class TestModel(RedisModel):
            __db__ = "tests"
            __action__ = "error"

        test = TestModel()

    expected2 = re.escape('TestModel: Define foreign key "fk" to define an action!')
    with pytest.raises(RedisModelForeignKeyException, match=expected2):
        class TestModel(RedisModel):
            __db__ = "tests"
            __action__ = {"fk": "cascade"}

        test = TestModel()

    expected3 = re.escape('TestModel: Set a value for the foreign key "fk".')
    with pytest.raises(RedisModelForeignKeyException, match=expected3):
        class TestModel(RedisModel):
            __db__ = "tests"
            __action__ = {"fk": "cascade"}
            __testing__ = True

            attr1: str
            fk: TestModel
        
        test = TestModel()

    expected4 = re.escape('TestModel: There is no record for foreign key "fk" (TestModel) with ID 0!')
    with pytest.raises(RedisModelForeignKeyException, match=expected4):
        class TestModel(RedisModel):
            __db__ = "tests"
            __action__ = {"fk": "cascade"}
            __testing__ = True

            attr1: str
            fk: TestModel
        
        test = TestModel(fk=0)

    expected5 = re.escape('TestModel: To define the foreign key "fk", add an action for it in __action__')
    with pytest.raises(RedisModelForeignKeyException, match=expected5):
        class TestModel(RedisModel):
            __db__ = "tests"
            __testing__ = True

            attr1: str
            fk: TestModel
        
        test = TestModel(fk=0)