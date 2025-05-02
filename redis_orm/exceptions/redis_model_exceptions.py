class RedisModelDBException(AttributeError):
    """
    Database not informed.
    """


class RedisModelAttributeException(AttributeError):
    """
    Non-existent attribute in the Model.
    """


class RedisModelTypeValueException(ValueError):
    """
    Invalid attribute value.
    """


class RedisModelNoValueException(AttributeError):
    """
    The attribute did not receive any value.
    """