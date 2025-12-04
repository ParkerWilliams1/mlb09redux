import os
import shutil
import pandas as pd

CELEBA_ROOT = "../../../../Courses/MachineLearning/final-project/celeba/img_align_celeba/img_align_celeba"
ATTR_FILE   = "../../../../Courses/MachineLearning/final-project/celeba/list_attr_celeba.csv"
OUTPUT_DIR  = "dataset/beard"

CATEGORIES  = ["full", "goatee", "mustache", "none", "stubble"]
#CATEGORIES  = ["full"]
MAX_PER_CAT = 1000

# Output folders
for c in CATEGORIES:
    os.makedirs(os.path.join(OUTPUT_DIR, c), exist_ok=True)

print("[INFO] Loading CSV attribute file...")

# Force correct parsing & cleanup
df = pd.read_csv(
    ATTR_FILE,
    sep=",",
    skipinitialspace=True,
    index_col=False
)

# Force rename the first column to image_id
df.rename(columns={df.columns[0]: "image_id"}, inplace=True)
df["image_id"] = df["image_id"].astype(str).str.strip()
df.set_index("image_id", inplace=True)
df.replace(-1, 0, inplace=True)

print(f"[INFO] Successfully loaded {len(df):,} images")

# Debug: show columns
print("\n[INFO] Columns detected:")
print(df.columns.tolist())

def categorize(row):
    if (
        row["No_Beard"] == 0 and
        (row["5_o_Clock_Shadow"] == 0) and
        (row["Mustache"] == 1 and row["Goatee"] == 1) and
        (row["Sideburns"] == 1)
    ):
        return "full"

    # Mustache only
    if row["Mustache"] == 1 and row["Goatee"] == 0:
        return "mustache"

    # Goatee only
    if row["Goatee"] == 1 and row["Mustache"] == 0:
        return "goatee"

    # Light / stubble
    if row["5_o_Clock_Shadow"] == 1 and row["No_Beard"] == 0:
        return "stubble"

    # Clean shaven
    if row["No_Beard"] == 1:
        return "none"

    return "none"

print(f"\n[INFO] Copying up to {MAX_PER_CAT} images per category...")

count = {c: 0 for c in CATEGORIES}
debug_prints = 0

for img_name, row in df.iterrows():
    # Stop once all folders are full
    if all(count[c] >= MAX_PER_CAT for c in CATEGORIES):
        break

    if row["Male"] == 0:
        continue

    src_path = os.path.join(CELEBA_ROOT, img_name)

    if not os.path.exists(src_path):
        continue

    cat = categorize(row)

    if debug_prints < 15:
        print(
            f"[DEBUG] {img_name} → {cat} | "
            f"G:{row['Goatee']} M:{row['Mustache']} "
            f"NB:{row['No_Beard']} S:{row['Sideburns']} "
            f"5S:{row['5_o_Clock_Shadow']}"
        )
        debug_prints += 1

    if count[cat] < MAX_PER_CAT:
        dst_path = os.path.join(OUTPUT_DIR, cat, img_name)
        shutil.copy(src_path, dst_path)
        count[cat] += 1

        if count[cat] == MAX_PER_CAT:
            print(f"   [DONE] {cat}: {count[cat]} images")

print("\n" + "=" * 50)
print("SUCCESS! Here are your final counts:")

for c in CATEGORIES:
    print(f"  {c:>9}: {count[c]:,} images")

print(f"\nTotal images copied: {sum(count.values()):,}")
print("=" * 50)

