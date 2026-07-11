from django.contrib import admin
from django.urls import path
from petappcore import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [

    # ================= ADMIN =================
    path('admin/', admin.site.urls),
    path('admin_signup/', views.admin_signup, name='admin_signup'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    

    path('admin-reports/', views.admin_reports, name='admin_reports'),
    path('approved-reports/', views.approved_reports, name='approved_reports'),
    
    path('admin-users/', views.admin_users, name='admin_users'),
    path(
    "admin-users/<int:user_id>/",
    views.admin_user_details,
    name="admin_user_details"
),
    path(
    "admin-users/delete/<int:user_id>/",
    views.delete_user,
    name="delete_user"
),
    path(
    "claim-request/<str:pet_type>/<int:pet_id>/",
    views.send_claim_request,
    name="send_claim_request"
),


    path('adoption/', views.adopt_pet, name='adopt_pet'),

    path('admin/lost-requests/', views.admin_lost_requests, name='admin_lost_requests'),
    path('admin/found-requests/', views.admin_found_requests, name='admin_found_requests'),
    path('admin/pending-tasks/', views.admin_pending_tasks, name='admin_pending_tasks'),

    # Adoption approval (ADMIN)
    path('admin/adoption/approve/<int:request_id>/', views.approve_adoption, name='approve_adoption'),
    path('admin/adoption/reject/<int:request_id>/', views.reject_adoption, name='reject_adoption'),

    # ================= PUBLIC =================
    path('', views.public_home, name='public_home'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(next_page='public_home'), name='logout'),

    # ================= USER =================
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('change-password/', views.change_password, name='change_password'),

    # ================= PET DETAILS =================
    path('pet/<str:pet_type>/<int:pet_id>/', views.pet_details, name='pet_details'),

    # ================= REPORT FORMS =================
    path('report/found/', views.report_found_pet, name='report_found_pet'),
    path('report/lost/', views.report_lost_pet, name='report_lost_pet'),

    # ================= ADOPTION =================
    path("adopt-request/<int:pet_id>/", views.adopt_request, name="adopt_request"),
    path(
    "dashboard/check-lost-pet/",
    views.search_found_pets,
    name="search_found_pets"
    ),

    path(
    "admin/chat-requests/",
    views.admin_chat_requests,
    name="admin_chat_requests"
),
    path(
    "admin/chat-requests/<int:request_id>/",
    views.admin_chat_request_detail,
    name="admin_chat_request_detail"
),
  
    # urls.py
    
    path(
    "admin/chat-requests/<int:request_id>/approve/",
    views.approve_chat_request,
    name="approve_chat_request"
),
    path(
    "admin/chat-requests/<int:request_id>/reject/",
    views.reject_chat_request,
    name="reject_chat_request"
),
    path(
        "staff/chat-room/<int:request_id>/close/",
        views.close_chat,
        name="close_chat"
    ),
    path("chat-room/<int:request_id>/", views.chat_room, name="chat_room"),

    path(
    "staff/chat-room/<int:request_id>/add-reporter/",
    views.add_reporter,
    name="add_reporter"
),
    path(
    "chats/",
    views.user_chats,
    name="user_chats"
),






    path('adopt/', views.adopt_pet, name='adopt_pet'),
    

    # ================= CLAIMS =================


    # ================= STATUS UPDATES =================
    path('admin/lost-status/<int:report_id>/<str:action>/', views.update_lost_status, name="update_lost_status"),
    path('report/<int:report_id>/<str:action>/', views.update_report_status, name='update_report_status'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
