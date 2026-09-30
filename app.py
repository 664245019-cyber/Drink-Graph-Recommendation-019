import streamlit as st
import os
from neo4j_service import Neo4jService

st.set_page_config(page_title="Drink Recommendation System", page_icon="🧋", layout="wide")

@st.cache_resource
def get_neo4j_service():
    return Neo4jService()

db = get_neo4j_service()

st.title("🧋 ระบบแนะนำเครื่องดื่มอัจฉริยะด้วย Graph Database")
st.write("ระบบแนะนำเครื่องดื่มจากพฤติกรรมของเพื่อนในเครือข่ายสังคม (Neo4j Graph Database)")

menu = st.sidebar.selectbox("📂 เมนูหลัก", ["🎯 หน้าแนะนำเครื่องดื่ม (Recommendation)", "⚙️ จัดการข้อมูล (CRUD Admin)"])

# ป้องกันแอปพังถ้าต่อ Neo4j ไม่ติด
try:
    user_query = "MATCH (u:User) RETURN u.name AS name ORDER BY name"
    user_result = db.run_query(user_query)
    user_list = [row["name"] for row in user_result] if user_result else []
except Exception:
    user_list = []

if menu == "🎯 หน้าแนะนำเครื่องดื่ม (Recommendation)":
    st.header("🎯 ค้นหาเมนูแนะนำสำหรับคุณ")
    
    if not user_list:
        st.error("⚠️ ไม่สามารถเชื่อมต่อกับฐานข้อมูล Neo4j หรือยังไม่มีข้อมูลผู้ใช้ในระบบ กรุณาตรวจสอบสถานะฐานข้อมูล Aura ว่าเปิดใช้งานอยู่หรือไม่")
    else:
        selected_user = st.selectbox("👤 เลือกรายชื่อผู้ใช้ที่คุณต้องการดูคำแนะนำ:", user_list)
        
        if selected_user:
            st.info(f"กำลังค้นหาคำแนะนำสำหรับ: **{selected_user}**")
            
            rec_query = """
            MATCH (u:User {name: $username})-[:FRIEND_WITH]-(friend:User)-[:ORDERED]->(d:Drink)
            WHERE NOT (u)-[:ORDERED]->(d)
            RETURN DISTINCT d.name AS drink_name, d.price AS price, d.image AS image_path, friend.name AS friend_name
            """
            recs = db.run_query(rec_query, {"username": selected_user})
            
            if recs:
                st.success(f"พบเมนูแนะนำจำนวน {len(recs)} รายการ!")
                cols = st.columns(3)
                for i, row in enumerate(recs):
                    with cols[i % 3]:
                        st.markdown(f"### 🥤 {row['drink_name']}")
                        img_path = row['image_path']
                        if img_path and os.path.exists(img_path):
                            st.image(img_path, caption=f"แนะนำโดยเพื่อน: {row['friend_name']}", use_container_width=True)
                        else:
                            st.warning(f"ไม่พบไฟล์รูปภาพ ({img_path}) ในโฟลเดอร์")
                        st.write(f"💰 **ราคา:** {row['price']} บาท")
                        st.write(f"👥 **เพื่อนที่กิน:** {row['friend_name']}")
            else:
                st.warning("ยังไม่มีคำแนะนำใหม่ในขณะนี้")

elif menu == "⚙️ จัดการข้อมูล (CRUD Admin)":
    st.header("⚙️ ระบบจัดการข้อมูลฐานข้อมูล Graph")
    st.write("ส่วนจัดการข้อมูล (เพิ่ม User, เมนู, เพื่อน)")