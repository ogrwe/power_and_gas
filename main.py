from dremio import query_dremio

def main():
    df = query_dremio("SELECT * FROM \"Core\".\"Preparation\".\"S3\".\"Team_CAO_US\".\"LT\".\"Environmental_Products\".\"processed_environmental_products\" LIMIT 100")
    print(df.to_markdown(100))


if __name__ == "__main__":
    main()
