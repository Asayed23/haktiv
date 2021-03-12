from django.urls import path, include
from rest_framework import routers
from rest_framework_nested import routers as nested_routers

from .views import ProgramView, ProgramTriagerView, ProgramTypeTagView, ProgramRewardView, ProgramReportView, \
    AllProgramReportView, ProgramVulnerabilityView, ProgramReportActivityView, ProgramScopeView, \
    PushedProgramReportView, ProgramReportRewardView, EarningView, ResearcherDashboardView, TriagerDashboardView

app_name = "api_programs"

router = nested_routers.DefaultRouter()
router.register('', ProgramView)

program_triager_router = nested_routers.DefaultRouter()
program_triager_router.register('', ProgramTriagerView, basename='program-triager')

report_router = nested_routers.NestedDefaultRouter(router, '', lookup='program')
report_router.register('report', ProgramReportView, basename='program-report')

reward_router = nested_routers.NestedDefaultRouter(router, '', lookup='program')
reward_router.register('reward', ProgramRewardView, basename='program-reward')
# router.register(r'reward', ProgramRewardView)

scope_router = nested_routers.NestedDefaultRouter(router, '', lookup='program')
scope_router.register('scope', ProgramScopeView, basename='program-scope')

report_vulnerability_router = routers.DefaultRouter()
report_vulnerability_router.register('', ProgramVulnerabilityView)

all_report_router = nested_routers.DefaultRouter()
all_report_router.register('', AllProgramReportView)

report_activity_router = nested_routers.NestedDefaultRouter(all_report_router, '', lookup='report')
report_activity_router.register('activity', ProgramReportActivityView, basename='program-report-activity')

pushed_report_router = nested_routers.NestedDefaultRouter(all_report_router, '', lookup='report')
pushed_report_router.register('report', PushedProgramReportView, basename='pushed-program-report')

report_reward_router = nested_routers.NestedDefaultRouter(all_report_router, '', lookup='report')
report_reward_router.register('reward', ProgramReportRewardView, basename='program-report-reward')

earning_router = routers.DefaultRouter()
earning_router.register('', EarningView)

researcher_dashboard_router = routers.DefaultRouter()
researcher_dashboard_router.register('', ResearcherDashboardView)

triager_dashboard_router = routers.DefaultRouter()
triager_dashboard_router.register('', TriagerDashboardView)

urlpatterns = [
    path('board/', include(arg=[
        path('', include(earning_router.urls)),
        path('researcher/<str:username>/', include(researcher_dashboard_router.urls)),
        path('triager/<str:username>/', include(triager_dashboard_router.urls)),
    ])),
    path('program/', include(arg=[
        path('tags/', ProgramTypeTagView.as_view({'get': 'list'}), name="program_view",),
        path('', include(router.urls)),
        path('', include(report_router.urls)),
        path('', include(reward_router.urls)),
        path('', include(scope_router.urls)),
    ])),
    path('triager/', include(arg=[
        path('program/', include(program_triager_router.urls)),
    ])),
    path('report/', include(arg=[
        path('vulnerability/', include(report_vulnerability_router.urls)),
        path('', include(all_report_router.urls)),
        path('pushed/', include(pushed_report_router.urls)),
        path('reward/', include(report_reward_router.urls)),
        path('', include(report_activity_router.urls)),
    ])),
]
