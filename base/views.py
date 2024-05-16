from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.views import View

from .models import Task


class CustomLogoutView(LoginRequiredMixin, View):
    # отвечает за обработку выхода пользователя из системы.
    def get(self, request):
        logout(request)
        return redirect(reverse_lazy('login'))


class CustomLoginView(LoginView):
    # отвечает за кастомизацию страницы входа пользователя
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tasks')


# регистрация нового пользователя
class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        user = form.save()  # Сохраняем данные из формы и получаем пользователя.
        if user is not None:  # Если пользователь успешно создан, выполняем вход для него.
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)  # Вызываем метод form_valid суперкласса для стандартной обработки формы.

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:  # Если пользователь уже аутентифицирован, перенаправляем его на страницу задач.
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)  # Иначе, позволяем суперклассу обработать GET-запрос.


class TaskList(LoginRequiredMixin, ListView):
    # отображение списка задач
    model = Task
    context_object_name = 'tasks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        sort_by = self.request.GET.get('sort_by', '')  # По умолчанию не сортируем

        if sort_by == 'completed_only':
            tasks = Task.objects.filter(user=user, complete=True)
        elif sort_by == 'incomplete_only':
            tasks = Task.objects.filter(user=user, complete=False)
        else:
            tasks = Task.objects.filter(user=user)

        search_input = self.request.GET.get('search-area', '')  # Получаем строку поиска из GET-параметра
        if search_input:
            tasks = tasks.filter(title__icontains=search_input)  # Фильтруем задачи по названию

        context['tasks'] = tasks
        context['count'] = tasks.filter(complete=False).count()
        context['sort_by'] = sort_by
        context['search_input'] = search_input

        # Если параметр search-area пустой, установим sort_by на пустую строку для выбора опции "All" в выпадающем списке
        if not search_input:
            context['sort_by'] = ''

        return context






class TaskDetail(LoginRequiredMixin, DetailView):
    # отображение деталей задачи
    model = Task
    context_object_name = 'task'
    template_name = 'base/task.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # Получаем контекст от суперкласса.
        task = self.get_object()  # Получаем объект задачи для этого представления.
        context['description'] = task.description  # Добавляем описание задачи в контекст.
        return context


class TaskCreate(LoginRequiredMixin, CreateView):
    # создание новой задачи
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        form.instance.user = self.request.user  # Присваиваем текущего пользователя (self.request.user) к полю 'user' формы.
        return CreateView.form_valid(self, form)  # Вызываем метод form_valid суперкласса CreateView для стандартной обработки формы.


class TaskUpdate(LoginRequiredMixin, UpdateView):
    # обновление информации о задаче
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')


class DeleteView(LoginRequiredMixin, DeleteView):
    # удаление задачи
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')

    def get_queryset(self):
        owner = self.request.user  # Получаем текущего пользователя, отправившего запрос.
        return self.model.objects.filter(user=owner)  # Возвращаем queryset модели, фильтруя по пользователю owner.


from django.contrib import messages
from django import forms
class UpdateProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'base/update_profile.html'
    success_url = reverse_lazy('tasks')
    model = User
    fields = ['username', 'first_name', 'last_name']

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, 'Your profile was successfully updated.')
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

    def get_form_class(self):
        class UpdateProfileForm(forms.ModelForm):
            class Meta:
                model = User
                fields = self.fields
                labels = {
                    'username': 'Username',
                    'first_name': 'First Name',
                    'last_name': 'Last Name',
                }
        return UpdateProfileForm