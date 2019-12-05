from django.apps import apps
from .panels import Panel

class Form:
    def __init__(self, panels=None, model=None, form_mode='edit'):
        if isinstance(panels, Panel):
            self.panels = [panels]
        elif panels:
            self.panels = panels
        else:
            self.panels = []
        self.model = model
        self.form_mode = form_mode

    @property
    def model(self):
        return getattr(self, '_model', None)

    @model.setter
    def model(self, value):
        if isinstance(value, str):
            self._model = apps.get_model(*value.split('.'))
        else:
            self._model = value

        for panel in self.panels:
            panel.model = self._model

    @property
    def form_mode(self):
        return getattr(self, '_form_mode', 'edit')

    @form_mode.setter
    def form_mode(self, value):
        self._form_mode = value

        for panel in self.panels:
            panel.form_mode = value

    @property
    def data_panels(self):
        for panel in self.panels:
            yield from panel.data_panels

    def serialize(self):
        return dict(
                object = 'form',
                panels = [panel.serialize() for panel in self.panels],
                form_mode = self.form_mode,
                )
