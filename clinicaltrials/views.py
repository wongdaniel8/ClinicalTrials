from django.shortcuts import render, redirect
from django.http import Http404
from django.http import HttpResponse
from django.template import loader
from django.views import generic
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from .forms import UserForm, DocumentForm, LoginForm
from django.utils.encoding import smart_str
from django.contrib import messages
import simplecrypt
from django.core.files.base import ContentFile
import hashlib
import os
from .models import clinicaltrial, file, block, User 

def index(request):

    # initAllGenesis()
    # validate(request.user)
    # replaceWithLongest(User.objects.all().get(username = "Genentech2"))


    all_trials = clinicaltrial.objects.all()
    context = {'all_trials': all_trials }
    return render(request, 'clinicaltrials/index.html', context)

def detail(request, clinicaltrial_id):
    try:
        trial = clinicaltrial.objects.get(pk = clinicaltrial_id)
        # allFiles = file.objects.all(clinicaltrial = clinicaltrial_id) #why doesnt this work?
        allFiles = trial.file_set.all()
    except:
        raise Http404("trial does not exist")
    return render(request, 'clinicaltrials/detail.html', {'trial': trial, 'allFiles': allFiles})

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

# class UserLoginView(View):
#     form_class = LoginForm
#     template_name = 'clinicaltrials/login.html'
#     #display blank form 
#     def get(self, request):
#         form = self.form_class(None)
#         return render(request, self.template_name, {'form' : form})
#         pass
#     #process form data
#     def post(self,request):
#         form = self.form_class(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']
#             #return User objects if credentials are correct
#             user = authenticate(username=username, password=password)
#             if user is not None:
#                 if user.is_active:
#                     login(request, user)
#                     return redirect("clinicaltrial:userhome")
#         # return render(request, 'clinicaltrials/login.html')
#         return render(request, self.template_name, {'form' :form})
        





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
    context = {"ownedFiles" : ownedFiles, "blocks" : blocks, "validityMessage": validityMessage}
    return render(request, 'clinicaltrials/user_home.html', context)

# def download(request, path, name):
#     print("PPP", path)
#     print("QQQQ", name)
#     file_name = name
#     path_to_file = path + "/" + file_name 

def download(request, path):
    print("PPP", path)
    file_name = path[path.index("media/") + 6:]#hacky - django appends random string to filename if a file already exists in media with the same name 
    path_to_file = path[path.index("media"):] #get the path of desired file, current directory: /Users/student/Desktop/ButteLab/clinicalnetwork
    
    response = HttpResponse(open(path_to_file, "rb"), content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name)
    response['X-Sendfile'] = smart_str(path_to_file)
    return response

def decryptdownload(request, path):
    #path starts at root: /Users/student/Desktop/ButteLab/clinicalnetwork/media/{file}
    #current directory: /Users/student/Desktop/ButteLab/clinicalnetwork
    print("DDDDD", os.getcwd())
    print("PPPP" ,path)
    input_password = request.POST.get("decryptpassword","")
    file_name = path[path.index("media/") + 6:] 
    path_to_file = path[path.index("media"):] 
    try:
        with open(path_to_file, "rb") as f:
            decrypted = returnDecrypted(f.read(), input_password) #decrypted is a decoded string
        save_path = "media/"
        new_file_name = file_name.replace(".txt","") + "_decrypted.txt"
        path_to_new_file = os.path.join(save_path, new_file_name)         
        f = open(path_to_new_file, "w")
        f.write(decrypted)
        f.close()
        response = HttpResponse(open(path_to_new_file, "rb"), content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(new_file_name)
        response['X-Sendfile'] = smart_str(path_to_new_file)
        return response
    except: #return to same page, HARDCODED TO RETURN TO TRIAL 2
        messages.error(request, "wrong passcode")        
        trial = clinicaltrial.objects.get(pk = 2)
        # return render(request, 'clinicaltrials/detail.html', {'trial': trial, 'allFiles': trial.file_set.all()})
        # return redirect("clinicaltrial:index")
        return redirect("clinicaltrial:userhome")



def hash(fileBytes):
    """
    input bytes, output String
    """
    hash_object = hashlib.sha256(fileBytes)
    hex_dig = hash_object.hexdigest()
    return hex_dig

def returnEncrypted(fileBytes, password):
    encrypted = simplecrypt.encrypt(password, fileBytes) #returns bytes
    return encrypted 

def returnDecrypted(fileBytes, password):
    decrypted = simplecrypt.decrypt(password, fileBytes).decode('utf8')
    return decrypted    


def addToEveryonesLedger(input_block, broadcaster):
    for person in User.objects.all():
        if person != broadcaster: #broadcaster already saved block
            lastBlock = person.block_set.order_by('index').last()
            #copy into new block, but with different owner
            newBlock = block(owner=person, index = input_block.index, fileReference=input_block.fileReference, previousHash = lastBlock.hashString, hashString=input_block.hashString, timeStamp=input_block.timeStamp)
            newBlock.save()

def model_form_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)

        #obtain hash string of the contents of the file here 
        fileObject = request.FILES['data']
        fileBytes = fileObject.read() #can only call read once on a file, else will return empty
        print(".read() result", fileBytes)
        hashString = hash(fileBytes)
        print("hash String", hashString)

        if form.is_valid():
            doc = form.save(commit=False)
            doc.filename = request.FILES['data'].name #will default to whatever name the file has that the user uploads #filename = 'data'? 
            
            #check for tampering of file if it was already in blockchain (just need one conflict to be invalid right now)
            for person in User.objects.all():
                if not person.is_superuser:
                    blocks = person.block_set.order_by('index')
                    for b in blocks[1:]:
                        print("BBBB", b.fileReference.filename, b.fileReference.data.read(), b.fileReference.dataHash)
                    for b in blocks[1:]:
                        if doc.filename == b.fileReference.filename and hashString != b.fileReference.dataHash:
                            messages.error(request, "Error:" + doc.filename + " already exists in the blockchain and the contents of the data are in conflict. Either resolve the conflict or change the filename to avoid discrepancy.")
                            return render(request, 'clinicaltrials/model_form_upload.html', {'form': form})
            
            #if encrypted is set to True, change the contents of the file to the encrypted bytes, also set hash of data to hash of encrypted bytes
            if doc.encrypted:
                byt = returnEncrypted(fileBytes, doc.password) #will return bytes
                doc.dataHash = hash(byt)
                doc.filename = request.FILES['data'].name.replace(".txt","") + "_encrypted.txt"
                doc.data.save(doc.filename, ContentFile(byt))
            else:
                # doc.filename = request.FILES['data'].name #will default to whatever name the file has that the user uploads #filename = 'data'? 
                doc.dataHash = hashString

            doc.sender = request.user
            # doc.dataHash = hashString
            doc.save() #if file already exists in media database, django will append "_{random 7 chars}"
                       #not an issue except for when distributing files for download, the name will be annoying
                       #blockchain only records filenames of what the user uploads, not internal media storage
            
            #add to own ledger
            lastBlock = request.user.block_set.order_by('index').last()
            b = block(owner=request.user, index = lastBlock.index + 1, fileReference=doc, previousHash=lastBlock.hashString, hashString = hash(str.encode(lastBlock.hashString + doc.dataHash)))
            b.save()

            #add new block to everyone's ledger
            addToEveryonesLedger(b, request.user) 

        # return render(request, 'clinicaltrials/index.html', {'all_trials': clinicaltrial.objects.all() })
        return redirect("clinicaltrial:userhome")

    
    else: #if request.method == 'GET':
        #default to prepopulate targeted clinical trial as second trial HARD CODED CHANGE LATER
        form = DocumentForm(initial = {'encrypted': False, 'clinicaltrial': clinicaltrial.objects.get(pk=2)})
        return render(request, 'clinicaltrials/model_form_upload.html', {'form': form})


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
    rerun hash calculations from beginning with current files in database and compare to user's ledger
    """
    # initAllGenesis()
    passing = True
    blocks = user.block_set.order_by('index')
    print(blocks.count())
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
        # print("BBBBBB", b.index, b.fileReference.filename)
        recomputedHashCurrent = hash(b.fileReference.data.read())
        passing = (b.hashString == hash(str.encode(previousBlock.hashString + recomputedHashCurrent)))
        if not passing:
            print("Failed, invalid blockchain at block index " + str(b.index) + ", file: " + b.fileReference.filename)
            return False, "Failed, invalid blockchain at block index " + str(b.index) + ", file: " + b.fileReference.filename
        previousBlock = b
    print("Passed, this is a valid blockchain")
    return passing, "Passed, this is a valid blockchain"

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

#check for tampering of file if it was already in blockchain
            # for f in file.objects.all():
            #     name = f.filename
            #     print("FILENAME", name)
            #     if doc.filename == name:
            #         if hashString != f.dataHash:
            #             messages.error(request, "Error:" + doc.filename + " already exists in the blockchain and the contents of the data are in conflict.")
            #             return render(request, 'clinicaltrials/model_form_upload.html', {'form': form})
            #            # raise forms.ValidationError('File exists in blockchain already, and uploaded data is in conflict.')
            




