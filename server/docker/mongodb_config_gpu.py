import os

mongodb_config = {
    'uri': os.environ['DB_URI'],
    'database': os.environ['DB_NAME'],
}
