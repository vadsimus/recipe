recipe

### backend
cd recipe
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py runserver

### frontend
cd recipe-fe
npm install
npm start
