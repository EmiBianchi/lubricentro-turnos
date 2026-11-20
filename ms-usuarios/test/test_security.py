import unittest

from app.services.security import EncriptadorWerkzeug


class EncriptadorWerkzeugTestCase(unittest.TestCase):

    def setUp(self):
        self.encriptador = EncriptadorWerkzeug()

    def test_el_hash_no_es_la_password_original(self):
        hash_generado = self.encriptador.generar_hash("clave123")
        self.assertNotEqual(hash_generado, "clave123")

    def test_verificar_password_correcta(self):
        hash_generado = self.encriptador.generar_hash("clave123")
        self.assertTrue(self.encriptador.verificar("clave123", hash_generado))

    def test_verificar_password_incorrecta(self):
        hash_generado = self.encriptador.generar_hash("clave123")
        self.assertFalse(self.encriptador.verificar("otraclave", hash_generado))
