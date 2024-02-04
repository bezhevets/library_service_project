import os
from datetime import date, timedelta

import stripe
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from book_service.models import Book
from borrowing.models import Borrowing
from borrowing.serializers import BorrowingListSerializer, BorrowingSerializer
from borrowing.views import BorrowingViewSet

BORROWING_URL = reverse("borrowing:borrowing-list")


def sample_book(**params):
    defaults = {
        "title": "Test",
        "author": "Test Test",
        "cover": "Hard cover",
        "inventory": 2,
        "daily_fee": 0.1,
    }
    defaults.update(params)
    return Book.objects.create(**defaults)


def sample_user(**params):
    defaults = {
        "email": "7859@test.com",
        "password": "Test122345",
    }
    defaults.update(params)
    return get_user_model().objects.create_user(**defaults)


def sample_borrowing(**params):
    defaults = {
        "expected_return_date": date.today() + timedelta(days=1),
        "book": sample_book(),
    }
    defaults.update(params)
    return Borrowing.objects.create(**defaults)


class UnauthenticatedPlayApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BORROWING_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPlayApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="123456@test.com", password="Test122345", is_staff=True
        )
        self.user2 = sample_user(email="qwer@test.com")
        self.borrowing1 = sample_borrowing(user=self.user)
        self.borrowing2 = sample_borrowing(user=self.user2)

    def test_list_borrowings_non_admin(self):
        self.client.force_authenticate(self.user)

        response = self.client.get(BORROWING_URL)
        borrowing = Borrowing.objects.filter(user=self.user)
        serializer = BorrowingListSerializer(borrowing, many=True)

        self.assertNotIn(serializer.data, response.data["results"])

    def test_list_borrowings_admin(self):
        self.client.force_authenticate(self.user)

        response = self.client.get(BORROWING_URL)
        serializer = BorrowingListSerializer(self.borrowing2)

        self.assertIn(serializer.data, response.data["results"])

    def test_admin_filter_by_user_id(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(BORROWING_URL, {"user_id": 2})

        serializer1 = BorrowingListSerializer(self.borrowing1)
        serializer2 = BorrowingListSerializer(self.borrowing2)

        self.assertIn(serializer2.data, response.data["results"])
        self.assertNotIn(serializer1.data, response.data["results"])

    def test_admin_filter_by_is_active(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(BORROWING_URL, {"is_active": "true"})

        serializer1 = BorrowingListSerializer(self.borrowing1)
        serializer2 = BorrowingListSerializer(self.borrowing2)
        serializer3 = BorrowingListSerializer(
            sample_borrowing(
                user=sample_user(email="asdfg@a.com"),
                actual_return_data=date.today(),
            )
        )

        self.assertIn(serializer2.data, response.data["results"])
        self.assertIn(serializer1.data, response.data["results"])
        self.assertNotIn(serializer3.data, response.data["results"])

    def test_get_serializer_class_list(self):
        self.client.force_authenticate(self.user)
        view = BorrowingViewSet()
        view.action = "list"

        serializer_class = view.get_serializer_class()

        self.assertEqual(serializer_class, BorrowingListSerializer)

    def test_get_serializer_class_create(self):
        self.client.force_authenticate(self.user)
        view = BorrowingViewSet()
        view.action = "create"

        serializer_class = view.get_serializer_class()

        self.assertEqual(serializer_class, BorrowingSerializer)

    def test_return_book(self):
        self.client.force_authenticate(self.user2)
        inventory = self.borrowing2.book.inventory
        # inventory = self.book.inventory
        response = self.client.post(f"/api/borrowing/{self.borrowing2.id}/return/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "This book was successfully returned.")

        self.borrowing2.refresh_from_db()
        self.borrowing2.book.refresh_from_db()

        self.assertTrue(self.borrowing2.actual_return_data)
        self.assertEqual(self.borrowing2.book.inventory, inventory + 1)

    def test_already_return_book(self):
        self.client.force_authenticate(self.user)
        self.borrowing1.actual_return_data = date.today()
        self.borrowing1.save()

        response = self.client.post(f"/api/borrowing/{self.borrowing1.id}/return/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "This borrowing has already been returned.")
