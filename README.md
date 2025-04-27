# RedisORM

Uma **ORM** _simples_ e _poderosa_ que facilita a conexão e manipulação do banco de dados do [Redis](https://redis.io/ "Redis - The Real-time Data Platform").

## Instalação

**Clone o repositório do [GitHub](https://github.com/paulindavzl/redis-orm "RedisORM"):**

```bash
git clone git@github.com:paulindavzl/redis-orm.git
```

ou **Instale do repositório [PyPI](https://pypi.org/project/redis-orm-py/ "RedisORM"):**

```bash
pip install redis-orm
```

---

## CRUD Básico com RedisORM

### Crie modelos

Modelos devem usar **BaseModel:**

```python
import datetime as dt 

from redis_orm.tools import BaseModel, RedisConnect


class UserModel(BaseModel):
	__db__ = 0 # informe o índice do banco de dados usando __db__ (obrigatório)
	__idname__ = "uid" # não é obrigatório informar o ID. Caso não informado, o primeiro atributo será considerado ID. Caso informado, não é necessário declará-lo no modelo

	# atributos do modelo (podem ser int, str ou float)
	uid: int
	name: str
	age: int

	# é possível definir valores padrões
	status = "ativo"
	created = dt.datetime.now # funções são chamadas automaticamente, gerando atributos dinâmicos


# instancie o modelo
user = UserModel(
	name="paulindavzl",
	age=18
)

...
```

### Adicione/atualize um modelo no banco de dados

Use **[RedisConnect](#RedisConnect "Veja mais sobre RedisConnect")** para comunicar-se com o banco de dados **[Redis](https://redis.io/ "Redis - The Real-time Data Platform"):**

```python
...

# use o RedisConnect.add(...) para adicionar registros no banco de dados
RedisConnect.add(model=user)


# note que se o ID deste modelo já existir no banco de dados, um erro será gerado. Para evitar isso, use "exists_ok=True"
RedisConnect.add(model=user, exists_ok=True) # isso atualizará o registro (caso ele exista)

...
```

### Obtenha modelos do banco de dados

```python
...

# use RedisConnect.get(...) para obter registros
models = RedisConnect.get(model=UserModel) # caso exista mais de um registro deste modelo, uma classe Getter será retornada. Caso exista somente um registro, o modelo dele será retorna. Se não existir nenhum registro, o retorno será None


# caso o retorno de RedisConnect.get(...) seja Getter, existem alguns métodos para realizar consultas específicas
model_uid_1 = models.filter_by(uid=1) # retorna um registro de ID 1. Caso o parâmetro usando para filtrar retorne mais de um registro, outro Getter será retornado
first_model = models.first() # retorna o primeiro registro obtido
last_model = models.last() # retorna o último registro obtido
length = models.length # retorna a quantidade de registros (int) retornados

...

```



**Obs: O retorno de RedisConnect.get pode ser:**

```python
RedisConnect.get(...) -> None # Caso o não exista nenhum registro daquele modelo
RedisConnect.get(...) -> UserModel # Caso só exista um registro daquele modelo (UserModel é exemplo, pode ser qualquer modelo)
RedisConnect.get(...) -> Getter # Caso exista mais de um registro daquele modelo (Getter possui métodos tipo: filter_by, first, ...)
```

### Apague um ou mais registro do banco de dados

```python
...

# use RedisConnect.delete(...) para apagar registros
RedisConnect.delete(model=user) # este apaga o registro de user, caso ele não exista, um erro será gerado. Para evitar isso, use "non_existent_ok=True"
RedisConnect.delete(model=user, non_existent_ok=True) # assim, caso o registro não exista, não gera um erro


# você pode apagar vários registros de uma só vez passando "identify=ID" ou "identify=[ID1, ID2,...]"
RedisConnect.delete(
	model=UserModel, 
	identify="ID", 
	non_existent_ok=True/False
)
RedisConnect.delete(
	model=UserModel, 
	identify=["ID1", "ID2",...], 
	non_existent_ok=True/False
)
```

---

## Configurações de conexão e outros

Ao iniciar um projeto com **RedisORM**, automaticamente será gerado um arquivo **JSON** de configuração será gerado na raiz do seu projeto:

```json
{
    "envfile": "",
    "tests": {
        "use_tests": true,
        "db": "tests",
        "restart_db": true
    },
    "network": {
        "host": "localhost",
        "port": 6379,
        "password": ""
    },
    "connection": {
        "decode_response": true,
        "timeout": 30,
        "retry_on_timeout": [
            true,
            3
        ]
    },
    "pools": {
        "max_connections": 10,
        "blocking_timeout": 3
    },
    "structure": {
        "separator": ":",
        "prefix": "cwd"
    },
    "dbnames": {
        "tests": 15
    }
}
```

Neste arquivo contém (deve conter) todas as informações que o **[Redis](https://redis.io/ "Redis - The Real-time Data Platform")** precisa para conectar-se.

Você não precisa acessar ou editar as configurações diretamente pelo **JSON**! Para isso, use **[Settings](#Settings "Veja mais sobre Settings"):**

```python
from redis_orm.tools import Settings, BaseModel


# instancie Settings
settings = Settings() # ao instanciar Settings, você pode passar o parâmetro "path", que aponta para um arquivio .json. Isso serve para poder criar diferentes configurações para diferentes propósitos
# por padrão, "path=redis_configure.json"


# você pode definir configurações usando Settings.set_config(...)
settings.set_config(host="localhost", port=6379,...)


# você pode obter configurações usando Settings.<nome da configuração>
host = settings.host
password = settings.password


# você também pode atrelar essa instância, com essas configurações à um modelo usando "__settings__"
class UserModel(BaseModel):
	__settings__ = settings
	__db__ = "tests" # "tests" é um banco de dados nomeado. Você pode fazer isso usando Settings.set_config(dbname="<name>:<index>")
	...


# caso você não defina "__settings__", ele receberá uma instância padrão. Você pode modificar essa instância padrão importando-a
from redis_orm.tools import settings # toda modificação que fizer na instância padrão será refletida aos modelos que à usam

```

**Settings** também tem suporte a variáveis de ambiente. Veja mais em **[Settings](#Settings "Veja mais sobre Settings")**.

---



## Docs

### RedisConnect

**RedisConnect** é a classe que se conecta de fato com o servidor **[Redis](https://redis.io/ "Redis - The Real-time Data Platform")**. Veja mais sobre ela em **[RedisConnect](./docs/RedisConnect.md "Veja mais sobre RedisConnect")**.

### Settings

**Settings** é a classe usada para configurar e obter configurações gerais sobre conexões e outras. Veja mais sobre ela em **[Settings](./docs/Settings.md "Veja mais sobre Settings")**.

### Getter

**Getter** é a classe retornada ao fazer uma consulta com **[RedisConnect](#RedisConnect "Veja mais sobre RedisConnect")**. Ela agrupa o retorno de mais de um modelo e permite consultas personalizadas. Veja mais sobre ela em **[Getter](./docs/Getter.md "Veja mais sobre Getter")**.

### Licença

**RedisORM** é distribuído sob a Licença MIT. Veja o arquivo **[LICENSE](./docs/LICENSE "LICENÇA de uso")** para mais detalhes.
