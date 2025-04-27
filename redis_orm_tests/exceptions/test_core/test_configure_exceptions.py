import re
import pytest

from redis_orm import Settings


def test__exceptions__settings__file_not_found_error(test_settings: Settings):
    expected = re.escape("The invalid_file.env file for environment variables was not found!")

    with pytest.raises(FileNotFoundError, match=expected):
        test_settings.set_config(envfile="invalid_file.env")


def test__exceptions__settings__environment_error(test_settings_env: Settings):
    expected = re.escape('"TESTING" key does not exist in environment variables (envfile_test.env)!')

    with pytest.raises(EnvironmentError, match=expected):
        test_settings_env._get_env_value("test", "env:TESTING")


def test__exceptions__settings__key_error(test_settings: Settings):
    expected = re.escape('There is no database named: test_db_invalid! User settings.set_config(dbname="test_db_invalid:db_index")')

    with pytest.raises(KeyError, match=expected):
        test_settings.get_db("test_db_invalid")


def test__exceptions__settings__value_error(test_settings: Settings):
    expected = re.escape('Could not set database "test_config" with index 15 because it already belongs to a database named (tests: 15)!')

    with pytest.raises(ValueError, match=expected):
        test_settings.set_config(dbname="test_config:15")