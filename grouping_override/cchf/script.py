import pandas as pd
import json

# Step 1: Download the dataset
url = "https://lapis.pathoplexus.org/cchf/sample/details?downloadAsFile=true&downloadFileBasename=cchf_metadata_2025-04-03T2223&dataFormat=tsv&fields=accessionVersion%2CdataUseTerms%2CdataUseTermsUrl%2CearliestReleaseDate%2CgeoLocAdmin1%2CgeoLocAdmin2%2CgeoLocCity%2CgeoLocCountry%2ChostNameScientific%2Clength_L%2Clength_M%2Clength_S%2CsampleCollectionDate%2CinsdcAccessionFull_L%2CinsdcAccessionFull_S%2CinsdcAccessionFull_M%2CspecimenCollectorSampleId%2Cauthors%2CauthorAffiliations&versionStatus=LATEST_VERSION&isRevocation=false"

df = pd.read_csv(url, sep="\t")

# Step 2: Mark presence of each segment
df["has_L"] = df["length_L"].apply(lambda x: x > 0)
df["has_M"] = df["length_M"].apply(lambda x: x > 0)
df["has_S"] = df["length_S"].apply(lambda x: x > 0)

# Step 3: Group and aggregate values
grouped = df.groupby("specimenCollectorSampleId").agg({
    "length_L": "max",
    "length_M": "max",
    "length_S": "max",
    "accessionVersion": lambda x: list(x),
    "insdcAccessionFull_L": lambda x: ", ".join(x.dropna().astype(str)),
    "insdcAccessionFull_M": lambda x: ", ".join(x.dropna().astype(str)),
    "insdcAccessionFull_S": lambda x: ", ".join(x.dropna().astype(str)),
    "sampleCollectionDate": lambda x: ", ".join(x.dropna().astype(str)),
    "geoLocCountry": lambda x: ", ".join(x.dropna().astype(str)),
    "hostNameScientific": lambda x: ", ".join(x.dropna().astype(str)),
    "authors": lambda x: list(x),
    "earliestReleaseDate": lambda x: ", ".join(x.dropna().astype(str)),
    "has_L": "sum",
    "has_M": "sum",
    "has_S": "sum"
}).reset_index()

# Step 4: Filter groups
filtered = grouped[
    (grouped["accessionVersion"].apply(lambda x: len(x) > 1)) &
    (grouped["has_L"] <= 1) &
    (grouped["has_M"] <= 1) &
    (grouped["has_S"] <= 1)
]

# Step 5: Build JSON dictionary
def extract_insdc_list(row):
    all_ids = []
    for col in ["insdcAccessionFull_L", "insdcAccessionFull_M", "insdcAccessionFull_S"]:
        if pd.notnull(row[col]):
            all_ids.extend([x.strip() for x in row[col].split(",") if x.strip()])
    return all_ids

json_dict = {}
for _, row in filtered.iterrows():
    insdc_ids = extract_insdc_list(row)
    unique_ids = list(dict.fromkeys(insdc_ids))  # preserve order
    key = "_".join(unique_ids)
    json_dict[key] = insdc_ids

# Step 6: Save results
filtered.to_csv("filtered_grouped_table.tsv", sep="\t", index=False)
with open("insdc_accession_groups.json", "w") as f:
    json.dump(json_dict, f, indent=2)

print("Done! Files saved:")
print("- filtered_grouped_table.tsv")
print("- insdc_accession_groups.json")
