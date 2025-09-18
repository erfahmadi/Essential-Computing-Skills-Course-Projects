import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sentence_transformers import SentenceTransformer
import os

TEXTUAL_COLUMNS = ["title", "tags", "description"]
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384
OUTPUT_DIR = "tmp/embeddings/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

us_df = pd.read_csv("USvideos.csv")
us_df["country"] = "US"
ca_df = pd.read_csv("CAvideos.csv")
ca_df["country"] = "CA"

df = pd.concat([us_df, ca_df], ignore_index=True).sample(1000, random_state=42).reset_index(drop=True)

print(f"[EMBEDDING][INFO]: Loading model {EMBEDDING_MODEL}...")
model = SentenceTransformer(EMBEDDING_MODEL)

def clean_tags(text):
    return " ".join(tag.replace('"', '') for tag in str(text).split('|'))

for col in TEXTUAL_COLUMNS:
    print(f"[EMBEDDING][INFO]: Embedding column '{col}'...")
    if col == "tags":
        text_data = df[col].fillna("").apply(clean_tags).tolist()
    else:
        text_data = df[col].fillna("").astype(str).tolist()
    
    emb = model.encode(text_data, show_progress_bar=True, batch_size=32)
    emb_df = pd.DataFrame(emb, columns=[f"{col}_emb_{i}" for i in range(emb.shape[1])])
    df = pd.concat([df.reset_index(drop=True), emb_df], axis=1)

df["tag_count"] = df["tags"].fillna("").apply(lambda x: len([t for t in str(x).split("|") if t.strip()]))

df["publish_time"] = pd.to_datetime(df["publish_time"], errors="coerce", utc=True)
df["publish_hour"] = df["publish_time"].dt.hour

df.drop(columns=[col for col in TEXTUAL_COLUMNS if col in df.columns], inplace=True)

df["engagement_rate"] = (df["likes"] + df["dislikes"] + df["comment_count"]) / (df["views"] + 1)
df["like_dislike_ratio"] = df["likes"] / (df["dislikes"] + 1)

cat_df = pd.get_dummies(df["category_id"], prefix="cat")
df = pd.concat([df, cat_df], axis=1)
df.drop(columns=["category_id"], inplace=True)

bool_cols = ["comments_disabled", "ratings_disabled", "video_error_or_removed"]
df[bool_cols] = df[bool_cols].astype(int)
df.drop(columns=bool_cols, inplace=True)

df = df.drop_duplicates().reset_index(drop=True)

numeric_attributes = [
    "views", "publish_hour", "likes", "dislikes", "comment_count",
    "engagement_rate", "like_dislike_ratio", "tag_count"
] + [col for col in df.columns if "_emb_" in col]

df[numeric_attributes] = df[numeric_attributes].apply(lambda col: np.log1p(col))

minmax_scaler = MinMaxScaler()
df[numeric_attributes] = minmax_scaler.fit_transform(df[numeric_attributes])

standard_scaler = StandardScaler()
df[numeric_attributes] = standard_scaler.fit_transform(df[numeric_attributes])

df.drop(columns=["likes", "dislikes"], inplace=True)

print("Preprocessing complete. Final shape:", df.shape)
