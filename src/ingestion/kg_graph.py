""" 

Prerequisites:

    * Make sure run 'data_downloader.py' before run this file and movie data csv file exists in the data directory . 
    * Create account at ' neo4j.com ' and create new instance and Save credintials 
        NEO4J_PASSWORD=jeD_....
        NEO4J_URI=neo4j+s://....
        NEO4J_USERNAME=...
        NEO4J_DB=....


Then Run this file using ' python src/ingestion/data_downloader.py ' to build knowledge graph in Neo4J Aura DB.


"""


from src.services import neo4j_client, get_embeddings
from src.utils import get_config

import pandas as pd

config = get_config()
embeddings = get_embeddings()
graph = neo4j_client()

df = pd.read_csv(config.data_path/ 'movies.csv')

for _, row in df.iterrows():

    #  Generate embedding for description
    description = row["description"] if pd.notna(row["description"]) else ""
    embedding = embeddings.embed_query(description)

    #  Create Movie node WITH embedding
    graph.query("""
        MERGE (m:Movie {title: $title})
        SET m.year = $year,
            m.rating = $rating,
            m.description = $description,
            m.embedding = $embedding
    """, {
        "title": row["title"],
        "year": row["year"],
        "rating": row["rating"],
        "description": description,
        "embedding": embedding
    })

    #  Create Actor relationships
    if pd.notna(row["actors"]):
        actors = row["actors"].split(",")

        for actor in actors:
            graph.query("""
                MERGE (a:Actor {name: $actor})
                MERGE (m:Movie {title: $title})
                MERGE (a)-[:ACTED_IN]->(m)
            """, {
                "actor": actor.strip(),
                "title": row["title"]
            })

    #  Director relationship
    if pd.notna(row["director"]):
        graph.query("""
            MERGE (d:Director {name: $director})
            MERGE (m:Movie {title: $title})
            MERGE (d)-[:DIRECTED]->(m)
        """, {
            "director": row["director"],
            "title": row["title"]
        })

    #  Genre relationships
    if pd.notna(row["genres"]):
        genres = row["genres"].split(",")

        for genre in genres:
            graph.query("""
                MERGE (g:Genre {name: $genre})
                MERGE (m:Movie {title: $title})
                MERGE (m)-[:HAS_GENRE]->(g)
            """, {
                "genre": genre.strip(),
                "title": row["title"]
            })