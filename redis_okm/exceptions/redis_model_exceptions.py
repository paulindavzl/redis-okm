class RedisModelDBException(Exception):
    """
    Database not informed.
    """


class RedisModelAttributeException(Exception):
    """
    Non-existent attribute in the Model.
    """


class RedisModelTypeValueException(Exception):
    """
    Invalid attribute value.
    """


class RedisModelNoValueException(Exception):
    """
    The attribute did not receive any value.
    """


class RedisModelForeignKeyException(Exception):
    """
    Foreign Key error
    """


class RedisModelInvalidNomenclatureException(Exception):
    """
    The attribute naming is invalid.
    """