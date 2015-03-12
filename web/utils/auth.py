# http://www.djangosnippets.org/snippets/501/
import ldap
from django.conf import settings
from users.models import User


class ActiveDirectoryBackend:

    supports_object_permissions = False
    supports_anonymous_user = False
    supports_inactive_user = False

    def authenticate(self, username=None, password=None):
        if username:
            username = username.lower()
        if not self.is_valid(username, password):
            return None
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            l = ldap.initialize(settings.AD_LDAP_URL)
            binddn = '%s@%s' % (username, settings.AD_NT4_DOMAIN)
            l.simple_bind_s(binddn, password)
            result = l.search_ext_s(settings.AD_SEARCH_DN, ldap.SCOPE_SUBTREE,
                                    'sAMAccountName=%s' % username, settings.AD_SEARCH_FIELDS)[0][1]
            l.unbind_s()

            # givenName == First Name
            if 'givenName' in result:
                first_name = result['givenName'][0]
            else:
                first_name = None

            # sn == Last Name (Surname)
            if 'sn' in result:
                last_name = result['sn'][0]
            else:
                last_name = None

            # mail == Email Address
            if 'mail' in result:
                email = result['mail'][0]
            else:
                email = None

            user = User(username=username, first_name=first_name, last_name=last_name, email=email)
            user.is_staff = False
            user.is_superuser = False
            user.set_password(password)
            user.save()
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def is_valid(self, username=None, password=None):
        # Disallowing null or blank string as password
        # as per comment: http://www.djangosnippets.org/snippets/501/#c868
        if password is None or password == '':
            return False
        if username:
            username = username.lower()
        binddn = '%s@%s' % (username, settings.AD_NT4_DOMAIN)
        try:
            l = ldap.initialize(settings.AD_LDAP_URL)
            l.simple_bind_s(binddn, password)
            l.unbind_s()
            return True
        except ldap.LDAPError:
            return False
