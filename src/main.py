from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/utils/health")
def read_health():
    return {"status": "healthy"}
