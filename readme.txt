How to run our code: 

‘poetry shell’
From db/generated, run ‘python gen.py’
Then, from the main repo page, run ‘db/setup.sh generated’
‘flask run’


What we each did: 

Bryce - (Users/Accounts)

- Added functionality to update account balance (addToAccountBalance.html, users.py)
- Cleaned up and debugged functionality to update user info (updateAccountInto.html, users.py)
- Added public account search and information (accountPublicView.html, users.py)
- Added functionality to view buyer search history: additional columns and linking to detailed orders page (buyerInformation.html, users.py)


Varun: 
- Created the functionality to add products to cart / wishlist from the products page
- Generate / view order page.
- Modify and remove cart wishlist contents.
- Track order fulfillment status
- Updating all necessary databases in the user interaction process

Hayden 
- Finished reviews functionality (pages for updating/viewing reviews)
- Helped with merge conflicts

Evan Glas: Products
- Finished product-related features
- Implemented hierarchical categories via a nested set model. Enabled filtering on these categories hierarchically.
- Added the ability to add and edit products.
- Added a new field to the products table corresponding to the user that created the given product.
- Added a search bar that lets the user filter according to matching sequences in the product name and/or product description.
- Updated the design of the landing page. Added a new logo, a favicon, updated some colors, and added the falling leaves in the background.
- Visualized the average review using stars on each product on the landing page.

Srikar
- Finished Inventory/ Order Fulfillment functionality
- Added seller analytics 

Link to video: 

https://youtu.be/fGKBHQ91TlY
