import warnings
import time
import requests


class API:

    URL = "https://hackathon-game.relaxdays.cloud/"
    REST_TIME = 0.1
    LAST_REQUEST = time.time()

    ID_VARS = {"stock_id", "supplier_id", "listing_id", "tag_id"}

    GET_ARTICLE = "stock/{stock_id}"
    GET_ALL_ARTICLES = "stock"

    GET_TAG = "tag/{tag_id}"
    GET_ALL_TAGS = "tag"

    GET_SUPPLIER = "supplier/{supplier_id}"
    GET_ALL_SUPPLIER = "supplier"

    BUY = "supplier/{supplier_id}/stock/{stock_id}/buy"    # { "count": 10, "price_per_unit": 10 }

    GET_PLAYERS = "player"
    GET_SELF = "player/self"

    GET_LISTING = "listing/{listing_id}"
    GET_ALL_LISTINGS = "listing"
    POST_NEW_LISTING = "listing/new"    # { "stock": 2, "count": 10, "price": 1.5 } RETURN { "id": 1 }
    DELETE_LISTING = "listing/delete/{listing_id}"
    PUT_LISTING = "listing/{listing_id}"      # { "count": 10, "price": 2.5 }

    CACHE = {}

    @staticmethod
    def make_request(method: str, req_sub_dir: str, **kwargs) -> [dict, list, None]:

        # Do at least 0.1 seconds breaks between requests
        time.sleep(max(time.time() + API.REST_TIME - API.LAST_REQUEST, 0))
        API.LAST_REQUEST = time.time()

        req_sub_dir = API.prep_request(req_sub_dir, **kwargs)

        try:
            response = requests.request(method, f"{API.URL}{req_sub_dir}", json=kwargs.get("json"))

            if response.status_code == 200:
                return eval(response.content.decode())
            else:
                raise requests.exceptions.RequestException("Wrong Status Code.")
        except requests.exceptions.RequestException as e:
            warnings.warn(str(e))

    @staticmethod
    def prep_request(req_sub_dir: str, **kwargs) -> str:
        assert all([key in API.ID_VARS for key in kwargs.keys()])
        return req_sub_dir.format(**kwargs)

    @staticmethod
    def get_stock(stock_id: int) -> dict:
        return API.make_request(method="GET", req_sub_dir=API.GET_ARTICLE, stock_id=stock_id)

    @staticmethod
    def get_all_stocks() -> list:
        return API.make_request(method="GET", req_sub_dir=API.GET_ALL_ARTICLES)

    @staticmethod
    def get_tag(tag_id: int) -> dict:
        return API.make_request(method="GET", req_sub_dir=API.GET_TAG, stock_id=tag_id)

    @staticmethod
    def get_all_tags() -> list:
        return API.make_request(method="GET", req_sub_dir=API.GET_ALL_TAGS)

    @staticmethod
    def get_supplier(supplier_id: int) -> dict:
        return API.make_request(method="GET", req_sub_dir=API.GET_SUPPLIER, stock_id=supplier_id)

    @staticmethod
    def get_all_suppliers() -> list:
        return API.make_request(method="GET", req_sub_dir=API.GET_ALL_SUPPLIER)

    @staticmethod
    def get_all_players() -> list:
        return API.make_request(method="GET", req_sub_dir=API.GET_PLAYERS)

    @staticmethod
    def get_self() -> dict:
        return API.make_request(method="GET", req_sub_dir=API.GET_SELF)

    @staticmethod
    def buy(supplier_id, stock_id, json) -> bool:
        assert all([key in json for key in ["count", "price_per_unit"]]), \
            "POST Buy requires count and price_per_unit"

        return API.make_request(method="POST", req_sub_dir=API.BUY, supplier_id=supplier_id, stock_id=stock_id,
                                json=json)

    @staticmethod
    def get_all_listings() -> list:
        return API.make_request(method="GET", req_sub_dir=API.GET_ALL_LISTINGS)

    @staticmethod
    def get_listing(listing_id: int) -> list:
        return API.make_request(method="GET", req_sub_dir=API.GET_LISTING, listing_id=listing_id)

    @staticmethod
    def make_listing(json) -> int:
        assert all([key in json for key in ["stock", "count", "price"]]),\
            "POST listings requires stock, count and price"

        return API.make_request(method="POST", req_sub_dir=API.POST_NEW_LISTING, json=json).get("id")

    @staticmethod
    def delete_listing(listing_id: int) -> bool:
        return API.make_request(method="DELETE", req_sub_dir=API.DELETE_LISTING, listing_id=listing_id)

    @staticmethod
    def put_listing(listing_id: int, json) -> bool:
        assert all([key in json for key in ["count", "price"]]),\
            "PUT listings requires count and price"

        return API.make_request(method="PUT", req_sub_dir=API.PUT_LISTING, listing_id=listing_id, json=json)


if __name__ == "__main__":
    print(API.get_all_listings())
    print(API.get_all_players())
    print(API.get_all_tags())
    print(API.get_all_stocks())
    print(API.get_all_suppliers())
    print(API.get_self())
