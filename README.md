goLME
=====

Cotação London Metal Exchange
-----------------------------

![Cobre](https://img.shields.io/badge/LME-Cobre-green.svg)
![Zinco](https://img.shields.io/badge/LME-Zinco-green.svg)
![Alumínio](https://img.shields.io/badge/LME-Aluminio-green.svg)
![Chumbo](https://img.shields.io/badge/LME-Chumbo-green.svg)
![Estanho](https://img.shields.io/badge/LME-Estanho-green.svg)
![Níquel](https://img.shields.io/badge/LME-Niquel-green.svg)

## Live demo
https://lme.gorilaxpress.com/

### Alguns endpoints de exmplo
```
/api/
/api/<date_from>/<date_to>
/chart/
/chart/<date_from>/<date_to>
/periodo/<date_from>/<date_to>
/cotacao/
/cotacao/<str:api_key>/
/cotacao/<str:api_key>/json/
/cotacao/<str:api_key>/json/v2/
...
```

### Como rodar o projeto

* Clone esse repositório.
* Crie um virtualenv com Python 3.
* Ative o virtualenv.
* Instale as dependências.
* Rode as migrações.

```
git clone https://github.com/tiagocordeiro/goLME.git
cd goLME
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python contrib/env_gen.py
python manage.py migrate
```

### Configurar administrador

Para cria um usuário administrador

```
python manage.py createsuperuser --username dev --email dev@foo.bar
```

### Populando o banco de dados

Cria timeseries

```
python manage.py loaddata lme_time_series
```

### Atualiza preços do LME

```
python manage.py update_lme
```

### Rodar em ambiente de desenvolvimento

Para rodar o projeto localmente

```
python manage.py runserver
```

### Banco de dados para ambiente de desenvolvimento com Docker

```
docker-compose up -d
```
