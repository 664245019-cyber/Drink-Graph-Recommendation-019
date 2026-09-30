import os
from neo4j import GraphDatabase
import streamlit as st

class Neo4jService:
    def __init__(self):
        # ดึงค่าจาก st.secrets หรือ Environment Variables
        try:
            uri = st.secrets["NEO4J_URI"]
            user = st.secrets["NEO4J_USER"]
            password = st.secrets["NEO4J_PASSWORD"]
        except Exception:
            uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
            user = os.getenv("NEO4J_USER", "neo4j")
            password = os.getenv("NEO4J_PASSWORD", "password")
            
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        if self.driver:
            self.driver.close()

    def run_query(self, query, parameters=None):
        if parameters is None:
            parameters = {}
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]