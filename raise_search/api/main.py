from fastapi import FastAPI

app = FastAPI(title="RAISE Search API")


@app.get("/")
def read_root():
    return {"Hello": "World"}
