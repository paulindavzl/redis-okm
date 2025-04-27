from redis_orm import Settings


# verifica se Settings está iniciando corretamente
def test__settings__get_values(test_settings: Settings):
    assert test_settings.host == "localhost"
    assert test_settings.retry_on_timeout == [True, 3]


# tenta obter valores de um env
def test__settings__get_values_env(test_settings_env: Settings):
    assert test_settings_env.host == "TEST_ENV_HOST"
    assert test_settings_env.port == 0000
    assert test_settings_env.password == "TEST_ENV_PASSWORD"


# testa definir e criar novas configurações
def test__settings__set__config(test_settings: Settings):
    assert test_settings.host == "localhost"

    test_settings.set_config(host="test_localhost", new_config="this is a new config")

    assert test_settings.host == "test_localhost"
    print(test_settings.__annotations__)
    assert test_settings.new_config == "this is a new config"


# testa obter os bancos de dados nomeados
def test__settings__get_db(test_settings: Settings):
    assert test_settings.get_db("tests") == 15

    test_settings.set_config(dbnames=["tests:14", "tests1:0"])

    assert test_settings.get_db("tests1") == 0
    assert test_settings.get_db("tests") == 14