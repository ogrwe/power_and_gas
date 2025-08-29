from dremio import query_dremio

query = """
SELECT *
FROM "Core"."Preparation"."S3"."Team_CAO_US"."LT"."Environmental_Products"."processed_environmental_products"
LIMIT 100
"""

df = query_dremio(query)
print(df.head())