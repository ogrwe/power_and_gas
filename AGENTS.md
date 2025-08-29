# AGENTS.md

## General
Always run with uv. 

## Analysis

You are an expert power and gas analyst. When writing analyst scripts, you must be extremely thorough and statistically competent. 

### Common Market Terms

The user may frequently use abbreviations. You are expected to understand these and respond with the same abbreviations. The following are very common abbreviations used in the power markets:

- DA = Day Ahead
- HH = Hourly
- RT = Real Time
- HE = Hour Ending (e.g. HE 21 refers to the hour of 20:00 to 21:00)
- Peaks = the 16 hour block from HE 7 to HE 22.
- Off Peaks/Nights = the 8 hour block from HE 0 to HE 6 and from HE 23 to HE 24
- MW = Megawatts
- MWh = Megawatt-hours
- GW = Gigawatts
- GWh = Gigawatt-hours
- Phys = Physical (e.g. physical power or gas)
- Fin = Financial (e.g. financial power or gas)
- ICE = Intercontinental Exchange (a trading platform)
- NDL = Nodal (a trading platform)


### Hour Blocks

The following are common hour blocks used in the power markets. The first integer is the 'days' and the second is the 'hours'.

- 7x16 = All days of the week (7), 16 hours a day (the peak hours)
- 7x8 = All days of the week (7), 8 hours a day (the off-peak hours)
- 5x16 = Monday to Friday, 16 hours a day (the peak hours)
- 5x8 = Monday to Friday, 8 hours a day (the off-peak hours)
- 2x16 = Saturday and Sunday, 16 hours a day (the peak hours)
- 2x8 = Saturday and Sunday, 8 hours a day (the off-peak hours)

## Data

### Dremio Querying Guidelines

#### IMPORTANT: Required Import

**The `query_dremio` function from the `dremio` module is the ONLY acceptable way to query Dremio data.** This function must be imported at the top of any script that queries Dremio:

```python
from dremio import query_dremio
```

#### SQL Query Conventions (MANDATORY)

When constructing SQL queries for Dremio, you **MUST** follow these guidelines to prevent errors caused by reserved keywords and ensure compatibility:

1. **Always quote all column names** with double quotes (`"`), regardless of whether they might be keywords. This ensures Dremio interprets them as identifiers.
2. **Use consistent quoting** for all table path segments in the `FROM` clause.
3. **Keep SQL functions lowercase** for better compatibility with Dremio's parser (e.g., `extract(month from "DATETIME")`).
4. **Quote all column references** in `WHERE` clauses and other expressions.
5. **Always wrap queries with """** to ensure they are properly formatted and passed to the `query_dremio` function.

#### Example Query

```sql
SELECT 
    "DATETIME", 
    "VALUE", 
    "TIMEZONE", 
    "event_date", 
    "event_date_year"
FROM 
    "Core"."Preparation"."S3"."Team_Source_Yesenergy"."ERCOT"."Gen"."ERCOTwindgenRT"
WHERE 
    extract(month from "DATETIME") = 8
    AND (extract(year from "DATETIME") = 2023 
         OR extract(year from "DATETIME") = 2024)
ORDER BY 
    "DATETIME"
```

#### Best Practices

- Format complex queries with proper indentation and line breaks
- Include comments for complex logic or business rules

#### Common Pitfalls to Avoid

- Mixing quoted and unquoted identifiers
- Using uppercase SQL keywords (use lowercase for better compatibility)
- Forgetting to quote column names that match SQL keywords
- Inconsistent quoting in JOIN conditions
- Not handling NULL values appropriately in WHERE clauses

## Analysis

### Data Analysis Package

**scikit-learn** (sklearn) is the preferred package for data analysis tasks. It has been added to the project dependencies and should be used for:

- Machine learning models and algorithms
- Data preprocessing and feature engineering
- Statistical analysis and data exploration
- Model evaluation and validation

The package is available as `scikit-learn` in the project dependencies and can be imported as:

```python
import sklearn
```

**matplotlib** is the preferred package for data visualization tasks. Use of seaborn is acceptable to enhance visuals.These modules should be imported as:

```python
import matplotlib.pyplot as plt
import seaborn as sns
```

### Analysis Guidelines
**Visualization Output:** If a data visualisation is requested, all data visualizations should be by default displayed using `plt.show()`. When generating multiple visualizations, ensure the script is structured to display them simultaneously (e.g., using `plt.figure()` for distinct figures). Clearly distinguish and label each chart within the code using comment breakers like:

```python
# ============== CHART 1: [Descriptive Title] ==============
# Brief description of the data manipulation and purpose of the chart.
```

For any time-series line charts, ensure the DataFrame is properly sorted by the time axis before plotting.

**Saving Visualizations:**

*   Unless explicitly requested by the user, visualizations should only be displayed using `plt.show()` and not saved to disk.

*   If the user requests to save the images, create a subfolder named `output_[script_name]` in the same directory as the script (replace `[script_name]` with the actual script's file name without the extension). For example, if the script is named `my_analysis.py`, the folder should be `output_my_analysis`.

*   If the user requests to save the images and specifies a `.png` format, save each figure as a separate `.png` file within the `output_[script_name]` folder. Overwrite any existing files with the same name if the script is re-run. Name the .png files descriptively (e.g., 'timeseries_value1.png', 'scatter_value1_value2.png').

*   If the user requests to save the images and specifies a `.pdf` format, save all visualizations into a single PDF file within the `output_[script_name]` folder. Ensure that each visualization appears on a separate page within the PDF.

**Code Clarity:** Add concise, descriptive comments throughout the generated Python script to explain the logical steps involved in data processing, analysis, and visualization. Aim for clarity and conciseness, focusing on *why* each step is performed rather than *how* (the code itself shows how).

**Code Modularity:** Code must be made modular such that it is straightfowrad to change the process of individual functions in the case that edits to the analysis process steps need to be made. Always attempt to achieve a good blend of code modularity and tackling the specific task at hand. Key input variables (such as date ranges) must be made easily editable towards the top of the script as variables that are consistently used throughout the rest of the analysis.