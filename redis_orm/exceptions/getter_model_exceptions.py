class GetterNotListModelsException(TypeError):
    """
    **Getter** requires a list of models.
    """


class GetterNotRedisModelException(ValueError):
    """
    A model did not inherit **RedisModel**.
    """


class GetterDifferentModelsException(TypeError):
    """
    Type/class model different from the others.
    """


class GetterAttributeException(AttributeError):
    """
    Condition or reference attribute does not exist in the model.
    """


class GetterReferenceTypeException(TypeError):
    """
    Reference must be string (str).
    """


