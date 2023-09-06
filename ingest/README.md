# Nextstrain Counts

Internal tooling for the Nextstrain team to curate and standardize various counts data such as COVID-19 case counts and SARS-CoV-2 clade sequence counts.

## Data Sources

- Global COVID-19 case counts: [Our World in Data](https://covid.ourworldindata.org/data/owid-covid-data.csv), originally from [JHU CSSE COVID-19 Data](https://github.com/CSSEGISandData/COVID-19)
- USA state COVID-19 case counts: [United States COVID-19 Cases and Deaths by State over Time](https://data.cdc.gov/Case-Surveillance/United-States-COVID-19-Cases-and-Deaths-by-State-o/9mfq-cb36)
- SARS-CoV-2 sequences: Nextstrain-curated metadata TSVs for GISAID and GenBank produced by [nextstrain/ncov-ingest](https://github.com/nextstrain/ncov-ingest)

## Outputs

> :warning: **WARNING: This is an alpha release.** Output file format and address may change at any time

This repository produces multiple TSVs that are routinely uploaded to a public AWS S3 bucket: `s3://nextstrain-data/files/workflows/forecasts-ncov`.

The case counts are stored at `s3://nextstrain-data/files/workflows/forecasts-ncov/cases/`.
The GISAID outputs are stored at `s3://nextstrain-data/files/workflows/forecasts-ncov/gisaid/`.
The open (GenBank) outputs are stored at `s3://nextstrain-data/files/workflows/forecasts-ncov/open/`.

Within each data provenance, the files are split by clade type and geographic resolution.
Within TSVs at the global resolution, the `location` column contains countries.
Within TSVs at the country resolution, the `location` column contains divisions (e.g. states for US).

### Summary of Available files

#### Case Counts
| Geographic Resolution | Address                                                                        |
| --------------------- | ------------------------------------------------------------------------------ |
| Global                | https://data.nextstrain.org/files/workflows/forecasts-ncov/cases/global.tsv.gz |
| USA                   | https://data.nextstrain.org/files/workflows/forecasts-ncov/cases/usa.tsv.gz    |

#### Sequence Counts
| Data Provenance | Clade Type        | Geographic Resolution | Address                                                                                           |
| --------------- | ----------------- | --------------------- | ------------------------------------------------------------------------------------------------- |
| GISAID          | Nextstrain clades | Global                | https://data.nextstrain.org/files/workflows/forecasts-ncov/gisaid/nextstrain_clades/global.tsv.gz |
|                 |                   | USA                   | https://data.nextstrain.org/files/workflows/forecasts-ncov/gisaid/nextstrain_clades/usa.tsv.gz    |
|                 | Pango lineages    | Global                | https://data.nextstrain.org/files/workflows/forecasts-ncov/gisaid/pango_lineages/global.tsv.gz |
|                 |                   | USA                   | https://data.nextstrain.org/files/workflows/forecasts-ncov/gisaid/pango_lineages/usa.tsv.gz    |
| open (GenBank)  | Nextstrain clades | Global                | https://data.nextstrain.org/files/workflows/forecasts-ncov/open/nextstrain_clades/global.tsv.gz   |
|                 |                   | USA                   | https://data.nextstrain.org/files/workflows/forecasts-ncov/open/nextstrain_clades/usa.tsv.gz      |
|                 | Pango lineages    | Global                | https://data.nextstrain.org/files/workflows/forecasts-ncov/open/pango_lineages/global.tsv.gz |
|                 |                   | USA                   | https://data.nextstrain.org/files/workflows/forecasts-ncov/open/pango_lineages/usa.tsv.gz    |

## Running locally

> **Note**
> All command examples in this section assume you are within the ingest directory.
> If running commands from the outer forecasts-ncov directory, please replace the `.` with `ingest`

Please follow [installation instructions](https://docs.nextstrain.org/en/latest/install.html#installation-steps) for Nextstrain's software tools.

[config/defaults.yaml](config/defaults.yaml) contains all of the default configuration parameters used for the ingest workflow.
Use Snakemake's `--configfile`/`--config` options to override these default values.


### Sequence Counts

Running the workflow for sequence counts requires AWS credentials to download the metadata from AWS S3:
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY

To summarize the sequence counts locally run:

```
nextstrain build . all_sequence_counts
```

If you only want to run the sequence counts for a single data provenance (e.g. GISAID) run:

```
nextstrain build . all_sequence_counts --config data_provenances="[gisaid]"
```
