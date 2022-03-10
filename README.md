


### TODO
- test uploads
  - measurement
    - setup
    - png
    - entries
    - grasp
    - sensor\_outputs
    - object\_instance
  - entries
- test how to discern existing/new object instances
- test downloads
  - measurement
  - entries

## 03/10
- created test measurement json
- created some validations

## 03/07
- begin writing tests for uploading
- image uploading test done
- begin validation
- **data can be at most a one layer deep dictionary**

## 28/02
- ObjectClass - ClassInstance (real object with unique id) - measurement of a property that one specific real object - grasp

## 26/02 - too many things to keep in mind
- tested out how to create objects on server when `perform_create()` in a viewset is called
- authenticated post command:
  - `http -a jeff:jeff POST http://127.0.0.1:8000/rest/snippets/ code="print(456)"`
the same can be done with the requests library
- **IDEA**: maybe upload the setup in the `data` field in the request in json format. This way the setup parameters can be found and matched on the server.


## random tricks
- sometimes you need to add models in `admin.py`
- migrate every time `models.py` is updated

create snippet model
`python manage.py makemigrations snippets`
`python manage.py migrate snippets`

manual reset & migration
`rm -f db.sqlite3`
`rm -r snippets/migrations`
`python manage.py makemigrations snippets`
`python manage.py migrate`



