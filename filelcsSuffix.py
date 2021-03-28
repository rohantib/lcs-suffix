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

def naive_compute_lcp_arr(string, suffs):
    """ Brute force LCP computation for reference """
    lcp_arr = [0] * (len(suffs)-1)
    for i in range(len(lcp_arr)):
        ind1, ind2 = suffs[i], suffs[i+1]
        lcp = compute_lcp(string, ind1, ind2, 0)
        lcp_arr[i] = lcp
    return lcp_arr

def get_type(sentinels, index):
    """ Determines what file a given position in the string comes from using linear search"""
    # TODO: change to binary search
    for i in range(1, len(sentinels)):
        if sentinels[i] > index:
            return i - 1
        if sentinels[i] == index:
            # Should not call this function on a sentinel position
            raise Exception("Passed in sentinel pos?")
    # Should not reach here either
    raise Exception("index not in range?")

def get_offset(sentinels, file_ind, str_ind):
    """ Finds offset within file of a particular index """
    return str_ind - sentinels[file_ind] - 1


""" Process Input """

if len(sys.argv) <= 2:
    print("Usage: python filelcs.py <file> <file> ... <file>")
    exit()

filenames = sys.argv[1:]
string_nums = ()
sentinels = [0] * (len(filenames) + 1)
# Placeholder for "imaginary" sentinel at beginning of string
sentinels[0] = -1
# Sentinel will range from 0 - len(filenames)-1. In the case of the 10 sample files, sentinels will be 0-9
cur_sentinel = 0

# Read bytes in, inject separating sentinels starting from 0
for i in range(len(filenames)):
    name = filenames[i]
    try:
        with open(name, "rb") as f:
            # Convert all bytes of the file to integers in an int array, and shift them up according to the number of sentinels needed
            string_nums += tuple([i + len(filenames) for i in f.read()]) + (cur_sentinel,)
            sentinels[i+1] = len(string_nums) - 1
            cur_sentinel += 1
    except FileNotFoundError:
        print("ERROR: FILE '{}' DOES NOT EXIST.".format(name))
        exit()


""" Build Data Structures """

# start = time.time()
suffs, lcp = build_suffix_arr(string_nums)
# end = time.time()
# print("Suffix array + LCP construction took {} seconds".format(end - start))


""" Find LCS """

start = time.time()

longest = 0
lcp_ind = 0

for cur_pos in range(len(filenames), len(lcp)):
    if lcp[cur_pos] > longest and get_type(sentinels, suffs[cur_pos]) != get_type(sentinels, suffs[cur_pos+1]):
        longest = lcp[cur_pos]
        lcp_ind = cur_pos

if longest == 0:
    print("There is no common sequence of bytes in the given files.")
else:
    print("Length of longest shared strand of bytes: {}".format(longest))
    cur_type = get_type(sentinels, suffs[lcp_ind])
    files_checked = set([cur_type])
    offsets = [[filenames[cur_type], get_offset(sentinels, cur_type, suffs[lcp_ind])]]
    cur_lcp_ind = lcp_ind
    while cur_lcp_ind < len(lcp) and lcp[cur_lcp_ind] == longest and len(files_checked) < len(filenames):
        cur_type = get_type(sentinels, suffs[cur_lcp_ind+1])
        if cur_type not in files_checked:
            files_checked.add(cur_type)
            offsets.append([filenames[cur_type], get_offset(sentinels, cur_type, suffs[cur_lcp_ind+1])])
        cur_lcp_ind += 1

    # Print in lexicographic order of filenames
    offsets.sort()
    for off in offsets:
        print("File name: {}, Offset where sequence begins: {}".format(off[0], off[1]))


end = time.time()
print("LCS Computation: {}".format(end - start))





""" Old Code """

# def suffix_array_ManberMyers(str):
#     result = []
#     def sort_bucket(str, bucket, order=1):
#         d = defaultdict(list)
#         for i in bucket:
#             key = str[i:i+order]
#             d[key].append(i)
#         for k, v in sorted(d.items()):
#             if len(v) > 1:
#                 sort_bucket(str, v, order*2)
#             else:
#                 result.append(v[0])
#         return result
#     return sort_bucket(str, (i for i in range(len(str))))


# class Suffix:
#     def __init__(self):
#         self.index = -1
#         self.rank = [-1, -1]


# def build_suffix_arr_class(string):
#     length = len(string)

#     suffs = [Suffix() for _ in range(length)]
#     suff_cmp = lambda s: s.rank

#     for i in range(length):
#         suffs[i].index = i
#         suffs[i].rank[0] = string[i]
#         suffs[i].rank[1] = string[i+1] if i < length-1 else -1

#     suffs.sort(key=suff_cmp)

#     k = 4
#     inds = [0] * length
#     while k <= length:
#         curr_rank = 0
#         prev_rank = suffs[0].rank[0]
#         suffs[0].rank[0] = curr_rank
#         inds[suffs[0].index] = 0

#         for i in range(1, length):
#             if suffs[i].rank[0] == prev_rank and suffs[i].rank[1] == suffs[i-1].rank[1]:
#                 suffs[i].rank[0] = curr_rank
#             else:
#                 prev_rank = suffs[i].rank[0]
#                 curr_rank += 1
#                 suffs[i].rank[0] = curr_rank
#             inds[suffs[i].index] = i

#         for i in range(length):
#             next_ind = suffs[i].index + k//2
#             suffs[i].rank[1] = suffs[inds[next_ind]].rank[0] if next_ind < length else -1

#         suffs.sort(key=suff_cmp)
#         # print(suffs[-1].rank[0])
#         k *= 2

#     return [s.index for s in suffs]


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

#     suffs = [[0, 0, 0] for _ in range(length)]

#     for i in range(length):
#         suffs[i][2]= i
#         suffs[i][0] = string[i]
#         suffs[i][1] = string[i+1] if i < length-1 else -1

#     suffs = radix_sort_ranks(suffs)

#     k = 4
#     inds = [0] * length
#     while k <= length:
#         curr_rank = 0
#         prev_rank = suffs[0][0]
#         suffs[0][0] = curr_rank
#         inds[suffs[0][2]] = 0

#         for i in range(1, length):
#             if suffs[i][0] == prev_rank and suffs[i][1] == suffs[i-1][1]:
#                 suffs[i][0] = curr_rank
#             else:
#                 prev_rank = suffs[i][0]
#                 curr_rank += 1
#                 suffs[i][0] = curr_rank
#             inds[suffs[i][2]] = i

#         for i in range(length):
#             next_ind = suffs[i][2] + k//2
#             suffs[i][1] = suffs[inds[next_ind]][0] if next_ind < length else -1

#         suffs = radix_sort_ranks(suffs)
#         # print(suffs[-1][0])
#         k *= 2
        
#     return [s[2] for s in suffs]


# start = time.time()
# suff_arr1 = suffix_array_ManberMyers(string_nums)
# end = time.time()
# print("Method 1 with dict took {}".format(end - start))


# start = time.time()
# suff_arr2 = build_suffix_arr_class(string)
# end = time.time()
# print("Method 2 with class took {}".format(end - start))

# start = time.time()
# suff_arr3, lcp = build_suffix_arr(string_nums)
# end = time.time()
# print("Method 3 with 3-elem arr took {}".format(end - start))

# start = time.time()
# suff_arr4 = build_suffix_arr_radix(string)
# end = time.time()
# print("Method 4 with 3-elem arr radix sort took {}".format(end - start))

# start = time.time()
# suff_arr5 = sorted(range(len(string)), key=lambda i: string[i:])
# end = time.time()
# print("Method 5 with naive sort arr took {}".format(end - start))

# print("Method 1 == Method 2: {}".format(suff_arr1 == suff_arr2))
# print("Method 1 == Method 3: {}".format(suff_arr1 == suff_arr3))
# print("Method 3 == Method 4: {}".format(suff_arr3 == suff_arr4))
# print("Method 3 == Method 5: {}".format(suff_arr3 == suff_arr5))


# test_str = b"allflksdjffaksdljf;alsdkjfa;sldfasdfklhasldfhaslj;;ladsjlaks fjwioefpwoaeupsadkl;fajsopiwea;klsk;ljsdl;jksdfjla;lkjsda90344893045ifkjladf"
# suffs = build_suffix_arr(test_str)
# lcp1 = compute_lcp_arr(test_str, suffs) + [" "]
# lcp2 = brute_force_lcp_arr(test_str, suffs) + [" "]
# rank = compute_rank(suffs)
# print("lcp1 == lcp2: " + str(lcp1 == lcp2))
# for i in range(len(suffs)):
#     print(lcp1[i], lcp2[i], rank[i], suffs[i], test_str[suffs[i]:],)