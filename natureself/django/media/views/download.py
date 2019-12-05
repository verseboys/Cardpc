from django.http import FileResponse

from natureself.django.core import api
from natureself.django.media.models import Image, Document, Slide

"""
下载文件

GET /download/documents/<str:key>

会设置 Content-Dispositon 头，因此浏览器会弹出下载另存为对话框。
另存为对话框中，默认的文件名为此前设置的 filename。
"""
def download_file(request, key, model):
    if model == 'image':
        Model = Image
    elif model == 'document':
        Model = Document
    elif model == 'slide':
        Model = Slide
    else:
        raise Exception(f'unknown model: {model}')

    try:
        file = Model.objects.filter(deleted_at__isnull=True).get(key=key)
    except Model.DoesNotExist:
        # TODO should return 404 webpage instead of json
        return api.not_found()

    # as django document claimed, we don't need to open the file with a context manager,
    # FileResponse will close it automatically.
    # see: https://docs.djangoproject.com/en/2.2/ref/request-response/#fileresponse-objects
    return FileResponse(open(file.local_abs_path, 'rb'), as_attachment=True, filename=file.filename)
