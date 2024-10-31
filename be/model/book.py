from be.model import db_conn


class Book(db_conn.DBConn):

    def __init__(self):
        super().__init__()

    def _search_in_store(self, condition, store_id, page_num, page_size):
        book_col = self.conn.book_col
        result = book_col.find(condition, {"_id": 0}).skip((page_num - 1) * page_size).limit(page_size)
        result_list = list(result)

        if store_id:
            store_col = self.conn.store_col
            result_list = self._filter_books_in_store(result_list, store_id, store_col)

        if not result_list:
            return 501, f"Books not found", []
        return 200, "ok", result_list

    def _filter_books_in_store(self, result_list, store_id, store_col):
        return [
            book for book in result_list
            if store_col.find_one({"store_id": store_id, "books.book_id": book.get('id')})
        ]

    def search_title_in_store(self, title: str, store_id: str, page_num: int, page_size: int):
        condition = {"title": title}
        return self._search_in_store(condition, store_id, page_num, page_size)

    def search_title(self, title: str, page_num: int, page_size: int):
        return self.search_title_in_store(title, "", page_num, page_size)

    def search_tag_in_store(self, tag: str, store_id: str, page_num: int, page_size: int):
        condition = {"tags": {"$regex": tag}}
        return self._search_in_store(condition, store_id, page_num, page_size)

    def search_tag(self, tag: str, page_num: int, page_size: int):
        return self.search_tag_in_store(tag, "", page_num, page_size)

    def search_content_in_store(self, content: str, store_id: str, page_num: int, page_size: int):
        condition = {"$text": {"$search": content}}
        return self._search_in_store(condition, store_id, page_num, page_size)

    def search_content(self, content: str, page_num: int, page_size: int):
        return self.search_content_in_store(content, "", page_num, page_size)

    def search_author_in_store(self, author: str, store_id: str, page_num: int, page_size: int):
        condition = {"author": author}
        return self._search_in_store(condition, store_id, page_num, page_size)

    def search_author(self, author: str, page_num: int, page_size: int):
        return self.search_author_in_store(author, "", page_num, page_size)
