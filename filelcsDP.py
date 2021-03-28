import sys
import os
import time

# Reference DP Solution

if len(sys.argv) <= 2:
    print("Usage: python filelcs.py <file> <file> ... <file>")
    exit()

def get_lcs_offsets(f1_data, f2_data):
    """ f2 is the smaller file """
    f1_len, f1_name, f1_str = f1_data
    f2_len, f2_name, f2_str = f2_data
    matrix = [[0] * (f2_len+1), [0] * (f2_len+1)]
    maxlen = 0
    end_ind1 = 0
    end_ind2 = 0
    for i in range(1, f1_len+1):
        b1 = f1_str[i-1]
        # print(i)
        for j in range(1, f2_len+1):
            b2 = f2_str[j-1]
            if b1 == b2:
                num = matrix[(i-1)%2][j-1] + 1
                matrix[i%2][j] = num
                if num > maxlen:
                    maxlen = num
                    end_ind1 = i-1
                    end_ind2 = j-1
            else:
                matrix[i%2][j] = 0
    offset_1 = (f1_name, end_ind1 - (maxlen - 1))
    offset_2 = (f2_name, end_ind2 - (maxlen - 1))
    return maxlen, [min(offset_1, offset_2), max(offset_1, offset_2)]


start = time.time()

filenames = sys.argv[1:]

maxlen = 0
offsets = []
for i in range(len(filenames)-1):
    name1 = filenames[i]
    try:
        f1 = open(name1, "rb")
    except FileNotFoundError:
        print("ERROR: FILE '{}' DOES NOT EXIST.".format(name1))
        exit()
    f1_len = os.path.getsize(name1)
    f1_data = (f1_len, name1, f1.read())
    for j in range(i+1, len(filenames)):
        name2 = filenames[j]
        try:
            f2 = open(name2, "rb")
        except FileNotFoundError:
            print("ERROR: FILE '{}' DOES NOT EXIST.".format(name2))
        f2_len = os.path.getsize(name2)
        f2_data = (f2_len, name2, f2.read())
        comp_start = time.time()
        lcs_len, lcs_offset = get_lcs_offsets(max(f1_data, f2_data), min(f1_data, f2_data))
        comp_end = time.time()
        print(lcs_offset, lcs_len)
        print("Elapsed time for computation: {} seconds".format(comp_end - comp_start))
        print()
        if lcs_len > 0:
            if lcs_len > maxlen:
                maxlen = lcs_len
                offsets = lcs_offset
            elif lcs_len == maxlen and lcs_offset[0][0] == offsets[0][0]:
                offsets.append(lcs_offset[1])
        f2.close()
    f1.close()

print("Length of longest shared strand of bytes: {}".format(maxlen))
for off in offsets:
    print("File name: {}, Offset where sequence begins: {}".format(off[0], off[1]))

end = time.time()
print()
print("DP Computation: {} seconds".format(end - start))