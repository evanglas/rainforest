from werkzeug.security import generate_password_hash
import csv
from faker import Faker
import numpy as np
from collections import defaultdict

num_users = 100
num_products = 2000
num_inventory = 10000
num_purchases = 3000
num_orders = 500
num_purchases = 10000

Faker.seed(0)
np.random.seed(42)
fake = Faker()


def get_csv_writer(f):
    return csv.writer(f, dialect="unix", quoting=csv.QUOTE_NONE, escapechar="\n")


def gen_users(num_users):
    available_uids = []
    with open("Users.csv", "w") as f:
        writer = get_csv_writer(f)
        for uid in range(num_users):
            available_uids.append(uid)
            profile = fake.profile()
            email = profile["mail"] if uid != 0 else "icecream@tastes.good"
            plain_password = f"test123"
            password = generate_password_hash(plain_password)
            name_components = profile["name"].split(" ")
            firstname = name_components[0]
            lastname = name_components[-1]
            balance = np.random.randint(0, 1000)
            fake_address = fake.address().replace("\n", "").replace(",", " ")
            writer.writerow(
                [uid, firstname, lastname, email, password, fake_address, balance]
            )
    return available_uids


def gen_productReviews(available_pids, num_users):
    with open("ProductReviews.csv", "w") as f:
        writer = get_csv_writer(f)
        rownum = 0
        for pid in available_pids:
            for rid in range(num_users):
                review = fake.sentence(nb_words=10)[:-1]
                rating = fake.random_int(min=1, max=5)
                # get fake datetime:
                time_reviewed = fake.date_time()
                # recover string from time
                time_reviewed = time_reviewed.strftime("%Y-%m-%d %H:%M:%S")
                writer.writerow(
                    [
                        int(rid),
                        int(pid),
                        int(rating),
                        review,
                        time_reviewed,
                    ]
                )
                rownum += 1
    return


def gen_sellerReviews(num_users):
    with open("SellerReviews.csv", "w") as f:
        writer = get_csv_writer(f)
        rownum = 0
        for rid in range(num_users):
            for sid in range(num_users):
                if rid == sid:
                    continue
                review = fake.sentence(nb_words=10)[:-1]
                rating = fake.random_int(min=1, max=5)
                # get fake datetime:
                time_reviewed = fake.date_time()
                # recover string from time
                time_reviewed = time_reviewed.strftime("%Y-%m-%d %H:%M:%S")
                writer.writerow(
                    [
                        int(rid),
                        int(sid),
                        int(rating),
                        review,
                        time_reviewed,
                    ]
                )
                rownum += 1
    return


def gen_products(num_products, available_uids):
    available_pids = []
    with open("Products.csv", "w") as f:
        writer = get_csv_writer(f)
        for pid in range(num_products):
            name = fake.sentence(nb_words=4)[:-1]
            description = fake.sentence(nb_words=50)
            available = fake.random_element(elements=("true", "false"))
            if available == "true":
                available_pids.append(pid)
            img_src = (
                "https://picsum.photos/id/" + str(np.random.randint(1, 85)) + "/1000"
            )
            creator_id = fake.random_element(elements=available_uids)
            writer.writerow([pid, name, name, description, img_src, creator_id])
    return available_pids


def gen_productCategory(available_pids):
    with open("ProductCategory.csv", "w") as f:
        writer = get_csv_writer(f)
        for pid in np.unique(available_pids):
            category = fake.random_element(
                elements=(
                    3,
                    4,
                    6,
                    7,
                    9,
                    10,
                    13,
                    14,
                    16,
                    17,
                    19,
                    20,
                    22,
                    23,
                    26,
                    27,
                    29,
                    30,
                    32,
                    33,
                    36,
                    37,
                    39,
                    40,
                    42,
                    43,
                    45,
                    46,
                )
            )
            writer.writerow([pid, category])
    return


def gen_inventory(num_inventory, available_pids):
    seller_products = []
    with open("Inventory.csv", "w") as f:
        writer = get_csv_writer(f)
        for id in range(num_inventory):
            sid = fake.random_int(min=0, max=num_users - 1)
            pid = fake.random_element(elements=available_pids)
            quantity = fake.random_int(min=0, max=100)
            price = fake.random_int(min=1, max=10)
            time_updated = fake.date_time()
            promo_code = f"DISCOUNT{fake.random_int(min = 1, max = 100)}"
            writer.writerow(
                [
                    id,
                    sid,
                    pid,
                    quantity,
                    price,
                    time_updated,
                    promo_code,
                ]
            )
            for _ in range(quantity):
                seller_products.append((sid, pid, price))
    return seller_products


def gen_cart(num_carts, available_uids, available_pids):
    triples = defaultdict(int)
    with open("Cart.csv", "w") as f:
        writer = get_csv_writer(f)
        for id in range(num_carts):
            uid = fake.random_element(elements=available_uids)
            pid = fake.random_element(elements=available_pids)
            sid = fake.random_int(min=0, max=num_users - 1)
            price = fake.random_int(max=500)
            quantity = fake.random_int(max=10)
            promo_code = fake.random_element(
                elements=("abc123", "def456", "ghi789", "jkl012")
            )
            if triples.get((uid, pid, sid)) == 1:
                continue
            else:
                triples[(uid, pid, sid)] = 1
            writer.writerow([uid, pid, sid, price, quantity, promo_code])
    return


def gen_saveforlater(num_saveforlaters, available_uids, available_pids):
    triples = defaultdict(int)
    with open("SaveForLater.csv", "w") as f:
        writer = get_csv_writer(f)
        for id in range(num_saveforlaters):
            uid = fake.random_element(elements=available_uids)
            pid = fake.random_element(elements=available_pids)
            sid = fake.random_int(min=0, max=num_users - 1)
            price = fake.random_int(max=500)
            quantity = fake.random_int(max=10)
            promo_code = fake.random_element(
                elements=("abc123", "def456", "ghi789", "jkl012")
            )
            if triples.get((uid, pid, sid)) == 1:
                continue
            else:
                triples[(uid, pid, sid)] = 1
            writer.writerow([uid, pid, sid, price, quantity, promo_code])
    return


def gen_orders(num_orders, available_uids):
    order_ids = []
    for id in range(num_orders):
        uid = fake.random_element(elements=available_uids)
        order_ids.append(id)
    return order_ids


def gen_purchases(num_purchases, seller_products, order_ids):
    orderline = []
    for order_num in order_ids:
        orderline.append((order_num, fake.date_time()))
    with open("Orderline.csv", "w") as g:
        writer_orderline = get_csv_writer(g)
        for id in range(num_purchases):
            uid = fake.random_int(min=0, max=num_users - 1)
            product = fake.random_element(elements=seller_products)
            seller_id, pid, price = product
            order_info = fake.random_element(elements=orderline)
            fulfillment_status = False
            order_id = order_info[0]
            time_purchased = order_info[1]
            quantity = 1
            time_bought = time_purchased
            # Check if order_id is valid
            if order_id in order_ids:
                writer_orderline.writerow(
                    [
                        id,
                        uid,
                        pid,
                        seller_id,
                        order_id,
                        quantity,
                        price,
                        fulfillment_status,
                        time_purchased,
                        time_bought,
                    ]
                )
                seller_products.remove(product)
                if len(seller_products) == 0:
                    break
    return order_ids


available_uids = gen_users(num_users)
available_pids = gen_products(num_products, available_uids)
gen_productCategory(available_pids)
seller_products = gen_inventory(num_inventory, available_pids)
order_ids = gen_orders(num_orders, available_uids)
gen_purchases(num_purchases, seller_products, order_ids)

gen_cart(num_purchases, available_uids, available_pids)
gen_saveforlater(num_purchases, available_uids, available_pids)
gen_productReviews(available_pids, num_users)
gen_sellerReviews(num_users)
