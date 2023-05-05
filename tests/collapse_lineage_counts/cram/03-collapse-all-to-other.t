Collapse lineages with a threshold of 100.
This should collapse everything to "other" since none of the lineages meet the threshold.

  $ python3 "$TESTDIR/../../../scripts/collapse-lineage-counts.py" \
  > --seq-counts "$TESTDIR/../data/prepared_seq_counts.tsv" \
  > --collapse-threshold 100 \
  > --output-seq-counts "$TESTDIR/collapsed_seq_counts.tsv" > /dev/null

Verify the output seq counts

  $ cat "$TESTDIR/collapsed_seq_counts.tsv"
  location\tvariant\tdate\tsequences (esc)
  USA\tother\t2022-11-27\t16 (esc)
  USA\tother\t2022-11-28\t17 (esc)

Clean up after test.

  $ rm "$TESTDIR/collapsed_seq_counts.tsv"
