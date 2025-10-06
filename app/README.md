
# Flask MySQL App

This is a simple Flask app that interacts with a MySQL database. The app allows users to submit messages, which are then stored in the database and displayed on the frontend.


## Run the application

1. Start the containers using Docker Compose:

   ```bash
   docker-compose up --build -d
   ```

2. Interact with the app:

   - Visit http://localhost:5000 to see the application. You can submit new messages using the form.

## Cleaning Up

```bash
docker-compose down
```

---
