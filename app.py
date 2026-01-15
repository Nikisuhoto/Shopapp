import streamlit as st
import pandas as pd
import sqlite3

# Настройка на базата данни
conn = sqlite3.connect('prices.db', check_same_thread=False)
c = conn.cursor()

def create_table():
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY, name TEXT, brand TEXT, shop TEXT, 
                  unit_price REAL, total_price REAL, weight REAL, unit_type TEXT)''')
    conn.commit()

def add_data(name, brand, shop, unit_price, total_price, weight, unit_type):
    c.execute('INSERT INTO products (name, brand, shop, unit_price, total_price, weight, unit_type) VALUES (?,?,?,?,?,?,?)',
              (name, brand, shop, unit_price, total_price, weight, unit_type))
    conn.commit()

create_table()

st.title("🛒 Моят Ценоразпис 2026")

# Форма за добавяне на продукт
with st.expander("➕ Добави нов продукт"):
    name = st.text_input("Продукт (напр. Кашкавал)")
    brand = st.text_input("Марка")
    shop = st.selectbox("Магазин", ["Lidl", "Kaufland", "Billa", "Фантастико", "T-Market", "Друг"])
    unit_type = st.radio("Мерна единица", ["кг", "брой"])
    
    col1, col2 = st.columns(2)
    with col1:
        weight = st.number_input("Грамаж/Количество (напр. 0.400)", min_value=0.01)
    with col2:
        price = st.number_input("Обща цена в лв.", min_value=0.01)
    
    # Автоматично изчисляване на цена за единица
    final_unit_price = round(price / weight, 2)
    st.info(f"Изчислена цена за 1 {unit_type}: {final_unit_price} лв.")

    if st.button("Запази продукта"):
        add_data(name, brand, shop, final_unit_price, price, weight, unit_type)
        st.success(f"Добавено: {name} ({brand}) в {shop}")

# Списък и Търсене
st.subheader("🔍 Сравнение на цени")
search_query = st.text_input("Търси продукт (напр. кашкавал)")

df = pd.read_sql_query("SELECT name as Продукт, brand as Марка, shop as Магазин, unit_price as 'Цена за 1кг/бр', total_price as 'Обща цена', weight as Количество FROM products", conn)

if search_query:
    df = df[df['Продукт'].str.contains(search_query, case=False)]

# Сортиране
sort_order = st.selectbox("Сортирай по цена:", ["Най-евтини първо", "Най-скъпи първо"])
if sort_order == "Най-евтини първо":
    df = df.sort_values(by='Цена за 1кг/бр', ascending=True)
else:
    df = df.sort_values(by='Цена за 1кг/бр', ascending=False)

st.dataframe(df, use_container_width=True)
