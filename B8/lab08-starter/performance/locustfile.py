"""Lab 4: weighted tasks, year filtering, and client-side simulated failures.

One percent of valid year-search responses are marked as failed by Locust.
This simulates an error for the exercise; the API still returns HTTP 200.

Run: locust -f performance/locustfile.py --headless -H http://127.0.0.1:5000 \
         -u 10 -r 2 -t 30s --html reports/A.html
"""
import itertools
import random

from locust import HttpUser, between, task

_counter = itertools.count(1)
SEARCH_YEARS = (1996, 2017, 2021, 2025)
SIMULATED_FAILURE_RATE = 0.01


class BooksUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def list_books(self):
        self.client.get("/books", name="GET /books")

    @task(2)
    def read_book(self):
        book_id = random.randint(1, 50)
        with self.client.get(
            f"/books/{book_id}", name="GET /books/{id}", catch_response=True
        ) as response:
            # Expected 404 (random id absent) is not an operational failure.
            if response.status_code in (200, 404):
                response.success()
            else:
                response.failure(f"Unexpected status {response.status_code}")

    @task(1)
    def create_book(self):
        unique = next(_counter)
        self.client.post(
            "/books",
            json={
                "title": f"Load test {unique}",
                "author": "locust",
                "year": random.choice(SEARCH_YEARS),
            },
            name="POST /books",
        )

    @task(1)
    def search_by_year(self):
        year = random.choice(SEARCH_YEARS)
        with self.client.get(
            "/books",
            params={"year": year},
            name="GET /books?year={year}",
            catch_response=True,
        ) as response:
            # Let Locust report connection errors and timeouts as real failures.
            if getattr(response, "error", None):
                return
            if response.status_code != 200:
                response.failure(f"Year search returned HTTP {response.status_code}")
                return

            try:
                books = response.json()
            except ValueError:
                response.failure("Year search returned invalid JSON")
                return

            if not isinstance(books, list) or any(
                not isinstance(book, dict) or book.get("year") != year
                for book in books
            ):
                response.failure("Year search returned an invalid list or wrong year")
                return

            # This changes Locust's result only, not the HTTP status from Flask.
            if random.random() < SIMULATED_FAILURE_RATE:
                response.failure("SIMULATED_500 (client-side only; actual HTTP 200)")
            else:
                response.success()
