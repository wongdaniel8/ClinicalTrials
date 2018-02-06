import Crypto.Hash.MD5 as MD5
import Crypto.PublicKey.RSA as RSA
import Crypto.PublicKey.DSA as DSA
import Crypto.PublicKey.ElGamal as ElGamal
import Crypto.Util.number as CUN
import os

plaintext = 'The rain in Spain falls mainly on the Plain'


# Here is a hash of the message
hash = MD5.new(plaintext).digest()
print(repr(hash))
# '\xb1./J\xa883\x974\xa4\xac\x1e\x1b!\xc8\x11'

for alg in (RSA, DSA, ElGamal):
    # Generates a fresh public/private key pair
    key = alg.generate(384, os.urandom)

    if alg == DSA:
        K = CUN.getRandomNumber(128, os.urandom)
    elif alg == ElGamal:
        K = CUN.getPrime(128, os.urandom)
        while CUN.GCD(K, key.p - 1) != 1:
            print('K not relatively prime with {n}'.format(n=key.p - 1))
            K = CUN.getPrime(128, os.urandom)
        # print('GCD({K},{n})=1'.format(K=K,n=key.p-1))
    else:
        K = ''

    # You sign the hash
    signature = key.sign(hash, K)
    print(len(signature), alg.__name__)
    # (1, 'Crypto.PublicKey.RSA')
    # (2, 'Crypto.PublicKey.DSA')
    # (2, 'Crypto.PublicKey.ElGamal')

    # You share pubkey with Friend
    pubkey = key.publickey()

    # You send message (plaintext) and signature to Friend.
    # Friend knows how to compute hash.
    # Friend verifies the message came from you this way:
    assert pubkey.verify(hash, signature)

    # A different hash should not pass the test.
    assert not pubkey.verify(hash[:-1], signature)




#=====================================================================================
##simple encryption/decrytion of string/bytes with password

# import simplecrypt
# ciphertext = simplecrypt.encrypt('password', "clin.txt blah blah") #returns bytes
# print(str(ciphertext))
# try:
# 	plaintext = simplecrypt.decrypt('password', ciphertext).decode('utf8')
# 	print(plaintext)
# except:
# 	print("wrong pass")


# print(simplecrypt.decrypt('password', ).decode('utf8'))

#=====================================================================================


##encrypting/decrypting pdf files with password

import hashlib
from PyPDF2 import PdfFileReader, PdfFileWriter

def decrypt_pdf(input_path, output_path, password):
  with open(input_path, 'rb') as input_file, \
    open(output_path, 'wb') as output_file:
    reader = PdfFileReader(input_file)
    reader.decrypt(password)

    writer = PdfFileWriter()

    for i in range(reader.getNumPages()):
      writer.addPage(reader.getPage(i))

    writer.write(output_file)


def encrypt(inputfile, outputfile, userpass, ownerpass):
	import os
	import PyPDF2
	# path, filename = os.path.split(inputfile)
	# output_file = os.path.join(path, outputfile)

	output = PyPDF2.PdfFileWriter()

	input_stream = PyPDF2.PdfFileReader(open(inputfile, "rb"))

	for i in range(0, input_stream.getNumPages()):
	    output.addPage(input_stream.getPage(i))

	outputStream = open(outputfile, "wb")

	# Set user and owner password to pdf file
	output.encrypt(userpass, ownerpass, use_128bit=True)
	output.write(outputStream)
	outputStream.close()


# encrypt("clin1pdf.pdf", "encrypted.pdf", "password", "password")
# decrypt_pdf("encrypted.pdf", "decrypted.pdf", "password")


#=====================================================================================

##hashing readable files with open command


# def file_hash(filename):
#     h = hashlib.sha256()
#     with open(filename, 'rb', buffering=0) as f:
#         for b in iter(lambda : f.read(128*1024), b''):
#             h.update(b)
#     print(h.hexdigest())
#     return h.hexdigest()

#     # file = open(filename , "r")
    # print(file.read())


# def file_hash(filename):
#     with open(filename, 'rb') as f:
#         h1 = hashlib.sha256(f.read()).digest()
#         print(h1)
#         print(type(h1))
#         return h1


# file_hash('clin.txt')
# file_hash('clin3.txt')
# file_hash('clin2.txt')
# file_hash('clin1pdf.pdf')
# file_hash('clin1pdf copy.pdf')
# file_hash('clin1pdfcopy.pdf')
# file_hash('DanielWong_BMI203_HW1.docx')
# file_hash('BMI203 copy.docx')




