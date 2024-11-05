#!/usr/bin/env python3
"""
Created on 17/04/19

author: fenia
"""

import argparse
import codecs
from collections import defaultdict

'''
Adaptation of https://github.com/patverga/bran/blob/master/src/processing/utils/filter_hypernyms.py
'''

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input_file', required=True, help='input file in 13col tsv')
parser.add_argument('-m', '--mesh_file', required=True, help='mesh file to get hierarchy from')
parser.add_argument('-o', '--output_file', required=True, help='write results to this file')

args = parser.parse_args()


def chunks(l, n):
    """
    Yield successive n-sized chunks from l.
    """
    for i in range(0, len(l), n):
        assert len(l[i:i + n]) == n
        yield l[i:i + n]


# read in mesh hierarchy
ent_tree_map = defaultdict(list)
with codecs.open(args.mesh_file, 'r') as f:
    lines = [l.rstrip().split('\t') for i, l in enumerate(f) if i > 0]
    [ent_tree_map[l[1]].append(l[0]) for l in lines]

# read in input file and organize by document
print('Loading examples from %s' % args.input_file)
neg_doc_examples = defaultdict(list)

unfilitered_neg_count = 0
text = {}
with open(args.input_file, 'r') as f:
    lines = [l.strip().split('\t') for l in f]

    for l in lines:
        pmid = l[0]
        text[pmid] = pmid + '\t' + l[1]

        for r in chunks(l[2:], 17):
            if r[0] == '1:NR:2':
                assert ((r[7] == 'Chemical') and (r[13] == 'Disease'))
                neg_doc_examples[pmid].append(r)
                unfilitered_neg_count += 1

# iterate over docs
hypo_count = 0
negative_count = 0

with open(args.output_file, 'w') as out_f:
    for doc_id in neg_doc_examples.keys():
        towrite = text[doc_id]

        filtered_neg_examples = []
        for ne in neg_doc_examples[doc_id]:
            neg_e1 = ne[5]
            neg_e2 = ne[11]
            example_hyponyms = 0
            for neg_node in ent_tree_map[ne[11]]:
                hyponyms = [pos_node for pos_node in ent_tree_map[neg_e1] if neg_node in pos_node]
                example_hyponyms += len(hyponyms)
            if example_hyponyms == 0:
                towrite += '\t' + '\t'.join(ne)
                negative_count += 1
            else:
                ne[0] = 'not_include'  # mark entries to exclude but retain entities
                towrite += '\t' + '\t'.join(ne)
                hypo_count += example_hyponyms
        out_f.write(towrite + '\n')

print('Mesh entities: %d' % len(ent_tree_map))
print('Negative Docs: %d' % len(neg_doc_examples))
print('Initial Negative Count: %d   Final Negative Count: %d   Hyponyms: %d' %
      (unfilitered_neg_count, negative_count, hypo_count))
