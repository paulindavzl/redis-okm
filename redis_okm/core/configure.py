import os
import json
import dotenv
import string

from ..exceptions.configure_exceptions import *


class Settings:
    """
    Configuração para conexão do Redis

    Cada instância pode ter suas configurações isoladas. Para isso, use:
        ```
        new_settings = Settings()
        new_settings.__configure_path__ = "new_settings_path.json" # note que deve ser um arquivo JSON
        ```
    Veja mais informações no [**GitHub**](https://github.com/paulindavzl/redis-okm "GitHub RedisOKM")
    """
    use_tests: bool
    db_test: str
    restart_db: bool
    host: str
    port: int
    password: str
    decode_response: str
    timeout: float
    retry_on_timeout: str|list[bool]
    max_connections: int
    blocking_timeout: int
    separator: str
    prefix: str
    hash_algorithm: str


    def __init__(self, path: str="redis_configure.json"):
        self.__configure_path__ = str(path)
        self._dbnames = {}
        self._envfile = None

        self.reload()


    def _get_file_data(self) -> dict:
        response: dict
        if not os.path.exists(self.__configure_path__):
            response = self._default_configure()
        else:
            with open(self.__configure_path__, "r") as file:
                response = json.load(file)

        return response


    def _set_settings(self):
        self._envfile = self._settings.get("envfile")
        if self._envfile:
            if not os.path.exists(self._envfile):
                raise SettingsEnvfileNotFoundException(f"The {self._envfile} file for environment variables was not found!")

        for set_names, settings in self._settings.items():
            if isinstance(settings, dict) and set_names != "dbnames":
                for setting, value in settings.items():
                    if str(value).startswith("env:"):
                        value = self._get_env_value(setting, value)
                    setattr(self, setting, value)

            elif set_names == "dbnames":
                for dbname, db_index in settings.items():
                    self._dbnames[dbname] = int(db_index)

            elif set_names != "envfile":
                setattr(self, set_names, settings)

        if self.prefix == "cwd":
            chars = list(string.ascii_lowercase + string.digits + "_")
            splits = os.getcwd().split(os.sep)
            prefix = splits[-1].lower().replace("-", "_")
            for c in prefix:
                if c not in chars:
                    prefix = prefix.replace(c, "")
            
            self.prefix = prefix


    def _get_env_value(self, config_name: str, value: str) -> any:
        dotenv.load_dotenv(self._envfile, override=True)
        typ = self._types(config_name)
        value = value.split("env:")[1].strip()
        env = os.getenv(value)
        print(env, value)
        if env is None:
            raise SettingsEnvkeyException(f'"{value}" key does not exist in environment variables ({self._envfile})!')
        value = typ(env)

        return value
    

    @staticmethod
    def _types(config_name: str) -> type:
        _types = {
            "int": [
                "port", "max_connections", "blocking_timeout"
            ],
            "float": [
                "timeout"
            ],
            "list": [
                "retry_on_timeout"
            ]
        }
        if config_name in _types["int"]: return int
        elif config_name in _types["float"]: return float
        elif config_name in _types["list"]: return list
        return str
    

    @property
    def redis_info(self) -> dict:
        """
        retorna todas as informações de conexão com Redis
        """
        infos = {
            "host": self.host,
            "port": self.port,
            "password": self.password if self.password else None,
            "decode_responses": bool(self.decode_response),
            "socket_timeout": self.timeout,
            "retry_on_timeout": bool(self.retry_on_timeout[0]) if isinstance(self.retry_on_timeout, list) else False,
            "max_connections": self.max_connections,
            "socket_connect_timeout": self.blocking_timeout
        }
        return infos
    
    
    def _default_configure(self):
        default = {
            "envfile": None,
            "tests": {
                "use_tests": True,
                "db": "tests",
                "restart_db": True
            },
            "network": {
                "host": "localhost",
                "port": 6379,
                "password": None
            },
            "connection": {
                "decode_response": True,
                "timeout": 30,
                "retry_on_timeout": [True, 3]
            },
            "pools": {
                "max_connections": 10,
                "blocking_timeout": 3
            },
            "structure": {
                "separator": ":",
                "prefix": "cwd",
                "hash_algorithm": "md5"
            },
            "dbnames": {
                "tests": 15
            },
            "others": {}
        }
    
        with open(self.__configure_path__, "w") as file:
            json.dump(default, file, indent=4)

        return default
    

    def get_db(self, dbname: str) -> int:
        """
        Retorna o índice do banco de dados, caso exista

        Params:

            dbname (str) - nome do índice do banco de dados nomeado

        Examples:

            settings = Settings()

            db_tests = settings.get_db("tests") # "tests" já vem nomeado por padrão (15)

            '''
            Para nomear um índice use: 
                Settings().set_config(dbname="name:index") ou 
                Settings().set_config(dbname=["name1:index", "name2:index"])
            '''

        Veja mais informações no [**GitHub**](https://github.com/paulindavzl/redis-okm "GitHub RedisOKM")
        """
        if dbname in self._dbnames:
            return self._dbnames[dbname]
        raise SettingsUnknownDBException(f'There is no database named: {dbname}! User settings.set_config(dbname="{dbname}:db_index")')


    def set_config(self, edit_dbname: bool=False, **configs):
        """
        Define / altera configurações

        Params:

            edit_dbname (bool) - permite editar um banco de dados nomeado
            **configs - configurações que serão definidas

        Examples:

            settings = Settings()

            settings.set_config(host="localhost", port=6379, ...)

            # existe um configuração especial, nomear índices de bancos de dados

            settings.set_config(dbname="name:index") ou 
            settings.set_config(dbname=["name1:index", "name2:index", ...])

            '''
            Note:
                "name" represente o nome do índice e "index" representa o índice. ":" representa o sinal de "="

                settings.set_config(dbname="tests:15") - tests já vem nomeado por padrão, representando índice 15
            '''

            # Você pode criar suas próprias configurações, desde que não tenham nomes já usados:

            settings.set_config(my_config="value")
        
        Veja mais informações no [**GitHub**](https://github.com/paulindavzl/redis-okm "GitHub RedisOKM")
        """
        local_config = {
            "dbname": "dbnames",
            "separator": "structure",
            "prefix": "structure",
            "max_connections": "pools",
            "blocking_timeout": "pools",
            "decode_response": "connection",
            "timeout": "connection",
            "retry_on_timeout": "connection",
            "host": "network",
            "port": "network",
            "password": "network",
            "use_tests": "tests",
            "db_test": "tests",
            "restart_db": "tests",
            "hash_algorithm": "structure"
        }
        settings = self._get_file_data()
        for config, value in configs.items():
            if config in local_config:
                local = local_config[config]
                if config == "dbname":
                    values = [value] if not isinstance(value, list) else value
                    for v in values:
                        if not ":" in v:
                            raise SettingsInvalidDBNameException(f'Database index definition must be in two parts, separated by ":"! Invalid definition: {v}.')
                        split = str(v).split(":")
                        config = split[0].strip()
                        value = int(split[1].strip())
                        dbs = {v: k for k, v in self._dbnames.items()}
                        for db_index, dbname in dbs.items():
                            if (db_index == value and dbname != config) or (dbname == config and db_index != value):
                                if not edit_dbname:
                                    named_db =  f"{dbs.get(value, dbname)}: {value if dbs.get(value) else self._dbnames[dbname]}"
                                    raise SettingsExistingDBException(f'Could not set database "{config}" with index {value} because it already belongs to a named database ({named_db})!')
                                else:
                                    settings[local].pop(dbname)
                        settings[local][config] = value
                settings[local][config] = value
            else:
                settings["others"][config] = value

        with open(self.__configure_path__, "w") as file:
            json.dump(settings, file, indent=4)

        self.reload()


    def reload(self):
        """
        Recarrega as configurações
        """
        self._settings = self._get_file_data()
        self._set_settings()




"""
created by:


▄▀█ █▀ ▀█▀ █░█ ▀█▀ █▀█
█▀█ ▄█ ░█░ █▄█ ░█░ █▄█

https://github.com/paulindavzl/redis-okm
"""