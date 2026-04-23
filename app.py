import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# --- 1. การตั้งค่าพื้นฐาน ---
FILE_NAME = "money_tracker.xlsx"
CURRENT_YEAR = datetime.now().year
CURRENT_MONTH = datetime.now().month
CURRENT_DAY = datetime.now().day

st.set_page_config(page_title="2026 Smart Wealth", layout="wide", page_icon="💰")

# ฟังก์ชันบันทึกข้อมูล
def save_all_data(df, year_sheet):
    with pd.ExcelWriter(FILE_NAME, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name=str(year_sheet), index=False)

def append_data(data, year_sheet):
    if os.path.exists(FILE_NAME):
        with pd.ExcelWriter(FILE_NAME, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            try:
                existing_df = pd.read_excel(FILE_NAME, sheet_name=str(year_sheet))
                updated_df = pd.concat([existing_df, data], ignore_index=True)
                updated_df.to_excel(writer, sheet_name=str(year_sheet), index=False)
            except:
                data.to_excel(writer, sheet_name=str(year_sheet), index=False)
    else:
        with pd.ExcelWriter(FILE_NAME, engine='openpyxl') as writer:
            data.to_excel(writer, sheet_name=str(year_sheet), index=False)

# --- 2. Sidebar ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2489/2489756.png", width=80)
    st.title("Settings")
    selected_year = st.number_input("📅 เลือกปีคริสต์ศักราช", value=CURRENT_YEAR)
    starting_balance = st.number_input("💵 เงินต้นตั้งต้น (บาท)", min_value=0.0, value=0.0, step=1000.0)
    st.divider()
    st.caption("Developed by Chin 🚀")

# --- 3. โหลดข้อมูล ---
df_current = pd.DataFrame()
if os.path.exists(FILE_NAME):
    try:
        df_current = pd.read_excel(FILE_NAME, sheet_name=str(selected_year))
    except:
        pass

# --- 4. คำนวณและแสดง Dashboard ---
income_total = 0
expense_total = 0
if not df_current.empty:
    income_total = df_current[df_current['ประเภทหลัก'] == 'รายรับ']['จำนวนเงิน'].sum()
    expense_total = df_current[df_current['ประเภทหลัก'] == 'รายจ่าย']['จำนวนเงิน'].sum()

final_balance = starting_balance + income_total - expense_total

st.markdown(f"<h1 style='text-align: center;'>📉 บัญชีรายรับ-รายจ่าย ปี {selected_year}</h1>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.container(border=True).metric("💰 เงินคงเหลือปัจจุบัน", f"{final_balance:,.2f} ฿")
c2.container(border=True).metric("📈 รายรับสะสม", f"{income_total:,.2f} ฿")
c3.container(border=True).metric("📉 รายจ่ายสะสม", f"{expense_total:,.2f} ฿", delta=f"{(income_total-expense_total):,.2f} ฿")

# --- 5. กราฟวิเคราะห์ (ย้ายมาไว้ข้างบนเพื่อให้เห็นภาพรวมก่อน) ---
if not df_current.empty:
    g1, g2 = st.columns([2, 1])
    with g1:
        df_graph = df_current.copy()
        df_graph['วันที่'] = pd.to_datetime(df_graph['วันที่'])
        df_graph['เดือน'] = df_graph['วันที่'].dt.month
        monthly_data = df_graph.groupby(['เดือน', 'ประเภทหลัก'])['จำนวนเงิน'].sum().reset_index()
        fig_bar = px.bar(monthly_data, x='เดือน', y='จำนวนเงิน', color='ประเภทหลัก', barmode='group', 
                         title="รายรับ-รายจ่าย รายเดือน", color_discrete_map={'รายรับ': '#2ecc71', 'รายจ่าย': '#e74c3c'})
        st.plotly_chart(fig_bar, use_container_width=True)
    with g2:
        fig_pie = px.pie(df_current[df_current['ประเภทหลัก'] == 'รายจ่าย'], values='จำนวนเงิน', names='รายการ', 
                         title="สัดส่วนรายจ่าย", hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

st.divider()

# --- 6. ส่วนเพิ่มรายการใหม่ (Full Width) ---
st.subheader("➕ เพิ่มรายการใหม่")
with st.container(border=True):
    d1, d2, d3, d4 = st.columns([1, 1, 1.5, 1])
    with d1:
        month = st.selectbox("เดือน", range(1, 13), index=CURRENT_MONTH - 1)
    with d2:
        day = st.selectbox("วันที่", range(1, 32), index=CURRENT_DAY - 1)
    with d3:
        category = st.selectbox("หมวดหมู่", ["ค่าอาหาร", "ค่าใช้จ่าย", "เติมเกม", "เงินเดือน(รายรับ)"])
    with d4:
        amount = st.number_input("จำนวนเงิน", min_value=0.0)
    
    suggestions = [""]
    if not df_current.empty:
        suggestions = [""] + df_current['หมายเหตุ'].dropna().unique().tolist()
    
    is_new = st.checkbox("พิมพ์รายละเอียดใหม่เอง", value=True)
    if is_new:
        note = st.text_input("รายละเอียด", placeholder="เช่น กะเพราไข่ดาว")
    else:
        note = st.selectbox("เลือกจากประวัติที่เคยบันทึก", options=suggestions)
    
    if st.button("💾 บันทึกข้อมูล", use_container_width=True, type="primary"):
        main_type = "รายรับ" if "รายรับ" in category else "รายจ่าย"
        new_data = pd.DataFrame([{
            "วันที่": f"{selected_year}-{month:02d}-{day:02d}",
            "รายการ": category, "ประเภทหลัก": main_type,
            "จำนวนเงิน": amount, "หมายเหตุ": note,
            "ID": datetime.now().strftime("%Y%m%d%H%M%S%f")
        }])
        append_data(new_data, selected_year)
        st.success("บันทึกสำเร็จ!")
        st.rerun()

st.divider()

# --- 7. จัดการประวัติการบันทึก ---
st.subheader("📋 จัดการประวัติการบันทึก")
if not df_current.empty:
    # สร้างสำเนาข้อมูลและแปลงทุกคอลัมน์เป็น String เพื่อป้องกัน OverflowError
    df_display = df_current.copy().astype(str) 
    
    if "ลบ" not in df_display.columns:
        # ใส่ค่า False เป็น Boolean เพื่อให้ Checkbox ทำงานได้
        df_display.insert(0, "ลบ", False)
        df_display["ลบ"] = False 

    edited_df = st.data_editor(
        df_display.iloc[::-1],
        column_config={
            "ลบ": st.column_config.CheckboxColumn(help="ติ๊กเพื่อเลือกรายการที่ต้องการลบ"),
            "ID": None # ซ่อน ID ไว้
        },
        disabled=["วันที่", "รายการ", "ประเภทหลัก", "จำนวนเงิน", "หมายเหตุ", "ID"],
        use_container_width=True,
        hide_index=True
    )

    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        if st.button("🗑️ ยืนยันการลบรายการที่เลือก", type="secondary", use_container_width=True):
            ids_to_delete = edited_df[edited_df["ลบ"] == True]["ID"].tolist()
            if ids_to_delete:
                df_final = df_current[~df_current["ID"].isin(ids_to_delete)]
                save_all_data(df_final, selected_year)
                st.success("ลบรายการเรียบร้อย!")
                st.rerun()
            else:
                st.warning("กรุณาติ๊กช่อง 'ลบ' ก่อนครับ")
    with col_btn2:
        csv = df_current.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Export ข้อมูลเป็น CSV", csv, "history.csv", "text/csv", use_container_width=True)
else:
    st.info("ยังไม่มีข้อมูลสำหรับปีนี้")
