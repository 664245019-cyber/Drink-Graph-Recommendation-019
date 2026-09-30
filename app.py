import streamlit as st
import os
from neo4j_service import Neo4jService

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Drink Recommendation System", page_icon="🥤", layout="wide")

# เชื่อมต่อฐานข้อมูล
db = Neo4jService()

st.title("🥤 ระบบแนะนำเครื่องดื่มด้วย Neo4j Graph Database")
st.markdown("---")

# สร้าง Sidebar สำหรับเลือกโหมดการใช้งาน
menu = st.sidebar.selectbox("📌 เลือกเมนูการใช้งาน", ["🔍 ระบบแนะนำเครื่องดื่ม (Recommendation)", "⚙️ จัดการระบบ (Admin CRUD)"])

# ==========================================
# 1. โหมดระบบแนะนำเครื่องดื่ม
# ==========================================
if menu == "🔍 ระบบแนะนำเครื่องดื่ม (Recommendation)":
    st.subheader("👥 ค้นหาเพื่อนและเมนูแนะนำ")
    
    # ดึงรายชื่อ User ทั้งหมดจากฐานข้อมูล
    user_query = "MATCH (u:User) RETURN u.name AS name ORDER BY name"
    user_result = db.run_query(user_query)
    user_list = [row["name"] for row in user_result] if user_result else []
    
    if user_list:
        selected_user = st.selectbox("เลือกรายชื่อของคุณ:", user_list)
        
        if st.button("🚀 ค้นหาคำแนะนำเพื่อน"):
            # Cypher Query สำหรับแนะนำเครื่องดื่มที่เพื่อนสั่ง แต่เรายังไม่เคยสั่ง
            rec_query = """
            MATCH (u:User {name: $username})-[:FRIEND_WITH]-(friend:User)-[:ORDERED]->(d:Drink)
            WHERE NOT (u)-[:ORDERED]->(d)
            RETURN DISTINCT d.name AS drink_name, d.price AS price, d.image AS image, collect(DISTINCT friend.name) AS recommended_by
            """
            recs = db.run_query(rec_query, {"username": selected_user})
            
            if recs:
                st.success(f"พบเมนูแนะนำจำนวน {len(recs)} รายการ!")
                
                # แสดงผลแบบ Grid พร้อมปรับขนาดรูปภาพให้เท่ากัน
                cols = st.columns(3)
                for index, row in enumerate(recs):
                    col = cols[index % 3]
                    with col:
                        st.markdown(f"### {row['drink_name']}")
                        # ตรวจสอบว่ามีไฟล์รูปภาพจริงไหม ถ้าไม่มีให้ใช้รูปสำรอง
                        img_path = row['image']
                        if not img_path or not os.path.exists(img_path):
                            img_path = "images/d1.jpg" # รูปสำรองพื้นฐาน
                        
                        # ปรับขนาดรูปภาพให้เท่ากันเป๊ะ (width=200)
                        st.image(img_path, width=200)
                        st.write(f"💰 ราคา: {row['price']} บาท")
                        st.write(f"👥 เพื่อนที่แนะนำ: {', '.join(row['recommended_by'])}")
                        st.markdown("---")
            else:
                st.info("ยังไม่มีคำแนะนำใหม่ในขณะนี้ หรือเพื่อนๆ ยังไม่ได้ลองเมนูอื่นๆ เพิ่มเติม")
    else:
        st.warning("ยังไม่พบข้อมูลผู้ใช้ในระบบ กรุณาตรวจสอบการสร้างข้อมูลใน Neo4j")

# ==========================================
# 2. โหมดจัดการระบบ (Admin CRUD: เพิ่ม / ลบ)
# ==========================================
elif menu == "⚙️ จัดการระบบ (Admin CRUD)":
    st.subheader("🛠️ แผงควบคุมผู้ดูแลระบบ (CRUD)")
    
    tab1, tab2 = st.tabs(["➕ เพิ่มเมนูเครื่องดื่มใหม่", "🗑️ ลบข้อมูลเครื่องดื่ม/ผู้ใช้"])
    
    with tab1:
        st.markdown("### เพิ่มเครื่องดื่มใหม่เข้าสู่ระบบ")
        with st.form("add_drink_form"):
            new_name = st.text_input("ชื่อเครื่องดื่ม")
            new_price = st.number_input("ราคา (บาท)", min_value=10, max_value=500, value=60)
            new_image = st.text_input("path รูปภาพ (เช่น images/d11.jpg)", value="images/d1.jpg")
            submit_drink = st.form_submit_button("บันทึกเครื่องดื่มใหม่")
            
            if submit_drink and new_name:
                create_query = "CREATE (d:Drink {name: \(name, price:\)price, image: $image})"
                db.run_query(create_query, {"name": new_name, "price": new_price, "image": new_image})
                st.success(f"เพิ่มเมนู '{new_name}' สำเร็จเรียบร้อย!")
                
    with tab2:
        st.markdown("### ลบเมนูเครื่องดื่มออกจากระบบ")
        drink_query = "MATCH (d:Drink) RETURN d.name AS name ORDER BY name"
        drink_res = db.run_query(drink_query)
        drink_list = [r["name"] for r in drink_res] if drink_res else []
        
        if drink_list:
            selected_drink_to_delete = st.selectbox("เลือกเมนูที่ต้องการลบ:", drink_list)
            if st.button("❌ ลบเมนูนี้", type="primary"):
                del_query = "MATCH (d:Drink {name: $name}) DETACH DELETE d"
                db.run_query(del_query, {"name": selected_drink_to_delete})
                st.success(f"ลบเมนู '{selected_drink_to_delete}' เรียบร้อยแล้ว! (กรุณารีเฟรชหน้าจอ)")
        else:
            st.info("ไม่มีเมนูเครื่องดื่มในระบบให้ลบ")