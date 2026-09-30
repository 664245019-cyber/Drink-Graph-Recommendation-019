import os
from neo4j import GraphDatabase
import streamlit as st

class Neo4jService:
    def __init__(self):
        try:
            # พยายามดึงค่าจาก st.secrets ของ Streamlit Cloud
            uri = st.secrets["NEO4J_URI"]
            user = st.secrets["NEO4J_USER"]
            password = st.secrets["NEO4J_PASSWORD"]
        except Exception:
            # ค่าสำรองหากรันในเครื่องหรือยังไม่ได้ตั้งค่า secrets
            uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
            user = os.getenv("NEO4J_USER", "neo4j")
            password = os.getenv("NEO4J_PASSWORD", "password")
            
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
            st.warning("ฐานข้อมูลยังไม่พร้อมใช้งาน กรุณาตรวจสอบการตั้งค่า Secrets บน Streamlit Cloud")
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
