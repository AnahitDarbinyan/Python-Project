
import json, os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Optional

DATA_FILE = "budget_data.json"

@dataclass
class Transaction:
    type: str  # "income" or "expense"
    amount: float
    date: str
    description: str

    def __post_init__(self):
        if self.type not in ("income", "expense") or self.amount < 0:
            raise ValueError
        datetime.strptime(self.date, "%Y-%m-%d")

class BudgetTracker:
    def __init__(self, data_file=DATA_FILE):
        self.data_file = data_file
        self.transactions: List[Transaction] = []
        self.expense_limits: Dict[str, float] = {}
        self.load()

    def load(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file) as f:
                    data = json.load(f)
                self.transactions = [Transaction(**t) for t in data.get("transactions",[])]
                self.expense_limits = data.get("expense_limits", {})
            except:
                self.transactions = []
                self.expense_limits = {}

    def save(self):
        with open(self.data_file, "w") as f:
            json.dump({"transactions": [asdict(t) for t in self.transactions],
                       "expense_limits": self.expense_limits}, f, indent=4)

    def add_transaction(self, ttype:str, amount:float, date:str, desc:str):
        self.transactions.append(Transaction(ttype, amount, date, desc))
        self.save()

    def set_limit(self, month:str, limit:float):
        datetime.strptime(month, "%Y-%m")
        self.expense_limits[month] = limit
        self.save()

    def summary(self, month:Optional[str]=None):
        if month is None:
            month = datetime.now().strftime("%Y-%m")
        datetime.strptime(month, "%Y-%m")
        inc = sum(t.amount for t in self.transactions if t.type=="income" and t.date.startswith(month))
        exp = sum(t.amount for t in self.transactions if t.type=="expense" and t.date.startswith(month))
        bal = inc - exp
        limit = self.expense_limits.get(month)
        status = "No limit set" if limit is None else ("Within limit" if exp <= limit else "Limit exceeded")
        return {"month": month, "income": inc, "expense": exp, "balance": bal, "limit": limit, "status": status}

    def months(self):
        return sorted({t.date[:7] for t in self.transactions})

def prompt_float(msg):
    while True:
        try:
            val = float(input(msg).strip())
            if val < 0: print("Must be positive."); continue
            return val
        except:
            print("Invalid number.")

def prompt_date(msg, fmt):
    while True:
        val = input(msg).strip()
        try: datetime.strptime(val, fmt); return val
        except: print(f"Invalid format ({fmt}).")

def main():
    b = BudgetTracker()
    options = {
        "1": "Add Income", "2": "Add Expense", "3": "Set Monthly Expense Limit",
        "4": "View Monthly Summary", "5": "List Months", "6": "Exit"
    }
    while True:
        print("\nMenu:")
        for k,v in options.items(): print(f"{k}. {v}")
        c = input("Choice: ").strip()
        if c=="1":
            amt = prompt_float("Amount: ")
            dt = prompt_date("Date (YYYY-MM-DD): ", "%Y-%m-%d")
            desc = input("Description: ")
            try: b.add_transaction("income", amt, dt, desc); print("Income added.")
            except Exception as e: print(f"Error: {e}")
        elif c=="2":
            amt = prompt_float("Amount: ")
            dt = prompt_date("Date (YYYY-MM-DD): ", "%Y-%m-%d")
            desc = input("Description: ")
            try: b.add_transaction("expense", amt, dt, desc); print("Expense added.")
            except Exception as e: print(f"Error: {e}")
        elif c=="3":
            month = prompt_date("Month (YYYY-MM): ", "%Y-%m")
            limit = prompt_float("Limit amount: ")
            try: b.set_limit(month, limit); print("Limit set.")
            except Exception as e: print(f"Error: {e}")
        elif c=="4":
            month = input("Month (YYYY-MM), blank=now: ").strip() or None
            try:
                s = b.summary(month)
                print(f"\nSummary for {s['month']}: Income={s['income']:.2f}, Expense={s['expense']:.2f}, Balance={s['balance']:.2f}")
                print(f"Limit: {s['limit'] if s['limit'] is not None else 'None'}, Status: {s['status']}")
            except Exception as e: print(f"Error: {e}")
        elif c=="5":
            mnths = b.months()
            print("Months with data:", ", ".join(mnths) if mnths else "No data.")
        elif c=="6":
            print("Bye."); break
        else:
            print("Invalid.")

if __name__ == "__main__":
    main()







