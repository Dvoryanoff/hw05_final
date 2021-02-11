import datetime as dt


def year(request):  # noqa
    date = dt.datetime.today().year
    return {
        'year': date
    }
