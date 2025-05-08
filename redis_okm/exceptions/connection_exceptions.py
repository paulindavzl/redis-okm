class RedisConnectionSettingsInstanceException(TypeError):
    """
    The settings passed to **Connect** via the model must be an instance of Settings.
    """


class RedisConnectionModelInstanceException(TypeError):
    """
    Model is not instantiated.
    """


class RedisConnectionAlreadyRegisteredException(ValueError):
    """
    Model already has registration.
    """


class RedisConnectConnectionFailedException(ConnectionError):
    """
    Connection to Redis server failed.
    """


class RedisConnectNoIdentifierException(ValueError):
    """
    No identification was provided.
    """


class RedisConnectNoRecordsException(ValueError):
    """
    No records with the identifier.
    """


class RedisConnectInvalidExpireException(ValueError):
    """
    Expire must be a int or float value (1, 1.5, "1", "1.5")
    """
