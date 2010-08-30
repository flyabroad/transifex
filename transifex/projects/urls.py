# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib.auth.decorators import login_required
from tagging.views import tagged_object_list

from projects.feeds import LatestProjects, ProjectFeed, ReleaseFeed, \
    ReleaseLanguageFeed
from projects.models import Project
from projects.permissions import pr_component_submit_file
from projects.views import *
from projects.views.project import *
from projects.views.component import *
from projects.views.permission import *
from projects.views.review import *
from projects.views.team import *
from projects.views.release import *

from txcommon.decorators import one_perm_required_or_403
from webtrans.wizards import TransFormWizard

from transifex.urls import PROJECTS_URL

project_list = {
    'queryset': Project.objects.all(),
    'template_object_name': 'project',
}

public_project_list = {
    'queryset': Project.public.all(),
    'template_object_name': 'project',
    'extra_context' : {'type_of_qset' : 'projects.all',},
}

feeds = {
    'latest': LatestProjects,
    'project': ProjectFeed,
    'release': ReleaseFeed,
    'release_language': ReleaseLanguageFeed,
}

# Used only in urls already under projects/, such as this one and
# resources/urls.py. For addons, use PROJECT_URL instead.
PROJECT_URL_PARTIAL = 'p/(?P<project_slug>[-\w]+)/'

# Full URL (including /projects/ prefix)
PROJECT_URL = PROJECTS_URL + PROJECT_URL_PARTIAL

#TODO: Temporary until we import view from a common place
urlpatterns = patterns('',
    url(
        regex = r'^feed/$',
        view = 'projects.views.slug_feed',
        name = 'project_latest_feed',
        kwargs = {'feed_dict': feeds,
                  'slug': 'latest'}),
    url(
        regex = '^p/(?P<param>[-\w]+)/components/feed/$',
        view = 'projects.views.project_feed',
        name = 'project_feed',
        kwargs = {'feed_dict': feeds,
                  'slug': 'project'}),
)


# Project
urlpatterns += patterns('',
    url(
        regex = '^add/$',
        view = project_create,
        name = 'project_create'),
    url(
        regex = PROJECT_URL_PARTIAL+r'edit/$',
        view = project_update,
        name = 'project_edit',),
    url(
        regex = PROJECT_URL_PARTIAL+r'edit/access/$',
        view = project_access_control_edit,
        name = 'project_access_control_edit',),
    url(
        regex = PROJECT_URL_PARTIAL+r'delete/$',
        view = project_delete,
        name = 'project_delete',),
    url(
        regex = PROJECT_URL_PARTIAL+r'access/pm/add/$',
        view = project_add_permission,
        name = 'project_add_permission'),
    url(
        regex = PROJECT_URL_PARTIAL+r'access/pm/(?P<permission_pk>\d+)/delete/$',
        view = project_delete_permission,
        name = 'project_delete_permission'),
    #url(
        #regex = PROJECT_URL_PARTIAL+r'access/rq/add/$',
        #view = project_add_permission_request,
        #name = 'project_add_permission_request'),
    url(
        regex = PROJECT_URL_PARTIAL+r'access/rq/(?P<permission_pk>\d+)/delete/$',
        view = project_delete_permission_request,
        name = 'project_delete_permission_request'),
        
    url(regex = PROJECT_URL_PARTIAL+r'access/rq/(?P<permission_pk>\d+)/approve/$',
        view = project_approve_permission_request,
        name = "project_approve_permission_request"),
    url(
        regex = PROJECT_URL_PARTIAL+r'$',
        view = project_detail,
        name = 'project_detail'),
)
      

urlpatterns += patterns('django.views.generic',
    url(
        regex = '^$',
        view = 'list_detail.object_list',
        kwargs = public_project_list,
        name = 'project_list'),
    url(
        '^recent/$', 'list_detail.object_list',
        kwargs = {
            'queryset': Project.public.recent(),
            'template_object_name': 'project',
            'extra_context' : {'type_of_qset' : 'projects.recent',},
        },
        name = 'project_list_recent'),
    url (
        regex = '^open_translations/$',
        view = 'list_detail.object_list',
        kwargs = {
            'queryset': Project.public.open_translations(),
            'template_object_name': 'project',
            'extra_context' : {'type_of_qset' : 'projects.open_translations',},
        },
        name = 'project_list_open_translations'),
    url(
        r'^tag/(?P<tag>[^/]+)/$',
        tagged_object_list,
        dict(queryset_or_model=Project, allow_empty=True,
             template_object_name='project'),
        name='project_tag_list'),
)

# Components

COMPONENT_URL = PROJECT_URL_PARTIAL + r'c/(?P<component_slug>[-\w]+)/'

urlpatterns += patterns('',
    url(
        regex = PROJECT_URL_PARTIAL+r'add-component/$',
        view = component_create_update,
        name = 'component_create',),
    url(
        regex = COMPONENT_URL+r'edit/checkout/$',
        view = component_create_update,
        name = 'component_edit',),
    url(
        regex = COMPONENT_URL+r'edit/submission/$',
        view = component_submission_edit,
        name = 'component_submission_edit',),
    url(
        regex = COMPONENT_URL+r'delete/$',
        view = component_delete,
        name = 'component_delete',),
    url(
        regex = COMPONENT_URL+r'clear_cache/$',
        view = component_clear_cache,
        name = 'component_clear_cache',),
    url(
        regex = COMPONENT_URL+r'set_stats/$',
        view = component_set_stats,
        name = 'component_set_stats',),
    url(
        regex = COMPONENT_URL+r'raw/(?P<filename>[_\./\-@\w]+)/$',
        view = component_file,
        name = 'component_raw_file',),
    url(
        regex = COMPONENT_URL+r'view/(?P<filename>[_\./\-@\w]+)/$',
        view = component_file,
        name = 'component_view_file',
        kwargs = {'view': True },),
    url(
        regex = COMPONENT_URL+r'submit/(?P<filename>[_\./\-@\w]+)/$',
        view = component_submit_file,
        name = 'component_submit_file',),
    url(
        regex = COMPONENT_URL+r'submit/$',
        view = component_submit_file,
        name = 'component_submit_new_file',),
    url(
        regex = COMPONENT_URL+r'l/(?P<language_code>(.*))/$',
        view = component_language_detail,
        name = 'component_language_detail',),
    url (
        regex = '^p/(?P<slug>[-\w]+)/component-added/$',
        view = 'django.views.generic.list_detail.object_detail',
        kwargs = {'object_list': project_list,
                  'message': 'Component added.' },
        name = 'component_created'),
    url(
        regex = COMPONENT_URL+r'$',
        view = component_detail,
        name = 'component_detail'),
)

# Releases

RELEASE_URL = PROJECT_URL_PARTIAL + r'r/(?P<release_slug>[-\w]+)/'

urlpatterns += patterns('',
    url(
        regex = RELEASE_URL+r'feed/$',
        view = release_feed,
        name = 'release_feed',
        kwargs = {'feed_dict': feeds,
                  'slug': 'release'}),
    url(
        regex = RELEASE_URL+r'l/(?P<language_code>[\-_@\w]+)/feed/$',
        view = release_language_feed,
        name = 'release_language_feed',
        kwargs = {'feed_dict': feeds,
                  'slug': 'release_language'}),
)

urlpatterns += patterns('',
    url(
        regex = PROJECT_URL_PARTIAL+r'add-release/$',
        view = release_create_update,
        name = 'release_create',),
    url(
        regex = RELEASE_URL+r'$',
        view = release_detail,
        name = 'release_detail'),
    url(
        regex = RELEASE_URL+r'edit/$',
        view = release_create_update,
        name = 'release_edit',),
    url(
        regex = RELEASE_URL+r'delete/$',
        view = release_delete,
        name = 'release_delete',),
    url(
        regex = RELEASE_URL+r'l/(?P<language_code>[\-_@\w]+)/$',
        view = release_language_detail,
        name = 'release_language_detail',
    ),
)

if getattr(settings, 'ENABLE_COMPRESSED_DOWNLOAD', True):
    urlpatterns += patterns('',
        url(
            name = 'release_language_download',
            regex = RELEASE_URL+r'l/(?P<language_code>[\-_@\w]+)/download_(?P<filetype>[\w]+)/$',
            view = release_language_download,
        ),
)

# Teams

TEAM_URL = PROJECT_URL_PARTIAL + r'team/(?P<language_code>[\-_@\w]+)/'

urlpatterns += patterns('',
    url(
        regex = PROJECT_URL_PARTIAL+r'teams/add/$',
        view = team_create,
        name = 'team_create',),
    url(
        regex = TEAM_URL+r'edit/$',
        view = team_update,
        name = 'team_update',),
    url(
        regex = PROJECT_URL_PARTIAL+r'teams/$',
        view = team_list,
        name = 'team_list',),
    url(
        regex = TEAM_URL+r'$',
        view = team_detail,
        name = 'team_detail',),
    url(
        regex = TEAM_URL+r'delete/$',
        view = team_delete,
        name = 'team_delete',),
    url(
        regex = TEAM_URL+r'request/$',
        view = team_join_request,
        name = 'team_join_request',),
    url(
        regex = TEAM_URL+r'approve/(?P<username>[-\w]+)/$',
        view = team_join_approve,
        name = 'team_join_approve',),
    url(
        regex = TEAM_URL+r'deny/(?P<username>[-\w]+)/$',
        view = team_join_deny,
        name = 'team_join_deny',),
    url(
        regex = TEAM_URL+r'withdraw/$',
        view = team_join_withdraw,
        name = 'team_join_withdraw',),
    url(
        regex = TEAM_URL+r'leave/$',
        view = team_leave,
        name = 'team_leave',),
    url(
        regex = PROJECT_URL_PARTIAL+r'teams/request/$',
        view = team_request,
        name = 'team_request',),
    url(
        regex = TEAM_URL+r'approve/$',
        view = team_request_approve,
        name = 'team_request_approve',),
    url(
        regex = TEAM_URL+r'deny/$',
        view = team_request_deny,
        name = 'team_request_deny',),
)

# Reviews
urlpatterns += patterns('',
    url(
        regex = COMPONENT_URL+r'reviews/$',
        view = review_list,
        name = 'review_list',),
    url(
        regex = COMPONENT_URL+r'reviews/(?P<id>\d+)/modify/$',
        view = review_modify,
        name = 'review_modify',),
)

# Resources
urlpatterns += patterns('',
    url('', include('resources.urls')),
)

#TODO: Make this setting work throughout the applications
if getattr(settings, 'ENABLE_WEBTRANS', True):
    urlpatterns += patterns('',
        url(
            regex = (COMPONENT_URL+r''
                    'edit/(?P<filename>[_\./\-@\w]+)/$'),
            # It needs to pass through both 'login_required'
            view = login_required(TransFormWizard(key=None, form_list=[])),
            name = 'component_edit_file',),
        )
