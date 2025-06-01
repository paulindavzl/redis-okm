class SettingsEnvfileNotFoundException(Exception):
    """
    Envfile not found.
    """


class SettingsEnvkeyException(Exception):
    """
    The key does not exist in the Envfile.
    """


class SettingsUnknownDBException(Exception):
    """
    The searched db does not exist.
    """


class SettingsExistingDBException(Exception):
    """
    The database is already named and cannot be overwritten.
    """


class SettingsInvalidDBNameException(Exception):
    """
    Invalid database index definition.
    """