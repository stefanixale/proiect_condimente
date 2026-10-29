from django.contrib import admin

from .models import Categorie, Furnizor, Eveniment, Produs, ArticolBlog, LotProdus


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ("nume", "culoare", "sigla", "ordine_afisare")


@admin.register(Furnizor)
class FurnizorAdmin(admin.ModelAdmin):
    list_display = ("nume", "tara_origine", "email", "data_parteneriat")


@admin.register(Eveniment)
class EvenimentAdmin(admin.ModelAdmin):
    list_display = ("titlu", "tip_eveniment", "locatie", "data_inceput", "data_sfarsit")


@admin.register(Produs)
class ProdusAdmin(admin.ModelAdmin):
    list_display = ("nume", "categorie", "furnizor", "pret", "gramaj_g", "nivel_iute", "este_bio")
    list_filter = ("categorie", "nivel_iute", "este_bio")
    search_fields = ("nume",)
    filter_horizontal = ("evenimente",)


@admin.register(ArticolBlog)
class ArticolBlogAdmin(admin.ModelAdmin):
    list_display = ("titlu", "autor", "data_publicare", "categorie")
    prepopulated_fields = {"slug": ("titlu",)}


@admin.register(LotProdus)
class LotProdusAdmin(admin.ModelAdmin):
    list_display = ("produs", "nr_lot", "data_receptie", "data_expirare", "cantitate_kg")