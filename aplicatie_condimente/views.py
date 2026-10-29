import platform
import re
from collections import Counter
from datetime import datetime
from urllib.parse import urlparse

import django
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe

PREFIX_APLICATIE = "/aplicatie_condimente"

ZILE = ["Luni", "Marți", "Miercuri", "Joi", "Vineri", "Sâmbătă", "Duminică"]
LUNI = ["Ianuarie", "Februarie", "Martie", "Aprilie", "Mai", "Iunie", "Iulie",
        "August", "Septembrie", "Octombrie", "Noiembrie", "Decembrie"]

FORMAT_IMPLICIT = "%A, %-d %B %Y"      # ex: Joi, 2 Octombrie 2025
FORMAT_ORA = "%H:%M:%S"
FORMAT_COMPLET = "%A, %-d %B %Y, %H:%M:%S"


def data_romana(data, format=FORMAT_IMPLICIT):
    inlocuiri = {
        "%-d": str(data.day),
        "%A": ZILE[data.weekday()],
        "%a": ZILE[data.weekday()][:3],
        "%B": LUNI[data.month - 1],
        "%b": LUNI[data.month - 1][:3],
    }
    for cod, valoare in inlocuiri.items():
        format = format.replace(cod, valoare)
    return data.strftime(format)


class Accesare:
    contor = 0
    toate = []

    def __init__(self, ip_client, url, parametri=None, data=None):
        Accesare.contor += 1
        self.id = Accesare.contor
        self.ip_client = ip_client
        self.url = url
        self.parametri = parametri if parametri is not None else {}
        self.data = data if data is not None else datetime.now()
        Accesare.toate.append(self)

    def lista_parametri(self):
        rezultat = []
        for nume, valori in self.parametri.items():
            if not isinstance(valori, (list, tuple)):
                valori = [valori]
            if not valori:
                rezultat.append((nume, None))
            for valoare in valori:
                rezultat.append((nume, valoare if valoare != "" else None))
        return rezultat

    def string_url(self):
        return self.url

    def pagina(self):
        cale = urlparse(self.url).path
        if cale.startswith(PREFIX_APLICATIE):
            cale = cale[len(PREFIX_APLICATIE):]
        return cale or "/"

    def calculeaza_data(self, format=FORMAT_IMPLICIT, tip=""):
        if tip == "":
            return data_romana(self.data, format)
        if tip == "zi":
            text = data_romana(self.data, format)
        elif tip == "timp":
            text = data_romana(self.data, FORMAT_ORA)
        else:
            text = data_romana(self.data, format + ", " + FORMAT_ORA)
        return f"<section><h2>Data și ora</h2><p>{text}</p></section>"

    def __str__(self):
        return "\n".join([
            f"id: {self.id}",
            f"ip_client: {self.ip_client}",
            f"string_url: {self.string_url()}",
            f"pagina: {self.pagina()}",
            f"calculeaza_data: {self.calculeaza_data()}",
            f"lista_parametri: {self.lista_parametri()}",
        ])


T = "aplicatie_condimente/"


def index(request):
    return render(request, T + "pagina_principala.html")


def despre(request):
    return render(request, T + "despre.html")


def istoric(request):
    return render(request, T + "istoric.html")


def info(request):
    tip = request.GET.get("data", "")
    if tip not in ("zi", "timp"):
        tip = "tot"
    sectiune = mark_safe(request.accesare.calculeaza_data(tip=tip))
    return render(request, T + "info.html", {
        "titlu": "Informații despre server",
        "sectiune_data": sectiune,
        "versiune_python": platform.python_version(),
        "versiune_django": django.get_version(),
    })
    

COLOANE_TABEL = ["id", "ip_client", "url", "parametri", "data"]


def _valoare_coloana(a, coloana):
    if coloana == "id":
        return a.id
    if coloana == "ip_client":
        return a.ip_client
    if coloana == "url":
        return a.string_url()
    if coloana == "parametri":
        return ", ".join(f"{n}={v}" for n, v in a.lista_parametri()) or "-"
    return a.calculeaza_data(format=FORMAT_COMPLET)


def log(request):
    toate = list(Accesare.toate)
    erori = []

    ultimele = request.GET.get("ultimele")
    if ultimele is not None and not re.fullmatch(r"[0-9]+", ultimele.strip()):
        return render(request, T + "log.html", {
            "titlu": "Log accesări",
            "eroare_fatala": "Parametrul „ultimele” trebuie să fie un număr întreg pozitiv.",
        })

    dubluri = request.GET.get("dubluri", "false").strip().lower() == "true"
    valori_iduri = request.GET.getlist("iduri")
    if valori_iduri:
        ids = []
        for grup in valori_iduri:
            for bucata in grup.split(","):
                bucata = bucata.strip()
                if not bucata:
                    continue
                if re.fullmatch(r"[0-9]+", bucata):
                    ids.append(int(bucata))
                else:
                    erori.append(f"Id invalid: {bucata}")
        if not dubluri:
            ids = list(dict.fromkeys(ids))
        dupa_id = {a.id: a for a in toate}
        afisate = []
        for i in ids:
            if i in dupa_id:
                afisate.append(dupa_id[i])
            else:
                erori.append(f"Nu există accesarea cu id-ul {i}")
    else:
        afisate = toate

    if ultimele is not None:
        n = int(ultimele)
        if n > len(afisate):
            erori.append(f"Exista doar {len(afisate)} accesari fata de {n} accesari cerute")
        else:
            afisate = afisate[len(afisate) - n:]

    mod = request.GET.get("accesari", "")
    numar_accesari = Accesare.contor if mod == "nr" else None
    detalii = None
    if mod == "detalii":
        detalii = [(a.id, a.calculeaza_data(format=FORMAT_COMPLET)) for a in afisate]
    elif mod not in ("", "nr"):
        erori.append("Valoare necunoscută pentru parametrul accesari (se acceptă „nr” sau „detalii”).")

    antet, randuri = None, None
    valori_tabel = request.GET.getlist("tabel")
    if valori_tabel:
        cerute = [c.strip() for g in valori_tabel for c in g.split(",") if c.strip()]
        if "tot" in cerute:
            coloane = COLOANE_TABEL
        else:
            for c in cerute:
                if c not in COLOANE_TABEL:
                    erori.append(f"Coloană necunoscută: {c}")
            coloane = [c for c in dict.fromkeys(cerute) if c in COLOANE_TABEL]
        if coloane:
            antet = coloane
            randuri = [[_valoare_coloana(a, c) for c in coloane] for a in afisate]

    lista = [(a, a.pagina(), a.calculeaza_data(format=FORMAT_COMPLET)) for a in afisate]

    numar_pe_pagina = Counter(a.pagina() for a in toate)
    maxim, minim = max(numar_pe_pagina.values()), min(numar_pe_pagina.values())
    pagini_max = [p for p, c in numar_pe_pagina.items() if c == maxim]
    pagini_min = [p for p, c in numar_pe_pagina.items() if c == minim]

    return render(request, T + "log.html", {
        "titlu": "Log accesări",
        "lista": lista,
        "antet": antet,
        "randuri": randuri,
        "numar_accesari": numar_accesari,
        "detalii": detalii,
        "nume_parametri": list(request.GET.keys()),
        "erori": erori,
        "pagini_max": ", ".join(pagini_max), "nr_max": maxim,
        "pagini_min": ", ".join(pagini_min), "nr_min": minim,
    })


def accesare_detalii(request, id_accesare):
    id_accesare = int(id_accesare)
    for a in Accesare.toate:
        if a.id == id_accesare:
            return render(request, T + "accesare.html", {
                "titlu": f"Accesarea {a.id}",
                "a": a,
                "pagina": a.pagina(),
                "data": a.calculeaza_data(format=FORMAT_COMPLET),
                "parametri": a.lista_parametri(),
                "url_log": reverse("log"),
            })
    raise Http404(f"Nu există accesarea cu id-ul {id_accesare}")


def _in_lucru(request, nume):
    return render(request, T + "in_lucru.html", {"pagina": nume})


def produse(request):
    return _in_lucru(request, "Produse")


def contact(request):
    return _in_lucru(request, "Contact")


def cos_virtual(request):
    return _in_lucru(request, "Coș virtual")


def retete(request):
    return _in_lucru(request, "Rețete")


def blog(request):
    return _in_lucru(request, "Blog")