import unittest
import SourceWatch


class TestServer(unittest.TestCase):
    def test_invalid_port(self):
        self.assertRaises(ValueError, SourceWatch.Server, "1.2.3.4", -1)
        self.assertRaises(ValueError, SourceWatch.Server, "1.2.3.4", 65536)
        self.assertRaises(TypeError, SourceWatch.Server, "1.2.3.4", "27015")

    def test_from_str(self):
        self.assertRaises(ValueError, SourceWatch.Server.from_str, "12")

    def test_from_str_valid(self):
        server = SourceWatch.Server.from_str("1.2.3.4:27016")
        self.assertEqual(server.ip, "1.2.3.4")
        self.assertEqual(server.port, 27016)

    def test_equality(self):
        server_a = SourceWatch.Server("1.2.3.4")
        server_b = SourceWatch.Server("1.2.3.4", 27015)
        server_c = SourceWatch.Server("4.3.2.1")

        self.assertEqual(server_a, server_b)
        self.assertNotEqual(server_a, server_c)

    def test_as_tuple(self):
        ip = "1.2.3.4"
        server = SourceWatch.Server(ip)

        self.assertEqual((ip, 27015), server.as_tuple())

    def test_server_name(self):
        server = SourceWatch.Server("1.2.3.4")
        server.name = "foobar"

        self.assertEqual("foobar", server.name)

    def test_none_existing_attribute(self):
        server = SourceWatch.Server("1.2.3.4")
        self.assertIsNone(server.foobar)
