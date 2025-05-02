# RedisORM

Uma **ORM** _simples_ e _poderosa_ que facilita a conexão e manipulação do banco de dados do **[Redis](https://redis.io/ "Redis - The Real-time Data Platform")**.

## Sumário

* **[Instalação](#instalação "Guia de instalação")** - veja como instalar o **RedisORM**.
* **[CRUD Básico com RedisORM](#crud-básico-com-redisorm "Guia de como realizar um CRUD simples com RedisORM")** - veja como fazer um **CRUD** com **RedisORM**.
  * **[1. Crie modelos](#1-crie-modelos "Guia de como criar modelos")** - veja como criar os modelos usados no **RedisORM**.
  * **[2. Adicione ou atualize registros no banco de dados](#2-adicione-ou-atualize-registros-no-banco-de-dados "Veja como adicionar ou atualizar registros no banco de dados Redis")** - veja como adicionar ou atualizar registros com **RedisORM**.
  * **[3. Obtenha modelos do banco de dados](#3-obtenha-modelos-do-banco-de-dados "Veja como obter dados do banco de dados Redis")** - veja como obter registros com **RedisORM**.
  * **[4. Apague um ou mais registros do banco de dados](#4-apague-um-ou-mais-registros-do-banco-de-dados "Veja como apagar registros do banco de dados Redis")** - veja como apagar registros com **RedisORM**.
* **[Configurações](#configurações-de-conexão-e-outros "Veja como fazer uma simples configuração do RedisORM")** - veja como configurar o **RedisORM**.
* **[Docs](#docs "Veja a documentação adicional do RedisORM")** - veja a documentação detalhada com exemplos e conceitos.

## Instalação

**Clone o repositório do [GitHub](https://github.com/paulindavzl/redis-orm "RedisORM"):**

```bash
git clone git@github.com:paulindavzl/redis-orm.git
```

Ou **instale pelo [PyPI](https://pypi.org/project/redis-orm-py/ "RedisORM"):**

```bash
pip install redis-orm
```

---

## CRUD Básico com RedisORM

### 1. Crie modelos

Um modelo é a representação de uma tabela em um banco de dados. Embora o **[Redis](https://redis.io/ "Redis - The Real-time Data Platform")** não funcione com o formato **tabela/coluna** como o  **SQL** , o **RedisORM** se organiza de maneira semelhante a esse formato.

Modelos devem herdar de **RedisModel:**

```python
import datetime as dt 

from redis_orm.tools import RedisModel, RedisConnect


class UserModel(RedisModel):
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

### 2. Adicione ou atualize registros no banco de dados

Use **[RedisConnect](https://chatgpt.com/c/6814f9d6-2fd8-8004-8fc6-f375e81b08ad#redisconnect "Veja mais sobre RedisConnect")** para comunicar-se com o banco de dados **[Redis](https://redis.io/ "Redis - The Real-time Data Platform"):**

```python
...

# use o RedisConnect.add(...) para adicionar registros no banco de dados
RedisConnect.add(model=user)


# note que se o ID deste modelo já existir no banco de dados, um erro será gerado. Para evitar isso, use "exists_ok=True"
RedisConnect.add(model=user, exists_ok=True) # isso atualizará o registro (caso ele exista)

...
```

### 3. Obtenha modelos do banco de dados

```python
...

# use RedisConnect.get(...) para obter registros
models = RedisConnect.get(model=UserModel) # caso exista mais de um registro deste modelo, uma classe Getter será retornada. Caso exista somente um registro, o modelo dele será retornado. Se não existir nenhum registro, o retorno será None


# caso o retorno de RedisConnect.get(...) seja Getter, existem alguns métodos para realizar consultas específicas
model_uid_1 = models.filter_by(uid=1) # retorna um registro de ID 1. Caso o parâmetro usado para filtrar retorne mais de um registro, outro Getter será retornado
first_model = models.first() # retorna o primeiro registro obtido
last_model = models.last() # retorna o último registro obtido
length = models.length # retorna a quantidade de registros (int) retornados

...

```

**Obs: O retorno de RedisConnect.get pode ser:**

```python
RedisConnect.get(...) -> None # Caso não exista nenhum registro daquele modelo
RedisConnect.get(...) -> UserModel # Caso só exista um registro daquele modelo (UserModel é exemplo, pode ser qualquer modelo)
RedisConnect.get(...) -> Getter # Caso exista mais de um registro daquele modelo (Getter possui métodos tipo: filter_by, first, ...)
```

### 4. Apague um ou mais registros do banco de dados

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

⚠️ Ao iniciar um projeto com  **RedisORM** , um arquivo **JSON** de configuração chamado `redis_configure.json` será gerado automaticamente na raiz do projeto.

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

Este arquivo contém todas as informações necessárias para que o **[Redis](https://redis.io/)** se conecte corretamente.

Você  **não precisa editar o JSON manualmente** ! Use a classe **[Settings](https://chatgpt.com/c/6814f9d6-2fd8-8004-8fc6-f375e81b08ad#settings "Veja mais sobre Settings")** para modificar ou acessar as configurações:

```python
from redis_orm.tools import Settings, RedisModel


# instancie Settings
settings = Settings() # você pode passar "path" para usar outro arquivo .json (por padrão é "redis_configure.json")


# defina configurações via Settings.set_config(...)
settings.set_config(host="localhost", port=6379,...)


# acesse as configurações como atributos
host = settings.host
password = settings.password


# associe essas configurações a um modelo usando "__settings__"
class UserModel(RedisModel):
	__settings__ = settings
	__db__ = "tests" # "tests" é um banco nomeado (definido via Settings.set_config(dbname="<name>:<index>"))
	...


# você também pode modificar a instância padrão
from redis_orm.tools import settings # todas as alterações afetarão os modelos que usam a instância padrão
```

**Settings** também tem suporte a variáveis de ambiente. Veja mais em  **[Settings](https://chatgpt.com/c/6814f9d6-2fd8-8004-8fc6-f375e81b08ad#settings)** .

---

## Docs

### RedisConnect

**RedisConnect** é a classe que se conecta de fato com o servidor **[Redis](https://redis.io/ "Redis - The Real-time Data Platform")**. Veja mais sobre ela em **[RedisConnect](./docs/RedisConnect.md "Veja mais sobre RedisConnect")**.

### Settings

**Settings** é a classe usada para configurar e obter configurações gerais sobre conexões e outras. Veja mais sobre ela em **[Settings](./docs/Settings.md "Veja mais sobre Settings")**.

### Getter

**Getter** é a classe retornada ao fazer uma consulta com **[RedisConnect](#RedisConnect "Veja mais sobre RedisConnect")**. Ela agrupa o retorno de mais de um modelo e permite consultas personalizadas. Veja mais sobre ela em **[Getter](./docs/Getter.md "Veja mais sobre Getter")**.

### Exceptions

O **RedisORM** possui exceções personalizadas. Veja mais informações em **[Exceptions](./docs/Exceptions.md "Veja mais sobre Exceptions")**.

### Licença

**RedisORM** é distribuído sob a Licença MIT. Veja o arquivo **[LICENSE](./docs/LICENSE "LICENÇA de uso")** para mais detalhes.
