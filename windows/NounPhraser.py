#-*-coding:utf-8-*-
########################################
# -- Module Loading
########################################
from collections import defaultdict
import ReChunker as newRe
from module.KLT import nouns

def select_max_leaf(elements):
    root = defaultdict(lambda: 0)
    for ele in elements:
        if len(ele) == 2:
            root[ele] = root.get(ele, []) + [ele]
        else:
            root[ele[:2]] = root.get(ele[:2], []) + [ele]

    for stem, branch in root.items():
        max_len = max(map(len, branch))
        for leaf in branch:
            if max_len == len(leaf):
                root[leaf[:2]] = leaf

    elements = list(root.values())
    root = defaultdict(lambda: 0)
    for ele in elements:
        if len(ele) == 2:
            root[ele] = root.get(ele, []) + [ele]
        else:
            root[ele[-2:]] = root.get(ele[-2:], []) + [ele]

    for stem, branch in root.items():
        max_len = max(map(len, branch))
        for leaf in branch:
            if max_len == len(leaf):
                root[leaf[-2:]] = leaf
    return root

def extract(sent):
    stat = defaultdict(lambda: 0)
    try:
        ns = nouns(sent)
    except:
        return []

    if ns:
        for t in ns:
            if len(t) > 1:
                stat[t] = stat.get(t, 0) + 1
    res = newRe.chunk(sent)
    if res :
        for t, f in res:
            stat[t] = stat.get(t, 0) + f

    NTERM = list(stat.items())
    cand_nterms = []
    for nt,f in NTERM:
        nt = nt.split('!_!')
        if type(nt) == list:
            for n in nt:
                cand_nterms.append(n)
        else:
            cand_nterms.append(n)
    selected_leaves = select_max_leaf(cand_nterms)
    return list(selected_leaves.values())

def sentence_tokenizer(sents):
    tokens = []
    stt = 0
    for i, c in enumerate(sents):
        if i + 1 == len(sents):
            tokens.append(sents[stt:].strip())
            break
        if c in ['.', "!", "?", ":", ";"] and sents[i + 1] == ' ':
            tokens.append(sents[stt:i + 1].strip())
            stt = i + 1
    return tokens


def phrase(sents):
    res = []
    tokenized_sents = sentence_tokenizer(sents)

    for sent in tokenized_sents:
        res = res + extract(sent)

    return res