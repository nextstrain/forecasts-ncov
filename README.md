# Nextstrain Counts

Internal tooling for the Nextstrain team to curate and standardize various counts data such as COVID-19 case counts and SARS-CoV-2 clade sequence counts.

## Data Sources

- Global COVID-19 case counts: [Our World in Data](https://covid.ourworldindata.org/data/owid-covid-data.csv), originally from [JHU CSSE COVID-19 Data](https://github.com/CSSEGISandData/COVID-19)
- USA state COVID-19 case counts: [United States COVID-19 Cases and Deaths by State over Time](https://data.cdc.gov/Case-Surveillance/United-States-COVID-19-Cases-and-Deaths-by-State-o/9mfq-cb36)
- SARS-CoV-2 sequences: Nextstrain-curated metadata TSVs for GISAID and GenBank produced by [nextstrain/ncov-ingest](https://github.com/nextstrain/ncov-ingest)
## Running locally

1. Create a conda environment named `nextstrain-counts`
```
mamba create -n nextstrain-counts -c bioconda "csvtk>=0.23.0" "pandas>=1.0.0" --yes
```
2. Activate the conda environment
```
conda activate nextstrain-counts
```
