from redis_okm.models.getter_model import Getter
from redis_okm.core.connection import RedisConnect

from redis_okm_tests.conftest import TestModel


def test__redis_connection__add():
    assert RedisConnect.count(TestModel) == 0 # garante que o db está vazio

    model = TestModel(attr1="test", attr2="7357", attr3=0)
    RedisConnect.add(model)

    assert RedisConnect.count(TestModel) == 1

    up_model = TestModel(attr1="test", attr2=0, attr3=0)

    RedisConnect.add(up_model, exists_ok=True) # atualiza o valor do registro

    update_model = RedisConnect.get(TestModel)

    assert update_model.attr2 == 0

    assert RedisConnect.count(TestModel) == 1


def test__redis_connection__exists():
    model = TestModel(attr1="test", attr2="7357", attr3=0)
    assert not RedisConnect.exists(TestModel, identify="test")
    assert not RedisConnect.exists(model)

    RedisConnect.add(model)

    assert RedisConnect.exists(TestModel, identify="test")
    assert RedisConnect.exists(model)


def test__redis_connection__get():
    assert not RedisConnect.get(TestModel)

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


def test__redis_connect__delete():
    models = []
    for i in range(4):
        model = TestModel(attr1=i, attr2=i, attr3=i)
        RedisConnect.add(model)
        models.append(model)

    assert RedisConnect.count(TestModel) == 4

    RedisConnect.delete(TestModel, 0)
    RedisConnect.delete(models[1])

    assert RedisConnect.count(TestModel) == 2

    RedisConnect.delete(TestModel, [2, 3])

    assert RedisConnect.count(TestModel) == 0


def test__redis_connect__count():
    assert RedisConnect.count(TestModel) == 0

    model = TestModel(attr1="test", attr2="7357", attr3=0)
    RedisConnect.add(model)

    assert RedisConnect.count(TestModel) == 1