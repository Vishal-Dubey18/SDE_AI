# Credit Approval System

A Django-based credit approval system that provides RESTful APIs to manage customers and loans, check loan eligibility based on a credit score, and create new loans.

## Features

*   **Dockerized:** The entire application and its dependencies are containerized using Docker and Docker Compose.
*   **PostgreSQL Database:** Uses a PostgreSQL database for data persistence.
*   **RESTful API:** Provides a comprehensive set of API endpoints for all functionalities.
*   **Credit Score Calculation:** Implements a credit scoring model based on historical loan data.
*   **Loan Eligibility Checks:** Determines loan eligibility based on credit score, debt-to-income ratio, and approved credit limits.
*   **Data Ingestion:** Includes a management command to ingest initial customer and loan data from Excel files.

## Tech Stack

*   Python
*   Django
*   Django Rest Framework
*   PostgreSQL
*   Docker
*   Pandas

## Setup and Installation

### Prerequisites

*   Docker
*   Docker Compose

### Instructions

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Vishal-Dubey18/SDE_AI.git
    cd SDE_AI
    ```

2.  **Start the application:**
    Use Docker Compose to build and run the containers in detached mode.
    ```bash
    docker-compose up -d
    ```

3.  **Apply database migrations:**
    Run the following command to apply the initial database migrations and create the necessary tables.
    ```bash
    docker-compose exec web python manage.py migrate
    ```

4.  **Ingest initial data:**
    Populate the database with the initial customer and loan data from the provided Excel files.
    ```bash
    docker-compose exec web python manage.py ingest_data
    ```

## API Endpoints

The base URL for the API is `http://localhost:8000/api/`.

### 1. Register a new customer

*   **Endpoint:** `POST /api/register/`
*   **Description:** Creates a new customer and calculates their approved credit limit.
*   **Request Body:**
    ```json
    {
        "first_name": "John",
        "last_name": "Doe",
        "age": 30,
        "monthly_income": 50000,
        "phone_number": "1234567890"
    }
    ```
*   **Success Response (201 Created):**
    ```json
    {
        "customer_id": 101,
        "name": "John Doe",
        "age": 30,
        "monthly_income": 50000,
        "approved_limit": 1800000,
        "phone_number": "1234567890"
    }
    ```

### 2. Check loan eligibility

*   **Endpoint:** `POST /api/check-eligibility/`
*   **Description:** Checks if a customer is eligible for a new loan.
*   **Request Body:**
    ```json
    {
        "customer_id": 1,
        "loan_amount": 100000,
        "interest_rate": 10,
        "tenure": 12
    }
    ```
*   **Success Response (200 OK):**
    ```json
    {
        "customer_id": 1,
        "approval": true,
        "interest_rate": 10,
        "corrected_interest_rate": 12.0,
        "tenure": 12,
        "monthly_installment": 9333.33
    }
    ```

### 3. Create a new loan

*   **Endpoint:** `POST /api/create-loan/`
*   **Description:** Creates a new loan for a customer if they are eligible.
*   **Request Body:**
    ```json
    {
        "customer_id": 1,
        "loan_amount": 100000,
        "interest_rate": 10,
        "tenure": 12
    }
    ```
*   **Success Response (201 Created):**
    ```json
    {
        "loan_id": 101,
        "customer_id": 1,
        "loan_approved": true,
        "message": "Loan Approved",
        "monthly_installment": 9333.33
    }
    ```
*   **Failure Response (200 OK):**
    ```json
    {
        "message": "Loan not approved"
    }
    ```

### 4. View a specific loan

*   **Endpoint:** `GET /api/view-loan/{loan_id}/`
*   **Description:** Retrieves the details of a specific loan.
*   **Success Response (200 OK):**
    ```json
    {
        "loan_id": 1,
        "customer": {
            "id": 1,
            "first_name": "Aarav",
            "last_name": "Sharma",
            "phone_number": "1234567890",
            "age": 30
        },
        "loan_amount": 50000.0,
        "interest_rate": 12.0,
        "monthly_installment": 4166.67,
        "tenure": 12
    }
    ```

### 5. View all loans for a customer

*   **Endpoint:** `GET /api/view-loans/{customer_id}/`
*   **Description:** Retrieves a list of all loans for a specific customer.
*   **Success Response (200 OK):**
    ```json
    [
        {
            "loan_id": 1,
            "loan_amount": 50000.0,
            "interest_rate": 12.0,
            "monthly_installment": 4166.67,
            "repayments_left": 6
        },
        {
            "loan_id": 2,
            "loan_amount": 100000.0,
            "interest_rate": 10.0,
            "monthly_installment": 8333.33,
            "repayments_left": 10
        }
    ]
    ```

## Data Models

### Customer

| Field            | Type         | Description                               |
| ---------------- | ------------ | ----------------------------------------- |
| `customer_id`    | AutoField    | Primary key for the customer.             |
| `first_name`     | CharField    | First name of the customer.               |
| `last_name`      | CharField    | Last name of the customer.                |
| `age`            | IntegerField | Age of the customer.                      |
| `phone_number`   | CharField    | Phone number of the customer.             |
| `monthly_salary` | IntegerField | Monthly salary of the customer.           |
| `approved_limit` | IntegerField | Approved credit limit for the customer.   |
| `current_debt`   | FloatField   | Current outstanding debt of the customer. |

### Loan

| Field               | Type         | Description                                         |
| ------------------- | ------------ | --------------------------------------------------- |
| `loan_id`           | AutoField    | Primary key for the loan.                           |
| `customer`          | ForeignKey   | Foreign key to the `Customer` model.                |
| `loan_amount`       | FloatField   | The amount of the loan.                             |
| `tenure`            | IntegerField | The loan tenure in months.                          |
| `interest_rate`     | FloatField   | The annual interest rate of the loan.               |
| `monthly_repayment` | FloatField   | The monthly EMI amount.                             |
| `emis_paid_on_time` | IntegerField | The number of EMIs paid on time.                    |
| `start_date`        | DateField    | The date when the loan was approved.                |
| `end_date`          | DateField    | The date when the loan is due to be fully paid.     |
