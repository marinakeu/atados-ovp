from collections import OrderedDict

from django.test import TestCase
from django.core import mail
from django.utils import timezone

from dateutil.relativedelta import relativedelta
from django.utils import timezone

from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from ovp.apps.core.helpers import get_email_subject, is_email_enabled
from ovp.apps.channels.models import Channel
from ovp.apps.users.models import User
from ovp.apps.organizations.models import Organization, OrganizationInvite
from ovp.apps.projects.models import Project
from ovp.apps.gallery.models import Gallery
from ovp.apps.core.models import Cause
from ovp.apps.core.models import Skill
from ovp.apps.core.utils import present_in_list

import copy

base_organization = {
    "name": "test organization",
    "slug": "test-override-slug",
    "description": "test description",
    "details": "test details",
    "type": 0,
    "address": {
        "typed_address": "r. tecainda, 81, sao paulo"
    },
    "causes": [
        {"id": 1},
        {"id": 2}
    ],
    "contact_name": "test contact name",
    "contact_phone": "+551112345678",
    "contact_email": "test@contact.com"
}


class OrganizationResourceViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_cant_create_organization_unauthenticated(self):
        """
        Assert that it's not possible to create an
        organization while unauthenticated
        """
        response = self.client.post(
            reverse("organization-list"), {}, format="json")

        self.assertTrue(
            response.data["detail"]
            == "Authentication credentials were not provided."
        )
        self.assertTrue(response.status_code == 401)

    def test_can_create_organization(self):
        """
        Assert that it's possible to create a organization while authenticated
        """
        user = User.objects.create_user(
            email="test_can_create_organization@gmail.com",
            password="testcancreate",
            object_channel="default"
        )
        data = copy.deepcopy(base_organization)

        Channel.objects.create(slug="test-channel")
        c = Cause.objects.create(
            name="other-channel",
            object_channel="test-channel"
        )
        data["causes"].append({"id": c.id})

        g1 = Gallery.objects.create(
            name="test", owner=user, object_channel="default")
        g2 = Gallery.objects.create(
            name="other-channel",
            owner=user,
            object_channel="test-channel")
        data["galleries"] = [{"id": g1.id}, {"id": g2.id}]

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post(
            reverse("organization-list"),
            data,
            format="json")

        self.assertTrue(response.data["id"])
        self.assertTrue(response.data["name"] == data["name"])
        self.assertTrue(response.data["slug"] == "test-organization")
        self.assertTrue(response.data["details"] == data["details"])
        self.assertTrue(response.data["description"] == data["description"])
        self.assertTrue(response.data["contact_name"] == data["contact_name"])
        self.assertTrue(
            response.data["contact_phone"] == data["contact_phone"])
        self.assertTrue(
            response.data["contact_email"] == data["contact_email"])
        self.assertTrue(len(response.data["causes"]) == 3)
        self.assertTrue(len(response.data["galleries"]) == 2)

        organization = Organization.objects.get(pk=response.data["id"])
        self.assertTrue(organization.owner.id == user.id)
        self.assertTrue(user in organization.members.all())
        self.assertTrue(organization.address.typed_address ==
                        data["address"]["typed_address"])

    def test_can_hide_organization_address(self):
        """Assert that it's hide organization address"""
        owner = User.objects.create_user(
            email="owner@gmail.com",
            password="testcancreate",
            object_channel="default")
        member = User.objects.create_user(
            email="member@gmail.com",
            password="testcancreate",
            object_channel="default")
        volunteer = User.objects.create_user(
            email="volunteer@gmail.com",
            password="testcancreate",
            object_channel="default")

        data = copy.copy(base_organization)
        data['hidden_address'] = True

        client = APIClient()
        client.force_authenticate(user=owner)

        response = client.post(
            reverse("organization-list"),
            data,
            format="json")
        organization = Organization.objects.get(pk=response.data["id"])
        organization.members.add(member)

        # Retrieving as organization owner
        response = client.get(
            reverse(
                "organization-detail",
                ["test-organization"]),
            format="json")
        self.assertTrue(
            response.data["address"]["typed_address"]
            == data["address"]["typed_address"]
        )
        self.assertTrue(response.data["hidden_address"])

        # Retrieving as organization member
        client.force_authenticate(user=member)
        response = client.get(
            reverse(
                "organization-detail",
                ["test-organization"]),
            format="json")
        self.assertTrue(
            response.data["address"]["typed_address"]
            == data["address"]["typed_address"]
        )
        self.assertTrue(response.data["hidden_address"])

        # Retrieving as volunteer
        client.force_authenticate(user=volunteer)
        response = client.get(
            reverse(
                "organization-detail",
                ["test-organization"]),
            format="json")
        self.assertTrue(response.data["address"] is None)
        self.assertTrue(response.data["hidden_address"])

    def test_cant_create_organization_empty_name(self):
        """
        Assert that it's not possible to create a organization with empty name
        """
        user = User.objects.create_user(
            email="test_can_create_organization@gmail.com",
            password="testcancreate",
            object_channel="default")

        client = APIClient()
        client.force_authenticate(user=user)

        data = copy.copy(base_organization)
        data["name"] = ""

        response = client.post(
            reverse("organization-list"),
            data,
            format="json")
        self.assertTrue(response.data["name"][0]
                        == "This field may not be blank.")

    def test_organization_retrieval(self):
        """Assert organizations can be retrieved"""
        user = User.objects.create_user(
            email="test_retrieval@gmail.com",
            password="testretrieval",
            object_channel="default")

        client = APIClient()
        client.force_authenticate(user=user)

        data = copy.copy(base_organization)
        response = client.post(
            reverse("organization-list"),
            data,
            format="json")

        response = client.get(
            reverse(
                "organization-detail",
                ["test-organization"]),
            format="json")
        self.assertTrue(response.data["name"] == data["name"])
        self.assertTrue(response.data["slug"] == "test-organization")
        self.assertTrue(response.data["details"] == data["details"])
        self.assertTrue(response.data["description"] == data["description"])
        self.assertTrue(response.data["contact_name"] == data["contact_name"])
        self.assertTrue(
            response.data["contact_phone"] == data["contact_phone"])
        self.assertTrue(
            response.data["contact_email"] == data["contact_email"])
        self.assertTrue(response.data["published"] is False)
        self.assertTrue(len(response.data["causes"]) == 2)
        self.assertTrue(len(response.data["galleries"]) == 0)
        self.assertTrue("image" in response.data)
        self.assertTrue("cover" in response.data)

    def test_can_update_organization(self):
        """ Assert it's possible to update an organization """
        self.test_can_create_organization()
        organization = Organization.objects.last()

        client = APIClient()
        client.force_authenticate(user=User.objects.last())

        data = {"name": "updated name",
                "slug": "updated-slug",
                "details": "updated details",
                "description": "updated description",
                "address": {"typed_address": "campinas, sp"},
                "causes": [{"id": 3},
                           {"id": 4}],
                "contact_name": "updated name",
                "contact_phone": "+551198765432",
                "contact_email": "updated@email.com",
                "galleries": []}

        response = client.patch(
            reverse(
                "organization-detail",
                ["test-organization"]),
            data,
            format="json")
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.data["name"] == data["name"])
        self.assertTrue(response.data["slug"] == data["slug"])
        self.assertTrue(response.data["details"] == data["details"])
        self.assertTrue(response.data["description"] == data["description"])
        self.assertTrue(response.data["contact_name"] == data["contact_name"])
        self.assertTrue(
            response.data["contact_phone"] == data["contact_phone"])
        self.assertTrue(
            response.data["contact_email"] == data["contact_email"])

        self.assertTrue(len(response.data["causes"]) == 3)

        self.assertTrue(
            present_in_list(
                response.data["causes"],
                "name",
                "Conscious consumption"
            )
        )
        self.assertTrue(
            present_in_list(
                response.data["causes"],
                "name",
                "Culture, Sport and Art"
            )
        )
        self.assertTrue(
            present_in_list(
                response.data["causes"],
                "name",
                "other-channel"
            )
        )

    def test_can_retrieve_projects(self):
        """ Assert it's possible to retrieve organization projects """
        self.test_can_create_organization()

        organization = Organization.objects.last()
        organization.published = True
        organization.save()

        for i in range(5):
            project = Project.objects.create(
                name="project{}".format(
                    i,
                    object_channel="default"),
                published=True,
                organization=organization,
                owner=User.objects.last(),
                object_channel="default")

        client = APIClient()
        response = client.get(
            reverse(
                "organization-projects",
                ["test-organization"]),
            format="json")
        self.assertEqual(len(response.data["results"]), 5)
        self.assertIn("name", response.data["results"][0])

    def test_check_doc(self):
        user = User.objects.create_user(
            email="test_can_create_organization@gmail.com",
            password="testcancreate",
            object_channel="default")
        data = copy.copy(base_organization)
        data["document"] = "64479764000194"
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            reverse("organization-list"),
            data,
            format="json")

        invalid_response = client.get(
            "/organizations/check-doc/{}/".format("22222222222222"),
            format="json")
        taken_response = client.get(
            "/organizations/check-doc/{}/".format("64479764000194"),
            format="json")
        self.assertEqual(taken_response.data["taken"], True)
        self.assertEqual(invalid_response.data["invalid"], True)


class OrganizationInviteTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user(
            email="testemail@email.com",
            password="test_returned",
            object_channel="default")
        self.user = user

        user2 = User.objects.create_user(
            email="valid@user.com",
            password="test_returned",
            object_channel="default")
        self.user2 = user2

        organization = Organization(
            name="test organization",
            slug="test-organization",
            owner=user,
            type=0,
            published=True)
        organization.save(object_channel="default")
        self.organization = organization
        self.client = APIClient()
        self.client.force_authenticate(user)

    def test_cant_invite_invalid_email(self):
        """ Test serializer does not allow invalid emails """
        response = self.client.post(
            reverse(
                "organization-invite-user",
                ["test-organization"]),
            {
                "email": "invalidemail"},
            format="json")
        self.assertTrue(response.status_code == 400)
        self.assertTrue(response.data["email"] == [
                        "Enter a valid email address."])

    def test_cant_invite_valid_email_but_invalid_user(self):
        """ Test serializer does not allow invalid user """
        response = self.client.post(
            reverse(
                "organization-invite-user",
                ["test-organization"]),
            {
                "email": "invalid@user.com"},
            format="json")
        self.assertTrue(response.status_code == 400)
        self.assertTrue(response.data["email"] == ["This user is not valid."])

    def test_cant_invite_already_invited(self):
        """ Test serializer does not allow multiple invites to user """
        self.test_can_invite_user()
        response = self.client.post(
            reverse(
                "organization-invite-user",
                ["test-organization"]),
            {
                "email": "valid@user.com"},
            format="json")
        self.assertTrue(response.status_code == 400)
        self.assertTrue(
            response.data["email"]
            == [
                "This user was already invited to this organization"
                " in the last 60 minutes."
            ]
        )

        i = OrganizationInvite.objects.first()
        i.created_date = timezone.now() - relativedelta(hours=2)
        i.save()

        response = self.client.post(
            reverse(
                "organization-invite-user",
                ["test-organization"]),
            {
                "email": "valid@user.com"},
            format="json")
        self.assertTrue(response.status_code == 200)
        self.assertTrue(
            OrganizationInvite.objects.get(
                pk=i.pk).revoked_date is not None)

    def test_can_invite_user(self):
        """ Test it's possible to invite user """
        mail.outbox = []
        self.assertTrue(OrganizationInvite.objects.all().count() == 0)
        self.assertTrue(len(mail.outbox) == 0)

        response = self.client.post(
            reverse(
                "organization-invite-user",
                ["test-organization"]),
            {
                "email": "valid@user.com"},
            format="json")
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.data["detail"] == "User invited.")

        self.assertTrue(OrganizationInvite.objects.all().count() == 1)
        invite = OrganizationInvite.objects.last()
        self.assertTrue(invite.invitator == self.user)
        self.assertTrue(invite.invited == self.user2)

        subjects = [x.subject for x in mail.outbox]
        if is_email_enabled(
            "default",
                "userInvited-toUser"):  # pragma: no cover
            self.assertTrue(
                get_email_subject(
                    "default",
                    "userInvited-toUser",
                    "You are invited to an organization"))
        if is_email_enabled(
            "default",
                "userInvited-toOwnerInviter"):  # pragma: no cover
            self.assertTrue(
                get_email_subject(
                    "default",
                    "userInvited-toOwnerInviter",
                    "You invited a member to an organization you own"))

        third_user = User(email="third@user.com")
        third_user.save(object_channel="default")

        fourth_user = User(email="fourth@user.com")
        fourth_user.save(object_channel="default")

        self.organization.members.add(third_user)
        self.client.force_authenticate(third_user)

        mail.outbox = []
        self.assertTrue(len(mail.outbox) == 0)
        response = self.client.post(
            reverse(
                "organization-invite-user",
                ["test-organization"]),
            {
                "email": "fourth@user.com"},
            format="json")

        subjects = [x.subject for x in mail.outbox]
        if is_email_enabled(
            "default",
                "userInvited-toUser"):  # pragma: no cover
            self.assertTrue(
                get_email_subject(
                    "default",
                    "userInvited-toUser",
                    "You are invited to an organization"))
        if is_email_enabled(
            "default",
                "userInvited-toOwner"):  # pragma: no cover
            self.assertTrue(
                get_email_subject(
                    "default",
                    "userInvited-toOwner",
                    "A member has been invited to your organization"))
        if is_email_enabled(
            "default",
                "userInvited-toMemberInviter"):  # pragma: no cover
            self.assertTrue(
                get_email_subject(
                    "default",
                    "userInvited-toInviter",
                    "You invited a member to an organization you are part of"))

    def test_cant_invite_unauthenticated(self):
        """ Test it's not possible to invite user if not authenticated """
        client = APIClient()
        response = client.post(reverse("organization-invite-user",
                                       ["test-organization"]),
                               {"email": "valid@user.com"},
                               format="json")
        self.assertTrue(response.status_code == 401)
        self.assertTrue(
            response.data["detail"]
            == "Authentication credentials were not provided."
        )

    def test_cant_invite_if_not_owner_or_member(self):
        """
        Test it's not possible to invite user if not a member of organization
        """
        client = APIClient()
        client.force_authenticate(self.user2)
        response = client.post(reverse("organization-invite-user",
                                       ["test-organization"]),
                               {"email": "valid@user.com"},
                               format="json")
        self.assertTrue(response.status_code == 403)
        self.assertTrue(
            response.data["detail"]
            == "You do not have permission to perform this action."
        )

    def test_cant_join_unauthenticated(self):
        """
        Test it's not possible to join organization if not authenticated
        """
        client = APIClient()
        response = client.post(
            reverse(
                "organization-join",
                ["test-organization"]),
            {},
            format="json")
        self.assertTrue(response.status_code == 401)
        self.assertTrue(
            response.data["detail"]
            == "Authentication credentials were not provided."
        )

    def test_cant_join_if_not_invited(self):
        """ Test it's not possible to join organization if not invited """
        client = APIClient()
        client.force_authenticate(self.user2)
        response = client.post(
            reverse(
                "organization-join",
                ["test-organization"]),
            {},
            format="json")
        self.assertTrue(response.status_code == 403)
        self.assertTrue(
            response.data["detail"]
            == "You do not have permission to perform this action."
        )

    def test_can_join_if_invited(self):
        """ Test it's possible to join organization if invited """
        self.test_can_invite_user()
        self.assertTrue(self.user2 not in self.organization.members.all())

        mail.outbox = []
        self.assertTrue(len(mail.outbox) == 0)

        client = APIClient()
        client.force_authenticate(self.user2)
        response = client.post(
            reverse(
                "organization-join",
                ["test-organization"]),
            {},
            format="json")
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.data["detail"] == "Joined organization.")
        self.assertTrue(self.user2 in self.organization.members.all())

        subjects = [x.subject for x in mail.outbox]
        if is_email_enabled(
            "default",
                "userJoined-toUser"):  # pragma: no cover
            self.assertTrue(
                get_email_subject(
                    "default",
                    "userJoined-toUser",
                    "You have joined an organization"))
        if is_email_enabled(
            "default",
                "userJoined-toOwner"):  # pragma: no cover
            self.assertTrue(
                get_email_subject(
                    "default",
                    "userJoined-toOwner",
                    "An user has joined an organization you own"))

        # Don't allow joining twice or has after invite used
        response = client.post(
            reverse(
                "organization-join",
                ["test-organization"]),
            {},
            format="json")
        self.assertTrue(response.status_code == 403)

        self.organization.members.remove(self.user2)
        self.assertTrue(self.user2 not in self.organization.members.all())
        response = client.post(
            reverse(
                "organization-join",
                ["test-organization"]),
            {},
            format="json")
        self.assertTrue(response.status_code == 403)

    def test_cant_revoke_if_unauthenticated(self):
        """ Test it's not possible to revoke invitation if not authenticated"""
        client = APIClient()
        response = client.post(
            reverse(
                "organization-revoke-invite",
                ["test-organization"]),
            {},
            format="json")
        self.assertTrue(response.status_code == 401)
        self.assertTrue(
            response.data["detail"]
            == "Authentication credentials were not provided."
        )

    def test_cant_revoke_if_not_owner_or_member(self):
        """
        Test it's not possible to revoke invitation if not owner or member
        """
        client = APIClient()
        client.force_authenticate(self.user2)
        response = client.post(
            reverse(
                "organization-revoke-invite",
                ["test-organization"]),
            {},
            format="json")
        self.assertTrue(response.status_code == 403)
        self.assertTrue(
            response.data["detail"]
            == "You do not have permission to perform this action."
        )

    def test_cant_revoke_if_user_does_not_exist(self):
        """
        Test it's not possible to revoke invitation if user does not exist
        """
        response = self.client.post(
            reverse(
                "organization-revoke-invite",
                ["test-organization"]),
            {
                "email": "invalid@user.com"},
            format="json")
        self.assertTrue(response.status_code == 400)
        self.assertTrue(response.data["email"] == ["This user is not valid."])

    def test_cant_revoke_if_invite_does_not_exist(self):
        """
        Test it's not possible to revoke invitation
        if invitation does not exist
        """
        response = self.client.post(
            reverse(
                "organization-revoke-invite",
                ["test-organization"]),
            {
                "email": "valid@user.com"},
            format="json")
        self.assertTrue(response.status_code == 400)
        self.assertTrue(
            response.data["detail"]
            == "There is no pending invites "
            "for this user in this organization."
        )

    def test_can_revoke_invite(self):
        """ Test it's possible to revoke invitation """
        self.test_can_invite_user()

        mail.outbox = []
        self.assertTrue(len(mail.outbox) == 0)
        self.assertTrue(
            OrganizationInvite.objects.filter(
                revoked_date=None).count() == 2)
        response = self.client.post(
            reverse(
                "organization-revoke-invite",
                ["test-organization"]),
            {
                "email": "valid@user.com"},
            format="json")
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.data["detail"] == "Invite has been revoked.")
        self.assertTrue(
            OrganizationInvite.objects.filter(
                revoked_date=None).count() == 1)

        subjects = [x.subject for x in mail.outbox]
        if is_email_enabled(
            "default",
                "userInvitedRevoked-toUser"):  # pragma: no cover
            self.assertTrue(
                get_email_subject(
                    "default",
                    "userInvitedRevoked-toUser",
                    "Your invitation to an organization has been revoked"))
        if is_email_enabled(
            "default",
                "userInvitedRevoked-toOwnerInviter"):  # pragma: no cover
            self.assertTrue(
                get_email_subject(
                    "default",
                    "userInvitedRevoked-toOwnerInviter",
                    "You have revoked an user invitation"))

        mail.outbox = []
        self.client.force_authenticate(
            User.objects.get(email="third@user.com"))
        response = self.client.post(
            reverse(
                "organization-revoke-invite",
                ["test-organization"]),
            {
                "email": "fourth@user.com"},
            format="json")

        subjects = [x.subject for x in mail.outbox]
        if is_email_enabled(
            "default",
                "userInvitedRevoked-toUser"):  # pragma: no cover
            self.assertTrue(
                get_email_subject(
                    "default",
                    "userInvitedRevoked-toUser",
                    "Your invitation to an organization has been revoked"))
        if is_email_enabled(
                "default",
                "userInvitedRevoked-toOwner"):  # pragma: no cover
            self.assertTrue(
                get_email_subject(
                    "default",
                    "userInvitedRevoked-toOwner",
                    "An invitation to join your organization has been revoked"
                )
            )
        if is_email_enabled(
                "default",
                "userInvitedRevoked-toMemberInviter"):  # pragma: no cover
            self.assertTrue(
                get_email_subject(
                    "default",
                    "userInvitedRevoked-toMemberInviter",
                    "You have revoked an user invitation"))

    def test_pending_invites_permission_class(self):
        """
        Test it's not possible to retrieve pending invites
        if unauthenticated or not in organization
        """
        response = APIClient().get(
            reverse(
                "organization-pending-invites",
                ["test-organization"]),
            format="json")
        self.assertEqual(response.status_code, 401)

        client = APIClient()
        client.force_authenticate(user=self.user2)
        response = client.get(
            reverse(
                "organization-pending-invites",
                ["test-organization"]),
            format="json")
        self.assertEqual(response.status_code, 403)

    def test_pending_invites_list(self):
        """ Test it's possible to retrieve pending invites """
        response = self.client.get(
            reverse(
                "organization-pending-invites",
                ["test-organization"]),
            format="json")
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.data == [])

        self.test_can_invite_user()
        response = self.client.get(
            reverse(
                "organization-pending-invites",
                ["test-organization"]),
            format="json")
        self.assertEqual(len(response.data), 2)
        self.assertEqual(
            response.data[0]["invitator"]["email"],
            "testemail@email.com")
        self.assertEqual(
            response.data[0]["invited"]["email"],
            "valid@user.com")

    def test_revoked_and_used_not_included_in_pending_invites_list(self):
        """ Test revoked and used invites are not included in pending list """
        self.test_can_invite_user()
        response = self.client.get(
            reverse(
                "organization-pending-invites",
                ["test-organization"]),
            format="json")
        self.assertEqual(len(response.data), 2)

        i1 = OrganizationInvite.objects.first()
        i1.joined_date = timezone.now()
        i1.save()
        i2 = OrganizationInvite.objects.last()
        i2.revoked_date = timezone.now()
        i2.save()

        response = self.client.get(
            reverse(
                "organization-pending-invites",
                ["test-organization"]),
            format="json")
        self.assertEqual(len(response.data), 0)


class OrganizationLeaveTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user(
            email="testemail@email.com",
            password="test_returned",
            object_channel="default")
        self.user = user

        user2 = User.objects.create_user(
            email="valid@user.com",
            password="test_returned",
            object_channel="default")
        self.user2 = user2

        organization = Organization(
            name="test organization",
            slug="test-organization",
            owner=user,
            type=0,
            published=True)
        organization.save(object_channel="default")
        organization.members.add(user2)
        self.organization = organization
        self.client = APIClient()

    def test_cant_leave_organization_if_unauthenticated(self):
        """
        Test it's not possible to leave the organization
        if user is not authenticated
        """
        response = self.client.post(
            reverse(
                "organization-leave",
                ["test-organization"]),
            {},
            format="json")

        self.assertTrue(response.status_code == 401)
        self.assertTrue(
            response.data["detail"]
            == "Authentication credentials were not provided."
        )

    def test_cant_leave_organization_if_not_member(self):
        """
        Test it's not possible to leave the organization if user is not member
        """
        user = User.objects.create_user(
            email="not@member.com",
            password="test_returned",
            object_channel="default")
        self.client.force_authenticate(user)
        response = self.client.post(
            reverse(
                "organization-leave",
                ["test-organization"]),
            {},
            format="json")

        self.assertTrue(response.status_code == 403)
        self.assertTrue(
            response.data["detail"]
            == "You do not have permission to perform this action."
        )

    def test_cant_leave_organization_if_owner(self):
        """
        Test it's not possible to leave the organization if user is not owner
        """
        self.client.force_authenticate(self.user)
        response = self.client.post(
            reverse(
                "organization-leave",
                ["test-organization"]),
            {},
            format="json")

        self.assertTrue(response.status_code == 403)
        self.assertTrue(
            response.data["detail"]
            == "You do not have permission to perform this action."
        )

    def test_can_leave_organization(self):
        """ Test it's possible to leave the organization """
        mail.outbox = []
        self.assertTrue(len(mail.outbox) == 0)
        self.assertTrue(self.user2 in self.organization.members.all())
        self.client.force_authenticate(self.user2)
        response = self.client.post(
            reverse(
                "organization-leave",
                ["test-organization"]),
            {},
            format="json")

        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.data["detail"] ==
                        "You've left the organization.")
        self.assertTrue(self.user2 not in self.organization.members.all())

        subjects = [x.subject for x in mail.outbox]
        if is_email_enabled("default", "userLeft-toUser"):  # pragma: no cover
            self.assertTrue(
                get_email_subject(
                    "default",
                    "userLeft-toUser",
                    "You have left an organization"))
        if is_email_enabled("default", "userLeft-toOwner"):  # pragma: no cover
            self.assertTrue(
                get_email_subject(
                    "default",
                    "userLeft-toOwner",
                    "An user has left an organization you own"))

    def test_cant_remove_member_if_unauthenticated(self):
        """ Test it's not possible to remove a member while unauthenticated """
        response = self.client.post(
            reverse(
                "organization-remove-member",
                ["test-organization"]),
            {
                "email": "valid@user.com"},
            format="json")

        self.assertTrue(response.status_code == 401)
        self.assertTrue(
            response.data["detail"]
            == "Authentication credentials were not provided."
        )

    def test_cant_remove_member_if_not_owner(self):
        """ Test it's not possible to remove a member if not the owner """
        self.client.force_authenticate(self.user2)
        response = self.client.post(
            reverse(
                "organization-remove-member",
                ["test-organization"]),
            {
                "email": "valid@user.com"},
            format="json")

        self.assertTrue(response.status_code == 403)
        self.assertTrue(
            response.data["detail"]
            == "You do not have permission to perform this action."
        )

    def test_cant_remove_member_if_not_member(self):
        """
        Test it's not possible to remove a member if the user is not a member
        """
        self.client.force_authenticate(self.user)
        response = self.client.post(
            reverse(
                "organization-remove-member",
                ["test-organization"]),
            {
                "email": "invalid@user.com"},
            format="json")

        self.assertTrue(response.status_code == 400)
        self.assertTrue(response.data["email"] == ["This user is not valid."])

    def test_can_remove_member(self):
        """ Test it's possible to remove a member """
        mail.outbox = []
        self.client.force_authenticate(self.user)
        response = self.client.post(
            reverse(
                "organization-remove-member",
                ["test-organization"]),
            {
                "email": "valid@user.com"},
            format="json")

        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.data["detail"] == "Member was removed.")

        subjects = [x.subject for x in mail.outbox]
        if is_email_enabled(
            "default",
                "userRemoved-toUser"):  # pragma: no cover
            self.assertTrue(
                get_email_subject(
                    "default",
                    "userRemoved-toUser",
                    "You have have been removed from an organization"))
        if is_email_enabled(
            "default",
                "userRemoved-toOwner"):  # pragma: no cover
            self.assertTrue(
                get_email_subject(
                    "default",
                    "userRemoved-toOwner",
                    "You have removed an user from an organization you own"))


class OrganizationMemberList(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testemail@email.com",
            password="test_returned",
            object_channel="default")
        self.user2 = User.objects.create_user(
            email="valid@user.com",
            password="test_returned",
            object_channel="default")
        self.user3 = User.objects.create_user(
            email="invalid@user.com",
            password="test_returned",
            object_channel="default")

        organization = Organization(
            name="test organization",
            slug="test-organization",
            owner=self.user,
            type=0,
            published=True)
        organization.save(object_channel="default")
        # Owner is usually added to members by view
        organization.members.add(self.user)
        organization.members.add(self.user2)
        self.organization = organization
        self.client = APIClient()

    def test_can_list_members_in_organization(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(
            reverse(
                "organization-members",
                ["test-organization"]),
            format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["email"], "testemail@email.com")
        self.assertEqual(response.data[1]["email"], "valid@user.com")

    def test_cant_list_members_in_organization_if_unauthenticated(self):
        response = self.client.get(
            reverse(
                "organization-members",
                ["test-organization"]),
            format="json")
        self.assertEqual(response.status_code, 401)

    def test_cant_list_members_in_organization_if_not_part_of_organization(
            self):
        self.client.force_authenticate(user=self.user3)
        response = self.client.get(
            reverse(
                "organization-members",
                ["test-organization"]),
            format="json")
        self.assertEqual(response.status_code, 403)
