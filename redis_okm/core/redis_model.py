from __future__ import annotations
from types import MemberDescriptorType

from .. import settings
from .connection import RedisConnect
from ..exceptions.redis_model_exceptions import *



class RedisModel:
    """
    Base para todos os modelos em RedisOKM
    """
    __slots__ = ["__db__", "__instancied__", "__idname__", "__tablename__", "__autoid__", "__testing__", "__hashid__", "__settings__", "__expire__", "to_dict", "__action__", "__foreign_keys__", "__references__", "__key__", "__status__", "__params__"]

    def _set_attributes(cls, ann: dict[str|type]):
        cls_name = cls.__name__ if callable(cls) else type(cls).__name__
        cls.__slots__ = getattr(cls, "__slots__", []) + RedisModel.__slots__

        for attr in ann.keys():
            if attr.startswith("__") and attr.endswith("__") and attr not in cls.__slots__:
                raise RedisModelInvalidNomenclatureException(f'{cls_name}: Cannot set attributes that start and end with "__" ({attr})!')
        # valores padrões dos atributos
        d = {
            "__db__": None, "__idname__": None, "__autoid__": True, "__hashid__": False, "__testing__": False, "__tablename__": None, "__settings__": settings, "__expire__": None, "__action__": None
        }
        
        for attr in dir(cls):
            if isinstance(getattr(cls, attr, None), MemberDescriptorType) and attr in d:
                setattr(cls, attr, d[attr])

        # obtém informações do modelo
        db = getattr(cls, "__db__", None)
        idname = getattr(cls, "__idname__", None)
        autoid = getattr(cls, "__autoid__", True)
        hashid = getattr(cls, "__hashid__", False)
        testing = getattr(cls, "__testing__", False)
        tablename = getattr(cls, "__tablename__", None)
        sett = getattr(cls, "__settings__", settings)
        expire = getattr(cls, "__expire__", None)
        action = getattr(cls, "__action__", None)
        params = getattr(cls, "__params__", {})

        if db is None:
            raise RedisModelAttributeException(f"{cls_name}: Specify the database using __db__ when structuring the model")
        elif isinstance(db, str):
            db = sett.get_db(db)

        if not idname:
            for attr in ann:
                if not attr.startswith("__"):
                    idname = attr
                    break
        
        ann[idname] = ann[idname] if ann.get(idname) else str

        if not tablename:
            tablename = cls.__name__.lower()
            
        # repassa a informações para o modelo (exceção de __db__ que é obrigatório)
        cls.__db__ = db
        cls.__idname__ = idname
        cls.__settings__ = sett
        cls.__tablename__ = tablename
        cls.__testing__ = testing
        cls.__autoid__ = autoid
        cls.__hashid__ = hashid
        cls.__expire__ = expire
        cls.__action__ = action
        cls.__references__ = {}
        cls.to_dict = {}
        cls.__status__ = True
        cls.__key__ = "__await_identify__"
        cls.__params__ = params

        cls.__foreign_keys__: dict[type, any] = {}
        for attr, value in ann.items():
            if isinstance(value, cls):
                raise RedisModelForeignKeyException(f"{cls_name}: You cannot define a foreign key in a model of itself ({attr})!")
            if getattr(value, "__base__", None) is RedisModel:
                fk_settings = value(instance=False).__settings__
                differences = [
                    "HOST" if fk_settings.host != cls.__settings__.host else "", 
                    "PORT" if fk_settings.port != cls.__settings__.port else "",
                    "PASSWORD" if fk_settings.password != cls.__settings__.password else ""
                ] 
                differences = [d for d in differences if d]
                if differences:
                    raise RedisModelForeignKeyException(f"{cls_name}: The connection information (HOST, PORT and PASSWORD) of the reference model ({value.__name__}) and the referenced model ({cls_name}) must be the same. Differences: {", ".join(differences)}")
                    
                cls.__foreign_keys__[attr] = {"model": value}

        if ann[cls.__idname__] not in [str, int]:
            raise RedisModelTypeValueException(f"{cls_name}: The {cls.__idname__} must be of type int (integer) or str (string). {cls.__idname__}: {ann[cls.__idname__].__name__}")

        if cls.__hashid__:
            setattr(cls, cls.__idname__, str)

        cls.__instancied__ = False


    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        ann: dict[type] = cls.__annotations__

        RedisModel._set_attributes(cls, ann)


    def __init__(self, **attributes):
        """
        Cria uma instância de um modelo que usa **RedisModel**

        Params:

            **attributes - atributos/informações declaradas na estrutura do modelo.
        
        Examples:

            class UserModel(RedisModel):
                ...
                # attributes
                name: str
                age: int
            
            user = UserModel(name="example_user", age=18)

        Veja mais informações no [**GitHub**](https://github.com/paulindavzl/redis-okm "GitHub RedisOKM")
        """
        cls_name = type(self).__name__
        _set_fk = attributes.pop("set_fk") if attributes.get("set_fk") is not None else True 
        if not attributes.get("instance") is False:
            attrs = {}
            ann = self.__annotations__

            if not self.__idname__ in attributes and self.__autoid__:
                attributes[self.__idname__] = "__await_autoid__"

            if self.__action__ and _set_fk:
                # garante que as ações das chaves estrangeiras são dict
                if not isinstance(self.__action__, dict):
                    raise RedisModelAttributeException(f"{cls_name}: __action__ must be dict. __action__: {self.__action__} ({type(self.__action__).__name__})")
                
                for ref in self.__action__.keys():
                    if not ref in self.__foreign_keys__: 
                        raise RedisModelForeignKeyException(f'{cls_name}: Define foreign key "{ref}" to define an action!')
                    elif not ref in attributes and _set_fk:
                        raise RedisModelForeignKeyException(f'{cls_name}: Set a value for the foreign key "{ref}".')
                    
                    fk_model: type[RedisModel] = self.__foreign_keys__[ref]["model"] # obtém o modelo da chave estrangeira
                    class Return(fk_model):
                        pass
                    
                    fk_idname = fk_model.__idname__
                    id = attributes.pop(ref)
                    if type(id) == fk_model:
                        id = getattr(id, fk_idname)
                    typ_id = str if self.__autoid__ else ann[fk_idname]
                    id = typ_id(id)
                    f_id = {fk_idname:id} # filtro para id

                    if not RedisConnect.get(fk_model).filter_by(**f_id):
                        raise RedisModelForeignKeyException(f'{cls_name}: There is no record for foreign key "{ref}" ({fk_model.__name__}) with ID {id if isinstance(id, int) else f"{id}"}!')

                    def foreign_key() -> Return:
                        fk = RedisConnect.get(fk_model).filter_by(**f_id)
                        return fk
                    
                    setattr(self, ref, foreign_key)
                    self.__foreign_keys__[ref]["id"] = id
                    self.to_dict[ref] = id
                    

            # passa as informações para o modelo caso ele aceite-as
            for attr, value in attributes.items():
                if attr not in ann:
                    raise RedisModelAttributeException(f'{cls_name} does not have "{attr}" attribute!')
                elif attr.startswith("__") and attr.endswith("__"):
                    raise RedisModelAttributeException(f'{cls_name}: Cannot set attributes that start and end with "__" ({attr})!')
                      
                typ: type = ann[attr]
                if isinstance(getattr(typ, "__base__", None), RedisModel):
                    raise RedisModelForeignKeyException(f'{cls_name}: To define the foreign key "{attr}", add an action for it in __action__')
                
                try:
                    if typ in [dict, list, tuple]:
                        if not isinstance(value, typ):
                            raise RedisModelTypeValueException(f'{cls_name}: Divergence in the type of the attribute "{attr}". expected: "{typ.__name__}" - received: "{type(value).__name__}"')
                    attrs[attr] = typ(value) if value != "__await_autoid__" else value
                except ValueError as e:
                    raise RedisModelTypeValueException(f"{cls_name}: {attr} expected a possible {typ.__name__} value, but received a {type(value).__name__} ({value}) value!")
                except Exception as e:
                    raise e

            for attr, value in attrs.items():
                setattr(self, attr, value)

            self.to_dict = attrs # define to_dict

            ann = self.__annotations__ # recarrega __annotations__
            for attr in ann:
                if not str(attr).startswith("__") and attr not in attrs and attr not in self.__foreign_keys__:
                    name = type(self)
                    if not hasattr(name, attr):
                        raise RedisModelAttributeException(f"{cls_name}: {attr} must receive a value!")
                    value = getattr(name, attr)
                    if callable(value):
                        value = value()
                    setattr(self, attr, value)
                    self.to_dict[attr] = value
            
            self.__instancied__ = True
        else:
            identify = attributes.get("identify")
            if identify is not None:
                idname = self.__idname__
                typ: type = self.__class__.__annotations__[idname]
                setattr(self, idname, typ(identify))

        
     



# created by:


# █▀█ ▄▀█ █░█ █░░ █ █▄░█ █▀▄ ▄▀█ █░█ ▀█ █░░
# █▀▀ █▀█ █▄█ █▄▄ █ █░▀█ █▄▀ █▀█ ▀▄▀ █▄ █▄▄

# https://github.com/paulindavzl
#