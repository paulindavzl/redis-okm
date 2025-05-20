from redis_okm.tools import RedisModel, RedisConnect
from redis_okm_tests.conftest import TestModel, settings_test


# garante que atribuição customizada feita por RedisModel está funcionando
def test_create_model():
    model = TestModel(
        attr1="test",
        attr2="7357",
        attr3=73.57
    )

    assert model.attr1 == "test"
    assert model.attr2 == 7357
    assert model.attr3 == 73.57
    assert model.default == "default_value"

    assert model.__db__ == 15
    assert not model.__autoid__
    assert not model.__hashid__
    assert model.__idname__ == "attr1"
    assert model.__tablename__ == "test"
    assert model.__settings__ == settings_test
    assert model.__instancied__


def test__create_model__foreign_key():
    class TestFK(RedisModel):
        __db__ = "tests"
        __testing__ = True
        __action__ = {"fk": "cascade"}

        fk_id: int
        attr1: str
        fk: TestModel

    RedisConnect.add(TestModel(attr1="test", attr2="7357", attr3=73.57)) # adiciona o modelo no banco de dados

    test_fk = TestFK(attr1="testing", fk="test")

    reference = test_fk.fk()

    assert reference.attr1 == "test"
    assert reference.attr2 == 7357