import os
import time
import streamlit as st
from PIL import Image, ImageOps
from neo4j_service import Neo4jService

st.set_page_config(page_title="Drink Recommendation", page_icon="", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;600;700&display=swap');
html, body, .stApp, p, h1, h2, h3, h4, h5, h6, label, li, td, th, input, textarea, select, button,
[data-testid="stMarkdownContainer"] *, [data-testid="stSidebar"] label, .stTabs button *, .stToast *
{font-family:'Sarabun',sans-serif;}
/* คืนฟอนต์ไอคอนของ Streamlit (กันชื่อไอคอนโผล่เป็นข้อความ) */
[data-testid="stIconMaterial"], span[class*="material-symbols"], span[class*="material-icons"]
{font-family:'Material Symbols Rounded','Material Icons' !important;}
.stApp {background:linear-gradient(135deg,#fff8f1 0%,#fdeff7 50%,#eef1ff 100%); color:#2b2350;}
[data-testid="stHeader"] {background:transparent;}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#2b2350,#5b2c83);}
[data-testid="stSidebar"] * {color:#fff !important;}
.hero {background:linear-gradient(120deg,#ff6f91,#b56cff 60%,#6c7bff); color:#fff; padding:28px 34px;
       border-radius:24px; box-shadow:0 12px 30px rgba(181,108,255,.3); margin-bottom:18px;}
.hero h1 {margin:0; font-size:2rem; color:#fff;} .hero p {margin:6px 0 0; opacity:.9;}
.stat {background:#fff; border-radius:18px; padding:14px 18px; box-shadow:0 6px 18px rgba(43,35,80,.08); text-align:center;}
.stat b {display:block; font-size:1.9rem; color:#b56cff;} .stat span {color:#7a7594; font-size:.9rem;}
.pill {display:inline-block; background:#ffe3ec; color:#d6336c; border-radius:999px; padding:2px 12px;
       margin:2px 4px 2px 0; font-size:.85rem; font-weight:600;}
.pill.blue {background:#e5e9ff; color:#4c5bd4;}
.price {font-weight:700; color:#ff6f91; font-size:1.1rem;}
.ph {aspect-ratio:1/1; border-radius:16px; background:#f3eefc; display:flex; align-items:center; justify-content:center; font-size:3rem;}
[data-testid="stImage"] img {border-radius:16px; aspect-ratio:1/1; object-fit:cover; width:100%;}
[data-testid="stVerticalBlockBorderWrapper"] {border-radius:20px; background:#fff; box-shadow:0 6px 18px rgba(43,35,80,.08); border:none;}
.stButton>button, .stFormSubmitButton>button {border-radius:999px; font-weight:600; border:none;
       background:linear-gradient(120deg,#ff6f91,#b56cff); color:#fff; padding:.4rem 1.2rem;}
.stButton>button:hover, .stFormSubmitButton>button:hover {filter:brightness(1.08); color:#fff;}
h2, h3, h4 {color:#2b2350;}
</style>
""", unsafe_allow_html=True)

db = Neo4jService()
if not db.ok:
    st.error(f"เชื่อมต่อ Neo4j ไม่ได้: {db.error}")
    st.stop()

if "flash" in st.session_state:
    msg, icon = st.session_state.pop("flash")
    st.toast(msg, icon=icon)


def done(msg, icon="✅"):
    st.session_state["flash"] = (msg, icon)
    st.rerun()


def pills(items, cls=""):
    return "".join(f'<span class="pill {cls}">{i}</span>' for i in items) or "<i>ยังไม่มี</i>"


@st.cache_data(show_spinner=False)
def square_image(path, mtime, size=400):
    img = Image.open(path).convert("RGB")
    return ImageOps.fit(img, (size, size), Image.LANCZOS)  # ตัดกลางภาพให้เป็นจัตุรัส


def show_image(path):
    if path and os.path.exists(path):
        st.image(square_image(path, os.path.getmtime(path)))
    else:
        st.markdown('<div class="ph">🥤</div>', unsafe_allow_html=True)


# ---------- Hero + สถิติ ----------
st.markdown('<div class="hero"><h1> Drink Recommendation</h1>'
            '<p>แนะนำเครื่องดื่มจากเพื่อนของคุณ ด้วย Neo4j Graph Database</p></div>', unsafe_allow_html=True)
s = db.stats()
for col, (k, label) in zip(st.columns(4), [("users", "👤 คน"), ("drinks", "🥤 เมนู"),
                                           ("friends", "🤝 ความเป็นเพื่อน"), ("orders", "🧾 ออเดอร์")]):
    col.markdown(f'<div class="stat"><b>{s[k]}</b><span>{label}</span></div>', unsafe_allow_html=True)
st.write("")

page = st.sidebar.radio("เมนู", ["🔍 แนะนำเครื่องดื่ม", "👥 จัดการคน & เพื่อน",
                                 "🥤 จัดการเมนู & ออเดอร์", "🕸️ กราฟความสัมพันธ์"])
users = db.users()

# ==========================================
# 1. แนะนำเครื่องดื่ม
# ==========================================
if page.startswith("🔍"):
    if not users:
        st.info("ยังไม่มีคนในระบบ ไปเพิ่มที่หน้า 'จัดการคน & เพื่อน' ได้เลย")
        st.stop()
    me = st.selectbox("คุณคือใคร?", users)
    friends = db.friends_of(me)
    st.markdown(f"**เพื่อนของ {me}:** " + pills(friends, "blue"), unsafe_allow_html=True)
    recs = db.recommend(me)
    st.subheader(f"✨ เมนูแนะนำสำหรับ {me}" + (f" ({len(recs)})" if recs else ""))
    if not recs:
        st.info("ยังไม่มีเมนูแนะนำ: ลองเพิ่มเพื่อน หรือให้เพื่อนบันทึกออเดอร์เพิ่ม")
    cols = st.columns(3)
    for i, r in enumerate(recs):
        with cols[i % 3], st.container(border=True):
            show_image(r["image"])
            st.markdown(f'<div style="min-height:3.4rem;font-size:1.25rem;font-weight:700;margin-top:6px">{r["name"]}</div>',
                        unsafe_allow_html=True)
            st.markdown(f'<span class="price">฿{r["price"]}</span>', unsafe_allow_html=True)
            st.markdown('<div style="min-height:4.2rem;margin:6px 0">เพื่อนที่สั่ง: ' + pills(r["by"]) + "</div>",
                        unsafe_allow_html=True)
            if st.button("🥤 ฉันสั่งเมนูนี้แล้ว", key=f"rec_{me}_{r['name']}"):
                db.add_order(me, r["name"])
                done(f"บันทึกออเดอร์ {r['name']} ให้ {me} แล้ว")

# ==========================================
# 2. จัดการคน & เพื่อน
# ==========================================
elif page.startswith("👥"):
    t1, t2, t3 = st.tabs(["➕ เพิ่มคน", "🤝 เพิ่มความสัมพันธ์", "✂️ ลบ"])

    with t1:
        with st.form("add_user", clear_on_submit=True):
            name = st.text_input("ชื่อคนใหม่")
            if st.form_submit_button("เพิ่มคน"):
                name = name.strip()
                if not name:
                    st.warning("กรุณาใส่ชื่อ")
                elif name in users:
                    st.warning(f"มี '{name}' อยู่แล้ว")
                else:
                    db.add_user(name)
                    done(f"เพิ่ม {name} แล้ว", "🎉")
        st.markdown("**ทุกคนในระบบ:** " + pills(users), unsafe_allow_html=True)

    with t2:
        if len(users) < 2:
            st.info("ต้องมีอย่างน้อย 2 คนถึงจะเชื่อมความสัมพันธ์ได้")
        else:
            c1, c2 = st.columns(2)
            a = c1.selectbox("คนที่ 1", users, key="fa")
            b = c2.selectbox("คนที่ 2", [u for u in users if u != a], key="fb")
            st.markdown(f"เพื่อนของ {a} ตอนนี้: " + pills(db.friends_of(a), "blue"), unsafe_allow_html=True)
            if st.button("🤝 เชื่อมเป็นเพื่อนกัน"):
                if db.add_friend(a, b):
                    done(f"{a} 🤝 {b} เป็นเพื่อนกันแล้ว", "🤝")
                else:
                    st.warning("สองคนนี้เป็นเพื่อนกันอยู่แล้ว")

    with t3:
        st.markdown("##### ลบความเป็นเพื่อน")
        fr = db.friendships()
        if not fr:
            st.caption("ยังไม่มีความสัมพันธ์")
        for i, f in enumerate(fr):
            c1, c2 = st.columns([5, 1])
            c1.markdown(f'<span class="pill blue">{f["a"]}</span> 🤝 <span class="pill blue">{f["b"]}</span>',
                        unsafe_allow_html=True)
            if c2.button("ลบ", key=f"rf_{i}"):
                db.remove_friend(f["a"], f["b"])
                done("ลบความสัมพันธ์แล้ว", "🗑️")
        st.divider()
        st.markdown("##### ลบคน (ความสัมพันธ์และออเดอร์ของคนนั้นจะหายด้วย)")
        if users:
            du = st.selectbox("เลือกคนที่จะลบ", users, key="du")
            if st.checkbox(f"ยืนยันลบ {du}") and st.button("❌ ลบคนนี้"):
                db.delete_user(du)
                done(f"ลบ {du} แล้ว", "🗑️")

# ==========================================
# 3. จัดการเมนู & ออเดอร์
# ==========================================
elif page.startswith("🥤"):
    drinks = db.drinks()
    names = [d["name"] for d in drinks]
    t1, t2, t3 = st.tabs(["➕ เพิ่มเมนู", "🧾 บันทึกออเดอร์", "🗑️ ลบเมนู"])

    with t1:
        with st.form("add_drink", clear_on_submit=True):
            n = st.text_input("ชื่อเครื่องดื่ม")
            p = st.number_input("ราคา (บาท)", 10, 500, 60)
            up = st.file_uploader("รูปภาพ (ไม่บังคับ)", type=["jpg", "jpeg", "png"])
            if st.form_submit_button("บันทึกเมนู"):
                n = n.strip()
                if not n:
                    st.warning("กรุณาใส่ชื่อเมนู")
                elif n in names:
                    st.warning(f"มีเมนู '{n}' อยู่แล้ว")
                else:
                    path = ""
                    if up:
                        os.makedirs("images", exist_ok=True)
                        path = f"images/custom_{int(time.time())}.{up.name.rsplit('.', 1)[-1].lower()}"
                        with open(path, "wb") as fh:
                            fh.write(up.getbuffer())
                    db.add_drink(n, int(p), path)
                    done(f"เพิ่มเมนู {n} แล้ว", "🎉")
        if drinks:
            cols = st.columns(5)
            for i, d in enumerate(drinks):
                with cols[i % 5]:
                    show_image(d["image"])
                    st.caption(f"{d['name']} · ฿{d['price']}")

    with t2:
        if not users or not drinks:
            st.info("ต้องมีทั้งคนและเมนูก่อน")
        else:
            u = st.selectbox("ใครสั่ง?", users, key="ou")
            mine = db.orders_of(u)
            pick = st.multiselect("สั่งเมนูอะไร?", [x for x in names if x not in mine])
            if st.button("🧾 บันทึกออเดอร์") and pick:
                for x in pick:
                    db.add_order(u, x)
                done(f"บันทึก {len(pick)} ออเดอร์ให้ {u} แล้ว")
            st.markdown(f"**{u} เคยสั่ง:**")
            for x in mine:
                c1, c2 = st.columns([5, 1])
                c1.markdown(f'<span class="pill">{x}</span>', unsafe_allow_html=True)
                if c2.button("ลบ", key=f"ro_{u}_{x}"):
                    db.remove_order(u, x)
                    done("ลบออเดอร์แล้ว", "🗑️")
            if not mine:
                st.caption("ยังไม่เคยสั่งอะไร")

    with t3:
        if names:
            dd = st.selectbox("เลือกเมนูที่จะลบ", names, key="dd")
            if st.checkbox(f"ยืนยันลบ {dd}") and st.button("❌ ลบเมนูนี้"):
                db.delete_drink(dd)
                done(f"ลบ {dd} แล้ว", "🗑️")
        else:
            st.info("ยังไม่มีเมนู")

# ==========================================
# 4. กราฟความสัมพันธ์
# ==========================================
else:
    def q(t):
        return '"' + str(t).replace("\\", "\\\\").replace('"', '\\"') + '"'

    c1, c2 = st.columns([2, 1])
    focus = c1.selectbox("ไฮไลต์คน", ["— ทุกคน —"] + users)
    show_orders = c2.checkbox("แสดงเครื่องดื่มที่สั่ง", value=True)
    fr, orders, drinks = db.friendships(), db.orders(), db.drinks()
    near = {focus} | set(db.friends_of(focus)) if focus in users else set()

    g = ['graph G {', 'layout=fdp; overlap=false; splines=true; bgcolor="transparent"; K=1.1;',
         'node [fontname="Sarabun,Noto Sans Thai,sans-serif", fontsize=13, style=filled, penwidth=0, fontcolor="#2b2350"];']
    for u in users:
        col = "#ff5c8a" if u == focus else "#ffb3c7" if u in near else "#e3defa"
        fc = "white" if u == focus else "#2b2350"
        g.append(f'{q("u:"+u)} [label={q(u)}, shape=circle, fillcolor="{col}", fontcolor="{fc}", width=0.8];')
    for f in fr:
        hot = f["a"] in near and f["b"] in near
        g.append(f'{q("u:"+f["a"])} -- {q("u:"+f["b"])} [color="{"#6c7bff" if hot else "#b9c0f5"}", penwidth={3 if hot else 1.6}];')
    if show_orders:
        for d in drinks:
            g.append(f'{q("d:"+d["name"])} [label={q(d["name"])}, shape=box, style="rounded,filled", fillcolor="#ffe0b2"];')
        for o in orders:
            g.append(f'{q("u:"+o["user"])} -- {q("d:"+o["drink"])} [style=dashed, color="#d6b37a"];')
    g.append("}")

    with st.container(border=True):
        st.graphviz_chart("\n".join(g), use_container_width=True)
    st.markdown('<span class="pill">● คน</span><span class="pill blue">━ เพื่อน</span>'
                '<span class="pill" style="background:#ffe0b2;color:#a8742a">▭ เครื่องดื่ม (เส้นประ = สั่ง)</span>',
                unsafe_allow_html=True)