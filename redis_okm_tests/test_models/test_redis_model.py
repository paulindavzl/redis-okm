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
    assert model.__hashid__
    assert model.__idname__ == "attr1"
    assert model.__tablename__ == "test"
    assert model.__settings__ == settings_test
    assert model.__instancied__