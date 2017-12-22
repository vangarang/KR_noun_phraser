#-*-coding:utf-8-*-
########################################
# -- Loading Helper
########################################
import sys
module_path = '/'.join(__file__.split('/')[:-2])
sys.path.append(module_path)

import nltk
from MOP_linux.module.mKLT import mKlt
from MOP_linux.module.nPatternFinder import search
########################################
# -- RE-term Extraction
########################################

_strg1_1 = ('NP:{<N>+<B>?<N>+<j><V><e><U>}', 0, 4)      # '~~~에 관하ㄴ 것'
_strg2_1 = ('NP:{<N>{2}<j><V><e>}', 0, 3)               # 'N N 에 의하여', 'N N 를 통하여'
_strg2_2 = ('NP:{<is|ui|wa|gwa><N>{2}}', 1, 0)          # '은/는/이/가/의/와/과 N N'
_strg2_3 = ('NP:{<uro><N>{2,}<s>?<j><N><te>}', 1, 3)    # '으로 ~~~ 을 향상 시킨다.'
_strg2_4 = ('NP:{<N>{2}<is|ui|wa|gwa>}', 0, 1)          # 'N N 은/는/이/가/의/와/과'
_strg2_5 = ('NP:{<N><N>{2}}', 1, 0)                     # "'N {N N}'"
_strg2_6 = ('NP:{<N>{2}<N>}', 0, 1)                     # "'{N N} N'"
_strg3_1 = ('NP:{<N><s|N>+<N><s>?}', 0, 0)              # '산업용 설비 구조물', '흡수 성질 최대+화'

# 형용사 + 명사 + 명사

strategies = (_strg1_1, _strg2_1, _strg2_2, _strg2_3, _strg2_4, _strg2_5, _strg2_6, _strg3_1)

def suffix_regex(s, poses, strg):
    if not strg:
        return None
    gram, l, r = strg
    parser = nltk.RegexpParser(gram)
    chunks = parser.parse(poses)
    chunks = [chunk.leaves() if type(chunk) != tuple else chunk for chunk in chunks]
    chunks = [ chunk for chunk in chunks if type(chunk) == list]
    # return chunks
    if len(chunks):  # 후 처리 -> 리턴
        if r:
            return search(s, [' '.join([w for w, t in chunk[l:-r]]) for chunk in chunks])
        elif l:
            return search(s, [' '.join([w for w, t in chunk[l:]]) for chunk in chunks])
        else:
            return search(s, [' '.join([w for w, t in chunk]) for chunk in chunks])
    return None

def chunk(sent):
    if not sent:
        return None
    poses = mKlt.pos(sent)
    # print(poses)
    # -- 예외 처리
    if not len(poses):
        return None

    if len(poses) == 1:
        return []

    founds = []
    for strg in strategies:
        found = suffix_regex(sent, poses, strg)
        if found:
            founds += found
    chunk_set = set([('!_!'.join(chunks),freq) for chunks,freq in founds if type(freq) is int ])
    return list(chunk_set)