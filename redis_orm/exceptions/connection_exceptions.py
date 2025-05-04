class RedisConnectionSettingsInstanceException(TypeError):
    """
    The settings passed to **Connect** via the model must be an instance of Settings.
    """
    __redisorm__ = True


class RedisConnectionModelInstanceException(TypeError):
    """
    Model is not instantiated.
    """
    __redisorm__ = True


class RedisConnectionAlreadyRegisteredException(ValueError):
    """
    Model already has registration.
    """
    __redisorm__ = True


class RedisConnectConnectionFailedException(ConnectionError):
    """
    Connection to Redis server failed.
    """
    __redisorm__ = True


class RedisConnectNoIdentifierException(ValueError):
    """
    No identification was provided.
    """
    __redisorm__ = True


class RedisConnectNoRecordsException(ValueError):
    """
    No records with the identifier.
    """
    __redisorm__ = True



