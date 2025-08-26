# Data

*The Dremio source for the following tables is "Core.Preparation.MIX.RAW.ICEIPE.""ICE_FUTURES_SPECIAL"""*
The full table schema is as follows:

| Column Name            | Data Type           | Is Nullable | Numeric Precision |
| :--------------------- | :------------------ | :---------- | :---------------- |
| CurveKey               | CHARACTER VARYING   | YES         |                   |
| TradingDate            | TIMESTAMP           | YES         |                   |
| DeliveryDate           | TIMESTAMP           | YES         |                   |
| ChangedOn              | TIMESTAMP           | YES         |                   |
| RelativeDeliveryPeriod | DOUBLE              | YES         | 53                |
| TradingDateUtc         | TIMESTAMP           | YES         |                   |
| DeliveryDateUtc        | TIMESTAMP           | YES         |                   |
| LiDChangedOn           | TIMESTAMP           | YES         |                   |
| CurveName              | CHARACTER VARYING   | YES         |                   |
| OpenInterest           | DOUBLE              | YES         | 53                |
| OpenInterestTerms      | DOUBLE              | YES         | 53                |
| PriceChange            | DOUBLE              | YES         | 53                |
| PublicationDate        | TIMESTAMP           | YES         |                   |
| PublicationDateUtc     | TIMESTAMP           | YES         |                   |
| Settlement             | DOUBLE              | YES         | 53                |
| SpreadVolume           | DOUBLE              | YES         | 53                |
| TotalVolume            | DOUBLE              | YES         | 53                |
| Trades                 | DOUBLE              | YES         | 53                |
| Volume                 | DOUBLE              | YES         | 53                |
| WeightedAverage        | DOUBLE              | YES         | 53                |
| Closing                | DOUBLE              | YES         | 53                |
| BlockVolume            | DOUBLE              | YES         | 53                |
| DeliveryDate2          | TIMESTAMP           | YES         |                   |
| EfpVolume              | DOUBLE              | YES         | 53                |
| Low                    | DOUBLE              | YES         | 53                |
| EfsVolume              | DOUBLE              | YES         | 53                |
| High                   | DOUBLE              | YES         | 53                |
| Opening                | DOUBLE              | YES         | 53                |

# Power

## PJM

PJM Power is traded at a few key nodes. These include:
- WH (West Hub)
- AD (AEP Dayton Hub)
- NI Hub (Northern Illinois Hub)


| Product Code | CurveKey | Description |
| :----------- | :------- | :---------- |
| PDP          | ki6w0    |             |
| ODP          | 7q46g    |             |
| NDP          | 4hxbh    |             |
| NDO          | y5z7z    |             |
| DDP          | rwr2w    |             |
| ADO          | 43ue2    |             |
| CSS          | 2mpsx    |             |
| DSS          | h64w8    |             |
| TSS          | 5uz6y    |             |
| HHD          | 0pkv2    |             |

## ERCOT

| Product Code | CurveKey | Description |
| :----------- | :------- | :---------- |
| AAA          | aaaaa    |             |
| BBB          | bbbbb    |             |
| CCC          | cccccc    |             |
| DDD          | dddddd    |             |
| EEE          | eeeeee    |             |
| FFF          | ffffff    |             |
| GGG          | gggggg    |             |
| HHH          | hhhhhh    |             |
