from pathlib import Path
from datetime import date
import pandas as pd
import streamlit as st

DATA = Path(__file__).with_name("expenses.csv")
COLUMNS = ["date", "category", "description", "amount"]

def load_data():
    if DATA.exists():
        try:
            return pd.read_csv(DATA)
        except (pd.errors.EmptyDataError, pd.errors.ParserError):
            pass
    return pd.DataFrame(columns=COLUMNS)

def save_data(df):
    df.to_csv(DATA, index=False)

st.set_page_config(page_title="Personal Finance Dashboard", page_icon="💸", layout="wide")
st.title("💸 Personal Finance Dashboard")
st.caption("A local learning project. Avoid uploading real personal financial data to public GitHub.")

with st.form("add_expense", clear_on_submit=True):
    st.subheader("Add an expense")
    col1, col2 = st.columns(2)
    expense_date = col1.date_input("Date", value=date.today())
    category = col2.selectbox("Category", ["Food", "Transport", "Education", "Shopping", "Bills", "Other"])
    description = st.text_input("Description")
    amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0)
    submitted = st.form_submit_button("Add expense")
    if submitted:
        if amount <= 0:
            st.error("Enter an amount greater than zero.")
        else:
            df = load_data()
            row = pd.DataFrame([{
                "date": expense_date.isoformat(),
                "category": category,
                "description": description.strip(),
                "amount": float(amount)
            }])
            save_data(pd.concat([df, row], ignore_index=True))
            st.success("Expense saved locally.")
            st.rerun()

df = load_data()
st.subheader("Overview")
if df.empty:
    st.info("No expenses yet. Add your first expense above.")
else:
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
    c1, c2 = st.columns(2)
    c1.metric("Total spent", f"₹{df['amount'].sum():,.2f}")
    c2.metric("Number of entries", len(df))
    st.subheader("Spending by category")
    st.bar_chart(df.groupby("category")["amount"].sum().sort_values(ascending=False))
    st.subheader("Expense history")
    st.dataframe(df.sort_values("date", ascending=False), use_container_width=True)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "expense_export.csv", "text/csv")
