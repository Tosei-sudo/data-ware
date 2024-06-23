# coding: utf-8

import unicodedata

raw_data = u'日本語においてカタカナとｶﾀｶﾅとﾋﾗｶﾞﾅはdifficultですが①番　ＩＭＰＯＲＴＡＮＴです。'

converted_data = unicodedata.normalize('NFKD', raw_data).lower()

with open('output.txt', 'w') as f:
    f.write(converted_data.encode('utf-8'))
