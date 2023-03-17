# Contributing

Dodajanje novih funkcionalnosti ali popravljanje napak se dogaja prek [pull requestov](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests) (PR). To najlažje naredite prek svojega forka repozitorija. Vsebino PR in commitov pišite v slovenščini.

Poskrbite, da PR ni prevelik in da je zaključena celota. Po vsakem PR mora aplikacija še vedno delovati ter prestati vse teste. Pri vsakem PR:

* napišite smiselen naslov, ki pove, kaj PR naredi;
* napišite opis, kjer opišete, kaj je problem in kako ga rešite (lahko se sklicujete ali zaprete primeren issue)
* commiti v PRju so zaključene celote (če je potrebno kaj popraviti, uredite obstoječi commit in ne naredite novega)
* sprememba naj bo ena sama in koda naj bo čimbolj berljiva
* PR mora na githubu dobiti kljukico, da so vsi avtomatski testi ok. To vključuje
  * teste stila kode
  * test funkcionalnosti

Te teste lahko poženete tudi lokalno (glejte ukaze v [.github/workflows/](.github/workflows/)). Za poganjanje je potrebno imeti nameščene pakete `black`, `isort` in `flake8`. Za vse teste v imeniku `web` poženete

    python -m black .
    python -m isort .
    flake8
    python manage.py test

Morebitne napake popravite tako, da uredite svoje commite (ne dodati na koncu enega commita, ki popravi vse napake). Enako velja za spremembe med procesom pregleda.

Za dodajanje prevodov poženite:

    python manage.py makemessages --no-location --no-obsolete -l sl

ki datoteko `web/locale/sl/LC_MESSAGES/django.po` razširi z novimi neprevedenimi izrazi. Možnost `--no-location` v datoteki odstrani vrstice lokacije nizov (ker se to spreminja z vsakim commitom), možnost `--no-obsolete` pa odstrani neuporabljene prevode. Če želite prevode preizkusiti, morate pognati še:

    python manage.py compilemessages

ki datoteko `django.po` prevede v učinkovitejšo binarno različico `django.mo`.
