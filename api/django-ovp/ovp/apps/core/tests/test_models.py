from django.test import TestCase

from ovp.apps.core.models import GoogleAddress
from ovp.apps.core.models import AddressComponent
from ovp.apps.core.models import AddressComponentType
from ovp.apps.core.models import Skill
from ovp.apps.core.models import Cause


def remove_component(address, types):
    for component in address.address_components.all():
        for type in component.types.all():
            if type.name in types:
                component.delete()

    return address


class GoogleAddressModelTestCase(TestCase):

    def test_api_call(self):
        """
        Assert GoogleAddress calls google API and get address
        """
        a = GoogleAddress(
            typed_address="Rua Teçaindá, 81, SP",
            typed_address2="Casa"
        )
        a.save(object_channel="default")

        a = GoogleAddress.objects.get(pk=a.pk)
        self.assertEqual(a.typed_address, "Rua Teçaindá, 81, SP")
        self.assertEqual(a.typed_address2, "Casa")

        address_line = "Rua Teçaindá, 81, Pinheiros, São Paulo, SP, Brazil"
        self.assertEqual(a.address_line, address_line)
        self.assertEqual(a.__str__(), address_line)
        self.assertTrue(a.lat)
        self.assertTrue(a.lng)

        a.typed_address = "Rua Capote Valente, 701, SP"
        a.save()
        a = GoogleAddress.objects.get(pk=a.pk)
        self.assertEqual(a.typed_address, "Rua Capote Valente, 701, SP")
        self.assertEqual(a.typed_address2, "Casa")

        address_line_2 = "Rua Capote Valente, 701, " \
                         "Pinheiros, São Paulo, SP, Brazil"
        self.assertEqual(a.address_line, address_line_2)
        self.assertEqual(a.__str__(), address_line_2)
        self.assertTrue(a.lat)
        self.assertTrue(a.lng)

        a.address_line = None
        a.typed_address = 'Rua Teste'
        self.assertEqual(a.__str__(), "Rua Teste")

    def test_locality(self):
        """
        Assert GoogleAddressModel.get_city_state
        preference order is locality, administrative_area_2
        """
        a = GoogleAddress(typed_address="Chicago")
        a.save(object_channel="default")
        self.assertTrue("Chicago" in a.get_city_state())

        a = remove_component(a, ['locality'])
        self.assertTrue("Cook" in a.get_city_state())


class AddressComponentTypeModelTestCase(TestCase):

    def test_str_call(self):
        """
        Assert AddressComponentType __str__ returns name
        """
        a = AddressComponentType(name="xyz")
        a.save(object_channel="default")

        self.assertTrue(a.__str__() == "xyz")


class AddressComponentModelTestCase(TestCase):

    def test_str_call(self):
        """
        Assert AddressComponent __str__ returns long name
        """
        a = AddressComponent(short_name="short", long_name="long")
        a.save(object_channel="default")

        self.assertTrue(a.__str__() == "long")


class SkillModelTestCase(TestCase):

    def test_str_method_returns_name(self):
        """ Assert skill __str__ method returns name """
        n = "a" * 100
        s = Skill(name=n)
        s.save(object_channel="default")

        self.assertTrue(s.__str__() == n)


class CauseModelTestCase(TestCase):

    def test_str_method_returns_name(self):
        """
        Assert cause __str__ method returns name
        """
        n = "a" * 100
        c = Cause(name=n)
        c.save(object_channel="default")

        self.assertTrue(c.__str__() == n)
