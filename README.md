


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
  - compare images from the png and this could serve as something akin to the instance id
- test downloads
  - measurement
  - entries

## 04/10
- updated the database structure to reflect the newer structure according to the thesis
- added some better validation
  - it seems that the "Python schema validation library" doesn't have the proper (or at least I couldn't find them) functions to check nested conditional types and keys

## 03/20
- some validation in the `EntrySerializer`
- thesis: willy wonka television is basically what's needed, except that it clones the chocolate bar every time

## 03/18
- first full measurement entry test done
- done most validation in serizalizers.py
  - TODO: full test of validation
- TODO: entry uploading
- TOODO: THESIS - WRITE STUFF

## 03/17
- simplified models & structure


## PI day
- the error ```Could not resolve URL for hyperlinked relationship using view name "continuousproperty-detail". You may have failed to include the related model in your API, or incorrectly configured the `lookup_field` attribute on this field.``` is caused by not having created the `ContinuousPropertyViewSet` **and** not having it registered in the `url router` in `database/urls.py`
- make the `Property` have N `PropertyElement` children, each with the same fields as the old `ContinuousProperty`, where quantity is also material/class, units mug/bottle/etc., value probability, std=0 for categories


## 03/12
- added category & continous property adding - not tested yet

## 03/11
- `Setup` & `SetupElement` are created in `perform_create()` in `views.py`
- added some todos in `views.py`
- gotta find out how to override all the saves and properly create the object hierarchies and interlink them in the correct way
- generated a new graph

## 03/10
- created test measurement json
- created some validations
- begin making `perform_create` in `views.py`

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



