# -*- coding: utf-8 -*-

# Copyright (C) 2010 - 2011, A. Murat Eren
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

import sys
import os

def evaluate_indel(query, target, index, shift = 0):
    # HP stands for Homo-polymer in this context..
    if index < 3 or len(query) - index < 3:
        # it is too early or too late in the sequence to control before and/or after.
        return None
  
    isHP = lambda x: len(set(x)) == 1
   

    # following two functions, DownStream and UpStream would return three nucleotides
    # before or after the index position respectively, if there is no homopolymer region
    # around the index. in case there is a homopolymer region, they make it sure that
    # they both return the exact length of it.
    #
    # if '-' denotes index position, these would be the results:
    #
    # DownStream('ATCG-')    -> TCG
    # DownStream('TAAA-')    -> AAA
    # DownStream('TGGGGGG-') -> GGGGGG
    def DownStream(sequence):
        i = 3
        while isHP(sequence[index - i - 1:index]):
            i += 1
        return sequence[index - i:index]

    def UpStream(sequence):
        i = 4
        while isHP(sequence[index + 1:index + i + 1]):
            i += 1
        return sequence[index + 1:index + i]


    HPonlyBefore = lambda x: isHP(DownStream(x)) and not isHP(UpStream(x))
    HPonlyAfter = lambda x: isHP(UpStream(x)) and not isHP(DownStream(x))
    HPbothWays = lambda x: isHP(UpStream(x)) and isHP(DownStream(x))
    HPnowhere = lambda x: not isHP(UpStream(x)) and not isHP(DownStream(x))

    RepeatingNucleotide = lambda x: list(set(x))[0]

    RemoveNucleotide = lambda x: x[0:index] + x[index + 1:]

    if target[index] == '-':
        
        # There is a gap in target sequence, therefore there is an insertion
        # in query sequence..
        
        if HPonlyBefore(target): #homopolymer region before index in target
            # ...GGG-ATCG...
            # ...????ATCG...
            if HPonlyBefore(query) and DownStream(query) == DownStream(target):
                # ...GGG-ATCG...
                # ...GGG?ATCG...
                if RepeatingNucleotide(DownStream(query)) == query[index]:
                    # ...GGG-ATCG...
                    # ...GGGGATCG...
                    return (RemoveNucleotide(query), RemoveNucleotide(target), ('ins', index + shift, query[index]))
                else:
                    # ...GGG-ATCG...
                    # ...GGGTATCG...
                    return None
        

        if HPonlyAfter(target): #homopolymer region after index in target
            # ...ATCG-GGGT...
            # ...ATCG????T...
            if HPonlyAfter(query) and UpStream(query) == UpStream(target):
                # ...ATCG-GGGT...
                # ...ATCG?GGGT...
                if RepeatingNucleotide(UpStream(query)) == query[index]:
                    # ...ATCT-GGGT...
                    # ...ATCTGGGGT...
                    return (RemoveNucleotide(query), RemoveNucleotide(target), ('ins', index + shift, query[index]))
                else:
                    # ...ATCT-GGGT...
                    # ...ATCTAGGGT...
                    return None
                    

        if HPbothWays(target): # homopolymer region both before and after index in target
            # ...ATCCCC-GGGT...
            # ...AT????????T...
            if isHP(DownStream(query)) and RepeatingNucleotide(DownStream(query)) == query[index]:
                # ...ATCCCC-GGGT... 
                # ...ATCCCCC???T...
                return (RemoveNucleotide(query), RemoveNucleotide(target), ('ins', index + shift, query[index]))
            elif isHP(UpStream(query)) and RepeatingNucleotide(UpStream(query)) == query[index]:
                # ...ATCCCC-GGGT... 
                # ...AT????GGGGT...
                return (RemoveNucleotide(query), RemoveNucleotide(target), ('ins', index + shift, query[index]))
            else:
                return None


        if HPnowhere(target):
            return None
    
    elif query[index] == '-':

        # query has a gap, compared to target at 'index' location.

        pass


def treat_homopolymer_noise(query, target):
    """
    This function expects two pair-wise aligned sequences as parameters: a query sequence and a target sequence.

    target: 'ATCGCAGCCTTT-GCGGTAATACGTAGGG-CGCAAGCGT-TATCC-GGGAATTATTGGGCGTAAA-GGGAGCTTGTAGGCGGTATCAT'
    query : '----CAGCCTTTAGCGGTAATACGTAGGGGCGCAAGCGTCTATCCGGGGAATTATTGGGCGTAAAAGGGAGCTTGTAGGCGGT-----'

    """

    shift = 0
    index = 0
    changes = []
    
    while True:
        if index + 1 >= len(query):
            break
    
        if target[index] == '-' or query[index] == '-':
            # insertion in query
            result = evaluate_indel(query, target, index, shift)
    
            if result:
                query, target, change = result
                changes.append(change)
                shift += 1
            else:
                index += 1
        else:
            index += 1

    return (query, target, changes)


if __name__ == '__main__':
    import argparse
    import Oligotyping.lib.fastalib as u
    
    parser = argparse.ArgumentParser(description='Homopoylmer Region Treatment')

    parser.add_argument('-i', '--input-alignment', required = True, metavar = 'FASTA_ALIGNMENT', help = 'align2first output (.paf file)')
    parser.add_argument('-o', '--output-fasta', required = True, help = 'Output FASTA file to store homopolymer-treated sequences')
    parser.add_argument('-l', '--log', help = 'Log file. Default, STDOUT.', default = None)

    args = parser.parse_args()

    input_alignment = u.SequenceSource(args.input_alignment)
    
    if os.path.exists(args.output_fasta):
        sys.stderr.write('Output file ("%s") exists. Overwrite? [Y|n] ' % args.output_fasta)
        response = raw_input()
        if response == '' or response.lower() == 'y':
            output_fasta = open(args.output_fasta, 'w')
        else:
            print 'Exiting.'
            sys.exit(1)
    else:
        output_fasta = open(args.output_fasta, 'w')

    if args.log:
        if os.path.exists(args.log):
            print 'Log file ("%s") exists. Exting.' % args.log
            sys.exit(1)
        else:
            log = open(args.log, 'w')
    else:
        log = sys.stdout

    
    while input_alignment.next():
        target_id = input_alignment.id
        target_seq = input_alignment.seq

        input_alignment.next()

        query_id = input_alignment.id
        query_seq = input_alignment.seq

        query_fixed, target, changes = treat_homopolymer_noise(query_seq, target_seq)

        output_fasta.write('>' + query_id + '\n')
        output_fasta.write(query_fixed.replace('-', '') + '\n')

        log.write(query_id + '\t' + target_id + '\t' + '\t'.join([','.join([j.__str__() for j in t]) for t in changes]) + '\n')
        
        if len(changes):
            log.write('#\n')
            log.write('#            ' + '     '.join(['      %s: %s     ' % (x[0], x[2]) for x in changes]) + '\n')
            log.write('#            ' + '     '.join([' =============== ' for x in changes]) + '\n')
            log.write('#    TARGET: ' + '(...)'.join(['  %s  ' % target_seq[x[1] - 6:x[1] + 7] for x in changes]) + '\n')
            log.write('#    QUERY : ' + '(...)'.join(['  %s  ' % query_seq[x[1] - 6:x[1] + 7] for x in changes]) + '\n')
            log.write('#\n')
            log.write('#\n')
                

    output_fasta.close()
    
    if args.log:
        log.close()
