import unittest
import sys
sys.path.append('../backend')
from server import ChatHandler, vectorshift
from unittest.mock import patch, MagicMock
from http.server import HTTPServer
import json
import os

class TestChatHandler(unittest.TestCase):
    def setUp(self):
        # Mock API key
        os.environ['VECTORSHIFT_API_KEY'] = 'test-key'
        vectorshift.api_key = 'test-key'

    @patch('vectorshift.pipeline.Pipeline.new')
    @patch('vectorshift.pipeline.Pipeline.run')
    def test_post_chat_success(self, mock_run, mock_new):
        # Mock pipeline creation and run
        mock_pipeline = MagicMock()
        mock_new.return_value = mock_pipeline
        mock_run.return_value = {'output_0': 'Test reply'}

        # Simulate POST request (manual env setup for test)
        class MockRequest:
            path = '/chat'
            headers = {'Content-Length': '20'}
            rfile = MagicMock()
            rfile.read.return_value = b'{"message": "Hi"}'
            wfile = MagicMock()
            send_response = MagicMock()
            send_header = MagicMock()
            end_headers = MagicMock()

        handler = ChatHandler(MagicMock(), MagicMock(), MockRequest())
        handler.do_POST()

        # Assertions
        mock_run.assert_called_once()
        handler.send_response.assert_called_with(200)
        self.assertIn(b'"reply":"Test reply"', handler.wfile.write.call_args[0][0])

    @patch('vectorshift.pipeline.Pipeline.new')
    def test_post_chat_error(self, mock_new):
        mock_new.side_effect = Exception('API Error')

        class MockRequest:
            path = '/chat'
            headers = {'Content-Length': '20'}
            rfile = MagicMock()
            rfile.read.return_value = b'{"message": "Hi"}'
            wfile = MagicMock()
            send_response = MagicMock()
            send_header = MagicMock()
            end_headers = MagicMock()

        handler = ChatHandler(MagicMock(), MagicMock(), MockRequest())
        handler.do_POST()

        handler.send_response.assert_called_with(500)

if __name__ == '__main__':
    unittest.main()