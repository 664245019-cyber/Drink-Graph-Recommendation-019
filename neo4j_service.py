from neo4j import GraphDatabase
import streamlit as st

class Neo4jService:
    def __init__(self):
        # ใส่ค่าเชื่อมต่อ Neo4j Aura ของคุณตรงนี้แบบชัดเจน ตัดปัญหาเรื่อง secrets หลุดไป localhost
        uri = "neo4j+s://4cd28f11.databases.neo4j.io"
        user = "4cd28f11"
        password = "8tAWX2hiF80MjrMPxBVLwPLatJnFIVdYMIDFLHcexBU"
            
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
        except Exception as e:
            self.driver = None
            st.error(f"ไม่สามารถเชื่อมต่อกับฐานข้อมูล Neo4j ได้: {e}")

    def close(self):
        if self.driver:
            self.driver.close()

    def run_query(self, query, parameters=None):
        if not self.driver:
            st.warning("ฐานข้อมูลยังไม่พร้อมใช้งาน")
            return []
        
        if parameters is None:
            parameters = {}
            
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters)
                return [record.data() for record in result]
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการรัน Query: {e}")
            return []