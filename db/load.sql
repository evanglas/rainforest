-- since id is auto-generated; we need the next command to adjust the counter
-- for auto-generation so next INSERT will not clash with ids loaded above:
\COPY Users FROM 'Users.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.users_id_seq',
                         (SELECT MAX(id)+1 FROM Users),
                         false);

\COPY Products FROM 'Products.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.products_id_seq',
                         (SELECT MAX(id)+1 FROM Products),
                         false);

\COPY Cart FROM 'Cart.csv' WITH DELIMITER ',' NULL '' CSV

\COPY Inventory FROM 'Inventory.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.inventory_id_seq',
                         (SELECT MAX(id)+1 FROM Inventory),
                         false);

\COPY Orderline FROM 'Orderline.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.orderline_id_seq',
                         (SELECT MAX(id)+1 FROM Orderline),
                         false);

\COPY ProductReviews FROM 'ProductReviews.csv' WITH DELIMITER ',' NULL '' CSV;

\COPY SaveForLater FROM 'SaveForLater.csv' WITH DELIMITER ',' NULL '' CSV


\COPY SellerReviews FROM 'SellerReviews.csv' WITH DELIMITER ',' NULL '' CSV;

\COPY Categories FROM 'Categories.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.categories_id_seq',
                         (SELECT MAX(id)+1 FROM Categories),
                         false);

\COPY ProductCategory FROM 'ProductCategory.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.productcategory_id_seq',
                         (SELECT MAX(id)+1 FROM ProductCategory),
                         false);
