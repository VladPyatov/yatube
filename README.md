### Description
Social network Yatube

### How to run project:

Clone repo and cd:

```
git clone https://github.com/VladPyatov/yatube.git
```

```
cd yatube
```

Create and activate virtual environment:

```
python3 -m venv env
```

```
source env/bin/activate
```

Install dependencies from requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Apply migrations:

```
python3 manage.py migrate
```

Run project:

```
python3 manage.py runserver
```

### Examples:

Documentation with examples is available at the endpoint:

```
http://127.0.0.1:8000/redoc/
```
