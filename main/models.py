import datetime
import os
from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
TYPES = (
    ('studentsBook', 'Podręcznik'),
    ('workbook', 'Zeszyt ćwiczeń'),
    ('collectionOfTasks', 'Zbiór zadań'),
)

class Book(models.Model):
    type = models.CharField(max_length=32, choices=TYPES, null=True, default=None, blank=True)
    authors = models.CharField(max_length=128, default=None, null=True, blank=True)
    name = models.CharField(max_length=255)
    publishing_house = models.CharField(max_length=255, null=True, blank=True, default=None)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    year = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

    def get_json_data(self):
        return {
            "name":self.name,
            "year":self.year,
            "publishing_house":self.publishing_house,
            "category":self.category.name
        }

class Page(models.Model):
    number = models.CharField(max_length=30)
    book = models.ForeignKey(Book, null=True, blank=True, on_delete=models.CASCADE)

    def get_tasks_json(self):
        json_data = {}
        for task in Task.objects.filter(page=self):
            json_data += task.id

        return json_data

    def __str__(self):
        return f"{self.number}"

class Task(models.Model):
    number = models.CharField(max_length=30)
    page = models.ForeignKey(Page, null=True, blank=True, on_delete=models.CASCADE)
    task = models.TextField(null=True, blank=True, default=None)
    answer = models.TextField(null=True, blank=True, default=None)
    datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    images_edited = models.BooleanField(default=False)

    def get_id(self):
        return int(self.id)

    def __str__(self):
        return f"{self.number} - {self.page} - {self.page.book.name}"

    def get_json_data(self):
        current_book = 0
        for book in Book.objects.filter(category=self.page.book.category):
            if book == self.page.book:
                break
            current_book += 1

        current_page = 0
        pages = list(Page.objects.filter(book=self.page.book))

        def sort_by_number(e):
            return int(e.number)

        pages.sort(key=sort_by_number)

        for page in pages:
            if page == self.page:
                break
            current_page += 1
        
        current_task = 0
        for task in Task.objects.filter(page=self.page).order_by('number'):
            if task == self:
                break
            current_task += 1

        current_category = 0
        for category in Category.objects.all().order_by('name'):
            if category == self.page.book.category:
                break
            current_category += 1

         
        return {
            "number": self.number,
            "page": self.page.number,
            "task": self.task,
            "book": self.page.book.get_json_data(),
            "answer": self.answer,
            "images": Image.get_all_images(self.id),
            "videos": Video.get_all_videos(self.id),
            "audios": Audio.get_all_audios(self.id),
            "current_task": current_task,
            "current_book": current_book,
            "current_page": current_page,
            "current_category": current_category
        }


def path_to_image(image, filename):
    return f'images/{image.task.page.book.id}/{image.task.page.number}/{filename}'


class Image(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    src = models.ImageField(upload_to=path_to_image)
    
    def __str__(self):
        return self.src.url

    def filename(self):
        return os.path.basename(self.src.name)

    @staticmethod
    def get_all_images(id):
        json_data = {}
        for image in Image.objects.filter(task__id=id).all():
            json_data[image.id] = "/" + str(image.src)

        return json_data



class Audio(models.Model):
    name = models.CharField(max_length=255)
    src = models.FileField(upload_to='audio/')
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

    def filename(self):
        return os.path.basename(self.src.name)

    def __str__(self):
        return self.src.url

    @staticmethod
    def get_all_audios(id):
        json_data = {}
        for audio in Audio.objects.filter(task__id=id).all():
            json_data[audio.id] = "/audio/" + str(audio.id)

        return json_data

class Video(models.Model):
    name = models.CharField(max_length=255)
    src = models.FileField(upload_to='video/')
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

    def filename(self):
        return os.path.basename(self.src.name)

    def __str__(self):
        return self.src.url

    @staticmethod
    def get_all_videos(id):
        json_data = {}
        for video in Video.objects.filter(task__id=id).all():
            json_data[video.id] = "/video/" + str(video.id)

        return json_data


class UsersForAuthorization(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    remove_code = models.CharField(max_length=30)
    datetime = models.DateTimeField(auto_now_add=True)