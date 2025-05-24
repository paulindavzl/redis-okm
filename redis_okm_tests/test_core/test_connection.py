from redis_okm.tools import Getter, RedisConnect, RedisModel

from redis_okm_tests.conftest import TestModel, settings_test


def test__redis_connection__add():
    assert RedisConnect.count("tests", settings_test, "True") == 0 # garante que o db está vazio

    model = TestModel(attr1="test", attr2="7357", attr3=0)
    RedisConnect.add(model)

    assert RedisConnect.count("tests", settings_test, "True") == 1

    up_model = TestModel(attr1="test", attr2=0, attr3=0)

    RedisConnect.add(up_model, exists_ok=True) # atualiza o valor do registro

    update_model = RedisConnect.get(TestModel).filter_by(attr1="test")

    assert update_model.attr2 == 0

    assert RedisConnect.count("tests", settings_test, "True") == 1


def test__redis_connection__exists():
    model = TestModel(attr1="test", attr2="7357", attr3=0)
    assert not RedisConnect.exists(TestModel, identify="test")
    assert not RedisConnect.exists(model)

    RedisConnect.add(model)

    assert RedisConnect.exists(TestModel, identify="test")
    assert RedisConnect.exists(model)


def test__redis_connection__get():
    assert RedisConnect.get(TestModel).length == 0

    instance1 = TestModel(attr1="test1", attr2=7357, attr3="73.57")
    instance2 = TestModel(attr1="test2", attr2=7357, attr3="73.57")

    RedisConnect.add(instance1)
    RedisConnect.add(instance2)

    models = RedisConnect.get(TestModel)

    assert isinstance(models, Getter)
    assert models.length == 2

    model1 = models.filter_by(attr1="test1")
    model2 = models.filter_by(attr1="test2")

    assert isinstance(model1, TestModel)
    assert isinstance(model2, TestModel)


def test__redis_connect__add_get__foreign_key():
    assert not RedisConnect.exists(TestModel, "test")
    RedisConnect.add(TestModel(attr1="test", attr2=7357, attr3="73.57"))

    class TestFK(RedisModel):
        __db__ = "tests"
        __testing__ = True
        __action__ = {"test_model":"cascade"}

        tid: int
        test_model: TestModel

    assert not RedisConnect.exists(TestFK, identify=0)
    fk = TestFK(test_model="test")
    RedisConnect.add(fk)

    test_fk = RedisConnect.get(TestFK).filter_by(tid=0)
    assert test_fk.tid == 0

    test_model = test_fk.test_model()

    assert test_model.attr1 == "test"


def test__redis_connect__delete():
    models = []
    for i in range(4):
        model = TestModel(attr1=i, attr2=i, attr3=i)
        RedisConnect.add(model)
        models.append(model)

    assert RedisConnect.count("tests", settings_test, "True") == 4

    RedisConnect.delete(TestModel, 0)
    RedisConnect.delete(models[1])

    assert RedisConnect.count("tests", settings_test, "True") == 2

    RedisConnect.delete(TestModel, [2, 3])

    assert RedisConnect.count("tests", settings_test, "True") == 0


def test__redis_connect__delete__foreign_key():
    RedisConnect.add(TestModel(attr1="test", attr2=0, attr3=0))
    assert RedisConnect.exists(TestModel, "test")

    class TestFK(RedisModel):
        __db__ = "tests"
        __testing__ = True
        __action__ = {"test_model":"cascade"}

        tid: int
        test_model: TestModel

    test = TestFK(test_model="test")
    RedisConnect.add(test)
    assert RedisConnect.exists(test)

    RedisConnect.delete(TestModel, "test")

    assert not RedisConnect.exists(test)


def test__redis_connect__count():
    assert RedisConnect.count("tests", settings_test, "True") == 0

    model = TestModel(attr1="test", attr2="7357", attr3=0)
    RedisConnect.add(model)

    assert RedisConnect.count("tests", settings_test, "True") == 1


def test__redis_connect__get__corrupt():
    test = TestModel(attr1="test", attr2=0, attr3=0)
    RedisConnect.add(test)

    handler = RedisConnect._connect(TestModel)
    name = RedisConnect._get_name(test)

    handler.hset(name, mapping={"attr2":"10"})

    flag = RedisConnect.get(TestModel, on_corrupt="flag")
    corrupted = flag.report()
    assert flag.has_corrupted
    assert corrupted == ["test"]


    skip = RedisConnect.get(TestModel, on_corrupt="skip").has_corrupted
    assert not skip

    ignore = RedisConnect.get(TestModel,on_corrupt="ignore")
    assert not ignore.has_corrupted

    model = ignore.filter_by(attr1="test")
    assert model.attr2 == 10

