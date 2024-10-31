from pymongo import MongoClient

#定义集合
class Store:
    def __init__(self, db_url):
        self.client = MongoClient(db_url)
        self.db = self.client['bookstore']
        self.init_collections()

    def init_collections(self):
        self.user_col = self.db['user']
        self.store_col = self.db['store']
        self.book_col = self.db['books']
        self.order_detail_col = self.db['order_detail']
        self.order_col = self.db['order']

        self.store_col.create_index([("store_id", 1)], unique=True)
        self.user_col.create_index([("user_id", 1)], unique=True)
        self.book_col.create_index(
            [("title", "text"), ("tags", "text"), ("book_intro", "text"), ("content", "text")])


database_instance = None

def init_database(db_url):
    global database_instance
    database_instance = Store(db_url)


def get_db_conn():
    global database_instance
    db_url = "mongodb://localhost:27017/"
    database_instance = Store(db_url)
    return database_instance
