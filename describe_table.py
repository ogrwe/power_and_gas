from dremio.dremio_client import query_dremio

table_to_describe = "\"Core\".\"Preparation\".\"MIX\".\"RAW\".\"ICEIPE\".\"ICE_FUTURES_SPECIAL\""


def main():
    data = query_dremio(f'DESCRIBE {table_to_describe}')
    print(data)


if __name__ == "__main__":
    main()