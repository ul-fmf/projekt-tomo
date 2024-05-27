# Aplikacija za migracijo Projekta Tomo na Putko

## Uporaba

Pretvorbo Tomo objektov na Putkine poženemo z ukazom:

```
python projekt-tomo/web/manage.py expurtka
```

## Struktura direktorija

```
expurtka/
├── admin.py
├── apps.py
├── export
│   ├── __init__.py
│   ├── courses.py
│   ├── problems.py
├── __init__.py
├── management
│   └── commands
│       ├── expurtka.py
├── migrations
├── models.py
├── putka
│   ├── preneseni modeli in nastavitve Putke
├── README.md
├── tests.py
└── views.py
```

## Kako prispevati k migaciji

Bistveni del migracije je prepis Tomo modelov v Putkine. To storimo tako, da v mapi `expurtka/export` dodamo manjkajoče funkcije v ustrezne datoteke.

Za vsako aplikacijo `web/ime_aplikacije/` in za vsak model v `web/ime_aplikacije/models.py` moramo v datoteko `ime_aplikacije.py` dodati funkcijo:

```
def export_imemodela(...):
    ...
```
