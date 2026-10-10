class Book:
    def __init__(self, title: str, isbn: str):
        self.title = title
        self.isbn = isbn
        self.is_available = True
        
    def check_available(self) -> bool:
        return self.is_available