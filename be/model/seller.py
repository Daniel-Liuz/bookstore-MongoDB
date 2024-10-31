import json
from be.model import error
from be.model import db_conn


class Seller(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    #添加书籍信息及描述
    def add_book(
            self,
            user_id: str,
            store_id: str,
            book_id: str,
            book_json_str: str,   #包含书籍详细信息的 JSON 字符串，描述书籍的各种属性（如标题、作者等）
            stock_level: int,
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)
            self.conn.store_col.update_one(
                {"store_id": store_id},
                {
                    "$push": {
                        "books": {
                            "book_id": book_id,
                            "stock_level": stock_level
                        }
                    }
                }
            )
            self.conn.book_col.insert_one(json.loads(book_json_str))
        except BaseException as e:
            return 528, "{}".format(str(e))
        return 200, "ok"

    #增加库存
    def add_stock_level(
            self, user_id: str, store_id: str, book_id: str, add_stock_level: int
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)
            self.conn.store_col.update_one({"store_id": store_id, "books.book_id": book_id},  {"$inc": {"books.$.stock_level": add_stock_level}})
        except BaseException as e:
            return 528, "{}".format(str(e))
        return 200, "ok"

    #创建店铺
    def create_store(self, user_id: str, store_id: str) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)
            self.conn.store_col.insert_one({ 
                "store_id": store_id,
                "user_id": user_id,
                "books": []
            })
        except BaseException as e:
            return 528, "{}".format(str(e))
        return 200, "ok"

    #发货
    def send_books(self, user_id: str, order_id: str) -> (int, str):
        try:
            result = self.conn.order_col.find_one({
                "$or": [
                    {"order_id": order_id, "status": 1},   #已支付、未发货
                    {"order_id": order_id, "status": 2},   #已发货、未收到
                    {"order_id": order_id, "status": 3},   #已收到
                ]
            })

            if result == None:
                return error.error_invalid_order_id(order_id)
            store_id = result.get("store_id")
            paid_status = result.get("status")

            result = self.conn.store_col.find_one({"store_id": store_id})
            seller_id = result.get("user_id")
            if seller_id != user_id:
                return error.error_authorization_fail()
            if paid_status == 2 or paid_status == 3:
                return error.error_books_repeat_sent()

            self.conn.order_col.update_one({"order_id": order_id}, {"$set": {"status": 2}})
        except BaseException as e:
            return 528, "{}".format(str(e))
        return 200, "ok"