from app.database import Database
from fastapi import FastAPI, status
from app.models import Balance, Spend, Transaction

db = Database()
app = FastAPI()

def balance_to_model(balance: dict) -> list:
    print(f"@balance_to_model {balance=}") # NOTE: Using prints in the place of log.DEBUG/INFO like calls throughout project
    return [Balance(payer=payer, points=points) for payer, points in balance.items()]

@app.post("/transactions", response_model=Transaction, description="Add transaction to database")
async def add_transaction(transaction: Transaction):
    print(f"@add_transaction {transaction=}")
    db.add_transaction(transaction)
    return transaction

@app.patch("/spend", response_model=list[Balance], description="Spends number of points passed if possible. Returns list of payer balance changes")
async def spend_points(spend: Spend):
    print(f"@spend_points {spend=}")
    balance_update = db.spend_points(spend.points)
    balance_model = balance_to_model(balance_update)
    print(f"@spend_points returning {balance_model=}")
    return balance_model

@app.get("/balances", response_model=dict[str,int], description="Returns all payer balances")
async def get_balances():
    print("@get_balances")
    balances = db.get_balances()
    print(f"@get_balances returning {balances=}")
    return balances

@app.delete("/clear_db", status_code=status.HTTP_204_NO_CONTENT, description="Clears database of transactions and balances")
async def clear_db():
    print("@clear_db")
    db.clear_db()

