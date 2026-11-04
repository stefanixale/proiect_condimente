import csv

from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html

from .models import Categorie, Furnizor, Eveniment, Produs, ArticolBlog, LotProdus

# ---------- personalizarea paginii de administrare ----------
admin.site.site_title = "Aroma Lumii – administrare"          # titlul tab-ului din browser
admin.site.site_header = "Aroma Lumii – panou de administrare"  # textul din antet
admin.site.index_title = "Gestionarea magazinului de condimente"  # titlul paginii principale
admin.site.site_url = "/aplicatie_condimente/"                # butonul "View site"


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ("nume", "culoare_afisata", "sigla", "ordine_afisare")
    search_fields = ("nume", "descriere")
    search_help_text = "Caută după numele sau descrierea categoriei."

    @admin.display(description="Culoare", ordering="culoare")
    def culoare_afisata(self, obj):
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;border-radius:4px;">{}</span>',
            obj.culoare,
            obj.culoare,
        )


@admin.register(Furnizor)
class FurnizorAdmin(admin.ModelAdmin):
    list_display = ("nume", "tara_origine", "email", "data_parteneriat")
    list_filter = ("tara_origine",)
    search_fields = ("nume", "tara_origine")
    search_help_text = "Caută după numele furnizorului sau după țara de origine."


@admin.register(Eveniment)
class EvenimentAdmin(admin.ModelAdmin):
    list_display = ("titlu", "tip_eveniment", "locatie", "data_inceput", "data_sfarsit")
    list_filter = ("tip_eveniment",)
    search_fields = ("titlu", "locatie")
    search_help_text = "Caută după titlul sau locația evenimentului."


@admin.register(ArticolBlog)
class ArticolBlogAdmin(admin.ModelAdmin):
    list_display = ("titlu", "autor", "data_publicare", "categorie")
    search_fields = ("titlu", "continut")
    search_help_text = "Caută după titlul sau conținutul articolului."
    prepopulated_fields = {"slug": ("titlu",)}


@admin.register(LotProdus)
class LotProdusAdmin(admin.ModelAdmin):
    list_display = ("produs", "nr_lot", "data_receptie", "data_expirare", "cantitate_kg")
    search_fields = ("produs__nume", "produs__categorie__nume")
    search_help_text = "Caută după numele produsului sau al categoriei lui."
    
@admin.register(Produs)
class ProdusAdmin(admin.ModelAdmin):
    # ordinea coloanelor din lista de produse
    list_display = ("nume", "categorie", "furnizor_info", "pret", "gramaj_g",
                    "stoc_afisat", "nivel_iute", "este_bio")
    list_filter = ("categorie", "nivel_iute", "este_bio", "furnizor")   # filtre laterale
    search_fields = ("nume", "descriere")
    search_help_text = "Caută după numele sau după descrierea produsului."
    ordering = ("-pret",)            # cele mai scumpe produse primele
    list_per_page = 5                # 5 produse pe pagină
    list_select_related = ("categorie", "furnizor")
    filter_horizontal = ("evenimente",)
    actions = ["exporta_csv", "reaproviziona"]

    # formularul, împărțit în două secțiuni (a doua e colapsabilă și are doar câmpuri opționale)
    fieldsets = (
        ("Informații principale", {
            "fields": ("nume", "categorie", "furnizor", "pret", "gramaj_g",
                       "nivel_iute", "este_bio", "stoc", "data_adaugare"),
        }),
        ("Detalii suplimentare (opțional)", {
            "classes": ("collapse",),
            "fields": ("descriere", "imagine", "alergeni", "taguri", "evenimente"),
        }),
    )

    @admin.display(description="Furnizor", ordering="furnizor__nume")
    def furnizor_info(self, obj):
        # caracteristici ale entității legate prin one-to-many (furnizorul produsului)
        return f"{obj.furnizor.nume} ({obj.furnizor.tara_origine})"

    @admin.display(description="Stoc", ordering="stoc")
    def stoc_afisat(self, obj):
        if obj.stoc < settings.STOC_MIN:
            return format_html('<b style="color:#c00000;">{} (limitat)</b>', obj.stoc)
        return format_html('<span style="color:#2e7d32;">{}</span>', obj.stoc)

    @admin.action(description="Exportă produsele selectate în CSV")
    def exporta_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="produse.csv"'
        response.write("\ufeff")   # ca Excel să citească corect diacriticele
        writer = csv.writer(response)
        writer.writerow(["nume", "categorie", "furnizor", "pret", "gramaj_g", "nivel_iute", "stoc", "taguri"])
        for p in queryset.select_related("categorie", "furnizor"):
            writer.writerow([p.nume, p.categorie.nume, p.furnizor.nume, p.pret,
                             p.gramaj_g, p.get_nivel_iute_display(), p.stoc, ", ".join(p.taguri)])
        return response

    @admin.action(description="Reaprovizionează: setează stocul la 50")
    def reaproviziona(self, request, queryset):
        nr = queryset.update(stoc=50)
        self.message_user(request, f"Stocul a fost setat la 50 pentru {nr} produse.")