Collapse lineages with a threshold of 12. The BQ.1.1 lineage would not meet
this threshold if the deeper lineage BQ.1.1.1 was not already collapsed into it.
This should only collapse BQ.1.1.1 into BQ.1.1 since we collapse from the
deepest lineages first.

  $ python3 "$TESTDIR/../../../scripts/collapse-lineage-counts.py" \
  > --seq-counts "$TESTDIR/../data/prepared_seq_counts.tsv" \
  > --collapse-threshold 12 \
  > --output-seq-counts "$TESTDIR/collapsed_seq_counts.tsv" > /dev/null

Verify the output seq counts

  $ cat "$TESTDIR/collapsed_seq_counts.tsv"
  location\tvariant\tdate\tsequences (esc)
  USA\tBQ.1\t2022-11-27\t10 (esc)
  USA\tBQ.1\t2022-11-28\t10 (esc)
  USA\tBQ.1.1\t2022-11-27\t6 (esc)
  USA\tBQ.1.1\t2022-11-28\t7 (esc)

Clean up after test.

  $ rm "$TESTDIR/collapsed_seq_counts.tsv"
