from fastapi import FastAPI

app = FastAPI()


@app.post("/pay/")
def process_payment(amount: float):
    return {"message": "Payment processed successfully", "amount": amount}
