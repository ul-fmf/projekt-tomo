Lokalna instanca za testiranje
==============================

Za testiranje novih funkcionalnosti, si lahko na lastnem računalniku poženemo lokalno instanco strežnika za projekt-tomo.

Strežnik za Projekt Tomo je aplikacija za [Django](https://www.djangoproject.com/), ki je razvojno ogrodje za spletne aplikacije v [Python-u](https://www.python.org/). Preden se lotite dela, si poglejte kaj malega o Djangu in Pythonu.

Priprava okolja
---------------

Namestimo vse potrebne pakete vključno z djangom
```
pip3 install -r requirements/sqlite_local.txt
```

Čeprav za delovni strežnik priporočamo postgrSQL, je za testni strežnik je najlažje uporabiti kar preprosto podatkovno bazo [SQLite](https://sqlite.org/index.html), za katero ne potrebujemo niti strežnika niti posebnih administratorskih pravic. Če kljub vsemu želite uporabiti *postrges*, lahko namesto `sqlite_local` uporabite  `local`.

Najprej nastavimo privzete nastavitve
```
export DJANGO_SETTINGS_MODULE=web.settings.sqlite_local
```

Ustvarimo tabele v podatkovni bazi

```
python3 manage.py migrate
```

Nato ustvarimo administratorski račun

```
python3 manage.py createsuperuser
```

Projekt Tomo je pripravljen na zagon.

Zagon strežnika
----------------

Lokalni strežnik poženemo z ukazom

```
python3 manage.py runserver
```
Ker je zaradi ArnesAAI specifičen login, je edini način za prijavo na [administratorskega vmesnika](http://localhost:8000/admin/), saj je po prijavi v administratorski vmesnik mogoče dostopati tudi na običajno stran.

Predmete in uporabnike ustvarimo kar v [administratorskem vmesniku](http://localhost:8000/admin/), prav tako jim tam lahko dodelimo pravice. 

Veselo testiranje!
