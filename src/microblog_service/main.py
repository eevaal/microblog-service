from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Microblog Service!"}

@app.get("/health")
async def check_health():
    return {"status": "healthy"}