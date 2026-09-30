import os
import streamlit as st
from neo4j import GraphDatabase


def _credentials():
    """อ่านค่าเชื่อมต่อจาก .streamlit/secrets.toml ก่อน ถ้าไม่มีใช้ environment variable"""
    try:
        s = st.secrets["neo4j"]
        return s["uri"], s["user"], s["password"]
    except Exception:
        return (os.getenv("NEO4J_URI"), os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))


@st.cache_resource(show_spinner=False)
def _driver():
    uri, user, pw = _credentials()
    if not (uri and user and pw):
        raise RuntimeError("ยังไม่ได้ตั้งค่า Neo4j (ดูไฟล์ .streamlit/secrets.toml.example)")
    d = GraphDatabase.driver(uri, auth=(user, pw))
    d.verify_connectivity()
    return d


class Neo4jService:
    def __init__(self):
        self.error = None
        try:
            self.driver = _driver()
        except Exception as e:
            self.driver, self.error = None, str(e)

    @property
    def ok(self):
        return self.driver is not None

    def run(self, query, **params):
        if not self.driver:
            return []
        try:
            with self.driver.session() as s:
                return [r.data() for r in s.run(query, params)]
        except Exception as e:
            st.error(f"Query ผิดพลาด: {e}")
            return []

    # ---------- อ่านข้อมูล ----------
    def users(self):
        return [r["name"] for r in self.run("MATCH (u:User) RETURN u.name AS name ORDER BY name")]

    def drinks(self):
        return self.run("MATCH (d:Drink) RETURN d.name AS name, d.price AS price, d.image AS image ORDER BY name")

    def friendships(self):
        return self.run("MATCH (a:User)-[:FRIEND_WITH]->(b:User) RETURN a.name AS a, b.name AS b ORDER BY a, b")

    def orders(self):
        return self.run("MATCH (u:User)-[:ORDERED]->(d:Drink) RETURN u.name AS user, d.name AS drink ORDER BY user, drink")

    def friends_of(self, name):
        return [r["name"] for r in self.run(
            "MATCH (:User {name:$n})-[:FRIEND_WITH]-(f:User) RETURN DISTINCT f.name AS name ORDER BY name", n=name)]

    def orders_of(self, name):
        return [r["drink"] for r in self.run(
            "MATCH (:User {name:$n})-[:ORDERED]->(d:Drink) RETURN d.name AS drink ORDER BY drink", n=name)]

    def recommend(self, name):
        return self.run("""
            MATCH (u:User {name:$n})-[:FRIEND_WITH]-(f:User)-[:ORDERED]->(d:Drink)
            WHERE NOT (u)-[:ORDERED]->(d)
            RETURN d.name AS name, d.price AS price, d.image AS image,
                   collect(DISTINCT f.name) AS by
            ORDER BY size(collect(DISTINCT f.name)) DESC, name""", n=name)

    def stats(self):
        r = self.run("""
            CALL { MATCH (u:User) RETURN count(u) AS users }
            CALL { MATCH (d:Drink) RETURN count(d) AS drinks }
            CALL { MATCH ()-[r:FRIEND_WITH]->() RETURN count(r) AS friends }
            CALL { MATCH ()-[r:ORDERED]->() RETURN count(r) AS orders }
            RETURN users, drinks, friends, orders""")
        return r[0] if r else dict(users=0, drinks=0, friends=0, orders=0)

    # ---------- เขียนข้อมูล ----------
    def add_user(self, name):
        self.run("CREATE (:User {name:$n})", n=name)

    def add_drink(self, name, price, image):
        self.run("CREATE (:Drink {name:$n, price:$p, image:$i})", n=name, p=price, i=image)

    def add_friend(self, a, b):
        """คืน True ถ้าสร้างใหม่ / False ถ้าเป็นเพื่อนกันอยู่แล้ว"""
        r = self.run("""
            MATCH (a:User {name:$a}), (b:User {name:$b})
            WHERE a <> b AND NOT (a)-[:FRIEND_WITH]-(b)
            CREATE (a)-[:FRIEND_WITH]->(b)
            RETURN count(*) AS n""", a=a, b=b)
        return bool(r and r[0]["n"])

    def remove_friend(self, a, b):
        self.run("MATCH (:User {name:$a})-[r:FRIEND_WITH]-(:User {name:$b}) DELETE r", a=a, b=b)

    def add_order(self, user, drink):
        self.run("""MATCH (u:User {name:$u}), (d:Drink {name:$d})
                    MERGE (u)-[:ORDERED]->(d)""", u=user, d=drink)

    def remove_order(self, user, drink):
        self.run("MATCH (:User {name:$u})-[r:ORDERED]->(:Drink {name:$d}) DELETE r", u=user, d=drink)

    def delete_user(self, name):
        self.run("MATCH (u:User {name:$n}) DETACH DELETE u", n=name)

    def delete_drink(self, name):
        self.run("MATCH (d:Drink {name:$n}) DETACH DELETE d", n=name)