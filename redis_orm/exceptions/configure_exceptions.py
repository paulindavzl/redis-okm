class SettingsEnvfileNotFoundException(FileNotFoundError):
    """
    Envfile not found.
    """


class SettingsEnvkeyException(EnvironmentError):
    """
    The key does not exist in the Envfile.
    """


class SettingsUnknownDBException(KeyError):
    """
    The searched db does not exist.
    """


class SettingsExistingDBException(ValueError):
    """
    The database is already named and cannot be overwritten.
    """


class SettingsInvalidDBNameException(ValueError):
    """
    Invalid database index definition.
    """