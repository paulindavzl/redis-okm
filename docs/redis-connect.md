# RedisConnect

O **RedisConnect** é a classe que se conecta com o **[Redis](https://redis.io/ "Redis - The Real-time Data Platform")**. A partir dela, é possível fazer todas as operações com o banco de dados que o **RedisOKM** disponibiliza.

---

## Sumário

* **[Como funciona](#como-funciona "Como a RedisConnect funciona por trás dos panos")** – Veja como a `RedisConnect` utiliza os dados dos modelos para se conectar ao **[Redis](https://redis.io/ "Redis - The Real-time Data Platform")**.
* **[Como utilizar](#como-utilizar "Como usar RedisConnect corretamente")** – Guia básico de como importar e usar a `RedisConnect`.
  * **[Salvar um registro](#salvar-um-registro "Veja como salvar um registro no Redis")** – Aprenda a salvar modelos com **RedisOKM**.
  * **[Obter registros](#obter-registros "Veja como buscar dados no Redis")** – Descubra como recuperar registros com base em um modelo.
  * **[Apagar registros](#apagar-registros "Como apagar registros no Redis")** – Apague um ou mais registros do banco de dados.
  * **[Contar registros](#contar-a-quantidade-de-registros-no-banco-de-dados "Conte a quantidade de registros existentes")** – Saiba como contar quantos registros existem.
  * **[Verificar existência](#verificar-se-um-registro-existe "Veja como verificar a existência de registros")** – Método para saber se um dado existe no **[Redis](https://redis.io/ "Redis - The Real-time Data Platform")**.
  * **[Apagar todos os registros](#apagar-todos-os-registros-de-um-banco-de-dados "Zere todo o banco de dados")** – Veja como limpar totalmente um ou mais bancos **[Redis](https://redis.io/ "Redis - The Real-time Data Platform")**.
* **[Docs](#docs "Outras documentações")** - Veja outras documentações com instruções para melhores usos da biblioteca

---

## Como funciona

O **RedisConnect** utiliza as informações de conexão que são definidas ao estruturar um **[modelo](./redis-model.md "Veja mais sobre modelos"):**

```python
class Model(RedisModel):
	__db__ = 0 # índice do banco de dados
	__settings__ = settings # configurações, onde estão as informações de conexão com o servidor Redis

	...
```

A partir destas duas informações, é possível realizar uma conexão com o servidor.

Cada registro é salvo em uma chave única, gerada pela combinação dos elementos: _"prefixo:nome_da_tabela:id"_, com isso, cada registro fica uma chave única no banco de dados.

> ⚠️**Atenção:** Esta chave é única desde que não exista mais de um **[modelo](./redis-model.md "Veja mais sobre modelos")** com o mesmo `__tablename__`:

```python
class Model(RedisModel):
	__tablename__ = "unique_name"
	__autoid__ = True # ID gerado automaticamente (recomendado)
```

- `__tablename__` é o nome do modelo. Serve para identificar a classe do modelo e gerar um **key** única.

---

## Como utilizar

Para utilizar a classe **RedisConnect** é muito simples, basta importá-la de `redis_okm.tools` e acessar seus métodos estáticos:

```python
from redis_okm.tools import RedisConnect
```

Como todos os métodos de RedisConnect são estáticos, não há necessidade de instanciar a classe:

```python
RedisConnect.add(...) # adiciona um registro no banco de dados
RedisConnect().add(...) # gera um erro
```

### Salvar um registro

Para adicionar um registro utilizamos o método **RedisConnect.add(...)**:

```python
class RedisConnect:
	@staticmethod
	def add(model: _model, exists_ok: bool=False):
		...


# model referencia-se ao modelo instânciado que será registrado
# exists_ok indica que um registro pode ser sobrescrito caso já exista (evita erro: RedisConnectionAlreadyRegisteredException)


class ModelRepository:
	# cria um novo registro
	@staticmethod
	def create(model: Model) -> dict:
		... # valida o modelo

		response = {}

		# tenta salvar um registro
		try:
			RedisConnect.add(model=model)
			response = {...}

		# trata o erro (caso ocorra)
		except RedisConnectionAlreadyRegisteredException: # caso o registro já esteja registrado
			response = {...}
		except RedisConnectConnectionFailedException: # erro de conexão interno do RedisOKM
			response = {...}
		except Exception as e: # outro erro
			response = {...}

		return response


	# atualiza um registro
	@staticmethod
	def update(model: Model) -> dict:
		... # valida o modelo

		response = {}

		# tenta atualizar um registro
		try:
			RedisConnect.add(model=model)
			response = {...}

		# trata o erro (caso ocorra)
		except RedisConnectConnectionFailedException: # erro de conexão interno do RedisOKM
			response = {...}
		except Exception as e: # outro erro
			response = {...}

		return response
```

> ⚠️**Atenção:** Foi criado um **Repositório** por questões de boas práticas de programação, não é obrigatório, porém, recomendado!
>
> O método `Repository.update(...)` irá gerar um novo registro do modelo caso ele não exista.

**RedisConnect.add(...)** também tem suporte a expiração de registros, basta adicionar `__expire__` na estrutura do modelo:

```python
class Model(RedisModel):
	__expire__ = 3600 # __expire__ deve ser em segundo e um valor que possa ser convetido para float
	...
```

> 🧠 Nota: Se o modelo possuir atributos relacionados a outras classes (`chaves estrangeiras`), a `RedisConnect` tratará essas referências automaticamente durante a operação `.add()`. Para saber mais, veja a documentação sobre **[modelos e chaves estrangeiras](./redis-model.md).**

### Obter registros

Para obter um registro, é utilizado o método **RedisConnect.get(...):**

```python
class RedisConnect:
	@staticmethod
	def get(model: _model, on_corrupt="flag") -> Getter:
		...


# model se refere a classe do modelo que será buscado no banco de dados
# on_corrupt indica o que fazer ao encontrar um registro corrompido ("flag" marca/invalida o modelo corrompido, "skip": não obtém os dados do registro corrompido, "ignore": ignora o fato do registro estar corrompido e retorna-o normalmente)
# Getter é uma classe que agrupa modelos e métodos de consultas 


class ModelRepository:
	# retorna um modelo pelo ID
	@staticmethod
	def get_by_id(id: any) -> Model|dict:
		... # valida o ID

		response = {}
		try:
			model = RedisConnect.get(Model).filter_by(id=id)
			if model:
				return model
			response = {"error": ...}
		except RedisConnectConnectionFailedException: # erro de conexão
			response = {...}
		except Exception as e:
			response = {...}

		return response


	# retorna todos os modelos
	@staticmethod
	def get_all() -> list[Model]|dict:
		response = {}

		try:
			models = RedisConnect.get(Model).list
			if len(models) > 1:
				return models
			response = {"error": ...}
		except RedisConnectConnectionFailedException: # erro de conexão
			response = {...}
		except Exception as e:
			response = {...}

		return response
```

> ⚠️**Observação:** Veja mais sobre a classe **[Getter](./getter.md)**.

### Apagar registros

**RedisOKM** disponibiliza o método **RedisConnect.delete(...)**, que permite apagar um ou mais registros de uma só vez:

```python
class RedisConnect:
	@staticmethod
	def delete(model: _model, identify: Any|list=None, non_existent_ok: bool=False):
		...


# model indica o a classe do modelo ou o modelo que será apagado
# identify é usado para informar um ou mais IDs que serão apagados
# non_existent_ok impede que um erro seja gerado caso um ID não possua registro (RedisConnectNoRecordsException)


class ModelRepository:
	# apaga um registro pelo ID
	@staticmethod
	def delete_by_id(id: any) -> dict:
		... # valida o ID

		response = {}
		try:
			RedisConnect.delete(Model, identify=id)
			response = {...}
		except RedisConnectNoRecordsException: # indica que o ID não possui registro
			response = {...}
		except RedisConnectConnectionFailedException: # erro de conexão
			response = {...}
		except Exception as e:
			response = {...}

		return response
```

> ⚠️**Nota:** O erro `RedisConnectNoRecordsException` poderia ser evitado se `non_existent_ok=True`!

### Contar a quantidade de registros no banco de dados

É possível contar a quantidade de registro em um banco de dados utilizando o método **RedisConnect.count(...):**

```python
class RedisConnect:
	@staticmethod
	def count(db: int|str, settings: Settings, testing: bool=False) -> int:
		...


# db indica o índicie do banco de dados que será contado
# settings é a instância de Settings que possui as informações de conexão
# testing indica se é um teste ou não


def get_length_db(db):
	... # valida db

	length = RedisConnect.count(db=db, settings=settings)
	return length
```

> ⚠️**Atenção:** **RedisConnect.count(...)** contabiliza todos os registros em um banco de dados, mesmo que não sejam do mesmo modelo. Para obter a quantidade de um único modelo, use a propriedade `length` de **[Getter](./getter.md)**, retornado de **[RedisConnect.get(...)](#obter-registros)**.

### Verificar se um registro existe

É possível verificar a existência de um registro usando **RedisConnect.exists(...)**:

```python
class RedisConnect:
	@staticmethod
	def exists(model: _model, identify: Any=None) -> bool:
		...


# model representa o modelo que será buscado
# identify refere-se ao ID do modelo (não necessário caso model esteja instanciado)


class ModelRepository:
	@staticmethod
	def create(model: Model) -> dict:
		if RedisConnect.exists(model):
			return {"error": "model_already_registered",...}
		...
```

### Apagar todos os registros de um banco de dados

É possível apagar  todos os registros do banco de dados usando o método **RedisConnect.restart_full_db(...):**

```python
class RedisConnect:
	@staticmethod
	def restart_full_db(db: Any|list, settings: Settings):
		...


# db indica qual índice do banco de dados será apagado (pode ser uma lista de índices)
# settings é a instância de Settings, contendo as informações de conexão e outras


def restart_all():
	RedisConnect.restart_full_db(db="__all__", settings) # "__all__" apaga todos os registros de todos os bancos de dados
```

> ⚠️**Cuidado:** Este processo é **irreversível**, cuidado ao usar!

---

## Docs

Veja também outras documentações úteis para trabalhar com **RedisOKM:**

### Boas práticas

O **RedisOKM** possui uma seção que **boas práticas** para melhorar o uso da biblioteca. Veja mais em **[Boas Práticas](./good-practices.md "Veja mais sobre Boas Práticas.").**

### RedisModel

**RedisModel** é a classe base de todo modelo de **RedisOKM** deve herdar. Veja mais sobre em **[RedisModel](./redis-model.md "Veja mais sobre RedisModel")**.

### Settings

**Settings** é a classe usada para configurar e obter configurações gerais sobre conexões e outras. Veja mais sobre ela em **[Settings](./settings.md "Veja mais sobre Settings")**.

### Getter

**Getter** é a classe retornada ao fazer uma consulta com **RedisConnect**. Ela agrupa o retorno de mais de um modelo e permite consultas personalizadas. Veja mais sobre ela em **[Getter](./getter.md "Veja mais sobre Getter")**.

### Exceptions

O **RedisOKM** possui exceções personalizadas. Veja mais informações em **[Exceptions](./exceptions.md "Veja mais sobre Exceptions")**.

### Licença

**RedisOKM** é distribuído sob a Licença MIT. Veja o arquivo **[LICENSE](./LICENSE "LICENÇA de uso")** para mais detalhes.
