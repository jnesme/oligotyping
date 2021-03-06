# -*- coding: utf-8 -*-

import sys

import Oligotyping.lib.fastalib as u

# eh..
fasta = u.SequenceSource(sys.argv[1], lazy_init = False)
fasta.next()

len_fasta_entry = len(fasta.seq)
fasta.reset()

invalid_columns = range(0, len_fasta_entry)

while fasta.next():
    if fasta.pos % 100 == 0:
        sys.stderr.write('\rSTEP 1: %.2d%% -- pos: %d' % (fasta.pos * 100 / fasta.total_seq, fasta.pos))
        sys.stderr.flush()

    for i in invalid_columns:
        if fasta.seq[i] != '-':
            invalid_columns.remove(i)

print
fasta.reset()

columns_to_keep = [x for x in range(0, len_fasta_entry) if x not in invalid_columns] 

f = open(sys.argv[1] + '-TRIMMED', 'w')

while fasta.next():
    if fasta.pos % 100 == 0:
        sys.stderr.write('\rSTEP 2: %.2d%% -- pos: %d' % (fasta.pos * 100 / fasta.total_seq, fasta.pos))
        sys.stderr.flush()
    new_seq = ''
    for i in columns_to_keep:
        new_seq += fasta.seq[i]
    f.write('>' + fasta.id + '\n')
    f.write(new_seq + '\n')

print
f.close()
