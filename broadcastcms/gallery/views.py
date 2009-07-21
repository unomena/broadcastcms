from django.shortcuts import render_to_response, get_object_or_404

from models import Gallery


def gallery_xml(request, slug):
    gallery = get_object_or_404(Gallery, slug=slug)
    context = {'gallery':gallery}
    return render_to_response('feeds/gallery.xml', context)
