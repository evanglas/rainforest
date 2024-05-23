from flask import current_app as app


class Category:
    def __init__(self, id, name, left, right, level):
        self.id = id
        self.name = name
        self.left = left
        self.right = right
        self.level = level

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "left": self.left,
            "right": self.right,
            "level": self.level,
        }

    @staticmethod
    def get_all():
        rows = app.db.execute(
            """
                SELECT *
                FROM Categories
            """,
        )
        return [Category(*row) for row in rows]
    
    @staticmethod
    def get(id):
        rows = app.db.execute(
            """
                SELECT *
                FROM Categories
                WHERE id = :id
            """,
            id=id,
        )
        return Category(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_next_level(parent_id):
        rows = app.db.execute(
            """
                WITH parent AS (
                    SELECT *
                    FROM Categories
                    WHERE id = :parent_id
                )
                SELECT child.*
                FROM Categories AS child
                JOIN parent ON child.left_idx > parent.left_idx AND child.right_idx <= parent.right_idx
                            AND child.level = parent.level - 1;
            """,
            parent_id=parent_id,
        )
        return [Category(*row) for row in rows]

    @staticmethod
    def get_previous_levels(child_id):
        rows = app.db.execute(
            """
                WITH child as (
                    SELECT *
                    FROM Categories
                    WHERE id = :child_id
                )
                SELECT parent.*
                FROM Categories AS parent
                JOIN child ON child.left_idx > parent.left_idx AND child.right_idx <= parent.right_idx
                AND child.level <= parent.level - 1;
            """,
            child_id=child_id,
        )
        return [Category(*row) for row in rows]
