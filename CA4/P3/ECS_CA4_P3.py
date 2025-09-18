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

def count_tags_loop(tag_str):
    if pd.isna(tag_str):
        return 0
    count = 0
    for tag in tag_str.split("|"):
        if tag.strip() != "":
            count += 1
    return count

tag_counts = []
for i in range(len(df)):
    tag_counts.append(count_tags_loop(df.iloc[i]["tags"]))
df["tag_count"] = tag_counts

publish_dates = []
publish_hours = []
for i in range(len(df)):
    try:
        dt = datetime.strptime(df.iloc[i]["publish_time"], "%Y-%m-%dT%H:%M:%S.%fZ")
        publish_dates.append(dt)
        publish_hours.append(dt.hour)
    except Exception:
        publish_dates.append(pd.NaT)
        publish_hours.append(np.nan)

df["publish_time"] = publish_dates
df["publish_hour"] = publish_hours

for col in TEXTUAL_COLUMNS:
    if col in df.columns:
        del df[col]

engagement_rates = []
ratios = []
for i in range(len(df)):
    row = df.iloc[i]
    views = row["views"]
    likes = row["likes"]
    dislikes = row["dislikes"]
    comments = row["comment_count"]
    engagement_rates.append((likes + dislikes + comments) / (views + 1))
    ratios.append(likes / (dislikes + 1))
df["engagement_rate"] = engagement_rates
df["like_dislike_ratio"] = ratios

unique_cats = sorted(df["category_id"].dropna().unique())
one_hot = []
for i in range(len(df)):
    row = []
    for cat in unique_cats:
        row.append(1 if df.iloc[i]["category_id"] == cat else 0)
    one_hot.append(row)

cat_df = pd.DataFrame(one_hot, columns=[f"cat_{int(c)}" for c in unique_cats])
df = pd.concat([df.reset_index(drop=True), cat_df], axis=1)
df = df.drop(columns=["category_id"])

bool_cols = ["comments_disabled", "ratings_disabled", "video_error_or_removed"]
for col in bool_cols:
    df[col] = [int(val) for val in df[col]]
df = df.drop(columns=bool_cols)

seen_rows = set()
deduped_rows = []
for i in range(len(df)):
    row_tuple = tuple(df.iloc[i].values)
    if row_tuple not in seen_rows:
        seen_rows.add(row_tuple)
        deduped_rows.append(df.iloc[i])
df = pd.DataFrame(deduped_rows).reset_index(drop=True)

numeric_attributes = [
    "views", "publish_hour", "likes", "dislikes", "comment_count",
    "engagement_rate", "like_dislike_ratio", "tag_count"
]
numeric_attributes += [col for col in df.columns if "_emb_" in col]

for col in numeric_attributes:
    transformed = []
    for i in range(len(df)):
        transformed.append(np.log1p(df.iloc[i][col]))
    df[col] = transformed

minmax_scaler = MinMaxScaler()
scaled_minmax = minmax_scaler.fit_transform(df[numeric_attributes])
for j, col in enumerate(numeric_attributes):
    for i in range(len(df)):
        df.at[i, col] = scaled_minmax[i][j]

standard_scaler = StandardScaler()
scaled_standard = standard_scaler.fit_transform(df[numeric_attributes])
for j, col in enumerate(numeric_attributes):
    for i in range(len(df)):
        df.at[i, col] = scaled_standard[i][j]

df = df.drop(columns=["likes", "dislikes"])

print("Preprocessing complete. Final shape:", df.shape)

