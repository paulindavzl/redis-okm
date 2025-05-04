import re
import pytest

from redis_orm import Settings
from redis_orm.exceptions.configure_exceptions import *


def test__exceptions__settings__envfile_not_found_exception(test_settings: Settings):
    expected = re.escape("The invalid_file.env file for environment variables was not found!")

    with pytest.raises(SettingsEnvfileNotFoundException, match=expected):
        test_settings.set_config(envfile="invalid_file.env")


def test__exceptions__settings__envkey_exception(test_settings_env: Settings):
    expected = re.escape('"TESTING" key does not exist in environment variables (envfile_test.env)!')

    with pytest.raises(SettingsEnvkeyException, match=expected):
        test_settings_env._get_env_value("test", "env:TESTING")


def test__exceptions__settings__unknowm_db_exception(test_settings: Settings):
    expected = re.escape('There is no database named: test_db_invalid! User settings.set_config(dbname="test_db_invalid:db_index")')

    with pytest.raises(SettingsUnknownDBException, match=expected):
        test_settings.get_db("test_db_invalid")


def test__exceptions__settings__existing_db_exception(test_settings: Settings):
    expected = re.escape('Could not set database "test_config" with index 15 because it already belongs to a named database (tests: 15)!')

    with pytest.raises(SettingsExistingDBException, match=expected):
        test_settings.set_config(dbname="test_config:15")


def test__exceptions__settings__invalid_dbname_exception(test_settings: Settings):
    expected = re.escape('Database index definition must be in two parts, separated by ":"! Invalid definition: test14.')

    with pytest.raises(SettingsInvalidDBNameException, match=expected):
        test_settings.set_config(dbname="test14")