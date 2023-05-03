Collapse lineages with a threshold of 20.
This should collapse everything to BQ.1 since the other lineages do not meet the threshold

  $ python3 "$TESTDIR/../../../scripts/collapse-lineage-counts.py" \
  > --seq-counts "$TESTDIR/../data/prepared_seq_counts.tsv" \
  > --collapse-threshold 20 \
  > --output-seq-counts "$TESTDIR/collapsed_seq_counts.tsv" > /dev/null

Verify the output seq counts

  $ cat "$TESTDIR/collapsed_seq_counts.tsv"
  location\tvariant\tdate\tsequences (esc)
  USA\tBQ.1\t2022-11-27\t16 (esc)
  USA\tBQ.1\t2022-11-28\t17 (esc)

Clean up after test.

  $ rm "$TESTDIR/collapsed_seq_counts.tsv"
