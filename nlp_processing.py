import numpy as np
import pandas as pd

import textacy
import spacy
nlp = spacy.load('en_core_web_lg')
from spacy.matcher import Matcher

from pattern.en import tenses

# https://gist.github.com/armsp/30c2c1e19a0f1660944303cf079f831a

# set up passive voice matching
matcher = Matcher(nlp.vocab)
passive_rule = [{'DEP': 'nsubjpass'},
                {'DEP': 'aux', 'OP': '*'},
                {'DEP': 'auxpass'},
                {'TAG': 'VBN'}]
# trying to improve passive rule
# passive_rule = [{'DEP': 'nsubjpass', 'OP': '*'},
#                 {'DEP': 'nsubj', 'OP': '*'},
#                 {'DEP': 'aux', 'OP': '*'},
#                 {'DEP': 'auxpass', 'OP': '?'},
#                 {'POS': 'VERB', 'OP': '+'}]
matcher.add('Passive', None, passive_rule)

# for testing:
text = """This will be a test of writing terribly, and is going to be an example of multiple verb clauses.
            I will be using a future progressive verb, horribly.
            This is a passive sentence."""

doc = nlp(text)

sents = list(doc.sents)
print("Number of Sentences = ", len(sents))

# gives match_id, start, end
matches = matcher(doc)
df = pd.DataFrame(matches, columns=['id', 'start', 'end'])
df.drop_duplicates(inplace=True)
print(df.shape[0], 'passive sentences detected')

# print out passive phrases
for i, r in df.iterrows():
    print(doc[r['start']:r['end']])

# progressive tense detection
# get verb phrase from sentences and check if progressive

# adverb detection
# "The road to hell is paved with adverbs." -- Stephen King

verb_clause_pattern = r'<VERB>*<ADV>*<PART>*<VERB>+<PART>*'

progressive_sentences, progressive_verb_clauses = [], []
adverb_sentences, adverbs = [], []
for s in sents:
    verb_clauses = list(textacy.extract.pos_regex_matches(s, verb_clause_pattern))
    for v in verb_clauses:
        if len(v) > 1:  # need to have some helper verbs to have a problem
            verb_tenses = pd.DataFrame(list(tenses(v.text)))
            if 'progressive' in verb_tenses.iloc[:, -1].tolist():  # last column
                progressive_sentences.append(s)
                progressive_verb_clauses.append(v)

    # was using this to detect verb clauses before, very inefficient
    pos = np.array([w.pos_ for w in s])
    # verbs = np.argwhere(pos == 'VERB').flatten()
    # # get continuous verb clauses
    # verb_diffs = np.concatenate((np.array([1]), np.diff(verbs)))
    # verb_chunks = []
    # temp_verb_chunk = []
    # for i, v in enumerate(verb_diffs):
    #     # print(s[verbs[i]].text)
    #     # first one will always be 1
    #     if v == 1:
    #         temp_verb_chunk.append(s[verbs[i]].text)
    #     else:
    #         if len(temp_verb_chunk) > 1:
    #             verb_ch = ' '.join(temp_verb_chunk)
    #         else:
    #             verb_ch = temp_verb_chunk[0]
    #
    #         print(verb_ch)
    #
    #         verb_chunks.append(verb_ch)
    #         temp_verb_chunk = [s[verbs[i]].text]
    #
    # if len(temp_verb_chunk) > 1:
    #     verb_ch = ' '.join(temp_verb_chunk)
    # else:
    #     verb_ch = temp_verb_chunk[0]
    #
    # verb_chunks.append(verb_ch)


    adverb_idxs = np.argwhere(pos == 'ADV').flatten()

    if len(adverb_idxs) != 0:
        adverb_sentences.append(s)
        adverbs.append([s[a] for a in adverb_idxs])

# print out sentences with adverbs and the adverb

print('\n\n\nADVERBS')
print(len(adverb_sentences), 'sentences detected with adverbs\n')
if len(adverb_sentences) > 0:
    for i, adv in enumerate(adverb_sentences):
        print(adv)
        print('has adverbs:', adverbs[i], '\n')

print('\n\n\nPRORGESSIVE TENSES')

print(len(progressive_sentences), 'sentences detected with progressive verb clauses\n')
if len(progressive_sentences) > 0:
    for i, adv in enumerate(progressive_sentences):
        print(adv)
        print('has progressive verb clause(s):', progressive_verb_clauses[i], '\n')
