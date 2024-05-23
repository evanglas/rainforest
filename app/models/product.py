from flask import current_app as app


class Product:
    def __init__(self, id, name, short_name, description, image_src, creator_id):
        self.id = id
        self.name = name
        self.short_name = short_name
        self.image_src = image_src
        self.description = description
        self.creator_id = creator_id

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "short_name": self.short_name,
            "description": self.description,
            "image_src": self.image_src,
            "creator_id": self.creator_id,
        }

    @staticmethod
    def get(id):
        rows = app.db.execute(
            """
                SELECT *
                FROM Products
                WHERE id = :id
            """,
            id=id,
        )
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all():
        rows = app.db.execute(
            """
                SELECT *
                FROM Products
            """
        )
        return [Product(*row) for row in rows]

    @staticmethod
    def get_pids(creator_id=None):
        if creator_id is not None:
            rows = app.db.execute(
                """
                SELECT DISTINCT id, name
                FROM Products
                WHERE creator_id = :creator_id
                ORDER BY id
            """,
                creator_id=creator_id,
            )
        else:
            rows = app.db.execute(
                """
                    SELECT DISTINCT id, name
                    FROM Products
                    ORDER BY id
                """
            )
        return [(item[0], str(item[0]) + ": " + str(item[1])) for item in rows]

    @staticmethod
    def add(name, short_name, description, image_src, creator_id):
        rows = app.db.execute(
            """
                INSERT INTO Products (name, short_name, description, image_src, creator_id)
                VALUES (:name, :short_name, :description, :image_src, :creator_id)
                RETURNING id
            """,
            name=name,
            short_name=short_name,
            description=description,
            image_src=image_src,
            creator_id=creator_id,
        )
        return Product.get(rows[0][0])

    @staticmethod
    def update(id, name, short_name, description, image_src):
        rows = app.db.execute(
            """
                UPDATE Products
                SET name = :name, short_name = :short_name, description = :description, image_src = :image_src
                WHERE id = :id
                RETURNING id
            """,
            id=id,
            name=name,
            short_name=short_name,
            description=description,
            image_src=image_src,
        )
        return Product.get(rows[0][0])
