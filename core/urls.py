from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    ProfileView,
    DeleteAccountView,
    ProductsView,
    OrdersView,
    CustomersView,
    InitializeSystemView,
    APIRootView,
    RoleViewSet,
    AccessRuleViewSet,
    BusinessElementViewSet,
    UserRoleViewSet
)

router = DefaultRouter()
router.register(r'admin/roles', RoleViewSet)
router.register(r'admin/access-rules', AccessRuleViewSet)
router.register(r'admin/elements', BusinessElementViewSet)
router.register(r'admin/user-roles', UserRoleViewSet)

urlpatterns = [
    path('', APIRootView.as_view(), name='api-root'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('delete-account/', DeleteAccountView.as_view(), name='delete-account'),
    path('products/', ProductsView.as_view(), name='products'),
    path('orders/', OrdersView.as_view(), name='orders'),
    path('customers/', CustomersView.as_view(), name='customers'),
    path('init/', InitializeSystemView.as_view(), name='init-system'),
    path('admin/', include(router.urls)),
]