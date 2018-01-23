import hashlib

def file_hash(filename):
    h = hashlib.sha256()
    # with open(filename, 'rb', buffering=0) as f:
    #     for b in iter(lambda : f.read(128*1024), b''):
    #         h.update(b)
    # print(h.hexdigest())
    # return h.hexdigest()

    file = open(filename , "r")
    print(file.read())


# def file_hash(filename):
#     with open(filename, 'rb') as f:
#         h1 = hashlib.sha256(f.read()).digest()
#         print(h1)
#         print(type(h1))
#         return h1


file_hash('clin.txt')
# file_hash('clin3.txt')
# file_hash('clin2.txt')

# file_hash('clin1pdf.pdf')
# file_hash('clin1pdf copy.pdf')
# file_hash('clin1pdfcopy.pdf')



# file_hash('DanielWong_BMI203_HW1.docx')
# file_hash('BMI203 copy.docx')

# import hashlib
# BLOCKSIZE = 65536
# hasher = hashlib.sha1()
# with open('anotherfile.txt', 'rb') as afile:
#     buf = afile.read(BLOCKSIZE)
#     while len(buf) > 0:
#         hasher.update(buf)
#         buf = afile.read(BLOCKSIZE)
# print(hasher.hexdigest())


