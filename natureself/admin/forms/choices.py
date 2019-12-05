from django.urls import reverse

class ApiChoices:
    def __init__(self, url_name, kwargs=None, queries=None, value_field='id', label_field='id'):
        self.url_name = url_name
        self.kwargs = kwargs
        self.queries = queries
        self.value_field = value_field
        self.label_field = label_field

    @property
    def url(self):
        url = reverse(self.url_name, kwargs=self.kwargs)
        if self.queries:
            url = f'{url}?{urlencode(self.queries)}'

        return url

    def serialize(self):
        return dict(
                type='url',
                url=self.url,
                value_field=self.value_field,
                label_field=self.label_field,
                )

class TupleChoices:
    def __init__(self, choices):
        self.choices = choices

    def serialize(self):
        return dict(
                type='list',
                choices = [ dict(value=value, label=label) for (value, label) in self.choices if value != '' ],
                )
