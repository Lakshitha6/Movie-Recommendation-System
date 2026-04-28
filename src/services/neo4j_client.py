from langchain_neo4j import Neo4jGraph
import os
from dotenv import load_dotenv

load_dotenv()

_neo4j_instance = None

def neo4j_client()-> Neo4jGraph:
    global _neo4j_instance

    if _neo4j_instance is None:
        Neo_URI = os.getenv('NEO4J_URI')
        Neo_User = os.getenv('NEO4J_USERNAME')
        Neo_pwd = os.getenv('NEO4J_PASSWORD')
        Neo_db = os.getenv('NEO4J_DB')

        if not Neo_URI or not Neo_User or not Neo_pwd or not Neo_db:
            raise ValueError("Set Neo URI, Username , Password and db name in .env")

        _neo4j_instance = Neo4jGraph(
                url=Neo_URI,
                username=Neo_User,
                password=Neo_pwd,
                database=Neo_db
        )

    return _neo4j_instance