
from pypinyin import pinyin, Style
import numpy as np
import matplotlib.pyplot as plt

con_dict = {'y': 9129, 'j': 6742, 'sh': 6431, 'x': 5554, 'zh': 5239, 'l': 5208,
            'b': 5020, 'd': 4668, 'h': 4406, 'q': 4123, 'g': 3924, 'w': 3797, 'f': 3758,
            'm': 3717, 'ch': 3555, 't': 3462, 'r': 2432, 's': 2316, 'z': 2092, 'k': 1532,
            'c': 1522, '': 1482, 'p': 1336, 'n': 1341}

vow_dict = {'i': 15006, 'u': 12481, 'an': 5419, 'ing': 3938, 'ian': 3681, 'eng': 3480,
            'ou': 3412, 'ong': 3311, 'en': 3175, 'ao': 3142, 'ang': 3095, 'e': 3050, 
            'in': 2848, 'ai': 2539, 'uan': 2391, 'ei': 2308, 'uo': 2300, 'a': 2164,
            'ui': 2160, 'un': 1746, 'iao': 1663, 'iu': 1336, 'ie': 1314, 'iang': 1237,
            'ue': 1011, 'o': 944, 'ia': 804, 'uang': 741, 'ua': 613, 'er': 545, 'v': 319,
            'iong': 317, 'uai': 256, 've': 40}

N = 23196

d = {'consonant': 0, 'vowel': 1, 'tune': 2}  # The order of each list.

def _score(con_list, vow_list, weight_con=3, weight_vow=1):
    score = 0
    for i in range(len(con_list)):
        score += (con_dict[con_list[i]] * weight_con +
                  vow_dict[vow_list[i]] * weight_vow) / (weight_con + weight_vow) / 4 / N
    return score

def _all_diff(l):
    return len(set(l)) == len(l)

def _parse(word):
    con_list = pinyin(word, style=Style.INITIALS, strict=False, neutral_tone_with_five=True)
    vow_list = pinyin(word, style=Style.FINALS, strict=False, neutral_tone_with_five=True)
    tune_list = pinyin(word, style=Style.TONE3, strict=False, neutral_tone_with_five=True)
    return [[i[0] for i in con_list], [i[0] for i in vow_list], [i[0][-1] for i in tune_list]]

def _solve_blue(blue, parse_list):
    pos, key, value = blue
    return parse_list[d[key]][pos-1] == value

def _solve_yellow(yellow, parse_list):
    pos, key, value = yellow
    return (parse_list[d[key]][pos-1] != value) and (value in parse_list[d[key]])

def _solve_gray(gray, parse_list):
    pos, key, value = gray
    return value not in parse_list[d[key]]

def _possible(parse_list, blue, yellow, gray):
    for b in blue:
        if not _solve_blue(b, parse_list):
            return False
    for y in yellow:
        if not _solve_yellow(y, parse_list):
            return False
    for g in gray:
        if not _solve_gray(g, parse_list):
            return False
    return True





def stat(f=open('./data/all.txt', 'r')):
    con_list, vow_list = [], []
    for line in f.readlines():
        parse_list = _parse(line[:-1])
        con_list += parse_list[0]
        vow_list += parse_list[1]

    con_dict, vow_dict = {}, {}
    for i in range(len(con_list)):
        con_dict[con_list[i]] = con_dict.get(con_list[i], 0) + 1
        vow_dict[vow_list[i]] = vow_dict.get(vow_list[i], 0) + 1
    
    return con_dict, vow_dict

def initial_guess(con_dict, vow_dict, thres=None, weight_con=3, weight_vow=1):
    f = open('./data/all.txt', 'r')
    max_score = 0. if thres is None else thres

    for line in f.readlines():
        parse_list = _parse(line[:-1])

        score = _score(parse_list[0], parse_list[1], weight_con=weight_con, weight_vow=weight_vow)
        if (score > max_score and '5' not in parse_list[2] and _all_diff(parse_list[2])
            and _all_diff(parse_list[0]) and _all_diff(parse_list[1])):
            if thres is None:
                max_score = score
            else:
                print("较好的初始猜测是 is %s (%.2f)\n" %(line, max_score))
            best = line
    print("最佳的初始猜测是 %s (%.6f)\n" %(best, max_score))

def plot_bar(con_dict, vow_dict):
    plt.figure(figsize=(20, 10))
    plt.subplots_adjust(left=.1, bottom=.1, right=.98, top=.95, hspace=.2)

    ax = plt.subplot(211)
    values = np.array(list(con_dict.values()))
    keys = np.array(list(con_dict.keys()))
    rev = np.argsort(values)[::-1]
    ax.bar(range(len(con_dict)), values[rev] / 4 / N, color='#367db7')
    x_ticks = range(len(con_dict))
    x_labels = keys[rev]
    ax.set_xlabel('Consonants', fontsize=20)
    ax.set_ylabel('Frequency', fontsize=20)
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_labels)
    ax.tick_params(axis='both', labelsize=20)

    ax = plt.subplot(212)
    values = np.array(list(vow_dict.values()))
    keys = np.array(list(vow_dict.keys()))
    rev = np.argsort(values)[::-1]
    ax.bar(range(len(vow_dict)), values[rev] / 4 / N, color='#df1d27')
    x_ticks = range(len(vow_dict))
    x_labels = keys[rev]
    ax.set_xlabel('Vowels', fontsize=20)
    ax.set_ylabel('Frequency', fontsize=20)
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_labels)
    ax.tick_params(axis='both', labelsize=20)

    plt.savefig('./fig/freq.png')

def solve(trial='研经铸史', blue=[[3, 'tune'], [4, 'vowel']], yellow=[[1, 'consonant']]):
    '''
    Parameters: trial: str
                       In general '研经铸史' is proved to be most efficient
                       and thus defaulted.

                blue: list
                       blue is a list like [[pos, key], [pos, key], ...],
                       showing where the blue hints are.
                       pos is the position.
                       key is the type, including 'consonant', 'vowel', and 'tune'.
                       If no blue, leave it as blank [].

                yellow: all the same as blue.
    
    Returns: None.
             It prints all the possible answers.

    '''

    gray = []
    trial_list = _parse(trial)

    for pos in [1, 2, 3, 4]:
        for key in ['consonant', 'vowel', 'tune']:
            if [pos, key] in blue:
                blue[blue.index([pos, key])] += [trial_list[d[key]][pos-1]]
            elif [pos, key] in yellow:
                yellow[yellow.index([pos, key])] += [trial_list[d[key]][pos-1]]
            else:
                gray.append([pos, key, trial_list[d[key]][pos-1]])

    f = open('./data/all.txt', 'r')
    for i, line in enumerate(f.readlines()):
        parse_list = _parse(line[:-1])
        if _possible(parse_list, blue, yellow, gray):
            print("可能是 %s" %(line))




if 'con_dict' not in locals() or 'vow_dict' or locals():
    con_dict, vow_dict = stat()

# plot_bar(con_dict, vow_dict)
# initial_guess(con_dict, vow_dict, thres=None, weight_con=3, weight_vow=1)
solve(blue=[],
      yellow=[[1, 'tune'], [2, 'tune'], [3, 'vowel'], [4, 'consonant'], [4, 'tune']])



