# Documentation API

Flask API for managing documentation records.

## Installation

```bash
pip install -r requirements.txt
```

## Running the Server

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## Environment Variables

Configure these environment variables to use non-default database credentials:

- `DB_HOST` - Database host (default: localhost)
- `DB_USER` - Database user (default: root)
- `DB_PASSWORD` - Database password (default: AldebaraN7#)
- `DB_NAME` - Database name (default: docs_db)

## API Endpoints

### 1. Create Document
**POST** `/api/documents`

Create a new documentation record.

**Request Body:**
```json
{
  "title": "Document Title",
  "content": "Document content here",
  "sector": "IT",
  "author": "Author Name"
}
```

**Required Fields:** title, content  
**Optional Fields:** sector, author

**Response (201):**
```json
{
  "success": true,
  "message": "Document created successfully",
  "id": 1
}
```

---

### 2. Update Document
**PUT** `/api/documents/<id>`

Update an existing documentation record.

**Request Body:**
```json
{
  "title": "Updated Title",
  "content": "Updated content",
  "sector": "Elektricarji",
  "author": "New Author"
}
```

**Optional Fields:** title, content, sector, author

**Response (200):**
```json
{
  "success": true,
  "message": "Document updated successfully",
  "id": 1
}
```

---

### 3. Delete Document
**DELETE** `/api/documents/<id>`

Delete a documentation record.

**Response (200):**
```json
{
  "success": true,
  "message": "Document deleted successfully",
  "id": 1
}
```

---

### 4. Get Document
**GET** `/api/documents/<id>`

Retrieve a specific documentation record.

**Response (200):**
```json
{
  "success": true,
  "document": {
    "id": 1,
    "title": "Document Title",
    "content": "Document content here",
    "sector": "IT",
    "author": "Author Name",
    "created_at": "2026-05-07T10:30:00",
    "updated_at": "2026-05-07T10:30:00"
  }
}
```

---

### 5. List All Documents
**GET** `/api/documents`

Retrieve all documentation records.

**Response (200):**
```json
{
  "success": true,
  "count": 2,
  "documents": [
    {
      "id": 1,
      "title": "Document 1",
      "content": "Content 1",
      "sector": "IT",
      "author": "Author 1",
      "created_at": "2026-05-07T10:30:00",
      "updated_at": "2026-05-07T10:30:00"
    },
    {
      "id": 2,
      "title": "Document 2",
      "content": "Content 2",
      "sector": "Kotlovnica",
      "author": "Author 2",
      "created_at": "2026-05-07T11:00:00",
      "updated_at": "2026-05-07T11:00:00"
    }
  ]
}
```

---

### 6. Search Documents
**GET** `/api/documents/search?q=<search_query>`

Search documentation records by title or content.

**Query Parameters:**
- `q` (required) - Search string

**Response (200):**
```json
{
  "success": true,
  "count": 1,
  "results": [
    {
      "id": 1,
      "title": "IP Address",
      "content": "Moonstalker: 192.168.7.230, Zoran Robic: 192.168.7.75",
      "author": "Zoran Robic",
      "created_at": "2026-05-07T10:30:00",
      "updated_at": "2026-05-07T10:30:00"
    }
  ]
}
```

---

## Valid Sectors

The `sector` field accepts the following values:
- `IT`
- `Kotlovnica`
- `Elektricarji`

---

## Error Responses

All endpoints return error responses in the following format:

**400 Bad Request:**
```json
{
  "error": "Error description"
}
```

**404 Not Found:**
```json
{
  "error": "Document with id X not found"
}
```

**500 Internal Server Error:**
```json
{
  "error": "Error description"
}
```

---

## Example Usage with cURL

### Create a document
```bash
curl -X POST http://localhost:5000/api/documents \
  -H "Content-Type: application/json" \
  -d '{
    "title": "IP Address",
    "content": "Moonstalker: 192.168.7.230",
    "sector": "IT",
    "author": "Zoran Robic"
  }'
```

### Update a document
```bash
curl -X PUT http://localhost:5000/api/documents/1 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Title",
    "content": "Updated content"
  }'
```

### Delete a document
```bash
curl -X DELETE http://localhost:5000/api/documents/1
```

### Get a document
```bash
curl http://localhost:5000/api/documents/1
```

### List all documents
```bash
curl http://localhost:5000/api/documents
```

### Search documents
```bash
curl "http://localhost:5000/api/documents/search?q=IP"
```
