import os
import pytest

from redis_okm.models import RedisModel
from redis_okm import settings, Settings
from redis_okm.core.connection import RedisConnect


@pytest.fixture(autouse=True)
def check_if_use_tests():
    if not settings.use_tests:
        pytest.fail("Tests have been disabled! Use settings.set_config(use_tests=True)")


settings_test = Settings("test_redis_configure.json")
settings_test.set_config(testing=True, timeout=0.1, retry_on_timeout=False)


class TestModel(RedisModel):
    __test__ = False
    __db__ = "tests"
    __tablename__ = "test"
    __settings__ = settings_test
    __testing__ = True
    __autoid__ = False

    attr1: str
    attr2: int
    attr3: float
    default = "default_value"


@pytest.fixture(autouse=True)
def remove_test_redis_configure():
    yield
    if os.path.exists("test_redis_configure.json"):
        os.remove("test_redis_configure.json")
    if os.path.exists("envfile_test.env"):
        os.remove("envfile_test.env")


@pytest.fixture
def test_settings() -> Settings:
    __test__ = False
    sett = Settings()
    sett.__configure_path__ = "test_redis_configure.json"
    return sett


@pytest.fixture
def test_settings_env(test_settings: Settings) -> Settings:
    __test__ = False
    with open("envfile_test.env", "w") as file:
        file.write("""HOST=TEST_ENV_HOST
PORT=0000
PASSWORD=TEST_ENV_PASSWORD
""")
    test_settings.set_config(envfile="envfile_test.env", host="env:HOST", port="env:PORT", password="env:PASSWORD")
    return test_settings


@pytest.fixture(autouse=True)
def restart_db():
    if settings.restart_db:
        RedisConnect.restart_full_db(db="__all__", settings=settings_test)