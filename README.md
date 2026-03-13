# e-commerce-api

[Project Link](https://roadmap.sh/projects/ecommerce-api)

## TODOS

### Database Tables
1. Users:
    ```JSON
    {
        "1" : {
            "id": 1,
            "username": "jiehoon",
            "password": "hashed_password",
            "createdAt": "2026-03-11T00:00:00Z"
        },
    }
    ```
2. Products:
    ```JSON
    {
        "1" : {
            "id": 1,
            "name": "Product Name",
            "price": 29.99,
            "quantity": 100,
            "createdAt": "2026-03-11T00:00:00Z"
        }
    }
    ```
3. Shopping Cart:
    ```JSON
    {
        "1" : {
            "cart": {
                "1" : {
                    "product_id": 1,
                    "quantity" : 5,
                    "price": 29.99
                },
                "2" : {
                    "product_id": 2,
                    "quantity" : 2,
                    "price": 13.99
                },
            },
            "totalPrice": 177.93
        }
    }
    ```
4. Payments
    ```JSON
    {
        "1": {
            "id": 1,
            "user_id": 1,
            "cart": {
                "1" : {
                    "product_id": 1,
                    "quantity" : 5,
                    "price": 29.99
                }
            },
            "total": 149.95,
            "status": "completed",
            "createdAt": "2026-03-11T00:00:00Z"
        }
    }
    ```

### Endpoints
1. Auth
    ```bash
    POST /api/auth/register
    POST /api/auth/login
    ```
2. Products
    ```bash
    GET    /api/products
    GET    /api/products/<id>
    POST   /api/products
    PUT    /api/products/<id>
    DELETE /api/products/<id>
    ```
3. Cart
    ```bash
    GET    /api/cart
    POST   /api/cart
    PUT    /api/cart/<product_id>
    DELETE /api/cart/<product_id>
    ```
4. Payments
    ```bash
    POST /api/payments/checkout
    GET  /api/payments
    ```
