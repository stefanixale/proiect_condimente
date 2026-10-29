from .views import Accesare, PREFIX_APLICATIE


def get_ip(request):
    str_lista_ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if str_lista_ip:
        return str_lista_ip.split(',')[-1].strip()
    return request.META.get('REMOTE_ADDR')


class MiddlewareAccesari:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.ip = get_ip(request)

        if request.path.startswith(PREFIX_APLICATIE):
            accesare = Accesare(
                ip_client=request.ip,
                url=request.build_absolute_uri(),
                parametri=dict(request.GET.lists()),
            )
            request.accesare = accesare
            print(accesare)
            print()

        return self.get_response(request)