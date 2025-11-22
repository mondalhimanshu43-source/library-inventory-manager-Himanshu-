"""Library Inventory Management """

import json
from pathlib import Path
import sys


# Task 1: Book class

class Book:
    def __init__(self, title, author, isbn, status="available"):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.status = status  # "available" or "issued"

    def __str__(self):
        return f"{self.title} by {self.author} (ISBN: {self.isbn}) - {self.status}"

    def to_dict(self):
        return {
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "status": self.status
        }

    def issue(self):
        if self.status == "issued":
            raise ValueError("Book is already issued.")
        self.status = "issued"

    def return_book(self):
        if self.status == "available":
            raise ValueError("Book is already available.")
        self.status = "available"

    def is_available(self):
        return self.status == "available"


# Task 2 & 3: Inventory manager + JSON persistence

class LibraryInventory:
    def __init__(self, storage_path):
        self.storage_path = Path(storage_path)
        self.books = []
        self._load()

    def _load(self):
        try:
            if not self.storage_path.exists():
                # start with empty
                self.books = []
                return
            text = self.storage_path.read_text(encoding="utf-8").strip()
            if not text:
                self.books = []
                return
            data = json.loads(text)
            # build Book objects
            self.books = [Book(**item) for item in data]
        except Exception:
            # on any problem (missing / corrupted / parse error), start empty
            self.books = []

    def _save(self):
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            data = [b.to_dict() for b in self.books]
            # write a temp file then replace for safety
            tmp = self.storage_path.with_suffix('.tmp')
            tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
            tmp.replace(self.storage_path)
        except Exception:
            # simple implementation: ignore save errors
            pass

    def add_book(self, title, author, isbn):
        if self.search_by_isbn(isbn) is not None:
            raise ValueError("A book with this ISBN already exists.")
        book = Book(title=title, author=author, isbn=isbn)
        self.books.append(book)
        self._save()
        return book

    def search_by_title(self, title_query):
        q = (title_query or "").lower()
        return [b for b in self.books if q in b.title.lower()]

    def search_by_isbn(self, isbn):
        for b in self.books:
            if b.isbn == isbn:
                return b
        return None

    def display_all(self):
        return list(self.books)

    def issue_book(self, isbn):
        book = self.search_by_isbn(isbn)
        if not book:
            raise ValueError("Book not found.")
        book.issue()
        self._save()

    def return_book(self, isbn):
        book = self.search_by_isbn(isbn)
        if not book:
            raise ValueError("Book not found.")
        book.return_book()
        self._save()

# Task 4: Menu-driven CLI

def print_menu():
    print("\nLibrary Inventory Manager")
    print("1. Add Book")
    print("2. Issue Book")
    print("3. Return Book")
    print("4. View All Books")
    print("5. Search by Title")
    print("6. Search by ISBN")
    print("7. Exit")

def safe_input(prompt):
    try:
        return input(prompt).strip()
    except (KeyboardInterrupt, EOFError):
        print("\nExiting.")
        sys.exit(0)

def main():
    # default storage path: ./data/books.json
    storage = Path.cwd() / "data" / "books.json"
    inv = LibraryInventory(storage)

    while True:
        print_menu()
        choice = safe_input("Choose an option (1-7): ")
        if choice == "1":
            title = safe_input("Title: ")
            author = safe_input("Author: ")
            isbn = safe_input("ISBN: ")
            try:
                inv.add_book(title, author, isbn)
                print("Book added successfully.")
            except Exception as e:
                print("Error:", e)

        elif choice == "2":
            isbn = safe_input("ISBN to issue: ")
            try:
                inv.issue_book(isbn)
                print("Book issued.")
            except Exception as e:
                print("Error:", e)

        elif choice == "3":
            isbn = safe_input("ISBN to return: ")
            try:
                inv.return_book(isbn)
                print("Book returned.")
            except Exception as e:
                print("Error:", e)

        elif choice == "4":
            books = inv.display_all()
            if not books:
                print("No books in catalog.")
            for b in books:
                print(b)

        elif choice == "5":
            q = safe_input("Enter title search query: ")
            results = inv.search_by_title(q)
            if not results:
                print("No matches.")
            for r in results:
                print(r)

        elif choice == "6":
            isbn = safe_input("Enter ISBN: ")
            b = inv.search_by_isbn(isbn)
            if not b:
                print("Not found.")
            else:
                print(b)

        elif choice == "7":
            print("Goodbye.")
            break
        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    main()
