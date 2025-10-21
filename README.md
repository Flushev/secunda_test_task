Create virtual env:
* ```bash bin/venv_create.sh``` 
* ```source venv/bin/activate```

Make sure that MySql user have permission in target db:
* ```GRANT ALL PRIVILEGES ON `target_database`.* TO 'user'@'%';```

Make sure that MySqk user have permission for working with test databases (need for unit tests):
* ```GRANT ALL PRIVILEGES ON `test_secunda\_%`.* TO 'user'@'%';```

Apply migrations (inside venv):
* ```alembic upgrade head```

Create test data (inside venv):
* ```python bin/seed_data.py```

To run local (inside venv):
* ```python main.py```

To run in docker:
* ```sudo docker build -t secunda_test .```
* ```sudo docker run --rm -d -p 8000:8000 --env-file .env secunda_test```

To access SWAGGER:
* Connect to ```http://localhost:8000/docs```

To run tests (inside venv):
* ```pytest```

Project have 94% coverage