import pytest
import os

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.sync_api import Page, expect
from typing import List, Dict


@pytest.fixture(scope="function")
def live_server_url(live_server):
    """URL сервера для тестов"""
    return live_server.url


class TodoPage:
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url
        
    def goto(self):
        """Переход на домашнюю страницу"""
        self.page.goto(self.base_url)
        self.page.wait_for_load_state("networkidle")
        
    def add_todo(self, text: str):
        """Добавить новую задачу"""
        input_field = self.page.locator('input[name="text"]')
        input_field.fill(text)
        add_button = self.page.locator('button:has-text("ADD")')
        add_button.click()
        self.page.wait_for_load_state("networkidle")
        
    def get_all_todos(self) -> List[str]:
        """Получить текст всех задач"""
        todo_items = self.page.locator('li.list-group-item').all()
        return [item.inner_text() for item in todo_items]
    
    def get_incomplete_todos(self) -> List[str]:
        """Получить текст незавершенных задач"""
        incomplete = self.page.locator('a li.list-group-item').all()
        return [item.inner_text() for item in incomplete]
    
    def get_completed_todos(self) -> List[str]:
        """Получить текст завершенных задач"""
        completed = self.page.locator('li.todo-completed').all()
        return [item.inner_text() for item in completed]
    
    def complete_todo(self, text: str):
        """Отметить задачу как завершенную, кликнув на нее"""
        todo_link = self.page.locator(f'a:has(li:has-text("{text}"))')
        todo_link.click()
        self.page.wait_for_load_state("networkidle")
        
    def complete_todo_by_index(self, index: int):
        """Отметить задачу как завершенную по ее позиции"""
        todo_links = self.page.locator('a li.list-group-item').all()
        if index < len(todo_links):
            todo_links[index].click()
            self.page.wait_for_load_state("networkidle")
        else:
            raise IndexError(f"Todo index {index} out of range")
    
    def delete_completed(self):
        """Нажать кнопку 'DELETE COMPLETED'."""
        delete_btn = self.page.locator('button:has-text("DELETE COMPLETED")')
        delete_btn.click()
        self.page.wait_for_load_state("networkidle")
        
    def delete_all(self):
        """Нажать кнопку 'DELETE ALL'."""
        delete_all_btn = self.page.locator('button:has-text("DELETE ALL")')
        delete_all_btn.click()
        self.page.wait_for_load_state("networkidle")
        
    def is_todo_completed(self, text: str) -> bool:
        """Проверить, отмечена ли задача как завершенная."""
        completed = self.page.locator(f'li.todo-completed:has-text("{text}")')
        return completed.count() > 0
    
    def is_todo_clickable(self, text: str) -> bool:
        """Проверить, кликабельна ли задача"""
        clickable = self.page.locator(f'a li.list-group-item:has-text("{text}")')
        return clickable.count() > 0
    
    def get_todo_count(self) -> int:
        """Получить общее количество задач"""
        return self.page.locator('li.list-group-item').count()
    
    def get_completed_count(self) -> int:
        """Получить количество завершенных задач"""
        return self.page.locator('li.todo-completed').count()
    
    def get_incomplete_count(self) -> int:
        """Получить количество незавершенных задач"""
        return self.page.locator('a li.list-group-item').count()
    
    def has_css_class(self, text: str, css_class: str) -> bool:
        element = self.page.locator(f'li.list-group-item:has-text("{text}")')
        if element.count() > 0:
            class_attr = element.first.get_attribute("class")
            return css_class in class_attr if class_attr else False
        return False
    
    def get_input_value(self) -> str:
        """Получить текущее значение поля ввода"""
        input_field = self.page.locator('input[name="text"]')
        return input_field.input_value()
    
    def get_input_placeholder(self) -> str:
        """Получить плейсхолдер поля ввода"""
        input_field = self.page.locator('input[name="text"]')
        return input_field.get_attribute("placeholder") or ""
    
    def is_input_focused(self) -> bool:
        """Проверить, находится ли поле ввода в фокусе"""
        input_field = self.page.locator('input[name="text"]')
        return input_field.is_focused()


@pytest.fixture(scope="function")
def todo_page(page: Page, live_server_url: str) -> TodoPage:
    return TodoPage(page, live_server_url)


@pytest.fixture(scope="function", autouse=True)
def clean_database(django_db_blocker):
    with django_db_blocker.unblock():
        from todo.models import Todo
        Todo.objects.all().delete()
