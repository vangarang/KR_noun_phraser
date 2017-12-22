#-*- coding:utf8 -*-
import os, re, codecs, string, random
from subprocess import DEVNULL, STDOUT, check_call
from soynlp.hangle import compose
from soynlp.hangle import decompose
from glob import glob as gl
module_path = '/'.join(__file__.split('\\')[:-1])
c_tags = [(('와','j'),('와','wa')),(('과','j'),('과','gwa')), (('으로', 'j'),('으로','uro')),(('의', 'j'),('의','ui')), (('도', 'j'),('도','N')), (('이상','N'),('이상','deg')),
          (('이하', 'N'), ('이하', 'deg')), (('미만','N'),('미만','deg')), (('초과','N'),('초과','deg')), (('경우','N'),('경우','case')),
          (('는', 'j'), ('는', 'is')),(('은', 'j'), ('은', 'is')),(('이', 'j'), ('이', 'is')),(('가', 'j'), ('가', 'is')), ]
os.chdir(module_path)

def _parse(ele):
    ele = ele.replace(' ', "','")
    ele = ele.replace('(', "('")
    ele = ele.replace(')', "')")
    try:
        ele = eval(ele)
        return (ele[1], ele[0])
    except:
        return ('','')

from nltk import RegexpParser
# file write -> input file 생성 -> KLT.exe 호출 -> output file 생성 -> file read
def pos(s, remove_tag=[], c_tag=[], _opt = '-tip1+sw', _in = 'sample.in', _out = 'sample.out', thread=True):
    try:
        c_tag = c_tags
        # -- 멀티 세션 돌릴때 파일이름 겹치면 오류발생함
        if thread:
            def _idGenerator():
                return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            _in = _idGenerator()+'.in'
            _out = _idGenerator()+'.out'

        _i = gl('*.in')
        if len(_i):
            for i in _i:
                os.remove(i)
        _o = gl('*.out')
        if len(_o):
            for o in _o:
                os.remove(o)
        # 50 단어 마다 줄바꿈 ( 안하면 KLT에서 WARNING 발생 )
        words = s.split()
        s = [ ' '.join(words[i:i + 50]) for i in range(0, len(words), 50) ]
        s = '\n'.join(s)
        f = codecs.open(_in, 'w+', encoding='KSC5601')
        f.write(s)
        f.close()

        command = ["kma.exe",_opt,_in,_out]
        check_call(command, stdout=DEVNULL, stderr=STDOUT)



        os.remove(_in)   # 파일 지우기

        f = codecs.open(_out, encoding='KSC5601')
        tokend_text = f.read()
        f.close()

        os.remove(_out)  # 파일 지우기

        str_token = re.findall(pattern='\([\w ]+\)', string=tokend_text)
        poses = list(map(_parse, str_token))

        # -- 불용태그 제거
        if len(remove_tag):
            poses = [(w,t) for w,t in poses if t not in remove_tag ]

        chunker = RegexpParser('JOSA:{<t|c><e>}')
        chunks  = chunker.parse(poses)
        chunks  = [chunk.leaves() if type(chunk) != tuple else chunk for chunk in chunks]
        poses = []
        for pos in chunks:
            if type(pos) == list:
                w1, t1 = pos[0]
                jong, t2 = pos[1]
                try:
                    chojung = decompose(w1)
                    w = compose(chojung[0], chojung[1], jong)
                except:
                    w = w1+jong

                if w1 == '하' and jong == '어':
                    w = '해'
                pos = (w, t1+t2)
            for org,cus in c_tag:
                if org == pos:
                    pos = cus
            poses.append(pos)

        # 불용어 제거
        stop_words = [('의','N'),('을','N'),('를','N'),('대한','N'),('인해','N'),('중','N'),('등','N')]
        poses = [ pos for pos in poses if pos not in stop_words]
        return poses
    except:
        return []



# 명사추출
def nouns(s, mop_score=False):
    try:
        if mop_score:
            return [(m,s) for m,t,s in pos(s, True) if t == 'N']
        return [m for m, t in pos(s) if t == 'N']
    except:
        return []
