import json
import os
import string
import re
import random
import requests
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import datetime
from django.contrib.auth.models import User, Group
from django.http import JsonResponse, FileResponse, HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from .models import Book, Task, Image, Video, Audio, Page, Category, UsersForAuthorization
from django.middleware.csrf import get_token
from django.contrib.auth import authenticate, login as login_request, logout as logout_request
from django.db.models import Q
from django.core.mail import EmailMessage
from django.conf import settings
from django.core.files import File

def addMessage(request, text, color="#FF0000"):
    request.session['message'] = {"text": text, "color": color}



def get_random_string(length):
    letters = string.ascii_letters
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

def index(request):
    return render(request, "api.html", {})

email_regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

def remove_comments(request):
    tasks = Task.objects.all()
    for task in tasks:
        html = re.sub(r"<!--(.|\s|\n)*?-->", "", task.answer)
        task.answer = html
        task.save()
    return JsonResponse({
        "code": 200,
    })

def rob_images(request):
    tasks = Task.objects.filter(images_edited=False)
    counter = len(tasks)
    for task in tasks:
        if "<img " in task.answer:
            res = [i for i in range(len(task.answer)) if task.answer.startswith('<img ', i)]
            for r in res:
                r = int(r)
                strt = 0
                end = 0
                char = '"'
                url = ""
                for e in range(r, len(task.answer)):
                    if task.answer[e+0] == 's':
                        if task.answer[e+1] == 'r':
                            if task.answer[e+2] == 'c':
                                if task.answer[e+3] == '=':
                                    strt = e+5
                                    char = task.answer[e+4]
                                    break

                for ee in task.answer[strt:]:
                    if ee == char:
                        break
                    url+=ee
                try:
                    r = requests.get(url)
                except:
                    continue
                fname = ''

                if "Content-Disposition" in r.headers.keys():
                    fname = re.findall("filename=(.+)", r.headers["Content-Disposition"])[0]
                else:
                    fname = url.split("/")[-1]
                ext = fname.split(".")[-1]
                with open(f"file.{ext}", "wb") as file:
                    file.write(r.content)
                with open(f"file.{ext}", "rb") as file:
                    img = Image(src=File(file), task=task)
                    img.save()
                id = img.id
                new_link = f'http://localhost:8000/image/{id}'
                idsd = task.answer
                task.answer = idsd.replace(url, new_link)
                task.images_edited = True
                task.save()
                print(counter, task.id, new_link, url)

        counter -= 1



    return JsonResponse({
        "code": 200,
    })


def rob_content(request):
    change = [10, False]
    headers = {'Accept-Encoding': 'utf-8'}
    links = []
    with open('newlinks.txt', 'rb') as file:
        lines = file.readlines()
        for line in lines:
            line = line.decode('utf-8').rstrip()
            links.append(line.split(';'))

    counter = len(links)
    book = Book.objects.filter(id=change[0]).first()
    for link in links:
        id, task = link[0], ";".join(link[1:])
        rq = requests.get(f"https://zdam.xyz/{id}", headers=headers)
        number, page = None, None
        np1 = rq.text.split('Problem no.')[1]
        np2 = np1.split(' from ')[0]
        np4 = np1.split(' from ')[1]
        np3 = np4.split('</a>')[0]
        pn = [np2.strip(), np3, id]

        txt = rq.text.split('id="bb"')
        txt = txt[1]

        txt = txt.split('<div class="card mt-3 mb-3">')[0]
        txt = txt.split('</script>')[-1]
        while txt.endswith('</div>') or txt.endswith(' ') or txt.endswith('\t'):
            if txt.endswith('</div>'):
                txt = txt[0:-6]
            if txt.endswith(' ') or txt.endswith('\t'):
                txt = txt.rstrip()
        with open(f"done/{id}.html", "wb") as done_file:
            done_file.write(bytes(f"<span class='task-text'>{task}</span>", 'utf-8'))
            done_file.write(bytes("<br><br>", "utf-8"))
            done_file.write(bytes(txt.strip(), 'utf-8'))
        with open(f"done/{id}.html",'rb') as file1:
            with open(f"ddddn/{id}.html",'wb') as file2:
                for line in file1:
                    if not line.isspace():
                        file2.write(line)
        ctnt = ""
        with open(f"ddddn/{id}.html",'rb') as file:
            ctnt = "".join(file.read().decode('utf-8'))

        pg = Page.objects.filter(book=book, number=pn[1]).first()
        if pg is None:
            pg = Page(number=pn[1], book=book)
            if change[1]:
                pg.save()
        tsk = Task(number=pn[0], page=pg, task="", answer=ctnt)
        print(f"({counter}/{len(links)})", " Strona:", pn[1], " Zadanie:",pn[0], " ID zadania:", id, "Książka:", book.name)
        if change[1]:
            tsk.save()
        counter -= 1
    return JsonResponse({"text":"jest git"})


def book(request, id):
    book = Book.objects.filter(id=id).first()
    if book is not None:
        return JsonResponse(book.get_json_data())
    return JsonResponse({"error_code":404, "message": "Book not found"})



def all_books(request, f, t):
    books = Book.objects.all().order_by('category', 'name')
    if t == "end":
        t = len(books)
    books = books[int(f):int(t)]
    books_json = {}
    for book, i in zip(books, range(0, len(books))):
        task = Task.objects.filter(page__book=book).first()
        if task is not None:
            task = task.get_id()
        else:
            task = 1
        books_json[str(i)] = {
            "id": book.id,
            "type": book.get_type_display(),
            "authors": book.authors,
            "name": book.name,
            "publishing_house": book.publishing_house,
            "category": book.category.name,
            "year": book.year,
            "link": f"/task/{task}"
        }
    return JsonResponse(books_json)



def task(request, id):
    task = Task.objects.filter(id=id).first()
    if task is not None:
        return JsonResponse(task.get_json_data())
    return JsonResponse({"error_code":404, "message": "Task not found"})



def image_id(request, id):
    image = Image.objects.filter(id=id).first()
    return FileResponse(open(f'images/{image.task.page.book.id}/{image.task.page.number}/{image.filename()}', "rb"))



def images(self, book, page, filename):
    images = Image.objects.filter(task__book=book, task__page=page)
    for image in images:
        print(image.filename())
        if image.filename() == filename:
            return FileResponse(open(f'images/{book}/{page}/{image.filename()}', "rb"))




def videos(request, id):
    video = Video.objects.filter(id=id).first()
    file = open(video.src.path,"rb") 
    response = HttpResponse()
    response.write(file.read())
    response['Content-Type'] = 'video/webm'
    response['Content-Length'] = os.path.getsize(video.src.path)
    response['Accept-Ranges'] = 'bytes'
    return response




def audios(request, id):
    audio = Audio.objects.filter(id=id).first()
    file = open(audio.src.path,"rb") 
    response = HttpResponse()
    response.write(file.read())
    response['Content-Type'] = 'audio/mpeg'
    response['Content-Length'] = os.path.getsize(audio.src.path)
    response['Accept-Ranges'] = 'bytes'
    return response




def books(request, id):
    books = Book.objects.filter(category=id)
    json_data = {}
    i = 0
    for book in books:
        json_data[i] = {"0": book.id, "1":book.name}
        i+=1
    return JsonResponse(json_data)




def tasks_on_page(request, id):
    try:
        page = Page.objects.get(id=id)
    except Page.DoesNotExist:
        return JsonResponse({"error_code":404, "message": "Page not found"})

    tasks = Task.objects.filter(page=page).order_by('number')
    json_data = {}
    i = 0
    for task in tasks:
        json_data[i] = {"0": task.id, "1":task.number}
        i+=1
    return JsonResponse(json_data)




def pages(request, id):
    pages = list(Page.objects.filter(book=id))

    def sort_by_number(e):
        return int(e.number)

    pages.sort(key=sort_by_number)

    i = 0
    json_data = {}
    for page in pages:
        json_data[i] = {"0": page.id, "1":page.number}
        i+=1
    return JsonResponse(json_data)




def categories(request):
    categories = Category.objects.all().order_by('name')
    i = 0
    json_data = {}
    for category in categories:
        json_data[i] = {"0": category.id, "1":category.name}
        i+=1
    return JsonResponse(json_data)




def csrf(request):
    return JsonResponse({'csrfToken': get_token(request)})

def login(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        user = authenticate(request, username=data['login'], password=data['password'])
        user_auth = UsersForAuthorization.objects.filter(user=user).first()
        if user is not None:
            if user_auth is None:

                login_request(request, user)
                return JsonResponse({
                    "code": 200,
                    "message": "Zalogowano"
                })
            else:
                return JsonResponse({
                    "code": 401,
                    "message": "E-mail wymaga aktywacji"
                })

        else:
            return JsonResponse({
                "code": 401,
                "message": "Zły login lub hasło"
            })

    return JsonResponse({
        "code": 401,
        "message": "Błąd logowania"
    })

def message(request):
    message = ""
    try:
        message = request.session['message']
        request.session.pop('message')
    except:
        ...
    return JsonResponse({
        "code": 200,
        "message": message
    })

def user_info(request):
    if request.user.is_authenticated:
        jsn = {
            "code": 200,
            "username": request.user.username,
            "email": request.user.email,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "is_superuser": request.user.is_superuser
        }
        return JsonResponse(jsn)
    else:
        return JsonResponse({
            "code": 403,
            "message": "You're not logged in",
        })

def logout(request):
    if request.user.is_authenticated:
        logout_request(request)
    return JsonResponse({
        "code": 200,
        "message": "Logout successful"
    })

def register(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            username = data['username']
            email = data['email']
            password1 = data['password1']
            password2 = data['password2']
            first_name = data['firstName']
            last_name = data['lastName']
        except:
            return JsonResponse({
                "code": 401,
                "message": "Podaj poprawne dane"
            })
        if password1 != password2:
            return JsonResponse({
                "code": 401,
                "message": "Hasła muszą być takie same"
            })
        if not re.fullmatch(email_regex, email):
            return JsonResponse({
                "code": 401,
                "message": "Adres e-mail jest niepoprawny"
            })
        if User.objects.filter(username=username).first() is not None:
            return JsonResponse({
                "code": 401,
                "message": "Login jest zajęty"
            })
        if first_name == "":
            return JsonResponse({
                "code": 401,
                "message": "Podaj imię"
            })

        if last_name == "":
            return JsonResponse({
                "code": 401,
                "message": "Podaj nazwisko"
            })

        user = User.objects.create_user(
            username=username,
            password=password1,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )

        try:
            remove_code = get_random_string(30)
            email = EmailMessage(
                subject='Autorizate Email',
                body=render_to_string('email.html', {"link":f"{settings.HOSTNAME_FRONT}auth_email/{remove_code}"}),
                from_email='email@mateuszzebala.pl',
                to=[user.email],
            )
            email.content_subtype = 'html'

            email.send()

            auth_user = UsersForAuthorization(remove_code=remove_code, user=user)
            user.save()
            auth_user.save()
            addMessage(request, "Wymagana jest autoryzacja adresu e-mail", "#20ba20")
            return JsonResponse({
                "code": 200,
                "message": "Wymagana jest autoryzacja adresu e-mail"
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                "code": 401,
                "message": "Błąd przy rejestracji nowego użytkownika"
            })

def search(request, s):
    tasks = Task.objects.filter(Q(page__book__name__contains=s) | Q(answer__contains=s) | Q(number__contains=s) | Q(page__number__contains=s))
    tasks = tasks[0:4]
    tasks_json = {}
    i = 0
    for task in tasks:
        s = f"{task.page.book.name} - {task.number}/{task.page.number}"
        if len(s) > 40:
            tasks_json[i] = {"string": s[0:37] + "...", "link": f"task/{task.id}"}
        else:
            tasks_json[i] = {"string": s, "link": f"task/{task.id}"}
        i+=1
    return JsonResponse(tasks_json)

def auth_email(request, code):
    user = UsersForAuthorization.objects.filter(remove_code=code).first()
    if user is not None:
        user.delete()
    return JsonResponse({
        "code": 200,
        "message": "Autoryzacja uzyskana"
    })


def edit_user(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            username = data['username']
            email = data['email']
            first_name = data['firstName']
            last_name = data['lastName']
        except:
            return JsonResponse({
                "code": 401,
                "message": "Podaj wszystkie dane"
            })
        request.user.username = username
        request.user.email = email
        request.user.first_name = first_name
        request.user.last_name = last_name

        try:
            password1 = data['password1']
            password2 = data['password2']
            old_password = data['old_password']
            if old_password != "" and password2 != "":
                if password2 == password1:
                    if request.user.check_password(old_password):
                        user = request.user
                        request.user.set_password(password1)
                        login_request(request, user)
                    else:
                        return JsonResponse({
                            "code": 401,
                            "message": "Podaj poprawne hasło"
                        })
                else:
                    return JsonResponse({
                        "code": 401,
                        "message": "Hasła powinny być takie same"
                    })
        except Exception as e:
            print(e)

        request.user.save()
        return JsonResponse({
            "code": 200,
            "message": "Zmieniono dane"
        })
    return JsonResponse({
        "code": 401,
        "message": "Błąd edycji"
    })


def add_task(request):
    if request.method == "POST" and request.user.is_authenticated and request.user.is_superuser:
        number, page, task, book = None, None, None, None
        data = json.loads(request.body.decode('utf-8'))
        try:
            book = data['book']
        except:
            return JsonResponse({
                "code": 401,
                "message": {"text": "Nie ma takiej książki", "color":"#FF0000"}
            })

        try: page = int(data['page'])
        except:
            return JsonResponse({
                "code": 401,
                "message": {"text": "Podaj stronę", "color":"#FF0000"}
            })

        try: number = int(data['number'])
        except:
            return JsonResponse({
                "code": 401,
                "message": {"text": "Podaj nr zadania", "color":"#FF0000"}
            })

        try: answer = data['answer']
        except:
            return JsonResponse({
                "code": 401,
                "message": {"text": "Podaj odpowiedź", "color":"#FF0000"}
            })
        if answer == "":
            return JsonResponse({
                "code": 401,
                "message": {"text": "Podaj odpowiedź", "color":"#FF0000"}
            })
        book = Book.objects.filter(id=book).first()
        if book is None:
            return JsonResponse({
                "code": 401,
                "message": {"text": "Nie ma takiej książki", "color":"#FF0000"}
            })
        pg = Page.objects.filter(book=book, number=page).first()
        if pg is None:
            pg = Page(number=page, book=book)
            pg.save()
        tsk = Task(number=number, page=pg, task=task, answer=answer)
        if not request.user.is_authenticated:
            return JsonResponse({
                "code": 401,
                "message": {"text": "Nie jesteś zalogowny", "color":"#FF0000"}
            })
        if not request.user.is_superuser:
            return JsonResponse({
                "code": 401,
                "message": {"text": "Nie jesteś super userem", "color":"#FF0000"}
            })
        tsk.save()
        return JsonResponse({
            "code": 200,
            "message": {"text": "Dodano", "color":"#00FF00"}
        })
    return JsonResponse({
        "code": 401,
        "message": "Musisz być adminem"
    })


def test(request):
    tasks = Task.objects.all()
    max = 0
    for task in tasks:
        if len(task.answer) > max:
            max = task.id
    return JsonResponse({"max":max})

def edit_task(request):
    if request.user.is_authenticated and request.user.is_superuser:
        data = json.loads(request.body.decode('utf-8'))
        id = data['task']
        task = Task.objects.filter(id=int(id)).first()
        task.answer = data['answer']
        task.save()
        return JsonResponse({
            "code": 200,
            "message": "Zapisano"
        })
    return JsonResponse({
        "code": 401,
        "message": "Nie jesteś autoryzowanym userem"
    })

def add_image(request, id):
    if request.method == "POST":
        if request.user.is_authenticated and request.user.is_superuser:
            task = Task.objects.filter(id=id).first()
            img = Image(src=request.FILES.getlist('image')[0], task=task)
            img.save()
            return render(request, "add_image.html", {"added":str(img.id)})
    return render(request, "add_image.html", {})



def next_task(request, id):
    if request.user.is_authenticated and request.user.is_superuser:
        i = int(id) + 1
        while True:
            task = Task.objects.filter(id=i).first()
            if task is not None:
                return JsonResponse({"id":i})
            i += 1
        return JsonResponse({"id":1})
    return JsonResponse({"code":403})


def convert_svg(request, id):
    if request.method == "POST":
        if request.user.is_authenticated and request.user.is_superuser:
            task = Task.objects.filter(id=id).first()
            svg_code = request.POST.get('svg_code')
            with open('convert_svg.svg', 'wb') as file:
                file.write(bytes(svg_code, 'utf-8'))
            drawing = svg2rlg('convert_svg.svg', )
            renderPM.drawToFile(drawing, 'convert_svg.png', fmt='PNG')
            with open('convert_svg.png', 'rb') as file:
                img = Image(src=File(file), task=task)
                img.save()
            return render(request, "convert_svg.html", {"added":str(img.id)})
    return render(request, "convert_svg.html", {})


