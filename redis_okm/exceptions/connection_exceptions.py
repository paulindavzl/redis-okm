class RedisConnectionSettingsInstanceException(Exception):
    """
    The settings passed to **Connect** via the model must be an instance of Settings.
    """


class RedisConnectionModelInstanceException(Exception):
    """
    Model is not instantiated.
    """


class RedisConnectionAlreadyRegisteredException(Exception):
    """
    Model already has registration.
    """


class RedisConnectConnectionFailedException(Exception):
    """
    Connection to Redis server failed.
    """


class RedisConnectNoIdentifierException(Exception):
    """
    No identification was provided.
    """


class RedisConnectNoRecordsException(Exception):
    """
    No records with the identifier.
    """


class RedisConnectInvalidExpireException(Exception):
    """
    Expire must be a int or float value (1, 1.5, "1", "1.5")
    """


class RedisConnectForeignKeyException(Exception):
    """
    Foreign Key error
    """


class RedisConnectTypeValueException(Exception):
    """
    Invalid value type
    """