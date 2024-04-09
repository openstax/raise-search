# RAISE Search

This repo includes an API and tools to support search capabilities in RAISE.

## Development

The repo includes a `docker` environment which can be launched as follows:

Set environment variables:

```bash
$ export OPENSEARCH_INITIAL_ADMIN_PASSWORD=<password>
```

Start containers:

```bash
$ docker compose up --build -d
```

Once running, the application components can be accessed at the following URLs:

* API (docs): [http://localhost:9400/docs](http://localhost:9400/docs)
* OpenSearch (health): [https://localhost:9200/_cat/health?v](https://localhost:9200/_cat/health?v)
