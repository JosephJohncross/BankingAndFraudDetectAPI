from fastapi import FastAPI


app = FastAPI(
    title="NextGen Banking API",
    description="API for banking operations",
)

app.get("/health", tags=["Health"])(lambda: {"status": "ok"})