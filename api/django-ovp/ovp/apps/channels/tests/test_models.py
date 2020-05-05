from django.test import TestCase

from ovp.apps.channels.models import Channel
from ovp.apps.channels.exceptions import UnexpectedChannelAssociationError
from ovp.apps.channels.exceptions import NoChannelSupplied

from ovp.apps.users.models import User


class ChannelTestCase(TestCase):
    def test_models_that_extend_single_channel_relationship_raise_error_if_no_channel_supplied_on_save(
            self):
        """
        Assert models that extend ChannelRelationship model
        raises error if no channel supplied on save method
        """
        user = User(email="test@user.com", password="test_password")
        with self.assertRaises(NoChannelSupplied):
            user.save()

        self.assertEqual(User.objects.count(), 0)

    def test_models_that_extend_single_channel_relationship_can_be_created_with_custom_channel_on_save(
            self):
        """
        Assert models that extend ChannelRelationship can
        be created with custom channel on save method
        """
        Channel(name="Test", slug="test-channel").save()
        user = User(email="test@user.com", password="test_password")
        user.save(object_channel="test-channel")

        self.assertTrue(user.channel.slug == "test-channel")

    def test_models_that_extend_single_channel_relationship_raise_error_if_no_channel_supplied_on_create(
            self):
        """
        Assert models that extend ChannelRelationship model
        raises error if no channel supplied on manager create method
        """
        with self.assertRaises(NoChannelSupplied):
            user = User.objects.create(
                email="test@user.com",
                password="test_password"
            )

        self.assertEqual(User.objects.count(), 0)

    def test_models_that_extend_single_channel_relationship_can_be_created_with_custom_channel_on_create(
            self):
        """
        Assert models that extend ChannelRelationship can
        be created with custom channel on manager create method
        """
        Channel(name="Test", slug="test-channel").save()
        user = User.objects.create(
            email="test@user.com",
            password="test_password",
            object_channel="test-channel"
        )
        self.assertTrue(user.channel.slug == "test-channel")

    def test_models_that_extend_single_channel_cant_associate_channel_directly(
            self):
        """
        Assert models that extend ChannelRelationship
        raise exception when trying to associate channel directly
        """
        channel = Channel.objects.create(name="Test", slug="test-channel")
        user = User(
            email="test@user.com",
            password="test_password",
            channel=channel
        )
        with self.assertRaises(UnexpectedChannelAssociationError):
            user.save()

        with self.assertRaises(UnexpectedChannelAssociationError):
            user = User.objects.create(
                email="test@user.com",
                password="test_password",
                channel=channel
            )
