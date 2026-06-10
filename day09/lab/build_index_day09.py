import chromadb, os
from sentence_transformers import SentenceTransformer

client = chromadb.PersistentClient(path='./chroma_db')
col = client.get_or_create_collection('day09_docs')
model = SentenceTransformer('all-MiniLM-L6-v2')

docs_dir = './data/docs'
for fname in os.listdir(docs_dir):
    with open(os.path.join(docs_dir, fname), encoding="utf-8") as f:
        content = f.read()
        
    chunks = content.split("\n\n")
    for i, chunk in enumerate(chunks):
        if not chunk.strip(): continue
        chunk_id = f"{fname}_{i}"
        embedding = model.encode([chunk])[0].tolist()
        col.upsert(
            ids=[chunk_id],
            embeddings=[embedding],
            documents=[chunk],
            metadatas=[{"source": fname}]
        )
    print(f'Indexed: {fname}')
print('Index ready.')
