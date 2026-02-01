import os
import tempfile
from unittest.mock import patch

from django.test import SimpleTestCase

from services.webmania.client import WebmaniaClient


class DummyResponse:
    def __init__(self, payload=None, content=b""):
        self._payload = payload or {}
        self.content = content

    def json(self):
        return self._payload


class WebmaniaClientTests(SimpleTestCase):
    def test_send_nfs(self):
        client = WebmaniaClient("token", ambient=2)
        with patch("services.webmania.client.requests.post") as mock_post:
            mock_post.return_value = DummyResponse({"ok": True})
            payload = {"foo": "bar"}
            response = client.send_nfs(payload)
            self.assertEqual(response, {"ok": True})
            args, kwargs = mock_post.call_args
            self.assertTrue(args[0].endswith("/2/nfse/emissao"))
            self.assertEqual(kwargs["json"]["ambiente"], 2)
            self.assertEqual(kwargs["json"]["rps"], [payload])

    def test_cancel_nfs(self):
        client = WebmaniaClient("token")
        with patch("services.webmania.client.requests.put") as mock_put:
            mock_put.return_value = DummyResponse({"ok": True})
            response = client.cancel_nfs("uuid", "Erro")
            self.assertEqual(response, {"ok": True})
            args, _ = mock_put.call_args
            self.assertIn("cancelar/uuid", args[0])

    def test_get_nfs(self):
        client = WebmaniaClient("token")
        with patch("services.webmania.client.requests.get") as mock_get:
            mock_get.return_value = DummyResponse({"ok": True})
            response = client.get_nfs("uuid")
            self.assertEqual(response, {"ok": True})
            args, _ = mock_get.call_args
            self.assertIn("consulta/uuid", args[0])

    def test_get_pdf_nfs_writes_file(self):
        client = WebmaniaClient("token")
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("services.webmania.client.requests.get") as mock_get:
                mock_get.return_value = DummyResponse(content=b"pdf")
                client.get_pdf_nfs("uuid", tmpdir)
                path = os.path.join(tmpdir, "nfs_uuid.pdf")
                self.assertTrue(os.path.exists(path))

    def test_get_xml_nfs_writes_file(self):
        client = WebmaniaClient("token")
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("services.webmania.client.requests.get") as mock_get:
                mock_get.return_value = DummyResponse(content=b"xml")
                client.get_xml_nfs("uuid", tmpdir)
                path = os.path.join(tmpdir, "nfs_uuid.xml")
                self.assertTrue(os.path.exists(path))
