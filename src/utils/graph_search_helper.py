from src.services import get_embeddings, neo4j_client

graph = neo4j_client()
embeddings = get_embeddings()

def vector_search(query: str, k=10):

    emb = embeddings.embed_query(query)

    result = graph.query("""
        CALL db.index.vector.queryNodes('movie_embeddings', $k, $embedding)
        YIELD node, score
        OPTIONAL MATCH (node)-[:HAS_GENRE]->(g:Genre)
        OPTIONAL MATCH (d:Director)-[:DIRECTED]->(node)
        RETURN node.title     AS title,
               node.description AS description,
               node.year      AS year,
               node.rating    AS rating,
               score,
               collect(DISTINCT g.name) AS genres,
               d.name         AS director
    """, {"embedding": emb, "k": k})

    return result


# Knowledge Graph - Structured Retriever

def kg_search(actor=None, genre=None, director=None, limit=10):
    """Return full movie details from structured graph filters."""
    query = "MATCH (m:Movie) WHERE 1=1 "
    params = {}

    if actor:
        query += "AND EXISTS { MATCH (:Actor {name:$actor})-[:ACTED_IN]->(m) } "
        params["actor"] = actor

    if director:
        query += "AND EXISTS { MATCH (:Director {name:$director})-[:DIRECTED]->(m) } "
        params["director"] = director

    if genre:
        query += "AND EXISTS { MATCH (m)-[:HAS_GENRE]->(:Genre {name:$genre}) } "
        params["genre"] = genre

    # Return full details
    query += """
        OPTIONAL MATCH (m)-[:HAS_GENRE]->(g:Genre)
        OPTIONAL MATCH (d:Director)-[:DIRECTED]->(m)
        RETURN m.title AS title,
               m.description AS description,
               m.year AS year,
               m.rating AS rating,
               collect(DISTINCT g.name) AS genres,
               d.name AS director
        LIMIT $limit
    """
    params["limit"] = limit

    return graph.query(query, params)


def format_movie(r: dict) -> str:
    """Convert a result row into a readable movie card."""
    genres = ", ".join(r.get("genres") or [])
    parts = [
        f"Title: {r.get('title', 'N/A')}",
        f"Year: {r.get('year', 'N/A')} | Rating: {r.get('rating', 'N/A')}",
        f"Director: {r.get('director', 'N/A')}",
        f"Genres: {genres or 'N/A'}",
        f"Description: {(r.get('description') or 'N/A')[:300]}",
    ]
    return "\n".join(parts)