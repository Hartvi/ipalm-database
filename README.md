




## 26/02 - too many things to keep in mind
- tested out how to create objects on server when `perform_create()` in a viewset is called
- authenticated post command:
  - `http -a jeff:jeff POST http://127.0.0.1:8000/rest/snippets/ code="print(456)"`
the same can be done with the requests library
- **IDEA**: maybe upload the setup in the `data` field in the request in json format. This way the setup parameters can be found and matched on the server.


create snippet model
`python manage.py makemigrations snippets`
`python manage.py migrate snippets`

manual reset & migration
`rm -f db.sqlite3`
`rm -r snippets/migrations`
`python manage.py makemigrations snippets`
`python manage.py migrate`



