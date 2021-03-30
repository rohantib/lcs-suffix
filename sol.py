import sys
# import time


""" Suffix array construction with SA-IS - O(n) - inspired from zork.net """

BYTESIZE = 256

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

def build_suffix_arr_SAIS(string, alphabet_size):
    """ Build complete suffix array with SA-IS """
    is_S_typemap = build_type_map(string)
    bucket_sizes = calc_bucket_sizes(string, alphabet_size)

    approx_suff_arr = approx_LMS_sort(string, bucket_sizes, is_S_typemap)
    sort_L_type(string, approx_suff_arr, bucket_sizes, is_S_typemap)
    sort_S_type(string, approx_suff_arr, bucket_sizes, is_S_typemap)

    summ_str, summ_alph_size, summ_suff_indices = summarize_suff_arr(string, approx_suff_arr, is_S_typemap)
    summ_suff_arr = build_summ_suff_arr(summ_str, summ_alph_size)

    final_suff_arr = final_LMS_sort(string, bucket_sizes, is_S_typemap, summ_suff_arr, summ_suff_indices)
    sort_L_type(string, final_suff_arr, bucket_sizes, is_S_typemap)
    sort_S_type(string, final_suff_arr, bucket_sizes, is_S_typemap)

    return final_suff_arr

def approx_LMS_sort(string, bucket_sizes, is_S_typemap):
    """ Generate suffix array with LMS substrings approximately sorted by first characters """
    approx_suff_arr = [-1] * (len(string) + 1)
    # Empty string is lexicographically smallest
    approx_suff_arr[0] = len(string)
    bucket_tails = calc_bucket_tails(bucket_sizes)

    # Bucket sort by first char - only LMS substrings
    for i in range(len(string)):
        if not is_LMS(is_S_typemap, i):
            continue
        
        char_num = string[i]
        approx_suff_arr[bucket_tails[char_num]] = i
        bucket_tails[char_num] -= 1

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


def sort_S_type(string, suff_arr, bucket_sizes, is_S_typemap):
    bucket_tails = calc_bucket_tails(bucket_sizes)

    for suff in reversed(suff_arr):
        L_suff = suff - 1
        if L_suff < 0 or not is_S_typemap[L_suff]:
            continue
        
        char_num = string[L_suff]
        suff_arr[bucket_tails[char_num]] = L_suff
        bucket_tails[char_num] -= 1


def summarize_suff_arr(string, approx_suff_arr, is_S_typemap):
    lms_names = [-1] * (len(string) + 1)
    cur_name = 0
    last_LMS_ind = None

    lms_names[len(string)] = cur_name
    last_LMS_ind = len(string)

    for i in range(1, len(approx_suff_arr)):
        suff_ind = approx_suff_arr[i]
        if not is_LMS(is_S_typemap, suff_ind):
            continue
        if not is_equal_lms(string, is_S_typemap, last_LMS_ind, suff_ind):
            cur_name += 1
        last_LMS_ind = suff_ind
        lms_names[suff_ind] = cur_name

    summ_suff_inds = []
    summ_str = []
    for ind, name in enumerate(lms_names):
        if name != -1:
            summ_suff_inds.append(ind)
            summ_str.append(name)

    summ_alph_size = cur_name + 1
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
    bucket_tails = calc_bucket_tails(bucket_sizes)

    for i in range(len(summ_suff_arr)-1, 1, -1):
        str_ind = summ_suff_indices[summ_suff_arr[i]]
        char_num = string[str_ind]
        suff_arr[bucket_tails[char_num]] = str_ind
        bucket_tails[char_num] -= 1

    return suff_arr



""" LCP construction with Kasai's algorithm - O(n) """

def compute_lcp_arr(string, suffs, rank=None):
    """ Constructs the LCP array """
    if rank == None:
        rank = compute_rank(suffs)
    lcp_arr = [0] * (len(suffs)-1)
    last_lcp = 0
    for i in range(len(rank)):
        # Skip computation if rank[i] corresponds to last element in suffix array
        if (rank[i] == len(lcp_arr)):
            continue
        next_lcp = compute_lcp(string, suffs[rank[i]], suffs[rank[i] + 1], max(0, last_lcp-1))
        last_lcp = next_lcp
        lcp_arr[rank[i]] = next_lcp
    return lcp_arr

def compute_lcp(string, suff1, suff2, start):
    """ Computes the LCP of two given suffixes """
    assert start >= 0
    lcp = start
    s1 = min(suff1, suff2)
    s2 = max(suff1, suff2)
    s1 += start
    s2 += start
    while s2 < len(string) and string[s1] == string[s2]:
        lcp += 1
        s1 += 1
        s2  += 1
    return lcp
    
def compute_rank(suffs):
    """ Computes rank array (inverse of suffix array) - Not needed in current implementation """
    rank = [0] * len(suffs)
    for i in range(len(suffs)):
        rank[suffs[i]] = i
    return rank


""" Misc. functions to help compute LCS """

def get_type(ind_to_type, index):
    """ Determines what file a given position in the string comes from using linear search"""
    return ind_to_type[index]

def get_offset(sentinels, file_ind, str_ind):
    """ Finds offset within file of a particular index """
    return str_ind - sentinels[file_ind] - 1


""" Process Input """

if len(sys.argv) <= 2:
    print("Usage: python filelcs.py <file> <file> ... <file>")
    exit()

filenames = sys.argv[1:]
string_nums = ()
ind_to_type = []
sentinels = [0] * (len(filenames) + 1)
# # Placeholder for "imaginary" sentinel at beginning of string
sentinels[0] = -1
# Sentinel will range from 0 - len(filenames)-1. In the case of the 10 sample files, sentinels will be 0-9
cur_sentinel = 0

# Read bytes in, inject separating sentinels starting from 0
for i in range(len(filenames)):
    name = filenames[i]
    try:
        with open(name, "rb") as f:
            # Convert all bytes of the file to integers in an int array, and shift them up according to the number of sentinels needed
            string = f.read()
            string_nums += tuple([i + len(filenames) for i in string]) + (cur_sentinel,)
            sentinels[i+1] = len(string_nums) - 1
            ind_to_type.extend([cur_sentinel] * (len(string)+1))
            cur_sentinel += 1
    except FileNotFoundError:
        print("ERROR: FILE '{}' DOES NOT EXIST.".format(name))
        exit()

# Check that final sentinel is len(filenames) and all sentinels were used
assert string_nums[-1] == len(filenames)-1
assert cur_sentinel == len(filenames)

""" Build Data Structures """

# start = time.time()
suffs = build_suffix_arr_SAIS(string_nums, BYTESIZE+len(filenames))
lcp = compute_lcp_arr(string_nums, suffs)
# end = time.time()
# print("Suffix array SAIS construction took {} seconds".format(end - start))


""" Find LCS """

# start = time.time()

longest = 0
lcp_ind = 0

# Start from len(filenames) + 1 to include the inserted sentinels + the empty substring suffix created by the generic SA-IS implementation
for cur_pos in range(len(filenames)+1, len(lcp)):
    if lcp[cur_pos] > longest and get_type(ind_to_type, suffs[cur_pos]) != get_type(ind_to_type, suffs[cur_pos+1]):
        longest = lcp[cur_pos]
        lcp_ind = cur_pos

if longest == 0:
    print("There is no common sequence of bytes in the given files.")
else:
    print("Length of longest shared strand of bytes: {}".format(longest))
    cur_type = get_type(ind_to_type, suffs[lcp_ind])
    files_checked = set([cur_type])
    offsets = [[filenames[cur_type], get_offset(sentinels, cur_type, suffs[lcp_ind])]]
    cur_lcp_ind = lcp_ind
    while cur_lcp_ind < len(lcp) and lcp[cur_lcp_ind] == longest and len(files_checked) < len(filenames):
        cur_type = get_type(ind_to_type, suffs[cur_lcp_ind+1])
        if cur_type not in files_checked:
            files_checked.add(cur_type)
            offsets.append([filenames[cur_type], get_offset(sentinels, cur_type, suffs[cur_lcp_ind+1])])
        cur_lcp_ind += 1

    for off in offsets:
        print("File name: {}, Offset where sequence begins: {}".format(off[0], off[1]))


# end = time.time()
# print("LCS Computation: {} seconds".format(end - start))


