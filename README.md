# Projekt Tomo

Projekt Tomo je spletna storitev za učenje programiranja. Deluje tako, da učenec na svoj računalnik prenese datoteke z nalogami in jih začne dopolnjevati s svojimi rešitvami, strežnik pa te rešitve brez kakršnega koli dodatnega dela sproti shranjuje, preverja ter učencu nudi takojšen samodejen odziv o njihovi pravilnosti, učitelju pa pregled nad znanjem učencev.

Spletna storitev je napisana v [Djangu](https://www.djangoproject.com/), ki je razvojno ogrodje za spletne storitve v [Pythonu](https://www.python.org/). Če želite prispevati k razvoju Projekta Tomo, si najprej poglejte kaj malega o Djangu in Pythonu, nato pa si po spodnjih navodilih storitev namestite na računalnik. Za navodila glede dodajanja funkcionalnosti in popravljanja napak glejte
[CONTRIBUTING.md](CONTRIBUTING.md).

## Navodila za namestitev

Na začetku klonirajte repozitorij ter ustvarite virtualno okolje:

    git clone git@github.com:ul-fmf/projekt-tomo.git
    cd projekt-tomo
    python3 -m venv venv

Dobiti bi morali sledečo strukturo datotek:

    projekt-tomo/
        web/
            attempts/
            courses/
            ...
        manage.py
        ...
        venv/
            ...

Po prvi namestitvi, pa tudi na vsake toliko časa, greste v imenik `projekt-tomo/web/` ter s sledečimi ukazi kodo posodobite, aktivirate virtualno okolje, namestite potrebne pakete in posodobite bazo:

    git pull
    source ../venv/bin/activate
    pip install -r requirements/local.txt
    python manage.py migrate

Če uporabljate Windowse, je drugi ukaz drugačen

    git pull
    ..\venv\Scripts\activate
    pip install -r requirements\local.txt
    python manage.py migrate

Strežnik nato poženete z

    python manage.py runserver

Teste poženete z

    python manage.py test

Ker ima spletna storitev zaradi podpore ArnesAAI specifičen način prijave, morate pred prvo uporabo z ukazom

    python manage.py createsuperuser

ustvariti administratorskega uporabnika. Ob prvi in vseh ostalih prijavah pa se morate prijaviti prek [administratorskega vmesnika](http://localhost:8000/admin/), saj je po taki prijavi mogoče dostopati tudi na običajno stran. V administratorskem vmesniku lahko prav tako ustvarjate dodatne uporabnike in predmete.

Če želite, lahko uporabite tudi bazo z bolj realnimi (anonimiziranimi) podatki. Prenesite datoteko [db.sqlite3](https://unilj-my.sharepoint.com/:u:/g/personal/matija_pretnar_fmf_uni-lj_si1/EV9O7hBuKDhPuvBjTybIzRwBWrhu2NBW9twoPdun_t-WXQ?e=qXhBdy), ki jo shranite na `projekt-tomo/web/web/db.sqlite3`. Administratorski uporabnik z uporabniškim imenom `admin` in geslom `admin` je že vključen.

### Namestitev v Dev Container

Kdor ima nameščen Docker in urejevalnik [VS Code](https://code.visualstudio.com/), lahko za razvoj uporabi tudi [Dev Container](https://code.visualstudio.com/docs/devcontainers/containers). Pred zagonom morate datoteko `example.env` prekopirati v novo datoteko `.env` in po potrebi popraviti nastavitve. Nato poženete ukaz `Dev Containers: Open in Container` (lahko tudi `Build and Open` ali `Rebuild and Reopen`). Navodila za zagon so taka kot zgoraj, le da lahko izpustite vse ukaze za delo z virtualnim okoljem `venv`.
