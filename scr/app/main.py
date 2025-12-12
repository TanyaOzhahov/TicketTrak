from fastapi import FastAPI
from aviasales_api import PricesRequest, get_prices_data

app = FastAPI()


@app.post("/prices")
async def get_prices(request: PricesRequest):
    """Ручка для получения фактических цен на авиабилеты"""
    data = get_prices_data(request)
    return data


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8081, reload=True)

