from fastapi import HTTPException, status
from app.models import Transaction

class Database:
    def __init__(self) -> None:
        self.transactions: list[Transaction] = []
        self.balances: dict[str, int] = {}

    def add_transaction(self, new_transaction: Transaction) -> None:
        '''
        Add transaction to database
        '''
        print(f"@add_transaction {new_transaction=}")
        self.transactions.append(new_transaction)
        self._add_balance_points(self.balances, new_transaction.payer, new_transaction.points)
        self._sort_add_transaction()

    def get_balances(self) -> list:
        '''
        Get list of balance dicts

        balance: {payer: str, points: int}
        '''
        return self.balances

    def spend_points(self, points: int) -> dict[str, int]:
        '''
        Spend points by extracting points from earliest transactions

        If possible, spend a number of points from your transaction history.
        Transactions will have points taken from them:
        - In order of their datetime
        - In an amount that would not make the payer's remaining balance negative

        points: Number of points to spend

        return: dict of payers to net point change
        '''
        print(f"@spend_points {points=}")
        if points > sum(self.balances.values()):
            print("@spend_points Returning not enough points exception")
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Not enough points available to cover spend")

        index = 0
        payer_spend = {}
        done = False
        while not done:
            if index > len(self.transactions) or len(self.transactions) < 1:
                print("@spend_points Returning not enough transactions exception")
                raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Not enough transactions to cover spend")

            transaction = self.transactions.pop(index)

            if self.balances[transaction.payer] < 1:
                self.transactions.insert(index, transaction)
                index += 1
                continue

            amount_to_pay, done = self._calc_amount_to_pay(points, transaction)

            transaction.points -= amount_to_pay
            points -= amount_to_pay
            if transaction.points > 0:
                self.transactions.insert(index, transaction)
                index += 1
            self._add_balance_points(payer_spend, transaction.payer, amount_to_pay * -1)
            self._add_balance_points(self.balances, transaction.payer, amount_to_pay * -1)
        
        print(f"@spend_points returning {payer_spend=}")
        return payer_spend

    def clear_db(self):
        '''
        Clears both transactions and balances data
        '''
        print("@clear_db")
        self.transactions.clear()
        self.balances.clear()

    def _add_balance_points(self, balances: dict, payer: str, points: int):
        '''
        Add points to a payer balance dict
        '''
        print(f"@_add_balance_points {balances=}, {payer=}, {points=}")
        if payer in balances:
            balances[payer] += points
        else:
            balances[payer] = points

    def _sort_add_transaction(self) -> None:
        '''
        Sort transactions by timestamp

        NOTE: I considered using a binary tree insertion to do this in log(n) time;
        however, I decided against that since in a production environment "transactions"
        would likely be stored in a SQL database indexed around the transaction time.
        That would already be able to insert in log(n) time, so making that optimization
        in this testing solution would be redundant and removed if turned into a
        production version.
        '''
        print("@_sort_add_transaction")
        self.transactions.sort(key= lambda x: x.timestamp)

    def _calc_amount_to_pay(self, points, transaction) -> tuple[int, bool]:
        '''
        Calculate amount to pay from current transaction given remaining points

        points: Number of points remaining to be spent
        transaction: Current transaction

        returns
        amount_to_pay: Points to be spent from current transaction
        done: Will remaining debt be 0 after this payment?
        '''
        print(f"@_calc_amount_to_pay {points=}, {transaction=}")
        amount_to_pay = 0
        done = False

        # Transaction can pay off all remaining debt
        if transaction.points >= points and self.balances[transaction.payer] >= points:
            amount_to_pay = points
            done = True
        
        # Transaction needs to only partially pay. Full payment would cause negative payer balance
        elif transaction.points > self.balances[transaction.payer]:
            amount_to_pay = self.balances[transaction.payer]
        
        # All of transaction will be used to pay down debt
        else:
            amount_to_pay = transaction.points
        
        print(f"@_calc_amount_to_pay returning {amount_to_pay=}, {done=}")
        return amount_to_pay, done
