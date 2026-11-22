from caso_base import CasoBase


class AppTestCase(CasoBase):

    def test_app_existe(self):
        self.assertIsNotNone(self.app)

    def test_app_usa_configuracion_de_testing(self):
        self.assertTrue(self.app.config["TESTING"])
