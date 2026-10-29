from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import F, Q
from django.utils import timezone


class Categorie(models.Model):
    nume = models.CharField(
        max_length=50,
        unique=True,
        error_messages={
            "unique": "Există deja o categorie cu acest nume.",
            "max_length": "Numele categoriei poate avea maxim 50 de caractere.",
        },
    )
    descriere = models.TextField()
    culoare = models.CharField(
        max_length=7,
        default="#8a3b12",
        help_text="Culoare reprezentativă, în format hex (de exemplu #d98324), folosită la stilizarea categoriei în site.",
    )
    sigla = models.CharField(
        max_length=50,
        default="fa-pepper-hot",
        blank=True,
        help_text="Numele unui icon din FontAwesome (de exemplu fa-leaf). Poate fi lăsat gol.",
    )
    ordine_afisare = models.IntegerField(
        null=True,
        blank=True,
        help_text="Poziția categoriei în meniu. Categoriile fără poziție apar la final.",
    )

    class Meta:
        verbose_name = "categorie"
        verbose_name_plural = "categorii"
        ordering = ["ordine_afisare", "nume"]
        constraints = [
            models.CheckConstraint(
                condition=Q(culoare__startswith="#"),
                name="categorie_culoare_hex",
                violation_error_message="Culoarea trebuie să înceapă cu #.",
            ),
            models.CheckConstraint(
                condition=Q(ordine_afisare__isnull=True) | Q(ordine_afisare__gte=0),
                name="categorie_ordine_pozitiva",
                violation_error_message="Ordinea de afișare nu poate fi negativă.",
            ),
        ]

    def __str__(self):
        return self.nume


class Furnizor(models.Model):
    nume = models.CharField(
        max_length=80,
        unique=True,
        error_messages={
            "unique": "Există deja un furnizor cu acest nume.",
            "max_length": "Numele furnizorului poate avea maxim 80 de caractere.",
        },
    )
    tara_origine = models.CharField(max_length=50)
    email = models.EmailField(
        unique=True,
        null=True,
        blank=True,
        error_messages={
            "unique": "Acest email este deja folosit de alt furnizor.",
            "invalid": "Introdu o adresă de email validă.",
        },
    )
    data_parteneriat = models.DateField(
        default=timezone.localdate,
        help_text="Data de la care colaborăm cu furnizorul. Implicit, data de azi.",
    )

    class Meta:
        verbose_name = "furnizor"
        verbose_name_plural = "furnizori"
        ordering = ["nume"]
        indexes = [
            models.Index(fields=["tara_origine"], name="furnizor_tara_idx"),
        ]

    def __str__(self):
        return f"{self.nume} ({self.tara_origine})"
    
class Eveniment(models.Model):
    TIPURI = [
        ("targ", "Târg"),
        ("degustare", "Degustare"),
        ("atelier", "Atelier"),
    ]

    titlu = models.CharField(
        max_length=100,
        error_messages={
            "max_length": "Titlul evenimentului poate avea maxim 100 de caractere.",
        },
    )
    tip_eveniment = models.CharField(
        max_length=20,
        choices=TIPURI,
        default="targ",
        help_text="Alege tipul evenimentului dintre cele disponibile.",
    )
    locatie = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Adresa sau orașul unde are loc evenimentul. Pentru evenimentele online lasă gol.",
    )
    data_inceput = models.DateField()
    data_sfarsit = models.DateField(
        null=True,
        blank=True,
        help_text="Lasă gol dacă evenimentul durează o singură zi.",
    )

    class Meta:
        verbose_name = "eveniment"
        verbose_name_plural = "evenimente"
        ordering = ["-data_inceput"]
        indexes = [
            models.Index(fields=["data_inceput"], name="eveniment_inceput_idx"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(data_sfarsit__isnull=True) | Q(data_sfarsit__gte=F("data_inceput")),
                name="eveniment_date_corecte",
                violation_error_message="Data de sfârșit nu poate fi înaintea datei de început.",
            ),
        ]

    def __str__(self):
        return f"{self.titlu} ({self.get_tip_eveniment_display()})"


class Produs(models.Model):
    NIVELURI_IUTE = [
        ("nepicant", "Nepicant"),
        ("usor", "Ușor"),
        ("mediu", "Mediu"),
        ("iute", "Iute"),
        ("foarte_iute", "Foarte iute"),
    ]

    nume = models.CharField(
        max_length=100,
        unique=True,
        error_messages={
            "unique": "Există deja un produs cu acest nume.",
            "max_length": "Numele produsului poate avea maxim 100 de caractere.",
        },
    )
    descriere = models.TextField(null=True, blank=True)
    pret = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Prețul în lei, cu maxim două zecimale.",
        error_messages={
            "invalid": "Prețul trebuie să fie un număr, de exemplu 12.50.",
            "max_whole_digits": "Prețul poate avea maxim 6 cifre înainte de virgulă.",
        },
    )
    gramaj_g = models.PositiveIntegerField(
        help_text="Greutatea netă a unui ambalaj, în grame.",
        error_messages={
            "invalid": "Gramajul trebuie să fie un număr întreg.",
        },
    )
    nivel_iute = models.CharField(
        max_length=20,
        choices=NIVELURI_IUTE,
        default="nepicant",
        help_text="Cât de picant este produsul. Folosit la filtrarea din catalog.",
    )
    este_bio = models.BooleanField(default=False)
    data_adaugare = models.DateTimeField(
        default=timezone.now,
        help_text="Data și ora adăugării produsului în catalog. Se completează automat.",
    )
    alergeni = ArrayField(
        models.CharField(max_length=30),
        default=list,
        blank=True,
        help_text="Alergenii conținuți, separați prin virgulă (de exemplu: țelină, muștar). Lasă gol dacă nu are.",
    )
    imagine = models.ImageField(
        upload_to="produse/",
        null=True,
        blank=True,
        help_text="Poza produsului. Poate fi adăugată și mai târziu.",
    )

    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.PROTECT,
        related_name="produse",
    )
    furnizor = models.ForeignKey(
        Furnizor,
        on_delete=models.PROTECT,
        related_name="produse",
    )
    evenimente = models.ManyToManyField(
        Eveniment,
        blank=True,
        related_name="produse",
        help_text="Evenimentele la care este promovat produsul.",
    )

    class Meta:
        verbose_name = "produs"
        verbose_name_plural = "produse"
        ordering = ["nume"]
        indexes = [
            models.Index(fields=["nivel_iute"], name="produs_iute_idx"),
            models.Index(fields=["pret"], name="produs_pret_idx"),
            models.Index(fields=["data_adaugare"], name="produs_data_idx"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(pret__gt=0),
                name="produs_pret_pozitiv",
                violation_error_message="Prețul trebuie să fie mai mare ca 0.",
            ),
            models.CheckConstraint(
                condition=Q(gramaj_g__gt=0),
                name="produs_gramaj_pozitiv",
                violation_error_message="Gramajul trebuie să fie mai mare ca 0.",
            ),
        ]

    def __str__(self):
        return f"{self.nume} ({self.gramaj_g} g)"
    
class ArticolBlog(models.Model):
    titlu = models.CharField(
        max_length=150,
        error_messages={
            "max_length": "Titlul articolului poate avea maxim 150 de caractere.",
        },
    )
    slug = models.SlugField(
        max_length=150,
        unique=True,
        help_text="Partea din adresa articolului, doar litere mici, cifre și cratime (de exemplu: cum-folosesti-turmericul).",
        error_messages={
            "unique": "Există deja un articol cu acest slug.",
            "invalid": "Slug-ul poate conține doar litere, cifre, cratime și underscore.",
        },
    )
    continut = models.TextField()
    data_publicare = models.DateField(default=timezone.localdate)
    autor = models.CharField(max_length=80, default="Echipa Aroma Lumii")
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articole",
        help_text="Categoria de produse despre care vorbește articolul. Poate rămâne necompletată.",
    )

    class Meta:
        verbose_name = "articol de blog"
        verbose_name_plural = "articole de blog"
        ordering = ["-data_publicare", "titlu"]
        constraints = [
            models.CheckConstraint(
                condition=Q(autor__gt=""),
                name="articol_autor_completat",
                violation_error_message="Autorul nu poate fi gol.",
            ),
        ]

    def __str__(self):
        return self.titlu


class LotProdus(models.Model):
    produs = models.ForeignKey(
        Produs,
        on_delete=models.CASCADE,
        related_name="loturi",
        help_text="Produsul din care face parte lotul. Dacă produsul este șters, se șterg și loturile lui.",
    )
    nr_lot = models.PositiveIntegerField(
        help_text="Numărul lotului în cadrul produsului (1, 2, 3...). Se repetă între produse diferite.",
    )
    data_receptie = models.DateField(default=timezone.localdate)
    data_expirare = models.DateField()
    cantitate_kg = models.FloatField(
        help_text="Cantitatea primită în lot, în kilograme.",
        error_messages={
            "invalid": "Cantitatea trebuie să fie un număr, de exemplu 2.5.",
        },
    )

    class Meta:
        verbose_name = "lot de produs"
        verbose_name_plural = "loturi de produse"
        ordering = ["produs", "nr_lot"]
        constraints = [
            # entitate slabă: un lot e identificat prin (produs, nr_lot)
            models.UniqueConstraint(
                fields=["produs", "nr_lot"],
                name="lot_unic_per_produs",
                violation_error_message="Acest produs are deja un lot cu acest număr.",
            ),
            models.CheckConstraint(
                condition=Q(data_expirare__gt=F("data_receptie")),
                name="lot_expirare_dupa_receptie",
                violation_error_message="Data expirării trebuie să fie după data recepției.",
            ),
            models.CheckConstraint(
                condition=Q(cantitate_kg__gt=0),
                name="lot_cantitate_pozitiva",
                violation_error_message="Cantitatea trebuie să fie mai mare ca 0.",
            ),
        ]

    def __str__(self):
        return f"{self.produs.nume} – lotul {self.nr_lot}"