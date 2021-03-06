# -*- coding: utf-8 -*-
# takes an environment file and a cosine similarity threshold as a parameter,
# generates an environment file with sets of units defined by the similarity
# they possess with respect to the frequency distribution patterns among
# samples.

import sys
from Oligotyping.utils.utils import get_samples_dict_from_environment_file
from Oligotyping.utils.utils import get_oligos_sorted_by_abundance
from Oligotyping.utils.utils import get_units_across_samples_dicts
from Oligotyping.utils.utils import get_unit_counts_and_percents
from Oligotyping.utils.cosine_similarity import get_oligotype_sets
from Oligotyping.utils.cosine_similarity import get_oligotype_sets_greedy
from Oligotyping.visualization.oligotype_distribution_stack_bar import oligotype_distribution_stack_bar
from Oligotyping.utils.utils import generate_ENVIRONMENT_file 


input_file_path = sys.argv[1]
cosine_similarity_value = float(sys.argv[2])
sets_output_file_name = input_file_path + '-cos-%s-SETS' % cosine_similarity_value
environ_output_file_name = input_file_path + '-cos-%s-SETS-ENVIRON' % cosine_similarity_value

samples_dict = get_samples_dict_from_environment_file(input_file_path)
oligos = get_oligos_sorted_by_abundance(samples_dict)
unit_counts, unit_percents = get_unit_counts_and_percents(oligos, samples_dict)
samples = samples_dict.keys()

across_samples_sum_normalized, across_samples_max_normalized = get_units_across_samples_dicts(oligos, samples_dict.keys(), unit_percents) 
oligotype_sets = get_oligotype_sets_greedy(oligos,
                                    across_samples_sum_normalized,
                                    cosine_similarity_value,
                                    sets_output_file_name)

print '%d sets from %d units' % (len(oligotype_sets), len(oligos))

samples_dict_with_agglomerated_oligos = {}

for sample in samples:
    samples_dict_with_agglomerated_oligos[sample] = {}


for set_id in oligotype_sets:
    oligotype_set = oligotype_sets[set_id]
    for sample in samples:
        samples_dict_with_agglomerated_oligos[sample][set_id] = 0
        for oligo in samples_dict[sample]:
            if oligo in oligotype_set:
                samples_dict_with_agglomerated_oligos[sample][set_id] += samples_dict[sample][oligo]
    

oligotype_distribution_stack_bar(samples_dict_with_agglomerated_oligos, None)
generate_ENVIRONMENT_file(samples,
                          samples_dict_with_agglomerated_oligos,
                          environ_output_file_name)
