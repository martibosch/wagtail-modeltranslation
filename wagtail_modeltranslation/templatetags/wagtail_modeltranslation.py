# coding: utf-8

import re

from django import template
from django.core.urlresolvers import resolve
from django.http import Http404
from django.utils.translation import activate, get_language
from six import iteritems

from wagtail.contrib.wagtailroutablepage.models import RoutablePageMixin

register = template.Library()


# TODO: check templatetag usage

# CHANGE LANGUAGE
@register.simple_tag(takes_context=True)
def translated_url(context, lang=None, *args, **kwargs):
    current_language = get_language()

    if 'request' in context and lang and current_language:
        request = context['request']
        match = resolve(request.path)
        non_prefixed_path = re.sub(
            current_language + '/', '', request.path, count=1)

        # means that is an wagtail page object
        if match.url_name == 'wagtail_serve':
            path_components = [
                component for component in non_prefixed_path.split('/')
                if component]
            page, args, kwargs = request.site.root_page.specific.route(
                request, path_components)

            if isinstance(page, RoutablePageMixin):
                page_path_components = [
                    component for component in page.url.split('/')
                    if component]
                # see what comes after the page url i.e. the subpage path
                remainder = path_components[path_components.index(
                    page_path_components[-1]) + 1:]
                try:
                    # there must be '/' both at the beginning and end
                    view, args, kwargs = page.resolve_subpage(
                        '/' + '/'.join(remainder) + '/')
                    activate(lang)
                    translated_url = page.url + \
                        page.reverse_subpage(view.__name__, args)
                    activate(current_language)
                    return translated_url
                except Http404:
                    # if no subpage match was found, just return the main page
                    pass

            activate(lang)
            translated_url = page.url
            activate(current_language)

            return translated_url
        elif match.url_name == 'wagtailsearch_search':
            path_components = [
                component for component in non_prefixed_path.split('/')
                if component]

            translated_url = '/' + lang + '/' + path_components[0] + '/'
            if request.GET:
                translated_url += '?'
                for key, value in iteritems(request.GET):
                    translated_url += key + '=' + value
            return translated_url

    return ''
