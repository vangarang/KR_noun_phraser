import re

def search(s, terms):
    res = []
    for term in terms:
        if term == ' ':
            continue
        elif ' ' in term:
            terms_tmp = term.split()
            patterns = ['[ㄱ-ㅎㅏ-ㅣ가-힣]*'+term+'[ㄱ-ㅎㅏ-ㅣ가-힣]*' for term in terms_tmp[:-1]]
            patterns.append(terms_tmp[-1])
            pattern = re.compile('[\s/-]?'.join(patterns))
        else:
            pattern = re.compile(pattern=term)
        founds = re.findall(pattern, s)
        len_founds = len(founds)
        if not len_founds:
            continue
        founds = list(set(founds))
        ele = (founds, len_founds)
        if len(founds) > 1:
            founds = [(found, s.count(found)*len(found)) for found in founds]
            found = sorted(founds, key=lambda w: w[1], reverse=True)
            found = [w for w,f in found]
            ele = (found, len_founds)
        res.append(ele)

    return sorted(res, key=lambda x:x[1], reverse=True)