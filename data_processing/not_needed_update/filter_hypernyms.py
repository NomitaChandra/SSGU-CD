# #!/usr/bin/env python3
# """
# Created on 17/04/19

# author: fenia
# """

# import argparse
# import codecs
# import csv
# from collections import defaultdict

# '''
# Adaptation of https://github.com/patverga/bran/blob/master/src/processing/utils/filter_hypernyms.py
# '''

# parser = argparse.ArgumentParser()
# parser.add_argument('-i', '--input_file', required=True, help='input file in 13col tsv')
# parser.add_argument('-m', '--mesh_file', required=True, help='mesh file to get hierarchy from')
# parser.add_argument('-o', '--output_file', required=True, help='write results to this file')
# parser.add_argument('-d', '--debug_file', required=True, help='debug output file to save intermediate outputs')

# args = parser.parse_args()

# def chunks(l, n):
#     """
#     Yield successive n-sized chunks from l.
#     """
#     for i in range(0, len(l), n):
#         assert len(l[i:i + n]) == n
#         yield l[i:i + n]

# # Initialize debug file to write intermediate outputs
# with open(args.debug_file, 'w', newline='') as debug_csv:
#     debug_writer = csv.writer(debug_csv)
#     debug_writer.writerow(['Stage', 'Description', 'Data'])

#     # Read in mesh hierarchy
#     ent_tree_map = defaultdict(list)
#     with codecs.open(args.mesh_file, 'r') as f:
#         lines = [l.rstrip().split('\t') for i, l in enumerate(f) if i > 0]
#         [ent_tree_map[l[1]].append(l[0]) for l in lines]

#     # Read in positive input file and organize by document
#     print('Loading examples from %s' % args.input_file)
#     pos_doc_examples = defaultdict(list)
#     neg_doc_examples = defaultdict(list)
#     unfilitered_pos_count = 0
#     unfilitered_neg_count = 0
#     text = {}

#     with open(args.input_file, 'r') as f:
#         lines = [l.strip().split('\t') for l in f]
#         debug_writer.writerow(['Initial Lines', 'Parsed input lines', lines])

#         for l in lines:
#             pmid = l[0]
#             text[pmid] = pmid + '\t' + l[1]

#             for r in chunks(l[2:], 17):
#                 if r[0] == '1:NR:2':
#                     assert ((r[7] == 'Chemical') and (r[13] == 'Disease'))
#                     neg_doc_examples[pmid].append(r)
#                     unfilitered_neg_count += 1
#                 elif r[0] == '1:CID:2':
#                     assert ((r[7] == 'Chemical') and (r[13] == 'Disease'))
#                     pos_doc_examples[pmid].append(r)
#                     unfilitered_pos_count += 1

#         debug_writer.writerow(['Positives by Document', 'pos_doc_examples', dict(pos_doc_examples)])
#         debug_writer.writerow(['Negatives by Document', 'neg_doc_examples', dict(neg_doc_examples)])

#     # Iterate over docs and filter negative examples
#     hypo_count = 0
#     negative_count = 0
#     all_pos = 0

#     with open(args.output_file, 'w') as out_f:
#         for doc_id in pos_doc_examples.keys():
#             towrite = text[doc_id]

#             for r in pos_doc_examples[doc_id]:
#                 towrite += '\t'
#                 towrite += '\t'.join(r)
#             all_pos += len(pos_doc_examples[doc_id])

#             # Get nodes for all the positive diseases
#             pos_e2_examples = [(pos_node, pe) for pe in pos_doc_examples[doc_id]
#                                for pos_node in ent_tree_map[pe[11]]]
#             pos_e1_examples = [(pos_node, pe) for pe in pos_doc_examples[doc_id]
#                                for pos_node in ent_tree_map[pe[5]]]

#             debug_writer.writerow(['Positive e2 Examples', 'pos_e2_examples', pos_e2_examples])
#             debug_writer.writerow(['Positive e1 Examples', 'pos_e1_examples', pos_e1_examples])

#             if pos_doc_examples:  # Only proceed if there are positive examples
#                 pos_e2_examples = [(pos_node, pe) for pe in pos_doc_examples[doc_id]
#                                 for pos_node in ent_tree_map[pe[11]]]
#                 pos_e1_examples = [(pos_node, pe) for pe in pos_doc_examples[doc_id]
#                                 for pos_node in ent_tree_map[pe[5]]]
#             else:
#                 # No positive examples, so set pos_e1_examples and pos_e2_examples to empty lists
#                 pos_e2_examples = []
#                 pos_e1_examples = []

#             # Now process negative examples as before
#             filtered_neg_exampled = []
#             for ne in neg_doc_examples[doc_id]:
#                 neg_e1 = ne[5]
#                 neg_e2 = ne[11]
#                 example_hyponyms = 0
#                 matching_pos_nodes = []

#                 for neg_node in ent_tree_map[ne[11]]:
#                     # Check for matches in pos_e2_examples and pos_e1_examples only if they are not empty
#                     hyponyms = ([pos_node for pos_node, pe in pos_e2_examples
#                                 if neg_node in pos_node and neg_e1 == pe[5]]
#                                 + [pos_node for pos_node, pe in pos_e1_examples
#                                 if neg_node in pos_node and neg_e2 == pe[11]])

#                     example_hyponyms += len(hyponyms)
#                     matching_pos_nodes.extend(hyponyms)

#                 if example_hyponyms == 0:
#                     towrite += '\t' + '\t'.join(ne)
#                     negative_count += 1
#                     filtered_neg_exampled.append(ne)  # Store the included negative example
#                 else:
#                     ne[0] = 'not_include'
#                     towrite += '\t' + '\t'.join(ne)
#                     hypo_count += example_hyponyms

#                 debug_writer.writerow(['Negative e1', neg_e1])
#                 debug_writer.writerow(['Negative e2', neg_e2])
#                 debug_writer.writerow(['Neg node' , neg_node])
#                 debug_writer.writerow(['Negative filtered', filtered_neg_exampled])

#             debug_writer.writerow(['Document Filtering', f'Document {doc_id} processed', towrite])
#             out_f.write(towrite + '\n')

#     # Final counts
#     with open(args.debug_file, 'a', newline='') as debug_csv:  # reopen to append final outputs
#         debug_writer = csv.writer(debug_csv)
#         debug_writer.writerow(['Summary', 'Mesh entities count', len(ent_tree_map)])
#         debug_writer.writerow(['Summary', 'Positive Docs count', len(pos_doc_examples)])
#         debug_writer.writerow(['Summary', 'Negative Docs count', len(neg_doc_examples)])
#         debug_writer.writerow(['Summary', 'Positive Count', unfilitered_pos_count])
#         debug_writer.writerow(['Summary', 'Initial Negative Count', unfilitered_neg_count])
#         debug_writer.writerow(['Summary', 'Final Negative Count', negative_count])
#         debug_writer.writerow(['Summary', 'Hyponyms', hypo_count])
#         debug_writer.writerow(['Summary', 'Total Positive Examples', all_pos])

# print('Mesh entities: %d' % len(ent_tree_map))
# print('Positive Docs: %d' % len(pos_doc_examples))
# print('Negative Docs: %d' % len(neg_doc_examples))
# print('Positive Count: %d   Initial Negative Count: %d   Final Negative Count: %d   Hyponyms: %d' %
#       (unfilitered_pos_count, unfilitered_neg_count, negative_count, hypo_count))
# print(all_pos)

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

# read in positive input file and organize by document
print('Loading examples from %s' % args.input_file)
pos_doc_examples = defaultdict(list)
neg_doc_examples = defaultdict(list)

unfilitered_pos_count = 0
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
            elif r[0] == '1:CID:2':
                assert ((r[7] == 'Chemical') and (r[13] == 'Disease'))
                pos_doc_examples[pmid].append(r)
                unfilitered_pos_count += 1

# iterate over docs
hypo_count = 0
negative_count = 0

all_pos = 0
with open(args.output_file, 'w') as out_f:
    for doc_id in pos_doc_examples.keys():
        towrite = text[doc_id]

        for r in pos_doc_examples[doc_id]:
            towrite += '\t'
            towrite += '\t'.join(r)
        all_pos += len(pos_doc_examples[doc_id])

        # get nodes for all the positive diseases
        pos_e2_examples = [(pos_node, pe) for pe in pos_doc_examples[doc_id]
                           for pos_node in ent_tree_map[pe[11]]]

        pos_e1_examples = [(pos_node, pe) for pe in pos_doc_examples[doc_id]
                           for pos_node in ent_tree_map[pe[5]]]

        filtered_neg_exampled = []
        for ne in neg_doc_examples[doc_id]:
            neg_e1 = ne[5]
            neg_e2 = ne[11]
            example_hyponyms = 0
            for neg_node in ent_tree_map[ne[11]]:
                hyponyms = [pos_node for pos_node, pe in pos_e2_examples
                            if neg_node in pos_node and neg_e1 == pe[5]] \
                           + [pos_node for pos_node, pe in pos_e1_examples
                              if neg_node in pos_node and neg_e2 == pe[11]]
                example_hyponyms += len(hyponyms)
            if example_hyponyms == 0:
                towrite += '\t' + '\t'.join(ne)
                negative_count += 1
            else:
                ne[0] = 'not_include'  # just don't include the negative pairs, but keep the entities
                towrite += '\t' + '\t'.join(ne)
                hypo_count += example_hyponyms
        out_f.write(towrite + '\n')

print('Mesh entities: %d' % len(ent_tree_map))
print('Positive Docs: %d' % len(pos_doc_examples))
print('Negative Docs: %d' % len(neg_doc_examples))
print('Positive Count: %d   Initial Negative Count: %d   Final Negative Count: %d   Hyponyms: %d' %
      (unfilitered_pos_count, unfilitered_neg_count, negative_count, hypo_count))
print(all_pos)
