from dremio import query_dremio

def main():
    query = """
    SELECT *
    FROM "Core"."Preparation"."S3"."Team_CAO_US"."LT"."Environmental_Products"."processed_environmental_products"
    LIMIT 100
    """

    df = query_dremio(query)
    print(df.head())


if __name__ == "__main__":
    main()
