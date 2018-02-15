from string import lowercase as atoz
import re

SUBJECT_CODE = re.compile("[A-Z]{3} [0-9]{4}")
drop = "&-IVIII"



def levenshtein(str1, str2):
    n = len(str1)
    m = len(str2)
    dp = [[0] * (n + 1)] * (m + 1)
    for i in range(n + 1):
        for j in range(m + 1):
            if i == 0:
                dp[i][j] = j
            elif j == 0:
                dp[i][j] = i
            elif str1[i-1] == str2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i][j-1], dp[i-1][j], dp[i-1][j-1])
    return dp[n][m]


def possible_acronym(string):
    string = string.strip().split()
    a = []
    for s in string:
        if s not in drop:
            a.append(chr(ord(s[0]) & ~32))
    return ''.join(a)


def pascal_case(string):
    s = string.strip().split()
    for i in range(len(s)):
        if s[i] not in drop:
            s[i] = s[i].title()
    return " ".join(s)


def best_match(subject_list, token_to_match):

    # string matching
    for subject in subject_list:
        words = subject.split()
        for word in words:
            if len(word) >= 3 and word.find(token_to_match) == 0:
                return subject

    answer = ""
    # levenshtein of entire subject name
    edit_distance = 2000
    for subject in subject_list:
        dist = levenshtein(subject, token_to_match)
        if dist < edit_distance:
            answer = subject
            edit_distance = dist

    return []


def extract_subject_name(string):
    return string.split(SUBJECT_CODE.findall(str(string))[0])[-1].strip()


def subject_title(string):
    string = str(string).lower()
    if "open elective" in string:
        string = string.replace("open elective", "")
    string = string.split(":")[0]
    string = drop_non_alphabets(string)
    return pascal_case(string)


def drop_non_alphabets(string):
    x, y = 0, len(string) - 1
    try:
        while string[x] not in atoz:
            x += 1
        while string[y] not in atoz:
            y -= 1
        return string[x:y+1]
    except Exception:
        return ""


# levenshtein("1234", "1234567")

