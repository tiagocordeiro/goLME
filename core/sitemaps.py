from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse


class StaticViewSitemap(Sitemap):
    def items(self):
        return ['index', 'chart', 'summary', 'about', 'docs', 'group_by_week', 'profile_update']

    def location(self, item):
        return reverse(item)
