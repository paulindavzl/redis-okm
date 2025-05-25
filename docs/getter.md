# Getter

Classe responsável por agrupar modelos e disponibilizar métodos de consultas **"avançados"**. **Getter** é retorno do método **[RedisConnect.get(...)](./redis-connect.md "Veja mais sobre RedisConnect")**.

## Sumário

- **[Filtrar por dados](#filtrar-registros-por-dados-específicos)** - Filtre registros por valores específicos.
- **[Primeiro/último registro](#retornar-o-primeiro/último-registro)** - Obtenha o primeiro e/ou o último registro classificados por um atributo específico.
- **[Quantidade de registros](#quantidade-de-registros)** - Veja quantos registros de um modelo existem no banco de dados.
- **[Corrupção de dados](#corrupção-de-dados)** - Funções para lidar com registros corrompidos.
  - **[has_corrupted](#has_corrupted)** - Verifica se há registros corrompidos.
  - **[valid_only](#valid_only)** - Retorna um **Getter** somente com registros válidos.
  - **[report](#report)** - Saiba quais são os modelo corrompidos.
- **[Docs](#docs "Veja a documentação adicional do RedisOKM")** - Veja a documentação detalhada com exemplos e conceitos.

## Filtrar registros por dados específicos

**Getter** possui o método `filter_by(...)`, que permite filtrar registros com base nos valores de seus atributos:

```python
class Getter:
	def filter_by(self, **conditions) -> _model|Getter|None:
		...


# conditions: condições para filtragem (attribute=expected_value)
# retorno:
#	_model: retorna o modelo que cumpre as condições, caso somente um
#	Getter: pode retornar outro Getter, caso as condições apontem para mais de um registro
#	None: caso nenhum registro atenda as condições


model = RedisConnect.get(Model).filter_by(id=0) # retorna o modelo com ID 0
```

> ⚠️**Atenção:** caso o atributo usado na condição não exista no modelo, um erro será levantado. Veja mais em **[exceptions](./exceptions.md "Veja mais sobre exceções")**.

## Retornar o primeiro/último registro

**Getter** disponibiliza dois métodos para obter o _primeiro_ e o _último_ registro:

```python
class Getter:
	def first(reference: None|str=None) -> _model:
		...


	def last(reference: None|str=None) -> _model:
		...


# reference: qual atributo do modelo será usado para ordenar ao obter o registro (quando None, obtém o primeiro/último por ordem de chegada)
# retorno: primeiro/último registro obtido


first_model = RedisConnect.get(Model).first(reference="rank")
last_model = RedisConnect.get(Model).last(reference="rank")

# obtém o primeiro e o último registro baseado no atributo "rank" (por ordem alfabética ou numeral)
# first_model: maior valor de "rank" 
# last_model: menor valor de "rank"
```

⚠️**Atenção:** caso o atributo usado na **referência** não exista no modelo, um erro será levantado. Veja mais em **[exceptions](./exceptions.md "Veja mais sobre exceções")**.

## Quantidade de registros

Por meio da `propriedade` **length**, é possível saber a quantidade de registros de um determinado modelo:

```python
class Getter:
	@property
	def length(self) -> int:
		...


# sempre retorna um inteiro (int)


length = RedisConnect.get(Model).length
print(length) # 0, 1, 2...
```

## Corrupção de dados

Em caso de **corrupção de dados**, o **RedisOKM** por padrão/segurança invalida o registro ao obtê-lo. A classe **Getter** possui alguns métodos para manipulação destes registros:

### has_corrupted

Este não é um `método`, e sim uma `propriedade`. Ela retorna um `bool` (_True_/_False_) e informa se há algum registro corrompido:

```python
class Getter:
	@property
	def has_corrupted(self) -> bool:
		...


query = RedisConnect.get(Model)
print(query.has_corrupted) # True/False
```

### valid_only

Este método seleciona somente os registros que não estão corrompidos:

```python
class Getter:
	def valid_only(self) -> Getter|None:
		...


# pode retornar um Getter caso haja registros válidos
# None caso não haja nenhum registro válido


query = RedisConnect.get(Model)
valids = query.valid_only()
print(valids.has_corrupted) # False
```

### report

o método **report()** retorna uma lista com os **IDs** dos modelos corrompidos (caso haja):

```python
class Getter:
	def report(self) -> list[str|int]|None:
		...


# retorna uma lista contendo o ID dos modelos corrompidos
# None se não houver modelo corrompido


query = RedisConnect.get(Model)

corrupteds = query.report()
if corrupteds:
	RedisConnect.delete(Model, identify=corrupteds, non_existent=True) # apaga os modelos corrompidos
```

> ⚠️**Atenção:** Por padrão e segurança, todos os registros corrompidos são invalidados a partir do momento que são obtidos via **[RedisConnect.get(...)](./redis-connect.md "Veja mais sobre RedisConnect")**. Mas isso pode ser alterado mudando o valor do parâmetro **on_corrupt** deste método (`.get(...)`):
>
> - **flag:** Marcação padrão, invalida todos os dados do registro e marca como corrompido, inutilizando-o e permitindo identificá-lo pelo **Getter** (⚠️ **RECOMENDADO**)
> - **skip:** Ignora modelos corrompidos e não agrupa-os no **Getter**
> - **ignore:** Ignora o fato dos modelos estarem corrompidos e agrupa-os no **Getter** mesmo assim, permitindo acessá-los normalmente (**⚠️ NÃO RECOMENDADO**)
>
> Veja mais detalhes em **[RedisConnect](./redis-connect.md "Veja mais sobre RedisConnect").**

## Docs

Veja também outras documentações úteis para trabalhar com **RedisOKM:**

### Boas práticas

O **RedisOKM** possui uma seção que **boas práticas** para melhorar o uso da biblioteca. Veja mais em **[Boas Práticas](./good-practices.md "Veja mais sobre Boas Práticas.").**

### RedisConnect

**RedisConnect** é a classe que se conecta de fato com o servidor **[Redis](https://redis.io/ "Redis - The Real-time Data Platform")**. Veja mais sobre ela em **[RedisConnect](./redis-connect.md "Veja mais sobre RedisConnect")**.

### RedisModel

**RedisModel** é a classe que todo modelo de **RedisOKM** deve herdar. Veja mais sobre em **[RedisModel](./redis-model.md "Veja mais sobre RedisModel")**.

### Settings

**Settings** é a classe usada para configurar e obter configurações gerais sobre conexões e outras. Veja mais sobre ela em **[Settings](./settings.md "Veja mais sobre Settings")**.

### Exceptions

O **RedisOKM** possui exceções personalizadas. Veja mais informações em **[Exceptions](./docs/exceptions.md "Veja mais sobre Exceptions")**.

### Licença

**RedisOKM** é distribuído sob a Licença MIT. Veja o arquivo **[LICENSE](./docs/LICENSE "LICENÇA de uso")** para mais detalhes.
