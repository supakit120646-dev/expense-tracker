import streamlit as st
import pandas as pd
import plotly.express as px
import os
import random
from datetime import datetime, time, timedelta

# --- ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="โปรแกรมบันทึกรายจ่าย", layout="wide")

# 🛑 CSS ซ่อน Toolbar (รูปตา, แว่นขยาย) เพื่อความสะอาดตา
st.markdown("""
<style>
    [data-testid="stElementToolbar"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

FILE_NAME = 'expenses.csv'

# --- ฟังก์ชันโหลดข้อมูล ---
def load_data():
    if not os.path.exists(FILE_NAME):
        return pd.DataFrame(columns=['Date', 'Category', 'Description', 'Amount'])
    try:
        df = pd.read_csv(FILE_NAME)
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    except Exception:
        return pd.DataFrame(columns=['Date', 'Category', 'Description', 'Amount'])

# --- ฟังก์ชันบันทึกข้อมูล ---
def save_data(dt_input, category, desc, amount):
    new_data = pd.DataFrame({
        'Date': [dt_input], 
        'Category': [category],
        'Description': [desc],
        'Amount': [amount]
    })
    
    if not os.path.exists(FILE_NAME):
        new_data.to_csv(FILE_NAME, index=False)
    else:
        new_data.to_csv(FILE_NAME, mode='a', header=False, index=False)

# --- ฟังก์ชันสร้างข้อมูลทดสอบ ---
def generate_fake_data():
    categories = {
        "อาหาร": ["ข้าวมันไก่", "ก๋วยเตี๋ยวเรือ", "ชาบูหมูกระทะ", "กาแฟเย็น"],
        "เดินทาง": ["รถไฟฟ้า BTS", "รถเมล์", "วินมอเตอร์ไซค์", "แท็กซี่"],
        "ช้อปปิ้ง": ["เสื้อผ้า", "ของใช้ในบ้าน", "Shopee/Lazada"],
        "บิล/สาธารณูปโภค": ["ค่าไฟ", "ค่าน้ำ", "ค่าเน็ต", "Netflix"],
        "อื่นๆ": ["ทำบุญ", "ใส่ซอง", "ซื้อหวย"]
    }
    fake_rows = []
    for _ in range(50):
        rand_cat = random.choice(list(categories.keys()))
        rand_desc = random.choice(categories[rand_cat])
        if rand_cat == "อาหาร": amount = random.randint(40, 500)
        elif rand_cat == "เดินทาง": amount = random.randint(20, 300)
        else: amount = random.randint(100, 2000)
        days_offset = random.randint(0, 60)
        rand_date = datetime.now().date() - timedelta(days=days_offset)
        rand_time = time(random.randint(6, 23), random.randint(0, 59))
        full_datetime = datetime.combine(rand_date, rand_time)
        fake_rows.append({
            'Date': full_datetime,
            'Category': rand_cat,
            'Description': rand_desc,
            'Amount': float(amount)
        })
    df_fake = pd.DataFrame(fake_rows)
    header = not os.path.exists(FILE_NAME)
    df_fake.to_csv(FILE_NAME, mode='a', header=header, index=False)

# ================= Sidebar =================
st.sidebar.header("📝 บันทึกรายจ่าย")
tab1, tab2 = st.sidebar.tabs(["กรอกข้อมูล", "เครื่องมือทดสอบ"])

with tab1:
    with st.form("expense_form", clear_on_submit=True):
        col_d, col_t = st.columns(2)
        input_date = col_d.date_input("วันที่", datetime.now())
        input_time = col_t.time_input("เวลา", datetime.now())
        input_category = st.selectbox("หมวดหมู่", ["อาหาร", "เดินทาง", "ช้อปปิ้ง", "บิล/สาธารณูปโภค", "อื่นๆ"])
        input_desc = st.text_input("รายละเอียด")
        input_amount = st.number_input("จำนวนเงิน (บาท)", min_value=0.0, format="%.2f")
        
        if st.form_submit_button("บันทึกข้อมูล"):
            combined_datetime = datetime.combine(input_date, input_time)
            save_data(combined_datetime, input_category, input_desc, input_amount)
            st.success("บันทึกสำเร็จ!")
            st.rerun()

with tab2:
    if st.button("🎲 สุ่มข้อมูลทดสอบ"):
        generate_fake_data()
        st.success("สร้างข้อมูลเรียบร้อย")
        st.rerun()
    if st.button("🗑️ ล้างข้อมูลทั้งหมด"):
        if os.path.exists(FILE_NAME):
            os.remove(FILE_NAME)
            st.rerun()

# ================= Dashboard =================
st.title("💰 Dashboard สรุปค่าใช้จ่าย")
df = load_data()

if not df.empty:
    st.subheader("🔍 ค้นหาและกรองข้อมูล")
    
    # 1. กรองวันที่
    c1, c2 = st.columns(2)
    start_date = c1.date_input("ตั้งแต่วันที่", df['Date'].min().date())
    end_date = c2.date_input("ถึงวันที่", df['Date'].max().date())
    
    # 2. ช่องค้นหา (Search Box) - เพิ่มใหม่ตรงนี้!
    search_query = st.text_input("🔎 ค้นหา (พิมพ์วันที่, หมวดหมู่ หรือ รายละเอียด)", placeholder="เช่น อาหาร, 2024-01-29, ค่าไฟ")

    # --- Logic การ Filter ---
    # ขั้นที่ 1: กรองตามวันที่ก่อน
    mask_date = (df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)
    filtered_df = df.loc[mask_date].copy()

    # ขั้นที่ 2: กรองตามคำค้นหา (ถ้ามี)
    if search_query:
        # แปลงวันที่เป็น String เพื่อให้ค้นหาด้วย text ได้
        # และค้นหาใน Category กับ Description ด้วย
        mask_search = (
            filtered_df['Date'].astype(str).str.contains(search_query, case=False, na=False) |
            filtered_df['Category'].str.contains(search_query, case=False, na=False) |
            filtered_df['Description'].str.contains(search_query, case=False, na=False)
        )
        filtered_df = filtered_df[mask_search]

    st.markdown("---")

    # แสดง Metrics (ตัวเลขจะเปลี่ยนตามผลการค้นหา)
    total = filtered_df['Amount'].sum()
    m1, m2, m3 = st.columns(3)
    m1.metric("ยอดรวม (จากการกรอง)", f"{total:,.2f} ฿")
    m2.metric("จำนวนรายการ", f"{len(filtered_df)}")
    m3.metric("รายการล่าสุด", f"{filtered_df['Amount'].iloc[-1]:,.2f} ฿" if not filtered_df.empty else "-")

    # กราฟ
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("สัดส่วน (Pie)")
        if not filtered_df.empty:
            fig = px.pie(filtered_df, values='Amount', names='Category', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)     
    with col_g2:
        st.subheader("Timeline (Scatter)")
        if not filtered_df.empty:
            fig = px.scatter(filtered_df, x='Date', y='Amount', color='Category', size='Amount')
            st.plotly_chart(fig, use_container_width=True)

    # --- ส่วนแสดงตาราง ---
    st.subheader("📄 รายการทั้งหมด (เรียงตามเวลา)")
    
    if not filtered_df.empty:
        # 1. เรียงข้อมูลจาก อดีต -> ปัจจุบัน
        display_df = filtered_df.sort_values(by='Date', ascending=True).reset_index(drop=True)
        
        # 2. ปรับเลขหน้า (Index) ให้เริ่มที่ 1, 2, 3...
        display_df.index = display_df.index + 1
        
        # 3. จัดรูปแบบวันที่เป็นข้อความ
        display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d %H:%M')
        
        # 4. แสดงตาราง
        st.dataframe(
            display_df[["Date", "Category", "Description", "Amount"]], 
            width="stretch",
            hide_index=False 
        )
    else:
        st.warning(f"ไม่พบข้อมูลที่ตรงกับคำว่า '{search_query}' ในช่วงเวลานี้")

else:
    st.info("ยังไม่มีข้อมูลครับ")