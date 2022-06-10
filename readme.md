#Point Management Backend Test Project
This is a test project point management backend built using Python FastAPI.

##Features
The basic features of this backend include:
- Deposit transaction points from payers with the timestamp of the transaction.
- Check the account balance broken down by the payer balance.
- Spend points from the account. Points will be spent from previous transactions in order of earliest transaction date. Payer balances are not allowed to go negative.

##Endpoints
- POST /transactions : Add transaction to database
- PATCH /spend : Spends number of points passed if possible. Returns list of payer balance changes
- GET /balances : Returns all payer balances
- DELETE /clear_db : Clears database of transactions and balances

For more information view documentation when running server at `127.0.0.1:8000/redoc`

##Setup and Instructions
###Requirements
- Python 3.10

###Setup Instructions
- In root project folder run: `pip install -r requirements.txt` to install all needed packages.
- In the root project folder you can start the server with the command: `uvicorn main:app --reload`
- NOTE: By default uvicorn will host the server on `127.0.0.1:8000`
- If you want to run the pre-written tests you can run them with `pytest app`