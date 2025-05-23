from __future__ import annotations

from ..core import _model
from ..exceptions.getter_model_exceptions import *


class Getter:
    """
    agrupa e centraliza retornos do método RedisConnect.get(...)
    """
    def __init__(self, get_returns: list[_model]):
        if not isinstance(get_returns, list):
            raise GetterNotListModelsException(f"get_returns must be a list! get_returns: {get_returns} ({type(get_returns).__name__})")
        getter_type: classmethod = None
        for getter in get_returns:
            base_name = getter.__base__.__name__ if callable(getter) else getter.__class__.__base__.__name__
            if base_name != "RedisModel":
                raise GetterNotRedisModelException(f"All models passed to Getter must be a class that inherits from RedisModel. {type(getter).__name__} does not inherit RedisModel!")
            elif getter_type and not isinstance(getter, getter_type):
                raise GetterDifferentModelsException(fr"All models passed to Getter must be of the same type/class ({getter_type.__name__}). {type(getter).__name__} != {getter_type.__name__}")
            elif not getter_type:
                getter_type = type(getter)

        self._getters = get_returns


    @property
    def list(self) -> list:
        return self._getters


    @property
    def length(self) -> int:
        """
        retorna a quantidade de modelos armazenados
        """
        return len(self._getters)

    
    def filter_by(self, **conditions) -> None|Getter|_model:
        """
        filtra os models de acordo com as condições
        """
        models = []
        for model in self._getters:
            for param, condition in conditions.items():
                if param not in getattr(model, "__annotations__", {}):
                    raise GetterAttributeException(f"{type(model).__name__} does not have {param} attribute!")
                
                attr = getattr(model, param)
                typ: type = type(attr)
                try:
                    if attr == typ(condition):
                        models.append(model)
                except ValueError:
                    raise GetterConditionTypeException(f'The "{param}" condition must be a possible {typ.__name__}. {param}: "{condition}" ({type(condition).__name__})')

        if len(models) == 1:
            mdl = models[0]
            if mdl.__status__:
                return mdl
            raise GetterCorruptionException(f"{type(model).__name__}: The information in this record ({model.__idname__}: {getattr(model, model.__idname__)}) is corrupt!")
        elif len(models) > 1:
            return Getter(models)
        return None
        

    def first(self, reference: None|str=None) -> None|_model:
        """
        retorna o primeiro modelo na lista
        """
        if reference is not None and not isinstance(reference, str):
            raise GetterReferenceTypeException(f"reference must be a str (string)! reference: {reference} ({type(reference).__name__})")
        
        resp = ""
        if reference:
            models = {}
            references = []
            for model in self._getters:
                ref = getattr(model, reference, None)
                if ref is None:
                    raise GetterAttributeException(f"{type(model).__name__} does not have the {reference} attribute!")
                
                models[ref] = model
                references.append(ref)

            if not references:
                raise ValueError(f"The reference used did not return any model! reference: {reference}")
            
            references = sorted(references)
            key = references[0]
            resp = models.get(key)
            
        resp = self._getters[0] if self._getters else None
        if resp:
            if resp.__status__:
                return resp
            raise GetterCorruptionException(f"{type(resp).__name__}: The information in this record ({resp.__idname__}: {getattr(resp, resp.__idname__)}) is corrupt!")
        

    def last(self, reference: None|str=None) -> None|_model:
        """
        retorna o último modelo na lista
        """
        if reference is not None and not isinstance(reference, str):
            raise GetterReferenceTypeException(f"reference must be a str (string)! reference: {reference} ({type(reference).__name__})")
        
        resp = ""
        if reference:
            models = {}
            references = []
            for model in self._getters:
                ref = getattr(model, reference, None)
                if ref is None:
                    raise GetterAttributeException(f"{type(model).__name__} does not have the {reference} attribute!")
                
                models[ref] = model
                references.append(ref)

            if not references:
                raise ValueError(f"The reference used did not return any model! reference: {reference}")
            
            references = sorted(references, reverse=True)
            key = references[0]
            resp = models.get(key)
        resp = self._getters[-1] if self._getters else None
    
        if resp:
            if resp.__status__:
                return resp
            raise GetterCorruptionException(f"{type(resp).__name__}: The information in this record ({resp.__idname__}: {getattr(resp, resp.__idname__)}) is corrupt!")
        
    
    @property
    def has_corrupted(self) -> bool:
        """
        Verifica se possui algum modelo corrompido
        """
        for model in self._getters:
            if model.__status__ is False:
                return True
            
        return False
    

    def valid_only(self) -> Getter|None:
        """
        Retorna somente modelos válidos
        """
        getters = []
        for model in self._getters:
            if model.__status__:
                getters.append(model)

        if getters:
            return Getter(getters)
        

    def report(self) -> list[str|int]|None:
        """
        Retorna os modelos corrompidos
        """
        models = []
        for model in self._getters:
            if model.__status__ is False:
                identify = getattr(model, model.__idname__)
                models.append(identify)
        
        return models if models else None