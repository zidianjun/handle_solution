
from pypinyin import pinyin, Style
import numpy as np
import matplotlib.pyplot as plt

con_dict = {'y': 11394, 'j': 8658, 'sh': 8028, 'x': 7010, 'zh': 6786, 'l': 6517,
            'b': 6488, 'd': 6037, 'h': 5443, 'g': 5117, 'q': 5094, 'w': 4869, 'm': 4655,
            'f': 4636, 'ch': 4500, 't': 4232, 'r': 3368, 's': 2865, 'z': 2748, 'c': 2063,
            'k': 2010, '': 1905, 'n': 1837, 'p': 1696}

vow_dict = {'i': 19191, 'u': 12816, 'an': 6885, 'ing': 5067, 'ian': 4513, 'eng': 4237,
            'ong': 4127, 'en': 4125, 'ou': 4097, 'ao': 4045, 'ang': 4000, 'e': 3868, 
            'in': 3540, 'ai': 3318, 'uo': 2975, 'ei': 2903, 'a': 2780,
            'ui': 2655, 'iao': 2096, 'uan': 1834, 'iu': 1752, 'ie': 1679, 'iang': 1611,
            've': 1338, 'un': 1331, 'van': 1236, 'o': 1210, 'ia': 1068, 'uang': 980,
            'vn': 872, 'er': 798, 'ua': 780, 'v': 3530, 'iong': 355, 'uai': 344}

N = 29489

d = {'consonant': 0, 'vowel': 1, 'tune': 2}  # The order of each list.

def _score(con_list, vow_list, weight_con=3, weight_vow=1):
    score = 0
    for i in range(len(con_list)):
        score += (con_dict[con_list[i]] * weight_con +
                  vow_dict[vow_list[i]] * weight_vow) / (weight_con + weight_vow) / 4 / N
    return score

def _all_diff(l):
    return len(set(l)) == len(l)

def _parse(word, incorrect_mode=True):
    cons = pinyin(word, style=Style.INITIALS, strict=False, neutral_tone_with_five=True)
    vows = pinyin(word, style=Style.FINALS, strict=False, neutral_tone_with_five=True)
    tunes = pinyin(word, style=Style.TONE3, strict=False, neutral_tone_with_five=True)
    con_list, vow_list, tune_list = [], [], []
    for i in range(len(cons)):
        con_list.append(cons[i][0])
        if incorrect_mode:
            temp = ('v' + vows[i][0][1:] if vows[i][0].startswith('u') and
                    cons[i][0] in ['j', 'q', 'x', 'y'] else vows[i][0])
        else:
            temp = vows[i][0]
        vow_list.append(temp)
        tune_list.append(tunes[i][0][-1])
    return con_list, vow_list, tune_list

def _solve_blue(blue, parse_list):
    pos, key, value = blue
    return parse_list[d[key]][pos-1] == value

def _solve_yellow(yellow, parse_list):
    pos, key, value = yellow
    return (parse_list[d[key]][pos-1] != value) and (value in parse_list[d[key]])

def _solve_gray(gray, parse_list):
    pos, key, value = gray
    return value not in parse_list[d[key]]

def _possible(parse_list, blue_list, yellow_list, gray_list):
    for b in blue_list:
        if not _solve_blue(b, parse_list):
            return False
    for y in yellow_list:
        if not _solve_yellow(y, parse_list):
            return False
    for g in gray_list:
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

def initial_guess(thres=None, weight_con=3, weight_vow=1):
    f = open('./data/all.txt', 'r')
    max_score = 0. if thres is None else thres

    for line in f.readlines():
        parse_list = _parse(line[:-1])

        score = _score(parse_list[0], parse_list[1], weight_con=weight_con, weight_vow=weight_vow)
        if (score > max_score and '5' not in parse_list[2] and _all_diff(parse_list[2])
            and _all_diff(parse_list[0]) and _all_diff(parse_list[1])):
            best, max_score = line, score
            if thres is not None:
                print("较好的初始猜测是 is %s (分数为%.2f)\n" %(line, max_score))
    print("最佳的初始猜测是 %s (分数为%.2f)\n" %(best, max_score))

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

def solve(blue, yellow, trial='研经铸史'):
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
    blue_list, yellow_list, gray_list = [], [], []

    for pos in [1, 2, 3, 4]:
        for key in ['consonant', 'vowel', 'tune']:
            tmp = [pos, key, trial_list[d[key]][pos-1]]
            if [pos, key] in blue:
                blue_list.append(tmp)
            elif [pos, key] in yellow:
                yellow_list.append(tmp)
            else:
                gray_list.append(tmp)

    f = open('./data/all.txt', 'r')
    for i, line in enumerate(f.readlines()):
        parse_list = _parse(line[:-1])
        if _possible(parse_list, blue_list, yellow_list, gray_list):
            print("可能是 %s" %(line))




if 'con_dict' not in locals() or 'vow_dict' or locals():
    con_dict, vow_dict = stat()

# plot_bar(con_dict, vow_dict)
initial_guess(thres=0.25, weight_con=3, weight_vow=1)
# solve(blue=[[3, 'tune'], [4, 'vowel']],
      # yellow=[[1, 'consonant']])



