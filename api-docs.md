# API Documentation

This document provides details about all available API endpoints in the Habitus Finance application.

## Base URL

All API endpoints are relative to: `/api`

## Authentication

Most endpoints require authentication. Include a JWT token in the Authorization header:

```
Authorization: Bearer <your-token>
```

## Error Handling

All endpoints follow a standard error response format:

```json
{
  "msg": "Error message describing what went wrong"
}
```

---

## Authentication Endpoints

### Register User

```
POST /auth/register
```

Create a new user account.

**Request Body:**
```json
{
  "name": "User Name",
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response (200):**
```json
{
  "token": "jwt-token-here"
}
```

### Login

```
POST /auth/login
```

Authenticate a user and get a JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response (200):**
```json
{
  "token": "jwt-token-here"
}
```

### Get Current User

```
GET /auth/me
```

Get the profile of the currently authenticated user.

**Response (200):**
```json
{
  "_id": "user-id",
  "name": "User Name",
  "email": "user@example.com",
  "role": "user",
  "createdAt": "2023-09-15T12:00:00.000Z"
}
```

---

## User Management Endpoints (Admin Only)

### Get All Users

```
GET /users/admin/users
```

Get a list of all registered users.

**Response (200):**
```json
[
  {
    "_id": "user-id-1",
    "name": "User 1",
    "email": "user1@example.com",
    "role": "user",
    "createdAt": "2023-09-15T12:00:00.000Z"
  },
  {
    "_id": "user-id-2",
    "name": "Admin User",
    "email": "admin@example.com",
    "role": "admin",
    "createdAt": "2023-09-14T10:00:00.000Z"
  }
]
```

### Create User (Admin)

```
POST /users/admin/users
```

Create a new user as an administrator.

**Request Body:**
```json
{
  "name": "New User",
  "email": "newuser@example.com",
  "password": "securepassword",
  "role": "user" // or "admin"
}
```

**Response (201):**
```json
{
  "_id": "new-user-id",
  "name": "New User",
  "email": "newuser@example.com",
  "role": "user",
  "createdAt": "2023-09-16T14:30:00.000Z"
}
```

### Update User

```
PUT /users/admin/users/:id
```

Update an existing user's information.

**Request Body:**
```json
{
  "name": "Updated Name",
  "email": "updated@example.com",
  "password": "newpassword", // Optional - omit to keep current password
  "role": "admin"
}
```

**Response (200):**
```json
{
  "_id": "user-id",
  "name": "Updated Name",
  "email": "updated@example.com",
  "role": "admin",
  "createdAt": "2023-09-15T12:00:00.000Z",
  "updatedAt": "2023-09-16T15:00:00.000Z"
}
```

### Delete User

```
DELETE /users/admin/users/:id
```

Delete a user from the system.

**Response (200):**
```json
{
  "msg": "Usuário excluído com sucesso"
}
```

### Get Admin Stats

```
GET /users/admin/stats
```

Get statistics for the admin dashboard.

**Response (200):**
```json
{
  "totalUsers": 25,
  "totalScenarios": 150,
  "totalSpreadsheets": 40,
  "usersThisMonth": 5,
  "scenariosThisMonth": 30
}
```

### Get Admin Activity Logs

```
GET /users/admin/logs
```

Get recent system activity logs.

**Response (200):**
```json
[
  {
    "_id": "log-id-1",
    "user": {
      "_id": "user-id",
      "email": "user@example.com"
    },
    "action": "CREATED_SCENARIO",
    "resource": "Scenario Name",
    "timestamp": "2023-09-16T14:00:00.000Z"
  },
  {
    "_id": "log-id-2",
    "user": {
      "_id": "user-id",
      "email": "user@example.com"
    },
    "action": "UPLOADED_SPREADSHEET",
    "resource": "financial-data.xlsx",
    "timestamp": "2023-09-16T13:45:00.000Z"
  }
]
```

---

## Spreadsheet Endpoints

### Upload Spreadsheet

```
POST /spreadsheets/upload
```

Upload a financial data spreadsheet.

**Request:**
- Content-Type: multipart/form-data
- Body: file (Excel file)

**Response (200):**
```json
{
  "_id": "spreadsheet-id",
  "name": "financial-data.xlsx",
  "user": "user-id",
  "data": {
    // Parsed spreadsheet data
  },
  "createdAt": "2023-09-16T15:30:00.000Z"
}
```

### Get User Spreadsheets

```
GET /spreadsheets
```

Get all spreadsheets uploaded by the current user.

**Response (200):**
```json
[
  {
    "_id": "spreadsheet-id-1",
    "name": "Q3-Finances.xlsx",
    "user": "user-id",
    "createdAt": "2023-09-16T15:30:00.000Z"
  },
  {
    "_id": "spreadsheet-id-2",
    "name": "Annual-Budget.xlsx",
    "user": "user-id",
    "createdAt": "2023-09-15T10:15:00.000Z"
  }
]
```

### Get Spreadsheet by ID

```
GET /spreadsheets/:id
```

Get a specific spreadsheet's data.

**Response (200):**
```json
{
  "_id": "spreadsheet-id",
  "name": "financial-data.xlsx",
  "user": "user-id",
  "data": {
    "revenue": [...],
    "expenses": [...],
    "investments": [...]
    // Full spreadsheet data
  },
  "createdAt": "2023-09-16T15:30:00.000Z"
}
```

### Delete Spreadsheet

```
DELETE /spreadsheets/:id
```

Delete a spreadsheet and its data.

**Response (200):**
```json
{
  "msg": "Planilha excluída com sucesso"
}
```

---

## Scenario Endpoints

### Create Scenario

```
POST /scenarios
```

Create a new financial scenario.

**Request Body:**
```json
{
  "name": "Growth Scenario 2023",
  "description": "Projected growth with increased investments",
  "spreadsheetId": "spreadsheet-id",
  "data": {
    "revenue": {
      // Modified financial data
    },
    "expenses": {
      // Modified financial data
    },
    // Other financial categories
  }
}
```

**Response (201):**
```json
{
  "_id": "scenario-id",
  "name": "Growth Scenario 2023",
  "description": "Projected growth with increased investments",
  "user": "user-id",
  "spreadsheet": "spreadsheet-id",
  "data": {
    // Full scenario data
  },
  "createdAt": "2023-09-16T16:00:00.000Z"
}
```

### Get User Scenarios

```
GET /scenarios
```

Get all scenarios created by the current user.

**Response (200):**
```json
[
  {
    "_id": "scenario-id-1",
    "name": "Pessimistic Forecast",
    "description": "Worst case scenario for Q4",
    "user": "user-id",
    "spreadsheet": "spreadsheet-id",
    "createdAt": "2023-09-16T16:00:00.000Z"
  },
  {
    "_id": "scenario-id-2",
    "name": "Optimistic Growth",
    "description": "Best case with new product launch",
    "user": "user-id",
    "spreadsheet": "spreadsheet-id",
    "createdAt": "2023-09-15T14:30:00.000Z"
  }
]
```

### Get Scenario by ID

```
GET /scenarios/:id
```

Get details of a specific scenario.

**Response (200):**
```json
{
  "_id": "scenario-id",
  "name": "Growth Scenario 2023",
  "description": "Projected growth with increased investments",
  "user": "user-id",
  "spreadsheet": "spreadsheet-id",
  "data": {
    // Full scenario data with all financial categories
  },
  "createdAt": "2023-09-16T16:00:00.000Z"
}
```

### Update Scenario

```
PUT /scenarios/:id
```

Update an existing scenario.

**Request Body:**
```json
{
  "name": "Updated Scenario Name",
  "description": "New description",
  "data": {
    // Updated financial data
  }
}
```

**Response (200):**
```json
{
  "_id": "scenario-id",
  "name": "Updated Scenario Name",
  "description": "New description",
  "user": "user-id",
  "spreadsheet": "spreadsheet-id",
  "data": {
    // Updated scenario data
  },
  "createdAt": "2023-09-16T16:00:00.000Z",
  "updatedAt": "2023-09-16T18:00:00.000Z"
}
```

### Delete Scenario

```
DELETE /scenarios/:id
```

Delete a scenario.

**Response (200):**
```json
{
  "msg": "Cenário excluído com sucesso"
}
```

### Generate PDF Report

```
GET /scenarios/:id/report
```

Generate a PDF report for a specific scenario.

**Response (200):**
Binary PDF file with appropriate content-type headers. 