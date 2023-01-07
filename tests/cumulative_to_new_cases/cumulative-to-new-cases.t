Setup

  $ pushd "$TESTDIR" > /dev/null

Convert cumulative cases to daily new cases, where locations/days with 0 or
negative case counts are excluded.

  $ ../../ingest/bin/cumulative-to-new-cases \
  > --cumulative-cases us_cumulative_cases.csv > "$TMP"/new_cases.tsv

Verify output TSV matches expected output TSV.

  $ diff "$TMP"/new_cases.tsv us_expected_new_cases.tsv

