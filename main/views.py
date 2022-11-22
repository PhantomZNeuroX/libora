import email
from django.http import HttpResponse
from django.shortcuts import render,redirect
from ebooklib import epub
import ebooklib
import os
from django.contrib.auth.models import User
from .models import clas, teacher, profile, ebook, reading_day, ReadBook
from django.contrib.auth import login,logout
from ipware import get_client_ip
import geocoder
import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import datetime


volumes = 'https://www.googleapis.com/books/v1/volumes'
book_key = 'AIzaSyDKQ51Yqk5pb7gTjdLoa5M5rzTGe6ZMBDo'

def landing(request):
    return HttpResponse('Landing Page')

def register(request):
    if request.method == 'POST':
        post = request.POST
        if post['fname'] or post['lname'] or post['email'] or post['pass1'] or post['pass2'] == None:
        #    return render(request,'Register Land.html', {"msg":"Please fill in all the fields"})
            print('tf')
            
        if not User.objects.filter(email=post['email']):
            if post['pass1'] == post['pass2']:
                user = User.objects.create_user(username=post['email'], first_name=post['fname'], email=post['email'], last_name=post['lname'], password=post['pass1'])
                prof = profile.objects.create(user=user)
                return redirect('/login')
            else:
                return render(request,'Register Land.html', {"msg":"Passwords do not match"})
        else:
            return render(request,'Register Land.html', {"msg":"An account with this email already exits"})
    else:
        return render(request,'Register Land.html', {"msg":""})

def registerT(request):
    if request.method == 'POST':
        post = request.POST
        if not User.objects.filter(email=post['email']):
            if post['pass1'] == post['pass2']:
                user = User.objects.create_user(username=post['email'], first_name=post['fname'], email=post['email'], last_name=post['lname'], password=post['pass1'])
                teach = teacher.objects.create(user=user,school=post['school'],subject=post['sub'] )
                clas.objects.create(teacher=teach, name=teacher.user.first_name + "'s Class")
                return redirect('/login')
            else:
                return render(request,'Register Land.html', {"msg":"Passwords do not match"})
        else:
            return render(request,'Register Land.html', {"msg":"An account with this email already exits"})
    return render(request, 'registerT.html')

def JoinClass(request):
    if request.method == 'POST':
        post = request.POST
        user = User.objects.get(email=request.user.email)
        join = clas.objects.get(code=post['code'])
        join.students.add(user)
        prof = profile.objects.get(user=user)
        prof.clas = join
        prof.save()
        print(join.students.all())
        return redirect('/')
    else:
        if not request.user.is_authenticated:
            return redirect('/login')
        return render(request,'JoinClass.html')

def loginn(request):
    if request.user.is_authenticated:
            return redirect('/dashboard')
    if request.method == 'POST':
        post = request.POST
        if User.objects.filter(email=post['email']):
            user = User.objects.get(email=post['email'])
            if user.check_password(post['pass']):
                client_ip, is_routable = get_client_ip(request)
                print(client_ip)
                ip = geocoder.ip(client_ip)
                print(ip.city)
                if ip.city == None:
                    loca = 'localhost'
                else:
                    loca = ip.city
                try:
                    prof = profile.objects.get(user=user)
                    prof.location = loca
                    prof.save()
                except:
                    pass
                login(request=request, user=user)
                return redirect('/dashboard')
            else:
                return render(request, 'login.html', {"msg":"Password is incorect"})
        else:
            return render(request, 'login.html', {"msg":"This user dosent exist"})
    return render(request, 'login.html', {"msg":""})

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    user = User.objects.get(id=request.user.id)
    if teacher.objects.filter(user=user):
        return redirect('/dashboard/teacher')
    prof = profile.objects.get(user=user)
    classs = prof.clas
    print(classs)
    try:
        goal = classs.goal
    except:
        pass
    try:
        readDay=reading_day.objects.get(user=user, date=datetime.date.today())
        read = readDay.words
        print(read)
    except:
        read = 0

    percent = round((read/goal)*100,2)
    deg = (read/goal)*180
    if read>goal:
        deg = 180
    print(deg, percent)
    booooks = ebook.objects.filter(clas=classs).order_by('deadline')
    filtered = []
    for x in booooks:
        if ReadBook.objects.filter(user=user,book=x):
            readbo = ReadBook.objects.get(user=user,book=x)
            print(readbo.completed)
            if not readbo.completed:
                filtered.append(x)
        else:
            filtered.append(x)
    print(filtered)
    
    
    return render(request, 'dashboard.html', {'books':filtered[:4], 'deg': deg, 'percent':percent, 'read':read, 'words':prof.words})

def dashboardT(request):
    if not request.user.is_authenticated:
        return redirect('/login')    
    user = User.objects.get(id=request.user.id)
    if not teacher.objects.filter(user=user):
        return redirect('/dashboard')
    teach = teacher.objects.get(user=user)
    clas = teach.clas
    books = ebook.objects.filter(clas=clas)
    lead = profile.objects.filter(clas=clas).order_by('-score')
    profs = profile.objects.filter(clas=clas).order_by('user')
    
    return render(request,'dashboardt.html',{'class':clas,'books':books, 'lead':lead,'profs':profs, 'goal':clas.goal})

    
def MyClass(request):
    if not request.user.is_authenticated:
        return redirect('/login')

def logoutt(request):
    logout(request)
    return redirect('/')

def profiles(request, id):
    if User.objects.filter(id = id):
        user = User.objects.get(id=id)
        prof = profile.objects.get(user=user)
        return render(request, 'profile.html', {'user':user, "profile": prof})
    else:
        return HttpResponse('404 Not Found')
'''
def bookView(request,id):
    book = requests.get(url=volumes + '/' + id, params={'key':book_key}).json()
    try: 
        print(book,book['volumeInfo']['title'])
        return render(request, 'book.html', {'title':book['volumeInfo']['title'],'author':book['volumeInfo']['authors'][0],'desc':book['volumeInfo']['description'],'img':book['volumeInfo']['imageLinks']['thumbnail']})
    except:
        return HttpResponse('404 NOT FOUND')
'''
def search(request,q):
    book = requests.get(url=volumes, params={'key':book_key,'q':q}).json()
    
    print(book['items'][0])
    return render(request, 'searchResults.html',{'query':q,'items':book['items']})

def chap2text(chap):
    blacklist = [   '[document]',   'noscript', 'header',   'html', 'meta', 'head','input', 'script',   ]
    output = ''
    soup = BeautifulSoup(chap, 'html.parser')
    text = soup.find_all(text=True)
    for t in text:
        if t.parent.name not in blacklist:
            output += '{} '.format(t)
    return output

def thtml2ttext(thtml):
    Output = []
    for html in thtml:
        text =  chap2text(html)
        Output.append(text)
    return Output

def epub2text(epub_path):
    chapters = epub_path
    ttext = thtml2ttext(chapters)
    return ttext

def sendBook(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    user = User.objects.get(id=request.user.id)
    if not teacher.objects.filter(user=user):
        return redirect('/dashboard')
    if request.method == 'POST':
        teach = teacher.objects.get(user=user)
        classs = clas.objects.get(teacher=teach)
        post = request.POST
        try:
            cover = request.FILES['cover']
            print(cover.name,cover.content_type)
            if cover.content_type != 'image/jpeg':
                return HttpResponse('Incorrect Epub Cover Format')    
        except:
            pass
        ebok = request.FILES['ebook']
        print(ebok.name,cover.content_type)
        if ebok.content_type != 'application/epub+zip':
            return HttpResponse('Incorrect File Format')    
        bok = ebook.objects.create(name=post['name'],deadline=post['deadline'],book=ebok, clas=classs, cover=cover, description = post['desc'])
        media_url = settings.MEDIA_ROOT
        book = epub.read_epub(os.path.join(media_url,bok.book.name))
        chapters = []
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                chapters.append(item.get_content())
        allText = epub2text(chapters)
        allstring = ''
        for ele in allText:
            allstring += ele
        words = len(allstring.replace("\n", '').split())
        bok.words = words
        bok.save()
        return redirect('/dashboard')
    else:
        return render(request,'sendBook.html')

def bookPage(request,id):
    if not request.user.is_authenticated:
        return redirect('/login')
    user = User.objects.get(id=request.user.id)
    bok = ebook.objects.get(id=id)
    classs = bok.clas
    if request.method == 'POST':
        try:
            if request.POST['Completed'] == 'Completed':
                print('com\n\n\n\n')
                reado = ReadBook.objects.get(user=user,book=bok)
                reado.completed = True
                reado.finished = datetime.date.today()
                reado.save()
                return redirect('/dashboard')
        except:
            pass


    comp = ReadBook.objects.filter(book=bok,completed=True)
    comp_user= []
    for x in comp:
        comp_user.append(x.user)
    all_stud = classs.students.all()
    not_comp = [i for i in all_stud if i not in comp_user]
    percen = round((len(comp)/len(all_stud))*100,2)
    try:
        readBo  = ReadBook.objects.get(user=user, book=bok)
        print(readBo.completed)
        if (bok.words*0.77 > readBo.words or readBo.completed):
            print('0')
            if readBo.completed == True:
                print('3')
                return render(request, 'Abook.html', {'book':bok, 'students':comp, 'no_students':not_comp, 'percent':percen, 'completed':3})    
            return render(request, 'Abook.html', {'book':bok, 'students':comp, 'no_students':not_comp, 'percent':percen, 'completed':0})
        return render(request, 'Abook.html', {'book':bok, 'students':comp, 'no_students':not_comp, 'percent':percen, 'completed':1})
    except:
        return render(request, 'Abook.html', {'book':bok, 'students':comp, 'no_students':not_comp, 'percent':percen, 'completed':0})
    
    

def book(request,id):
    if not request.user.is_authenticated:
        return redirect('/login')
    if request.method != 'GET':
        return redirect('/dashboard')
    user = User.objects.get(id=request.user.id)
    try:
        bok = ebook.objects.get(id=id)
    except:
        return HttpResponse('404 Not Found')
    prof = profile.objects.get(user=user)

    print(prof.clas,bok.clas)

    if prof.clas != bok.clas:
        return HttpResponse('404 Not Found')
    bookurl = 'http://localhost:8000/media/'+ bok.book.name
    print(bookurl)
    return render(request, 'Epub.html', {'book':bok.id,'user':user.id, 'bookurl':bookurl})

@csrf_exempt
def progress(request):
    if request.method == 'POST':
        post = request.POST
        #print(post)
        user = User.objects.get(id=post['user'])
        bok = ebook.objects.get(id=post['book'])
        prof = profile.objects.get(user = user)
        newWords = len(post['words'].split())
        newTime = int(post['time'])/1000
        print(newWords, newTime, newWords/newTime)
        print(prof.words)
        prof.words = newWords + prof.words
        prof.time = newTime + int(prof.time)
        prof.score= prof.words/prof.time
        prof.save()
        prof.score=round(prof.score,2)
        prof.save()

        try:
            readDay=reading_day.objects.get(user=user, date=datetime.date.today())
        except:
            readDay=reading_day.objects.create(user=user)
        readDay.words= newWords+readDay.words
        readDay.time= newTime+readDay.time
        readDay.save()
        try:
            readBok = ReadBook.objects.get(user=user, book=bok)
        except:
            readBok = ReadBook.objects.create(user=user, book=bok)
        readBok.words = readBok.words+newWords
        readBok.time = readBok.time+newTime
        readBok.score= readBok.words/readBok.time
        readBok.save()
        print(prof.score)
        return HttpResponse('')
        
def leaderboard(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    globall = profile.objects.all().order_by('-score')
    try:
        user = User.objects.get(id=request.user.id)
        prof = profile.objects.get(user=user)
        local = profile.objects.filter(location = prof.location).order_by('-score')
    except:
        local = profile.objects.all().order_by('-score')
    return render(request, 'leaderboard.html', {'global':globall, 'local':local})

def read_goal(request):
    if request.method != 'POST':
        return redirect('/')
    user = User.objects.get(id=request.user.id)
    teach = teacher.objects.get(user = user)
    classs = clas.objects.get(teacher=teach)
    classs.goal = request.POST['goal']
    classs.save()
    return redirect('/dashboard/teacher')
    

def classView(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    user = User.objects.get(id=request.user.id)
    try:
        prof = profile.objects.get(user=user)
        clas = prof.clas
    except:
        teach = teacher.objects.get(user=user)
        clas = clas.objects.get(teacher=teach)
    lead = profile.objects.filter(clas=clas).order_by('-score')
    profs = profile.objects.filter(clas=clas).order_by('user')
    books = ebook.objects.filter(clas=clas)
    avg = 0
    for x in clas.students.all():
        y = profile.objects.get(user = x)
        avg = avg + y.score
    clas.avg = avg/len(clas.students.all())
    clas.save()
    try:
        filtered = []
        for x in books:
            if ReadBook.objects.filter(user=user,book=x):
                readbo = ReadBook.objects.get(user=user,book=x)
                print(readbo.completed)
                if not readbo.completed:
                    filtered.append(x)
            else:
                filtered.append(x)
    except:
        return render(request,'class.html',{'class':clas,'books':books, 'lead':lead,'profs':profs})

    return render(request,'class.html',{'class':clas,'books':filtered, 'lead':lead,'profs':profs})

def StudentView(request, id):
    try:
        user = User.objects.get(id=id)
        prof = profile.objects.get(user=user)
    except:
        return HttpResponse('404 Not found')
    books= ReadBook.objects.filter(user=user,completed=True)
    classs = prof.clas
    goal = classs.goal
    try:
        readDay=reading_day.objects.get(user=user, date=datetime.date.today())
        read = readDay.words
        print(read)
    except:
        read = 0

    percent = round((read/goal)*100,2)
    deg = (read/goal)*180
    if read>goal:
        deg = 180
    print(deg, percent)
    days = reading_day.objects.filter(user=user).order_by('-date')
    d = datetime.datetime.now()
    dates = []
    scores = []
    reads = []
    times = []
    for y in range(10):
        for x in reversed(days):
            print(x.date)
            print(d-datetime.timedelta(days=9-y))
            if x.date == (d-datetime.timedelta(days=9-y)).date():
                dates.append(x.date.strftime("%d"))
                scores.append(round(x.words/x.time,1))
                reads.append(round(x.words,1))
                times.append(round(x.time,1))
            elif x == days[0]:
                if len(dates) != y:
                    dates.append((d-datetime.timedelta(days=9-y)).date().strftime("%d"))
                    scores.append(0)
                    reads.append(0)
                    times.append(0)

    return render(request, 'StudentView.html', {'prof':prof,'books':books,'percent':percent,'read':read,'deg':deg, 'words': prof.words,'time':round(prof.time/60,2), 'dates':dates, 'scores':scores, 'reads':reads,'times':times})