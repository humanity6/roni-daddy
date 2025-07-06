
# Database Schema for Pimp My Case

This document outlines the recommended MySQL database schema for the "Pimp My Case" application. The schema is designed to store all necessary data, including users, product information, design assets, generated images, and customer orders.

## Entity-Relationship Summary

The core entities of the application are:

-   **Users**: Represents customers who create designs and place orders.
-   **Phone Brands & Models**: Stores the product catalog of phone cases available. This can be populated from the Chinese API.
-   **Design Templates**: The creative styles offered to users (e.g., "Retro Remix", "Cover Shoot").
-   **Generated Images**: The AI-generated images created by users. This is the central creative asset.
-   **Orders & Order Items**: Tracks customer orders, linking users, the products they chose, and the custom images they designed.

---

## A Note on Storing Images in MySQL

You mentioned wanting to store images directly in the database. This can be achieved using the `BLOB` (Binary Large Object) data type. Here’s a quick comparison of the two main approaches:

### Approach 1: Storing Image Data as `BLOB`s (As requested)

-   **Pros**:
    -   **Simplicity**: Images are stored and retrieved in the same database transactions as their metadata.
    -   **Data Integrity**: The image is directly tied to its record, preventing broken links. Backups of the database contain everything.
-   **Cons**:
    -   **Database Size**: The database can grow very large, very quickly, which can complicate backups and maintenance.
    -   **Performance**: Retrieving many large `BLOB`s can be slower than serving files from a dedicated file system or CDN.
    -   **Complexity**: Application code becomes more complex as it needs to handle binary data streams from the database.

### Approach 2: Storing a File Path

-   **Pros**:
    -   **High Performance**: Web servers and Content Delivery Networks (CDNs) are highly optimized for serving static files like images.
    -   **Scalability**: Keeps the database lean and fast. Image files can be stored on scalable object storage like Amazon S3, Google Cloud Storage, etc.
    -   **Standard Practice**: This is the most common and recommended approach for web applications.
-   **Cons**:
    -   **Synchronization**: You must ensure that if a database record is deleted, the corresponding file is also deleted, and vice-versa.

**Recommendation**: The schema below includes a `LONGBLOB` field as requested. However, for a production application, it is **strongly recommended to use the file path approach**. You can store the images in a cloud bucket (like S3) and save the URL or path in a `VARCHAR(255)` column instead of the `image_data` column.

---

## Table Definitions

Here are the detailed definitions for each table.

### 1. `users`

Stores basic information about your customers.

| Column Name | Data Type      | Constraints                      | Description                                |
| :---------- | :------------- | :------------------------------- | :----------------------------------------- |
| `id`        | `INT`          | `PRIMARY KEY`, `AUTO_INCREMENT`  | Unique identifier for the user.            |
| `email`     | `VARCHAR(255)` | `UNIQUE`, `NOT NULL`             | User's email address, used for login/contact. |
| `password`  | `VARCHAR(255)` | `NULL`                           | Hashed password (if you implement auth).   |
| `created_at`| `TIMESTAMP`    | `DEFAULT CURRENT_TIMESTAMP`      | When the user account was created.         |

### 2. `phone_brands`

Stores the phone brands you support (e.g., Apple, Samsung).

| Column Name   | Data Type      | Constraints                     | Description                                      |
| :------------ | :------------- | :------------------------------ | :----------------------------------------------- |
| `id`          | `INT`          | `PRIMARY KEY`, `AUTO_INCREMENT` | Unique identifier for the brand.                 |
| `name`        | `VARCHAR(100)` | `NOT NULL`                      | The display name of the brand (e.g., "Samsung"). |
| `api_brand_id`| `VARCHAR(100)` | `UNIQUE`, `NULL`                | The corresponding ID from the Chinese API.       |
| `created_at`  | `TIMESTAMP`    | `DEFAULT CURRENT_TIMESTAMP`     | When the brand was added.                        |

### 3. `phone_models`

Stores the specific phone models for each brand.

| Column Name   | Data Type        | Constraints                     | Description                                      |
| :------------ | :--------------- | :------------------------------ | :----------------------------------------------- |
| `id`          | `INT`            | `PRIMARY KEY`, `AUTO_INCREMENT` | Unique identifier for the model.                 |
| `brand_id`    | `INT`            | `NOT NULL`                      | Foreign key linking to the `phone_brands` table. |
| `name`        | `VARCHAR(100)`   | `NOT NULL`                      | The name of the model (e.g., "Galaxy S24").      |
| `api_model_id`| `VARCHAR(100)`   | `UNIQUE`, `NULL`                | The corresponding ID from the Chinese API.       |
| `price`       | `DECIMAL(10, 2)` | `NOT NULL`                      | The price for a case for this model.             |
| `stock`       | `INT`            | `DEFAULT 0`                     | Available stock count from the API.              |
| `created_at`  | `TIMESTAMP`      | `DEFAULT CURRENT_TIMESTAMP`     | When the model was added.                        |

### 4. `design_templates`

Stores the different AI design styles you offer.

| Column Name   | Data Type      | Constraints                     | Description                                                  |
| :------------ | :------------- | :------------------------------ | :----------------------------------------------------------- |
| `id`          | `INT`          | `PRIMARY KEY`, `AUTO_INCREMENT` | Unique identifier for the template.                          |
| `template_key`| `VARCHAR(50)`  | `UNIQUE`, `NOT NULL`            | The unique key used in the code (e.g., "retro-remix").       |
| `name`        | `VARCHAR(100)` | `NOT NULL`                      | The user-friendly name (e.g., "Retro Remix").                |
| `description` | `TEXT`         | `NULL`                          | A brief description of the style.                            |
| `is_active`   | `BOOLEAN`      | `DEFAULT TRUE`                  | Whether the template is currently available to users.        |

### 5. `generated_images`

Stores the images created by the AI, along with their metadata.

| Column Name        | Data Type      | Constraints                     | Description                                                  |
| :----------------- | :------------- | :------------------------------ | :----------------------------------------------------------- |
| `id`               | `INT`          | `PRIMARY KEY`, `AUTO_INCREMENT` | Unique identifier for the image.                             |
| `user_id`          | `INT`          | `NULL`                          | Foreign key to `users`. Can be NULL for anonymous creations. |
| `design_template_id`| `INT`          | `NOT NULL`                      | Foreign key to `design_templates`.                           |
| `prompt`           | `TEXT`         | `NOT NULL`                      | The full prompt sent to the AI to generate the image.        |
| `filename`         | `VARCHAR(255)` | `NOT NULL`                      | The unique filename generated for the image.                 |
| `image_data`       | `LONGBLOB`     | `NOT NULL`                      | The binary data of the generated image. **(See note above)** |
| `created_at`       | `TIMESTAMP`    | `DEFAULT CURRENT_TIMESTAMP`     | When the image was generated.                                |

### 6. `orders`

Stores information about a customer's order.

| Column Name             | Data Type                                                           | Constraints                     | Description                                                  |
| :---------------------- | :------------------------------------------------------------------ | :------------------------------ | :----------------------------------------------------------- |
| `id`                    | `INT`                                                               | `PRIMARY KEY`, `AUTO_INCREMENT` | Unique identifier for the order.                             |
| `user_id`               | `INT`                                                               | `NOT NULL`                      | Foreign key to the `users` table.                            |
| `status`                | `ENUM('pending', 'paid', 'processing', 'shipped', 'delivered', 'cancelled')` | `NOT NULL`, `DEFAULT 'pending'` | The current status of the order.                             |
| `total_price`           | `DECIMAL(10, 2)`                                                    | `NOT NULL`                      | The total cost of the order.                                 |
| `shipping_address`      | `TEXT`                                                              | `NULL`                          | The customer's shipping address.                             |
| `payment_id`            | `VARCHAR(255)`                                                      | `NULL`                          | The transaction ID from the payment gateway.                 |
| `chinese_api_order_id`  | `VARCHAR(255)`                                                      | `NULL`                          | The `third_id` returned by the Chinese API upon order creation. |
| `created_at`            | `TIMESTAMP`                                                         | `DEFAULT CURRENT_TIMESTAMP`     | When the order was placed.                                   |
| `updated_at`            | `TIMESTAMP`                                                         | `DEFAULT CURRENT_TIMESTAMP`     | When the order was last updated.                             |

### 7. `order_items`

A linking table that details which products and designs are in which order.

| Column Name         | Data Type        | Constraints                     | Description                                      |
| :------------------ | :--------------- | :------------------------------ | :----------------------------------------------- |
| `id`                | `INT`            | `PRIMARY KEY`, `AUTO_INCREMENT` | Unique identifier for the order item.            |
| `order_id`          | `INT`            | `NOT NULL`                      | Foreign key to the `orders` table.               |
| `generated_image_id`| `INT`            | `NOT NULL`                      | Foreign key to the `generated_images` table.     |
| `phone_model_id`    | `INT`            | `NOT NULL`                      | Foreign key to the `phone_models` table.         |
| `quantity`          | `INT`            | `NOT NULL`, `DEFAULT 1`         | Number of items for this specific design.        |
| `price`             | `DECIMAL(10, 2)` | `NOT NULL`                      | The price for this single item at time of purchase. |

---

## SQL `CREATE TABLE` Statements

You can use the following SQL code to create the tables in your MySQL database.

```sql
-- Use InnoDB engine to support foreign keys and transactions
SET default_storage_engine=InnoDB;

-- Table for users
CREATE TABLE `users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `email` VARCHAR(255) NOT NULL UNIQUE,
  `password` VARCHAR(255) NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
);

-- Table for phone brands
CREATE TABLE `phone_brands` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL,
  `api_brand_id` VARCHAR(100) NULL UNIQUE,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
);

-- Table for phone models
CREATE TABLE `phone_models` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `brand_id` INT NOT NULL,
  `name` VARCHAR(100) NOT NULL,
  `api_model_id` VARCHAR(100) NULL UNIQUE,
  `price` DECIMAL(10, 2) NOT NULL,
  `stock` INT DEFAULT 0,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`brand_id`) REFERENCES `phone_brands`(`id`) ON DELETE CASCADE
);

-- Table for design templates
CREATE TABLE `design_templates` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `template_key` VARCHAR(50) NOT NULL UNIQUE,
  `name` VARCHAR(100) NOT NULL,
  `description` TEXT NULL,
  `is_active` BOOLEAN DEFAULT TRUE,
  PRIMARY KEY (`id`)
);

-- Table for generated images
CREATE TABLE `generated_images` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NULL,
  `design_template_id` INT NOT NULL,
  `prompt` TEXT NOT NULL,
  `filename` VARCHAR(255) NOT NULL,
  `image_data` LONGBLOB NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE SET NULL,
  FOREIGN KEY (`design_template_id`) REFERENCES `design_templates`(`id`)
);

-- Table for orders
CREATE TABLE `orders` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `status` ENUM('pending', 'paid', 'processing', 'shipped', 'delivered', 'cancelled') NOT NULL DEFAULT 'pending',
  `total_price` DECIMAL(10, 2) NOT NULL,
  `shipping_address` TEXT NULL,
  `payment_id` VARCHAR(255) NULL,
  `chinese_api_order_id` VARCHAR(255) NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`)
);

-- Table for individual items within an order
CREATE TABLE `order_items` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `order_id` INT NOT NULL,
  `generated_image_id` INT NOT NULL,
  `phone_model_id` INT NOT NULL,
  `quantity` INT NOT NULL DEFAULT 1,
  `price` DECIMAL(10, 2) NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`order_id`) REFERENCES `orders`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`generated_image_id`) REFERENCES `generated_images`(`id`),
  FOREIGN KEY (`phone_model_id`) REFERENCES `phone_models`(`id`)
);

```
