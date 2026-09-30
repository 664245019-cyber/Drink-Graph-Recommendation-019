import streamlit as st
import os
from neo4j_service import Neo4jService

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Drink Recommendation System", page_icon="🧋", layout="wide")

# เชื่อมต่อ Neo4j Service
@st.cache_resource
def get_neo4j_service():
    return Neo4jService()

db = get_neo4j_service()

st.title("🧋 ระบบแนะนำเครื่องดื่มอัจฉริยะด้วย Graph Database")
st.write("ระบบแนะนำเครื่องดื่มจากพฤติกรรมของเพื่อนในเครือข่ายสังคม (Neo4j Graph Database)")

# สร้าง Sidebar สำหรับเลือกโหมดการใช้งาน
menu = st.sidebar.selectbox("📂 เมนูหลัก", ["🎯 หน้าแนะนำเครื่องดื่ม (Recommendation)", "⚙️ จัดการข้อมูล (CRUD Admin)"])

# ==========================================
# โหมดที่ 1: หน้าแนะนำเครื่องดื่ม
# ==========================================
if menu == "🎯 หน้าแนะนำเครื่องดื่ม (Recommendation)":
    st.header("🎯 ค้นหาเมนูแนะนำสำหรับคุณ")
    
    # ดึงรายชื่อ User ทั้งหมดจากฐานข้อมูลมาแสดงใน Dropdown
    user_query = "MATCH (u:User) RETURN u.name AS name ORDER BY name"
    user_result = db.run_query(user_query)
    user_list = [row["name"] for row in user_result] if user_result else ["หนึ่ง"]
    
    selected_user = st.selectbox("👤 เลือกรายชื่อผู้ใช้ที่คุณต้องการดูคำแนะนำ:", user_list)
    
    if selected_user:
        st.info(f"กำลังค้นหาคำแนะนำสำหรับ: **{selected_user}** (อ้างอิงจากสิ่งที่เพื่อนสนิทชื่นชอบแต่คุณยังไม่เคยลอง)")
        
        # Query Cypher: เพื่อนของ User เลือกสั่งอะไร ที่ User คนนี้ยังไม่เคยสั่ง
        rec_query = """
        MATCH (u:User {name: $username})-[:FRIEND_WITH]-(friend:User)-[:ORDERED]->(d:Drink)
        WHERE NOT (u)-[:ORDERED]->(d)
        RETURN DISTINCT d.name AS drink_name, d.price AS price, d.image AS image_path, friend.name AS friend_name
        """
        recs = db.run_query(rec_query, {"username": selected_user})
        
        if recs:
            st.success(f"พบเมนูแนะนำจำนวน {len(recs)} รายการ!")
            
            # แสดงผลแบบ Grid Columns
            cols = st.columns(3)
            for i, row in enumerate(recs):
                with cols[i % 3]:
                    st.markdown(f"### 🥤 {row['drink_name']}")
                    
                    # ตรวจสอบและแสดงรูปภาพจากโฟลเดอร์ images/
                    img_path = row['image_path']
                    if img_path and os.path.exists(img_path):
                        st.image(img_path, caption=f"แนะนำโดยเพื่อน: {row['friend_name']}", use_container_width=True)
                    else:
                        st.warning(f"ไม่พบไฟล์รูปภาพ ({img_path}) ในโฟลเดอร์")
                        
                    st.write(f"💰 **ราคา:** {row['price']} บาท")
                    st.write(f"👥 **เพื่อนที่กินเมนูล่าสุด:** {row['friend_name']}")
                    
                    if st.button(f"สั่งซื้อเมนูนี้", key=f"buy_{i}"):
                        st.success(f"บันทึกการสั่งซื้อ {row['drink_name']} เรียบร้อยแล้ว!")
        else:
            st.warning("ยังไม่มีคำแนะนำใหม่ในขณะนี้ (เพื่อนอาจจะกินเมนูเหมือนคุณหมดแล้ว หรือยังไม่ได้เพิ่มความสัมพันธ์เพื่อน)")

# ==========================================
# โหมดที่ 2: จัดการข้อมูล (CRUD Admin)
# ==========================================
elif menu == "⚙️ จัดการข้อมูล (CRUD Admin)":
    st.header("⚙️ ระบบจัดการข้อมูลฐานข้อมูล Graph")
    
    tab1, tab2, tab3 = st.tabs(["➕ เพิ่มผู้ใช้ (User)", "➕ เพิ่มเมนูเครื่องดื่ม (Drink)", "🤝 เพิ่มความสัมพันธ์เพื่อน"])
    
    # 1. เพิ่ม User
    with tab1:
        st.subheader("เพิ่มรายชื่อผู้ใช้ใหม่")
        new_user = st.text_input("ชื่อผู้ใช้ (เช่น สมชาย)")
        if st.button("บันทึกผู้ใช้"):
            if new_user:
                q = "CREATE (u:User {name: $name})"
                db.run_query(q, {"name": new_user})
                st.success(f"เพิ่มผู้ใช้ {new_user} สำเร็จ!")
            else:
                st.error("กรุณากรอกชื่อผู้ใช้")
                
    # 2. เพิ่ม Drink
    with tab2:
        st.subheader("เพิ่มเมนูเครื่องดื่มใหม่ (ผูกกับไฟล์รูปในโฟลเดอร์ images/)")
        drink_name = st.text_input("ชื่อเครื่องดื่ม")
        price = st.number_input("ราคา (บาท)", min_value=0, value=50)
        
        # ดึงรายชื่อไฟล์ภาพจากโฟลเดอร์ images/ มาให้เลือกอัตโนมัติ
        image_folder = "images"
        if os.path.exists(image_folder):
            image_files = os.listdir(image_folder)
        else:
            image_files = []
            
        selected_img_file = st.selectbox("เลือกไฟล์รูปภาพจากโฟลเดอร์ images/", image_files)
        
        if selected_img_file:
            st.image(os.path.join(image_folder, selected_img_file), width=150, caption="ตัวอย่างรูปภาพ")
            
        if st.button("บันทึกเมนูเครื่องดื่ม"):
            if drink_name and selected_img_file:
                img_path = f"images/{selected_img_file}"
                q = "CREATE (d:Drink {name: \(name, price:\)price, image: $image})"
                db.run_query(q, {"name": drink_name, "price": price, "image": img_path})
                st.success(f"เพิ่มเมนู {drink_name} สำเร็จ!")
            else:
                st.error("กรุณากรอกข้อมูลให้ครบถ้วน")
                
    # 3. เพิ่มความสัมพันธ์เพื่อน
    with tab3:
        st.subheader("ผูกความสัมพันธ์เพื่อน (Friend With)")
        
        # ดึงรายชื่อ User มาทำ Dropdown
        user_res = db.run_query("MATCH (u:User) RETURN u.name AS name ORDER BY name")
        all_users = [r["name"] for r in user_res] if user_res else []
        
        if len(all_users) >= 2:
            u1 = st.selectbox("ผู้ใช้คนที่ 1", all_users, key="u1")
            u2 = st.selectbox("ผู้ใช้คนที่ 2", all_users, key="u2")
            
            if st.button("เชื่อมความสัมพันธ์เพื่อน"):
                if u1 != u2:
                    q = """
                    MATCH (a:User {name: \(u1}), (b:User {name:\)u2})
                    MERGE (a)-[:FRIEND_WITH]-(b)
                    """
                    db.run_query(q, {"u1": u1, "u2": u2})
                    st.success(f"เชื่อมความสัมพันธ์ระหว่าง {u1} และ {u2} เป็นเพื่อนกันเรียบร้อย!")
                else:
                    st.error("ไม่สามารถเลือกชื่อเดียวกันได้")
        else:
            st.warning("ต้องมีข้อมูลผู้ใช้อย่างน้อย 2 คนในระบบจึงจะเชื่อมเพื่อนได้")