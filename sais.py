""" SA-IS"""

BYTESIZE = 256

def naive_build_suff_arr(string):
    return sorted(range(len(string)+1), key=lambda i: string[i:])



def build_type_map(string):
    """ Returns boolean array for each index of string (including empty suffix) - True for if it is S-Type, False for L-Type """
    is_S_typemap = [False] * (len(string) + 1)

    is_S_typemap[-1] = True
    if len(string) == 0:
        return is_S_typemap
    
    for i in range(len(string)-2, -1, -1):
        if string[i] < string[i+1] or (string[i] == string[i+1] and is_S_typemap[i+1]):
            is_S_typemap[i] = True

    return is_S_typemap

def is_LMS(is_S_typemap, index):
    return index != 0 and is_S_typemap[index] and not is_S_typemap[index-1]


def print_type_LMS(string):
    print(string.decode("ascii"))
    is_S_typemap = build_type_map(string)
    for is_S in is_S_typemap:
        print("S" if is_S else "L", end="")
    print()
    for i in range(len(is_S_typemap)):
        if is_LMS(is_S_typemap, i):
            print("^", end="")
        else:
            print(" ", end="")
    print()

def is_equal_lms(string, is_S_typemap, indA, indB):
    """ Compare two LMS substrings to be exactly equal - assumes input is LMS index """
    if indA == len(string) or indB == len(string):
        return False

    pos = 0
    while True:
        a_is_LMS = is_LMS(is_S_typemap, indA + pos)
        b_is_LMS = is_LMS(is_S_typemap, indB + pos)
        
        # Reached the end of one LMS substring
        if a_is_LMS != b_is_LMS:
            return False

        # Characters are different
        if string[indA+pos] != string[indB+pos]:
            return False
        
        # Reached next LMS substring
        if pos > 0 and a_is_LMS and b_is_LMS:
            return True
        pos += 1

def calc_bucket_sizes(string, alphabet_size):
    sizes = [0] * alphabet_size
    for num in string:
        sizes[num] += 1
    return sizes

def calc_bucket_heads(bucket_sizes):
    heads = [0] * len(bucket_sizes)
    offset = 1
    for index, size in enumerate(bucket_sizes):
        heads[index] = offset
        offset += size
    return heads

def calc_bucket_tails(bucket_sizes):
    tails = [0] * len(bucket_sizes)
    offset = 0
    for index, size in enumerate(bucket_sizes):
        offset += size
        tails[index] = offset
    return tails

def print_suff_arr(arr, pos=None):
    print(" ".join("%02d" % each for each in arr))

    if pos is not None:
        print(" ".join(
                "^^" if each == pos else "  "
                for each in range(len(arr))
        ))

def build_suffix_arr_SAIS(string, alphabet_size):
    """ Build complete suffix array with SA-IS """
    is_S_typemap = build_type_map(string)
    bucket_sizes = calc_bucket_sizes(string, alphabet_size)

    approx_suff_arr = approx_LMS_sort(string, bucket_sizes, is_S_typemap)
    print()
    sort_L_type(string, approx_suff_arr, bucket_sizes, is_S_typemap)
    print()
    sort_S_type(string, approx_suff_arr, bucket_sizes, is_S_typemap)
    print()
    summ_str, summ_alph_size, summ_suff_indices = summarize_suff_arr(string, approx_suff_arr, is_S_typemap)
    print()
    summ_suff_arr = build_summ_suff_arr(summ_str, summ_alph_size)
    print()
    final_suff_arr = final_LMS_sort(string, bucket_sizes, is_S_typemap, summ_suff_arr, summ_suff_indices)
    print()
    sort_L_type(string, final_suff_arr, bucket_sizes, is_S_typemap)
    print()
    sort_S_type(string, final_suff_arr, bucket_sizes, is_S_typemap)
    print()

    return final_suff_arr

def approx_LMS_sort(string, bucket_sizes, is_S_typemap):
    """ Generate suffix array with LMS substrings approximately sorted by first characters """
    approx_suff_arr = [-1] * (len(string) + 1)
    # Empty string is lexicographically smallest
    approx_suff_arr[0] = len(string)
    print_suff_arr(approx_suff_arr)
    bucket_tails = calc_bucket_tails(bucket_sizes)

    # Bucket sort by first char - only LMS substrings
    for i in range(len(string)):
        if not is_LMS(is_S_typemap, i):
            continue
        
        char_num = string[i]
        approx_suff_arr[bucket_tails[char_num]] = i
        bucket_tails[char_num] -= 1

        print_suff_arr(approx_suff_arr)
    return approx_suff_arr

def sort_L_type(string, suff_arr, bucket_sizes, is_S_typemap):
    bucket_heads = calc_bucket_heads(bucket_sizes)

    for suff in suff_arr:
        L_suff = suff - 1
        if L_suff < 0 or is_S_typemap[L_suff]:
            continue
        
        char_num = string[L_suff]
        suff_arr[bucket_heads[char_num]] = L_suff
        bucket_heads[char_num] += 1

        print_suff_arr(suff_arr)

def sort_S_type(string, suff_arr, bucket_sizes, is_S_typemap):
    bucket_tails = calc_bucket_tails(bucket_sizes)

    for suff in reversed(suff_arr):
        L_suff = suff - 1
        if L_suff < 0 or not is_S_typemap[L_suff]:
            continue
        
        char_num = string[L_suff]
        suff_arr[bucket_tails[char_num]] = L_suff
        bucket_tails[char_num] -= 1

        print_suff_arr(suff_arr)

def summarize_suff_arr(string, approx_suff_arr, is_S_typemap):
    lms_names = [-1] * (len(string) + 1)
    cur_name = 0
    last_LMS_ind = None

    lms_names[len(string)] = cur_name
    last_LMS_ind = len(string)
    print_suff_arr(lms_names)

    for i in range(1, len(approx_suff_arr)):
        suff_ind = approx_suff_arr[i]
        if not is_LMS(is_S_typemap, suff_ind):
            continue
        if not is_equal_lms(string, is_S_typemap, last_LMS_ind, suff_ind):
            cur_name += 1
        # if last_LMS_ind < len(string) and string[suff_ind] != string[last_LMS_ind]:
        #     cur_name += 1
        last_LMS_ind = suff_ind
        lms_names[suff_ind] = cur_name
        print_suff_arr(lms_names)

    summ_suff_inds = []
    summ_str = []
    for ind, name in enumerate(lms_names):
        if name != -1:
            summ_suff_inds.append(ind)
            summ_str.append(name)

    summ_alph_size = cur_name + 1
    print()
    print_suff_arr(summ_str)
    print()
    print_suff_arr(summ_suff_inds)
    return summ_str, summ_alph_size, summ_suff_inds

def build_summ_suff_arr(summ_str, summ_alph_size):
    if summ_alph_size == len(summ_str):
        summ_suff_arr = [-1] * (len(summ_str) + 1)
        summ_suff_arr[0] = len(summ_str)
        for i in range(len(summ_str)):
            rank_num = summ_str[i]
            summ_suff_arr[rank_num+1] = i
    else:
        # Recursively make suffix array of new string
        summ_suff_arr = build_suffix_arr_SAIS(summ_str, summ_alph_size)
    return summ_suff_arr

def final_LMS_sort(string, bucket_sizes, is_S_typemap, summ_suff_arr, summ_suff_indices):
    suff_arr = [-1] * (len(string) + 1)
    suff_arr[0] = len(string)
    print_suff_arr(suff_arr)
    bucket_tails = calc_bucket_tails(bucket_sizes)

    for i in range(len(summ_suff_arr)-1, 1, -1):
        str_ind = summ_suff_indices[summ_suff_arr[i]]
        char_num = string[str_ind]
        suff_arr[bucket_tails[char_num]] = str_ind
        bucket_tails[char_num] -= 1
        print_suff_arr(suff_arr)

    return suff_arr




# string = b'rikki-tikki-tikka'
# print_type_LMS(string)
# t = build_type_map(string)
# print(is_equal_lms(string, t, 1, 13))

string = b"caabcaac"
# # bucket_sizes = calc_bucket_sizes(string, 256)
# # is_S_typemap = build_type_map(string)
print_type_LMS(string)
print()
# # print()
# # guess = approx_LMS_sort(string, bucket_sizes, is_S_typemap)
# # print()
# # sort_L_type(string, guess, bucket_sizes, is_S_typemap)
# # print()
# # sort_S_type(string, guess, bucket_sizes, is_S_typemap)
# # print()

# # str_summ, str_summ_alph, str_summ_offs = summarize_suff_arr(string, guess, is_S_typemap)
# # print()
# # print_suff_arr(str_summ)
# # print()
# # print_suff_arr(str_summ_offs)
# # print()

# # summ_suff_arr = build_summ_suff_arr(str_summ, str_summ_alph)
# # print_suff_arr(summ_suff_arr)
# # print()

suff_arr = build_suffix_arr_SAIS(string, 256)
print()
print_suff_arr(suff_arr)
print()

print_suff_arr(naive_build_suff_arr(string))

exit()