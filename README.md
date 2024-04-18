# RAISE Search

This repo includes an API and tools to support search capabilities in RAISE.

## Development

The repo includes a `docker` environment which can be launched as follows:


```bash
$ docker compose up --build -d
```

Code coverage reports can be generated when running tests locally:

```bash
$ pip install -e .[test]
$ pytest --cov=raise_search --cov-report=term --cov-report=html
```


Once running, the application components can be accessed at the following URLs:

* API (docs): [http://localhost:9400/docs](http://localhost:9400/docs)
* OpenSearch (health): [https://localhost:9200/_cat/health?v](https://localhost:9200/_cat/health?v)

Default OpenSearch credentials:

```bash
user = admin
password = admin
```