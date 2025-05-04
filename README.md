# RedisORM

Uma **ORM** _simples_ e _poderosa_ que facilita a conexão e manipulação do banco de dados do **[Redis](https://redis.io/ "Redis - The Real-time Data Platform")**.

## Sumário

* **[Instalação](#instalação "Guia de instalação")** - Passo a passo de como instalar o **RedisORM**.
* **[CRUD Básico com RedisORM](#crud-básico-com-redisorm "Guia de como realizar um CRUD simples com RedisORM")** - Como fazer operações básicas com **RedisORM**.

  * **[1. Crie modelos](#1-crie-modelos "Guia de como criar modelos")** - Aprenda a criar os modelos  usados no **RedisORM**.
  * **[2. Adicione ou atualize registros no banco de dados](#2-adicione-ou-atualize-registros-no-banco-de-dados "Veja como adicionar ou atualizar registros no banco de dados Redis")** - Veja como adicionar ou atualizar registros com **RedisORM**.
  * **[3. Obtenha modelos do banco de dados](#3-obtenha-modelos-do-banco-de-dados "Veja como obter dados do banco de dados Redis")** - Obtenha registros de forma simples com **RedisORM**.
  * **[4. Apague um ou mais registros do banco de dados](#4-apague-um-ou-mais-registros-do-banco-de-dados "Veja como apagar registros do banco de dados Redis")** - Aprenda a apagar registros com **RedisORM**.
* **[Configurações](#configurações "Veja como fazer uma simples configuração do RedisORM")** - Configure o **RedisORM** de forma simples.
* **[Dependências](#dependências "Veja as versões de dependências que são compatíveis com o RedisORM")** - Dependências usadas pelo **RedisORM**.

  * **[Principais dependências](#principais-dependências "As principais dependências.")** - Dependências principais e que o **RedisORM** não funciona sem.
  * **[Dependências para testes](#dependências-para-testes "Dependências usadas em testes.")** - Dependências usadas para testar o **RedisORM**
* **[Exemplo de uso](#exemplo-de-uso)** - Demonstração prática do **RedisORM** com boas práticas.
* **[Docs](#docs "Veja a documentação adicional do RedisORM")** - Veja a documentação detalhada com exemplos e conceitos.

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

Um modelo é a representação de uma tabela em um banco de dados. Embora o **[Redis](https://redis.io/ "Redis - The Real-time Data Platform")** não funcione com o formato **tabela/coluna** como o  **SQL**, o **RedisORM** se organiza de maneira semelhante a esse formato.

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

Use **[RedisConnect](#redisconnect "Veja mais sobre RedisConnect")** para comunicar-se com o banco de dados **[Redis](https://redis.io/ "Redis - The Real-time Data Platform"):**

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

## Configurações

> ⚠️ Ao iniciar um projeto com  **RedisORM**, um arquivo **JSON** de configuração chamado `redis_configure.json` será gerado automaticamente na raiz do projeto.

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

Você  **não precisa editar o JSON manualmente**! Use a classe **[Settings](#settings "Veja mais sobre Settings")** para modificar ou acessar as configurações:

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

**Settings** também tem suporte a variáveis de ambiente. Veja mais em  **[Settings](#settings)** .

---

## Dependências

O **RedisORM** utiliza algumas bibliotecas específicas para funcionar corretamente. Embora nem todas exijam uma versão fixa, é **recomendado utilizar as mesmas versões** adotadas no desenvolvimento para evitar incompatibilidades.

### Principais dependências

- **[Python 3.13.x](https://www.python.org/downloads/release/python-3130/)** - Linguagem usada no desenvolvimento do RedisORM. Ainda **não há suporte para Python 3.14 ou superior**.
- **[poetry 2.1.1](https://pypi.org/project/poetry/2.1.1/)** - Gerenciador de dependências utilizado pelo projeto. Não possui restrições de versão, mas é ideal manter esta.
- **[redis-py 5.2.1](https://pypi.org/project/redis/5.2.1/)** - Cliente oficial para conexão com servidores Redis.
- **[python-dotenv 1.1.0](https://pypi.org/project/python-dotenv/1.1.0/)** - Carrega variáveis de ambiente a partir de arquivos `.env`.

### Dependências para testes

* **[pytest 8.3.5](https://pypi.org/project/pytest/8.3.5/)** - Framework de testes automatizados. Opcional — não é necessário para o uso da biblioteca.

- **[fakeredis 2.28.1](https://pypi.org/project/fakeredis/2.28.1/)** - Emula o Redis em memória para testes sem um servidor real. Embora usado somente para fins de testes, não é possível (nem recomendado) instalar o **RedisORM** sem ele.

> ⚠️ **Recomendação**: embora o RedisORM não bloqueie versões mais recentes, mantenha as versões acima sempre que possível para evitar comportamentos inesperados.

---

## Exemplo de uso

```python
import datetime as dt # somente para exemplo (não obrigatório)

from redis_orm.tools import RedisModel, Settings, RedisConnect
from redis_orm.exceptions import RedisConnectionAlreadyRegisteredException, RedisConnectNoRecordsException


# instância de Settings
settings = Settings(path="you_settings_path.json") # não é obrigatório informar o arquivo de configuração (padrão: "redis_configure.json")

# define algumas configurações básicas (SEM .env)
settings.set_config(
    host="localhost", # define o servidor do Redis (padrão "localhost")
    port=6379, # define a porta de conexão com Redis (padrão 6379)
    password="your_password", # senha para conexão do Redis (padrão None)
    dbname="user:0"  # nomeio o banco de dados com índice 0 de "user"
)

# define algumas configurações básicas (COM .env)
settings.set_config(
    envfile=".env", # define um arquivo de variável de ambiente
    host="env:HOST", # define o servidor (inicia-se com "env:" seguido da chave no .env)
    port="env:PORT", # define a porta de conexão com Redis
    password="env:PASSWORD",
    dbname="user:0"
)


# modelo de Usuário
class UserModel(RedisModel):
    __settings__ = settings # informo a instância da configuração usada (se não informada, usa uma padrão - from redis_orm.tools import settings)
    __db__ = "user" # informo o banco de dados nomeado (não é obrigatório estar nomeado, pode ser "__db__ = 0")
    __tablename__ = "users" # nome da "tabela" (caso não informado será o nome da classe do modelo: "usermodel")
    __idname__ = "uid" # informo o identificador do modelo (se não informado será o primeiro parâmetro)

    # parâmetros do modelo (representa colunas)
    uid: int
    name: str
    password: str

    # valores padrões
    status = "active"
    created = dt.datetime.now



# repositório para UserModel
class UserModelRepository:
  
    # cria um registro do usuário
    @staticmethod
    def create(user: UserModel) -> dict:
        ... # validação do modelo

        response = {"result": str}
        try:
            RedisConnect.add(user) # tenta adicionar um novo usuário
            response["result"] = "success"
  
        # caso ocorra um erro
        except RedisConnectionAlreadyRegisteredException: # este erro indica que este modelo de usuário com este ID já possui registro
            response["result"] = "err"
            response["cause"] = "already_registered"
            response["message"] = "This user already has a registration."
        # se o erro não for "RedisConnectionAlreadyRegisteredException"
        except Exception as e: 
            # verifica se é um erro de conexão do RedisORM (os erros de conexão possuem o parâmetro "__redisorm__")
            if getattr(e, "__redisorm__", False):
                response["result"] = "err"
                response["cause"] = "connection_error"
                response["message"] = "An internal error occurred connecting to the Redis server."
            else:
                ... # trata o erro

        return response # retorna a resposta para o usuário
  

    # atualiza um registro
    @staticmethod
    def update(user: UserModel) -> dict:
        ... # validação do modelo

        response = {}
        try:
            RedisConnect.add(user, exists_ok=True) # exists_ok permite atualizar o usuário caso ele já possua registro
            response["result"] = "success"
        except Exception as e: # o único erro interno do RedisORM que pode ocorrer é o de conexão (se exists_ok=True e se a validação do usuário for bem feita)
            if getattr(e, "__redisorm__", False):
                response["result"] = "err"
                response["cause"] = "connection_error"
                response["message"] = "An internal error occurred connecting to the Redis server."
            else:
                ... # trata o erro

        return response # retorna a resposta para o usuário
  

    # obtém um registro pelo ID
    @staticmethod
    def get_by_uid(uid: int) -> None|UserModel|dict:
        ... # validação do UID

        response = {}
        try:
            user = RedisConnect.get(UserModel).filter_by(uid=uid)
            return user
        except Exception as e: # o único erro interno do RedisORM que pode ocorrer é o de conexão
            if getattr(e, "__redisorm__", False):
                response["result"] = "err"
                response["cause"] = "connection_error"
                response["message"] = "An internal error occurred connecting to the Redis server."
            else:
                ... # trata o erro

        return response
  

    # obtém todos os registros de usuários
    @staticmethod
    def get_all() -> None|list|dict:
        response = {}
        try:
            users = RedisConnect.get(UserModel).list
            return users
        except Exception as e: # o único erro interno do RedisORM que pode ocorrer é o de conexão
            if getattr(e, "__redisorm__", False):
                response["result"] = "err"
                response["cause"] = "connection_error"
                response["message"] = "An internal error occurred connecting to the Redis server."
            else:
                ... # trata o erro

        return response
  

    # apaga um registro de usuário pelo ID
    @staticmethod
    def delete(uid: int) -> dict:
        ... # validação do UID

        response = {}
        try:
            RedisConnect.delete(UserModel, uid)
            response["result"] = "success"
        except RedisConnectNoRecordsException: # ocorre quando não possui registro do ID especificado. use "RedisConnect.delete(..., non_existent_ok=True)" para evitar.
            response["result"] = "err"
            response["cause"] = "no_records"
            response["message"] = "The UID provided has no record."
        except Exception as e: 
            if getattr(e, "__redisorm__", False):
                response["result"] = "err"
                response["cause"] = "connection_error"
                response["message"] = "An internal error occurred connecting to the Redis server."
            else:
                ... # trata o erro

        return response


```

> ⚠️**Recomendação:** Neste exemplo, todas as funções e classes estão no mesmo código, mas para fins de organização faça a separação em arquivos e módulos separados.

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
