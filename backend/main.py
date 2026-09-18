# ponytail: single-file entrypoint router; split into APIRouter submodules when endpoints exceed 10 per domain.
try:
    from fastapi import FastAPI
    app = FastAPI(
        title="DrugTime API",
        version="1.0.0",
        description="Medication reminder and drug safety platform"
    )
except ImportError:
    app = None

def health_check():
    return {"status": "ok", "service": "drugtime-api"}

if app:
    @app.get("/healthz")
    def _health_endpoint():
        return health_check()

if __name__ == "__main__":
    # Self-check sanity
    res = health_check()
    assert res["status"] == "ok", "Health check failed"
    print("Health check sanity passed.")
    if app:
        import uvicorn
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    else:
        print("FastAPI not installed yet. Run: pip install -r requirements.txt")
