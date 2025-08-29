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



| Product Code | CurveKey | CurveName                                                                         |
| :----------- | :------- | :-------------------------------------------------------------------------------- |
| PDP          | ki6w0    | ICE - PDP - PJM WH RT - Peak Futures                                            |
| ODP          | 7q46g    | ICE - ODP - PJM WH RT Off-Peak - Off-Peak Futures                              |
| NDP          | 4hxbh    | ICE - NDP - NI Hub RT - Peak Futures                                           |
| NDO          | y5z7z    | ICE - NDO - NI Hub RT Off-Peak - Off-Peak Futures                               |
| DDP          | rwr2w    | ICE - DDP - AD Hub RT - Peak Futures                                           |
| ADO          | 43ue2    | ICE - ADO - AD Hub RT Off-Peak - Off-Peak Futures                              |
| CSS          | 2mpsx    | ICE - CSS - Chicago - NG Swing GDD Futures                                        |
| DSS          | h64w8    | ICE - DSS - Eastern Gas-South - NG Swing GDD Futures                             |
| TSS          | 5uz6y    | ICE - TSS - TETCO-M3 - NG Swing GDD Futures                                      |
| HHD          | 0pkv2    | ICE - HHD - Henry - NG Swing GDD Futures                                         |

## ERCOT

| Product Code | CurveKey | CurveName |
| :----------- | :------- | :---------- |
| ERN       | fjkk5    | ICE - ERN - ERCOT North 345KV Hub RT - Peak Futures (1 MW) |
| ER2       |          |             |
| END       | gu57b    | ERCOT North 345KV Real-Time Peak Fixed Price Future - ERN decommissioned |
| END       | ghr8h    |             |
| ERA       | 6bhd4    | ICE - ERA - ERCOT North 345KV Hub RT (16 MWh) - Peak Futures |
| EHD       | 2r06q    | ICE - EHD - ERCOT Houston 345KV Hub RT - Peak Futures |
| NDA       | p4ied    |             |
| NDC       | 20y3d    | ICE - NDC - ERCOT North 345KV Hub DA Off-Peak - Off-Peak Futures |
| NME       | 4koun    | ICE - NME - ERCOT North 345KV Hub RT Off-Peak (5 MWh) - Off-Peak Futures |
| ECI       | 2in24    | ICE - ECI - ERCOT North 345KV Hub RT Off-Peak 7x8 - Off-Peak Futures (1 MW) |
