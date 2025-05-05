class RedisConnectionSettingsInstanceException(TypeError):
    """
    The settings passed to **Connect** via the model must be an instance of Settings.
    """
    __RedisOKM__ = True


class RedisConnectionModelInstanceException(TypeError):
    """
    Model is not instantiated.
    """
    __RedisOKM__ = True


class RedisConnectionAlreadyRegisteredException(ValueError):
    """
    Model already has registration.
    """
    __RedisOKM__ = True


class RedisConnectConnectionFailedException(ConnectionError):
    """
    Connection to Redis server failed.
    """
    __RedisOKM__ = True


class RedisConnectNoIdentifierException(ValueError):
    """
    No identification was provided.
    """
    __RedisOKM__ = True


class RedisConnectNoRecordsException(ValueError):
    """
    No records with the identifier.
    """
    __RedisOKM__ = True



