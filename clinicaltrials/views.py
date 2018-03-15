"""
@author Daniel Wong
logic for most of the application
"""
from django.shortcuts import render, redirect
from django.http import Http404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views import generic
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from .forms import UserForm, DocumentForm, LoginForm
from django.utils.encoding import smart_str
from django.contrib import messages
from django.core.files.base import ContentFile

import simplecrypt
import hashlib
import os
import zipfile
import io
import re
from .models import clinicaltrial, file, block, User, adverseEvent 

def index(request):
    """
    home page to list all clinical trials
    """
    all_trials = clinicaltrial.objects.all()
    context = {'all_trials': all_trials }
    return render(request, 'clinicaltrials/index.html', context)

def detail(request, clinicaltrial_id):
    """
    specific page of a clinical trial
    """
    try:
        trial = clinicaltrial.objects.get(pk = clinicaltrial_id)
        # allFiles = file.objects.all(clinicaltrial = clinicaltrial_id) #why doesnt this work?
        allFiles = trial.file_set.all()
        blocks = request.user.block_set.order_by('index')
        # adverseEvents = trial.adverseEvents.split("|")
        # adverseEvents = trial.adverseEvent_set.all()
        adverseEvents = adverseEvent.objects.all() #HARD CODED, RETURN SET BELONGING TO TRIAL
    except:
        raise Http404("trial does not exist")
    return render(request, 'clinicaltrials/detail.html', {'trial': trial, 'allFiles': allFiles,'blocks': blocks, 'adverseEvents': adverseEvents})

class UserFormView(View):
    form_class = UserForm
    template_name = 'clinicaltrials/registration_form.html'
    #display blank form 
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form' : form})
        pass
    #process form data
    def post(self,request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit = False)
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()
            #return User objects if credentials are correct
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    #initiate the new user's ledger
                    genesis = block(owner=user, index=1, previousHash="null hash", hashString = hash(str.encode("genesis")))
                    genesis.save()
                    return redirect('clinicaltrial:index')
        return render(request, self.template_name, {'form' :form})

# Could write this like UserFormView.
# Written differently to serve as an example of more verbose form usage.
def userlogin(request): 
    if request.method == 'GET':
        return render(request, 'clinicaltrials/login.html')
    
    if request.method == 'POST':
        username = request.POST.get("name", "")
        input_password = request.POST.get("input_password", "") 
        user = authenticate(username=username, password=input_password)
        if user is not None:
            if user.is_active:
                login(request, user)                    
                # return redirect('clinicaltrial:index')
                return redirect("clinicaltrial:userhome")

        return render(request, 'clinicaltrials/login.html') 

def userlogout(request):
    logout(request)
    all_trials = clinicaltrial.objects.all()
    context = {'all_trials': all_trials }
    return render(request, 'clinicaltrials/index.html', context)
    
def userhome(request):
    if request.user.is_anonymous:
        return render(request, 'clinicaltrials/index.html', {'all_trials': clinicaltrial.objects.all() })
    ownedFiles = file.objects.all().filter(owner=request.user)
    blocks = request.user.block_set.order_by('index')
    validityMessage = validate(request.user)[1]
    # crossValidation = crossValidate(request.user)[1]
    context = {"ownedFiles" : ownedFiles, "blocks" : blocks, "validityMessage": validityMessage}
    return render(request, 'clinicaltrials/user_home.html', context)

def download(request, path, name):
    print("PPP", path)
    print("QQQQ", name)
    file_name = name
    path_to_file = path[path.index("media"):] #get the path of desired file, current directory: /Users/student/Desktop/ButteLab/clinicalnetwork
    response = HttpResponse(open(path_to_file, "rb"), content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name)
    response['X-Sendfile'] = smart_str(path_to_file)
    return response


def downloadMultiple(request):
    def getfilenames():
        rootDir = "media/" #"PATH" # add path of directory here
        fileSet = set()
        for dir_, _, files in os.walk(rootDir):
            for filename in files:
                fileSet.add(rootDir + filename)
        return list(fileSet)
    rootDir = ""
    filenames = []
    files= getfilenames()
    for names in files:
        filenames.append( rootDir+names)
    zip_subdir = "blockchain"
    zip_filename = "%s.zip" % zip_subdir
    # Open StringIO to grab in-memory ZIP contents
    s = io.BytesIO()
    # The zip compressor
    zf = zipfile.ZipFile(s, "w")
    for fpath in filenames:
        # Calculate path for file in zip
        fdir, fname = os.path.split(fpath)
        zip_path = os.path.join(zip_subdir, fname)
        # Add file, at correct path
        zf.write(fpath, zip_path)
    # Must close zip for all contents to be written
    zf.close()
    # Grab ZIP file from in-memory, make response with correct MIME-type
    resp = HttpResponse(s.getvalue(), content_type = "application/x-zip-compressed")
    # ..and correct content-disposition
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
    return resp

def decryptdownload(request, path):
    #path starts at root: /Users/student/Desktop/ButteLab/clinicalnetwork/media/{file}
    #current directory: /Users/student/Desktop/ButteLab/clinicalnetwork
    input_password = request.POST.get("decryptpassword","")
    file_name = path[path.index("media/") + 6:] 
    path_to_file = path[path.index("media"):] 
    try:
        with open(path_to_file, "rb") as f:
            decrypted = returnDecrypted(f.read(), input_password) #decrypted is a decoded string
        save_path = "media/"
        new_file_name = file_name.replace("_encrypted", "")
        path_to_new_file = os.path.join(save_path, new_file_name)         
        f = open(path_to_new_file, "wb")
        f.write(decrypted)
        f.close()
        response = HttpResponse(open(path_to_new_file, "rb"), content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(new_file_name)
        response['X-Sendfile'] = smart_str(path_to_new_file)
        os.remove(path_to_new_file) #remove decrypted file from database because we don't want to leave this exposed
        return response
    except: #return to same page, HARDCODED TO RETURN TO TRIAL 2
        messages.error(request, "incorrect password")        
        trial = clinicaltrial.objects.get(pk = 2)
        # return redirect("clinicaltrial:userhome")
        return redirect("clinicaltrial:detail", 2) #HARDCODED

def hash(fileBytes):
    """
    input bytes, output String
    """
    hash_object = hashlib.sha256(fileBytes)
    hex_dig = hash_object.hexdigest()
    return hex_dig

def returnEncrypted(fileBytes, password):
    """
    returns encoded bytes
    """
    encrypted = simplecrypt.encrypt(password, fileBytes)
    return encrypted 

def returnDecrypted(fileBytes, password):
    """
    returns decoded string
    """
    decrypted = simplecrypt.decrypt(password, fileBytes)#.decode('utf8') #perhaps return decoded bytes to generalize?
    return decrypted    

def addToEveryonesLedger(input_block, broadcaster):
    for person in User.objects.all():
        if person != broadcaster: #broadcaster already saved block
            lastBlock = person.block_set.order_by('index').last()
            #copy into new block, but with different owner
            newBlock = block(owner=person, index = input_block.index, fileReference=input_block.fileReference, previousHash = lastBlock.hashString, hashString=input_block.hashString, timeStamp=input_block.timeStamp)
            newBlock.save()

def versionControl(doc, hashString):
    """
    input doc is a form object, hashString is the hash string of the uploaded document 
    returns desired filename of uploaded file in adherence to version control
    method used in conjunction with model_form_upload
    check for tampering of file if it was already in blockchain (just need one conflict) 
    if so, return the name of the file of the appropriate version 
    """
    highestVersion = 0
    person = User.objects.get(username="admin")
    blocks = person.block_set.order_by('index')
    for b in blocks[1:]:
        print("QQQQ", doc.filename, b.fileReference.filename)
        extension = doc.filename[doc.filename.rfind("."):]
        #if uploaded matches original one 
        if doc.filename == b.fileReference.filename and hashString == b.fileReference.dataHash:
            highestVersion = 0 
            break
        #if uploaded doesn't match original, edge case for first mismatch
        if doc.filename == b.fileReference.filename and hashString != b.fileReference.dataHash and highestVersion == 0:
            highestVersion = 1
        regexp = re.compile('\(v([\d]+)\).[A-Za-z0-9]+$') #matches (v#).extension
        if regexp.search(b.fileReference.filename):
            versionNum = regexp.search(b.fileReference.filename).group(1)
            index = regexp.search(b.fileReference.filename).start() #index in block's file's name of match
            #update the highestVersion number if a current block's file's version is greater
            if doc.filename.replace(str(extension),"") == b.fileReference.filename[0:index-1] and hashString != b.fileReference.dataHash:
                highestVersion = max(highestVersion, int(versionNum))
            #old version matched, keep version number 
            elif doc.filename.replace(str(extension),"") == b.fileReference.filename[0:index-1] and hashString == b.fileReference.dataHash:
                highestVersion = int(versionNum) - 1
                break
    if highestVersion != 0:
        if extension != -1:
                return doc.filename.replace(extension,"") + " (v" + str(highestVersion + 1) + ")" + extension
        else:
            return " (v" + str(highestVersion + 1) + ")"
    else:
        return doc.filename


def model_form_upload(request):
    """
    original version with no file duplication
    method to handle file uploads
    iterates over each file and will hash its contents, 
    if encrypyted:
         this method hashes the encrypted bytes to determine the hash string
         _encrypted will be appended to the file's name before the extension
    the filename in the storage database will be saved as the name of the file that the user uploads
        if there is a duplicate in the database, django appends a random string to the name
    a block is then constructed and added to everyone's ledger 
    """
    files = request.FILES.getlist('data')
    if request.method == 'POST':
        for f in files:
            form = DocumentForm(request.POST, request.FILES)
            fileObject = f
            with f.open() as g:
                fileBytes = g.read()
                hashString = hash(fileBytes)
                if form.is_valid():
                    doc = form.save(commit=False)
                    doc.data = f #new addition for multifile
                    doc.filename = f.name #will default to whatever name the file has that the user uploads #filename = 'data'? 
                    #if encrypted is set to True, change the contents of the file to the encrypted bytes, also set hash of data to hash of encrypted bytes
                    if doc.encrypted:
                        byt = returnEncrypted(fileBytes, doc.password) #will return bytes
                        doc.dataHash = hash(byt)
                        extension = doc.filename.rfind(".")
                        #change filename before extension 
                        if extension != -1:
                            extension = doc.filename[extension:]
                            doc.filename = doc.filename.replace(extension,"") + "_encrypted" + extension 
                        else:
                            doc.filename = doc.filename + "_encrypted"
                        doc.data.save(doc.filename, ContentFile(byt))
                    else:
                        doc.dataHash = hashString
                    
                    doc.filename = versionControl(doc, hashString)

                    f.name = doc.filename #change filename stored in media
                                    # messages.error(request, "Error:" + doc.filename + " already exists in the blockchain and the contents of the data are in conflict. Either resolve the conflict or change the filename to avoid discrepancy.")
                                    # return render(request, 'clinicaltrials/model_form_upload.html', {'form': form})

                    doc.sender = request.user
                    doc.save() #if file already exists in media database, django will append "_{random 7 chars}" not an issue except for when distributing files for download, the name will be annoying, blockchain only records filenames of what the user uploads, not internal media storage
                    #add to own ledger
                    lastBlock = request.user.block_set.order_by('index').last()
                    b = block(owner=request.user, index = lastBlock.index + 1, fileReference=doc, previousHash=lastBlock.hashString, hashString = hash(str.encode(lastBlock.hashString + doc.dataHash)))
                    b.save()
                    #add new block to everyone's ledger
                    addToEveryonesLedger(b, request.user) 

                    if "CRF" in doc.filename:
                        updateAdverses(doc, f)

        # return redirect("clinicaltrial:userhome")
        return redirect("clinicaltrial:detail", 2) #HARDCODED


    if request.method == 'GET':
        form = DocumentForm(initial = {'encrypted': False, 'clinicaltrial': clinicaltrial.objects.get(pk=2)}) #default to prepopulate targeted clinical trial as second trial HARD CODED CHANGE LATER
        return render(request, 'clinicaltrials/model_form_upload.html', {'form': form})

def updateAdverses(doc, f):
    """
    input: form object doc, and django file object f
    method to update adverse events section in home page of trial
    constructs a new adverse event model instance if subject not included in current adverse event models
    else will append adverse events if they're not present
    """
    regexp = re.compile('SUB([\d]+)')
    subject = regexp.search(doc.filename).group(1)
    aes = extractAdverseEvents(f)
    subjects = [] #NOT MOST EFFICIENT WAY TO CHECK IF SUBJECT IN ADVERSE DATABASE - FIXME
    for ae in adverseEvent.objects.all():
        subjects.append(ae.subject)
    if subject not in subjects:
        newAE = adverseEvent(subject=subject, events=convertToString(aes))
        newAE.clinicaltrial = clinicaltrial.objects.get(pk=2) #HARD CODED
        newAE.save()
    else:
        ae = adverseEvent.objects.get(subject=subject)
        for event in aes:
            if event not in ae.events:
                ae.events += "|" + event
        ae.clinicaltrial = clinicaltrial.objects.get(pk=2) #HARD CODED
        ae.save()

def convertToString(l):
    """
    given a list of adverse events, returns them as a string seperated by a "|" delimeter
    """
    asString = ""
    for i in range(0,len(l)):
        if i == len(l) - 1:
            asString += str(l[i])
        else:
            asString += str(l[i]) + "|"
    return asString

def extractAdverseEvents(file):
    """
    given a django file object, will parse out the adverse events and return these as a list
    """
    adverseEvents = []
    file.open()
    beginParse = False
    for line in file.readlines():
        line = line.decode('utf-8')
        if "Adverse Reactions" in line:
            beginParse = True
            continue 
        if beginParse:
            # line=line.rstrip('\t')
            line=line.rstrip('\n')
            line = line[1:] #hackish to remove tabs, rstrip wasn't working...
            adverseEvents.append(line)
    return adverseEvents

def initAllGenesis():
    """
    lazy method to delete all blocks and files and generate new genesis blocks for each user, only meant to be used in development
    """
    blocks = block.objects.all()
    blocks.delete()
    for person in User.objects.all():
        genesis = block(owner=person, index=1, previousHash="null hash", hashString = hash(str.encode("genesis")))
        genesis.save()
    files = file.objects.all()
    files.delete()

def validate(user):
    """
    checks if user has a valid blockchain:
    rerun hash calculations in user's blockchain from beginning with current files in database and compare to user's ledger
    """
    passing = True
    blocks = user.block_set.order_by('index')
    if blocks.count() <= 1:
        print("Passed, this is a valid blockchain")
        return True, "Passed, this is a valid blockchain"
    if blocks.count() == 2:
        recomputedHash = hash(str.encode(blocks[0].hashString + hash(blocks[1].fileReference.data.read())))
        if recomputedHash == blocks[1].hashString:
            return True, "Passed, this is a valid blockchain" 
        return False, "Failed, block at index 2 has been falsified"    
    previousBlock = blocks[0]
    for b in blocks[1:]: #first block with file is blocks[1[]]
        recomputedHashCurrent = hash(b.fileReference.data.read())
        passing = (b.hashString == hash(str.encode(previousBlock.hashString + recomputedHashCurrent)))
        if not passing:
            print("Failed, invalid blockchain at block index " + str(b.index) + ", file: " + b.fileReference.filename)
            return False, "Failed, invalid blockchain at block index " + str(b.index) + ", file: " + b.fileReference.filename
        previousBlock = b
    print("Passed, this is a valid blockchain")
    # print("cross validate", crossValidate(user))
    return passing, "Passed, this is a valid blockchain"


def crossValidate(user):
    """
    validates a user's blockchain by comparing it to everyone else's, returns True, message if no conflicts
    else returns False, failure message
    """
    conflicts = []
    passing = True
    myBlocks = user.block_set.order_by('index')
    for person in User.objects.all():
        if person != user:
            blocks = person.block_set.order_by('index')
            previousMyBlock = myBlocks[0]
            previousOtherBlock = blocks[0]
            for i in range(1, len(blocks)):
                recomputedOther = hash(str.encode(previousOtherBlock.hashString + hash(blocks[i].fileReference.data.read())))
                recomputedSelf = hash(str.encode(previousMyBlock.hashString + hash(myBlocks[i].fileReference.data.read())))
                if recomputedOther != recomputedSelf:
                    passing = False
                    conflicts.append((person, blocks[i].index))
    if passing:
        return True, "Passed, there is no conflict with anyone in the network"
    failMessage = "Failed, there exists conflicts with "
    for i in range(0, len(conflicts)):
        failMessage += conflicts[i][0].username + " at block index: " + str(conflicts[i][1]) + " "
    return False, failMessage           

def replaceWithLongest(user):
    """
    replaces current user's blockchain with the longest one in the network, used when adding new nodes to the network
    """
    greatestLength = -1
    longestNode = user
    for person in User.objects.all():
        if person != user:
            if validate(person)[0]:
                # blockLength = person.block_set.order_by('index').last().index
                blockLength = person.block_set.all().count()
                if blockLength > greatestLength:
                    greatestLength = blockLength
                    longestNode = person

    #delete user's blockchain
    originalBlocks = user.block_set.all()
    originalBlocks.delete()

    #replace with longest valid chain
    for input_block in longestNode.block_set.order_by('index'):
        newBlock = block(owner=user, index = input_block.index, fileReference=input_block.fileReference, previousHash = input_block.hashString, hashString=input_block.hashString, timeStamp=input_block.timeStamp)
        newBlock.save()


def getConsensus():
    """
    get a universal blockchain that everyone agrees on???
    """
    return

def CRF(request):
    """
    form to process a manually entered CRF, saves the entry as a .txt file in database
    need to still implement processing this on the blockchain
    """
    if request.method == "GET":
        CRF_fields = ["subject_id", "race", "gender", "age_reported", "arm_accession", "assay_measurements", "adverse_events"] #don't put spaces in field names 
        context = {'CRF_fields': CRF_fields }
        return render(request, 'clinicaltrials/CRF.html', context)
    else:
        subject = request.POST.get("subject_id","")
        f = open("media/CRFexample" + subject + ".txt", "w")
        f.write("Subject: " + subject + '\n')
        hex_object = hashlib.sha256(subject.encode('utf-8'))
        hex_dig = hex_object.hexdigest()
        f.write("verification code: " + hex_dig[0:10] + '\n')

        f.write('\n' + "Meta Information" + '\n')
        for item in ["race", "gender", "age_reported", "arm_accession"]:
            f.write('\t' + item + ": " + request.POST.get(item, "") + '\n')
        f.write('\n' + "Assay Measurements"  + '\n')
        f.write('\t' + request.POST.get("assay_measurements", "") + '\n')
        f.write('\n' + "Adverse Events"  + '\n')
        adverse = request.POST.get("adverse_events", "")
        adverse = adverse.split(",")
        for item in adverse:
            f.write('\t' + item + '\n')
        f.close()
        # form = DocumentForm(initial = {'encrypted': False, 'clinicaltrial': clinicaltrial.objects.get(pk=2), 'data': f}) #default to prepopulate targeted clinical trial as second trial HARD CODED CHANGE LATER
        # request._mutable = True
        # request.method = 'POST'
        # return render(request, 'clinicaltrials/model_form_upload.html', {'form': form})
        return redirect("clinicaltrial:userhome")



#centralized vs decentralized storage:
# centralized:
    #only 1 physical version of uploaded document exists, each node ledger is a copy of central FDA's, all stored on one database
    #validation: check if file upload conflicts with central ledger owned by FDA, encrypted and backed up with each new upload
    #pros: easier to write and manage, more power and control to FDA
    #cons: security vulnerability with only one copy, but if backed up its ok

#decentralized (democracy) distributed database:
    #copy/duplicate uploaded file for each user's blockchain ledger
    #validation: check if file upload conflicts with other node's ledgers, take majority vote
        #if conflicts and passes then correct conflicted ledgers
        #if conflicts and fails then correct your own ledger and everyone else's you agreed with
    #pros: more like bitcoin, resistant to damage to single file, more like democracy in that everyone has a vote to accept/reject transaction instead of relying on FDA ledger to accept/reject
    #cons: more memory storage requirements (FDA has to maintain large database already, and each node has to maintain all files associated with trial on its own disk), also user has to install computer app to store and manage files locally


#for production:
# only keep local ledger -- can download json of database
# when upload/send file to someone else, update own local ledger 
# broadcast out potential transaction to all other nodes

# other nodes:
# when receiving transaction broadcast, check for file conflict with own ledger in network
#     if conflict broadcast out vote to reject transaction
#     if correct broadcast out vote to accept transaction
# take majority vote and update all ledgers accordingly (including global/FDA/regulator ledger), or reject original transaction



#

#======================================================================================



# def model_form_upload(request):
#     """
#     file duplication version
#     """
#     if request.method == 'POST':
#         #obtain hash string of the contents of the file here 
#         fileObject = request.FILES['data']
#         fileBytes = fileObject.read() #can only call read once on a file, else will return empty
#         print(".read() result", fileBytes)
#         hashString = hash(fileBytes)
#         print("hash String", hashString)
#         docName = request.FILES['data'].name
#         #check for tampering of file if it was already in blockchain (just need one conflict to be invalid right now)
#         for person in User.objects.all():
#             if not person.is_superuser:
#                 blocks = person.block_set.order_by('index')
#                 for b in blocks[1:]:
#                     if docName == b.fileReference.filename and hashString != b.fileReference.dataHash:
#                         messages.error(request, "Error:" + docName + " already exists in the blockchain and the contents of the data are in conflict. Either resolve the conflict or change the filename to avoid discrepancy.")
#                         return render(request, 'clinicaltrials/model_form_upload.html', {'form': DocumentForm(request.POST, request.FILES)})
        
#         for person in User.objects.all():    
#             form = DocumentForm(request.POST, request.FILES)
#             if form.is_valid():
#                 doc = form.save(commit=False)
#                 doc.filename = request.FILES['data'].name #will default to whatever name the file has that the user uploads #filename = 'data'? 
                
#                 #if encrypted is set to True, change the contents of the file to the encrypted bytes, also set hash of data to hash of encrypted bytes
#                 if doc.encrypted:
#                     byt = returnEncrypted(fileBytes, doc.password) #will return bytes
#                     doc.dataHash = hash(byt)
#                     doc.filename = request.FILES['data'].name.replace(".txt","") + "_encrypted.txt"
#                     doc.data.save(doc.filename, ContentFile(byt))
#                 else:
#                     # doc.filename = request.FILES['data'].name #will default to whatever name the file has that the user uploads #filename = 'data'? 
#                     doc.dataHash = hashString
#                 doc.sender = request.user
#                 # doc.dataHash = hashString
#                 doc.save() #if file already exists in media database, django will append "_{random 7 chars}"
#                            #not an issue except for when distributing files for download, the name will be annoying
#                            #blockchain only records filenames of what the user uploads, not internal media storage
#                 #add to own ledger
#                 lastBlock = person.block_set.order_by('index').last()
#                 b = block(owner=person, index = lastBlock.index + 1, fileReference=doc, previousHash=lastBlock.hashString, hashString = hash(str.encode(lastBlock.hashString + doc.dataHash)))
#                 b.save()
#                 #add new block to everyone's ledger
#                 # addToEveryonesLedger(b, request.user) 

#         # return render(request, 'clinicaltrials/index.html', {'all_trials': clinicaltrial.objects.all() })
#         return redirect("clinicaltrial:userhome")

    
#     else: #if request.method == 'GET':
#         #default to prepopulate targeted clinical trial as second trial HARD CODED CHANGE LATER
#         form = DocumentForm(initial = {'encrypted': False, 'clinicaltrial': clinicaltrial.objects.get(pk=2)})
#         return render(request, 'clinicaltrials/model_form_upload.html', {'form': form})






#check for tampering of file if it was already in blockchain
            # for f in file.objects.all():
            #     name = f.filename
            #     print("FILENAME", name)
            #     if doc.filename == name:
            #         if hashString != f.dataHash:
            #             messages.error(request, "Error:" + doc.filename + " already exists in the blockchain and the contents of the data are in conflict.")
            #             return render(request, 'clinicaltrials/model_form_upload.html', {'form': form})
            #            # raise forms.ValidationError('File exists in blockchain already, and uploaded data is in conflict.')
     


# <!-- {% for file in ownedFiles %}  original implementation before file duplication for each user 
#         <ul>
#             <h3> {{file.filename}} uploaded: {{file.uploadDate}} from: {{file.sender}} </h3> 
#             <a href="{% url 'clinicaltrial:download' file.data.path %}"> Download </a>
#             <br>
#         </ul>
#     {% endfor %} -->

