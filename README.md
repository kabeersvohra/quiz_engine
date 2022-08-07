## Toptal Interview Quiz Engine

Instructions to run:

```
docker-compose up -d
poetry install
poetry shell
uvicorn app:app --reload
```

once the server is up and running, you can query the endpoints at http://127.0.0.1:8000, watch the demo to see how it is queried

To run the tests:

```
poetry shell
pytest
```
