import sys
import time

""" Functions and algorithms """
def build_suffix_arr(string):
    """ Constructs and returns the suffix array and LCP array """
    length = len(string)

    # During computation, every suffix is represented by three numbers: the rank of its first half, the rank of its second half, and the index it corresponds to.
    # The index is irrelevant to sorting in construction of the suffix array, so it is at the end of the list so it naturally works with python's sort.
    suffs = [[0, 0, 0] for _ in range(length)]

    for i in range(length):
        suffs[i][2]= i
        suffs[i][0] = string[i]
        suffs[i][1] = string[i+1] if i < length-1 else -1

    suffs.sort()

    k = 2
    inds = [0] * length
    while k < length:
        curr_rank = 0
        prev_rank = suffs[0][0]
        suffs[0][0] = curr_rank
        inds[suffs[0][2]] = 0
        no_change = True

        for i in range(1, length):
            if suffs[i][0] == prev_rank and suffs[i][1] == suffs[i-1][1]:
                suffs[i][0] = curr_rank
                no_change = False
            else:
                prev_rank = suffs[i][0]
                curr_rank += 1
                suffs[i][0] = curr_rank
            inds[suffs[i][2]] = i

        for i in range(length):
            next_ind = suffs[i][2] + k
            suffs[i][1] = suffs[inds[next_ind]][0] if next_ind < length else -1

        if no_change:
            break
        suffs.sort()
        k *= 2

    suffs_arr = [s[2] for s in suffs]
    return suffs_arr, compute_lcp_arr(string, suffs_arr, inds)

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

# def naive_compute_lcp_arr(string, suffs):
#     """ Brute force LCP computation for reference """
#     lcp_arr = [0] * (len(suffs)-1)
#     for i in range(len(lcp_arr)):
#         ind1, ind2 = suffs[i], suffs[i+1]
#         lcp = compute_lcp(string, ind1, ind2, 0)
#         lcp_arr[i] = lcp
#     return lcp_arr

# def get_type(sentinels, index):
#     """ Determines what file a given position in the string comes from using linear search"""
#     # TODO: change to binary search
#     for i in range(1, len(sentinels)):
#         if sentinels[i] > index:
#             return i - 1
#         if sentinels[i] == index:
#             # Should not call this function on a sentinel position
#             raise Exception("Passed in sentinel pos?")
#     # Should not reach here either
#     raise Exception("index not in range?")

# def get_type(sentinels, index):
#     """ Determines what file a given position in the string comes from using linear search"""
#     if index < sentinels[0] or index > sentinels[-1]:
#         raise Exception("index not in range?")

#     low = 0
#     high = len(sentinels)-1
#     while low <= high:
#         mid = (low+high)//2
#         if sentinels[mid] == index:
#             # Should not call this function on a sentinel position
#             raise Exception("Passed in sentinel pos?")
#         elif sentinels[mid] < index:
#             low = mid+1
#         elif sentinels[mid] > index:
#             high = mid-1
#     return high

def get_type(ind_to_type, index):
    """ Determines what file a given position in the string comes from using linear search"""
    return ind_to_type[index]

def get_offset(sentinels, file_ind, str_ind):
    """ Finds offset within file of a particular index """
    return str_ind - sentinels[file_ind] - 1




""" SA-IS"""

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


""" Process Input """

# if len(sys.argv) <= 2:
#     print("Usage: python filelcs.py <file> <file> ... <file>")
#     exit()

# filenames = sys.argv[1:]
# string_nums = ()
# sentinels = [0] * (len(filenames) + 1)
# # Placeholder for "imaginary" sentinel at beginning of string
# sentinels[0] = -1
# # Sentinel will range from 0 - len(filenames)-1. In the case of the 10 sample files, sentinels will be 0-9
# cur_sentinel = 0

# start = time.time()
# # Read bytes in, inject separating sentinels starting from 0
# for i in range(len(filenames)):
#     name = filenames[i]
#     try:
#         with open(name, "rb") as f:
#             # Convert all bytes of the file to integers in an int array, and shift them up according to the number of sentinels needed
#             string_nums += tuple([i + len(filenames) for i in f.read()]) + (cur_sentinel,)
#             sentinels[i+1] = len(string_nums) - 1
#             cur_sentinel += 1
#     except FileNotFoundError:
#         print("ERROR: FILE '{}' DOES NOT EXIST.".format(name))
#         exit()

# end = time.time()
# print("Time to read in input: {} seconds".format(end-start))


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

start = time.time()
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

end = time.time()
print("Time to read in input: {} seconds".format(end-start))

""" Build Data Structures """

# start = time.time()
# suffs, lcp = build_suffix_arr(string_nums)
# end = time.time()
# print("Suffix array + LCP construction took {} seconds".format(end - start))

start = time.time()
# Remove the first element of the suffix array, corresponding to the empty suffix - may be unnecessary operation, but just in case - In order to accomplish this without doing so, add 1 to range below for lcp comp
suffs = build_suffix_arr_SAIS(string_nums, BYTESIZE+len(filenames))[1:]
lcp = compute_lcp_arr(string_nums, suffs)
end = time.time()
print("Suffix array SAIS construction took {} seconds".format(end - start))

# print("suffs == suffsSAIS: {}".format(suffs == suffsSAIS))

""" Find LCS """
# start = time.time()

# longest = 0
# lcp_ind = 0

# for cur_pos in range(len(filenames), len(lcp)):
#     if lcp[cur_pos] > longest and get_type(sentinels, suffs[cur_pos]) != get_type(sentinels, suffs[cur_pos+1]):
#         longest = lcp[cur_pos]
#         lcp_ind = cur_pos

# if longest == 0:
#     print("There is no common sequence of bytes in the given files.")
# else:
#     print("Length of longest shared strand of bytes: {}".format(longest))
#     cur_type = get_type(sentinels, suffs[lcp_ind])
#     files_checked = set([cur_type])
#     offsets = [[filenames[cur_type], get_offset(sentinels, cur_type, suffs[lcp_ind])]]
#     cur_lcp_ind = lcp_ind
#     while cur_lcp_ind < len(lcp) and lcp[cur_lcp_ind] == longest and len(files_checked) < len(filenames):
#         cur_type = get_type(sentinels, suffs[cur_lcp_ind+1])
#         if cur_type not in files_checked:
#             files_checked.add(cur_type)
#             offsets.append([filenames[cur_type], get_offset(sentinels, cur_type, suffs[cur_lcp_ind+1])])
#         cur_lcp_ind += 1

#     for off in offsets:
#         print("File name: {}, Offset where sequence begins: {}".format(off[0], off[1]))


# end = time.time()
# print("LCS Computation: {} seconds".format(end - start))



start = time.time()

longest = 0
lcp_ind = 0

for cur_pos in range(len(filenames), len(lcp)):
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


end = time.time()
print("LCS Computation: {} seconds".format(end - start))







# # Attempt at utilizing radix sort

# def counting_sort_ranks(arr, sort_ind):
#     largest = max(arr, key=lambda e: e[sort_ind])
#     counts = [0] * (largest[sort_ind] + 1)
#     out = [None] * len(arr)
#     for elem in arr:
#         counts[elem[sort_ind]] += 1
#     # Make cumulative
#     for i in range(1, len(counts)):
#         counts[i] += counts[i-1]
#     # Construct output
#     for elem in reversed(arr):
#         counts[elem[sort_ind]] -= 1
#         out[counts[elem[sort_ind]]] = elem
    
#     return out

# def radix_sort_ranks(arr):
#     arr = counting_sort_ranks(arr, 1)
#     # print(arr)
#     arr = counting_sort_ranks(arr, 0)
#     # print(arr)
#     return arr

# def build_suffix_arr_radix(string):
#     length = len(string)

#     # During computation, every suffix is represented by three numbers: the rank of its first half, the rank of its second half, and the index it corresponds to.
#     # The index is irrelevant to sorting in construction of the suffix array, so it is at the end of the list so it naturally works with python's sort.
#     suffs = [[0, 0, 0] for _ in range(length)]

#     for i in range(length):
#         suffs[i][2]= i
#         # Shift numbers up by 1 so that indicator for end of suffix can be 0
#         suffs[i][0] = string[i]+1
#         suffs[i][1] = string[i+1]+1 if i < length-1 else 0

#     suffs = radix_sort_ranks(suffs)

#     k = 2
#     inds = [0] * length
#     while k < length:
#         curr_rank = 0
#         prev_rank = suffs[0][0]
#         suffs[0][0] = curr_rank
#         inds[suffs[0][2]] = 0
#         no_change = True

#         for i in range(1, length):
#             if suffs[i][0] == prev_rank and suffs[i][1] == suffs[i-1][1]:
#                 suffs[i][0] = curr_rank
#                 no_change = False
#             else:
#                 prev_rank = suffs[i][0]
#                 curr_rank += 1
#                 suffs[i][0] = curr_rank
#             inds[suffs[i][2]] = i

#         for i in range(length):
#             next_ind = suffs[i][2] + k
#             suffs[i][1] = suffs[inds[next_ind]][0] if next_ind < length else 0

#         if no_change:
#             break
#         suffs = radix_sort_ranks(suffs)
#         k *= 2

#     suffs_arr = [s[2] for s in suffs]
#     return suffs_arr, compute_lcp_arr(string, suffs_arr, inds)



# import random
# test = []
# for _ in range(100000):
#     test.append([random.randint(0, 10000), random.randint(0, 10000)])


# print("Normal start:")
# start = time.time()
# normal = sorted(test)
# end = time.time()
# print("Normal sort: {} seconds".format(end-start))

# print()
# print("Radix start:")
# start = time.time()
# rad = radix_sort_ranks(test)
# end = time.time()
# print("Radix sort: {} seconds".format(end-start))

# print("Normal == Radix: {}".format(normal == rad))