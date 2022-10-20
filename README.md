# Projekt Tomo

A web service for teaching programming.

## Lokalna instanca za testiranje

Za testiranje novih funkcionalnosti, si lahko na lastnem računalniku poženemo lokalno instanco strežnika za projekt-tomo.

Strežnik za Projekt Tomo je aplikacija za [Django](https://www.djangoproject.com/), ki je razvojno ogrodje za spletne aplikacije v [Python-u](https://www.python.org/). Preden se lotite dela, si poglejte kaj malega o Djangu in Pythonu.

### Priprava okolja

Ustvarimo virtual environment v ukazni vrstici, odprti v mapi projekta. Poskrbeti moramo, da je narejen za Python 3.

```
python -m venv venv
```
in ga aktiviramo (okolje Linux)

```
source venv/bin/activate
```
ali za Windows

```
.\venv\Scripts\activate
```
Namestimo vse potrebne pakete vključno z Djangom

```
pip install -r web/requirements/sqlite_local.txt
```

Čeprav za delovni strežnik priporočamo postgrSQL, je za testni strežnik je najlažje uporabiti kar preprosto podatkovno bazo [SQLite](https://sqlite.org/index.html), za katero ne potrebujemo niti strežnika niti posebnih administratorskih pravic. Če kljub vsemu želite uporabiti *postgres*, lahko namesto `sqlite_local` uporabite  `local`.

Nato nastavimo privzete nastavitve. V okolju Linux:

```
export DJANGO_SETTINGS_MODULE=web.settings.sqlite_local
```
V okolju Windows:

```
set DJANGO_SETTINGS_MODULE=web.settings.sqlite_local
```
Namesto tega pa lahko neodvisno od okolja po vsakem ukazu dodamo še:

```
--settings=web.settings.sqlite_local
```

Ustvarimo tabele v podatkovni bazi

```
python manage.py migrate
```

Nato ustvarimo administratorski račun

```
python manage.py createsuperuser
```

Projekt Tomo je pripravljen na zagon.

### Zagon strežnika

Lokalni strežnik poženemo z ukazom

```
python manage.py runserver
```
Ker je zaradi ArnesAAI specifičen login, je edini način za prijavo na [administratorskega vmesnika](http://localhost:8000/admin/), saj je po prijavi v administratorski vmesnik mogoče dostopati tudi na običajno stran.

Predmete in uporabnike ustvarimo kar v [administratorskem vmesniku](http://localhost:8000/admin/), prav tako jim tam lahko dodelimo pravice. 

Veselo testiranje!
