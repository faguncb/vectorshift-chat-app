import json
import os
import socketserver
from http.server import SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import vectorshift
from vectorshift.pipeline import Pipeline, InputNode, OutputNode, LlmNode

# Authenticate with VectorShift
vectorshift.api_key = os.getenv('VECTORSHIFT_API_KEY')
if not vectorshift.api_key:
    raise ValueError("Set VECTORSHIFT_API_KEY environment variable")

class ChatHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Set document root to frontend dir for serving static files
        super().__init__(*args, directory='../frontend', **kwargs)

    def do_POST(self):
        if self.path == '/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                message = data.get('message', '')
                if not message:
                    self._send_error(400, "No message provided")
                    return

                # Create a basic LLM pipeline (in production, fetch existing by name/ID)
                input_node = InputNode(node_name="input_0")
                llm_node = LlmNode(
                    node_name="llm_node",
                    system="You are a helpful assistant.",
                    prompt=input_node.text,
                    provider="openai",
                    model="gpt-4o-mini",
                    temperature=0.7
                )
                output_node = OutputNode(
                    node_name="output_0",
                    value=llm_node.response
                )
                pipeline = Pipeline.new(
                    name=f"chat-pipeline-{id(input_node)}",  # Unique name to avoid conflicts
                    nodes=[input_node, llm_node, output_node]
                )

                # Run the pipeline
                input_data = {"input_0": message}
                result = pipeline.run(input_data)
                reply = result.get("output_0", "Error generating response")

                # Send JSON response
                response = json.dumps({"reply": reply}).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(response)
            except json.JSONDecodeError:
                self._send_error(400, "Invalid JSON")
            except Exception as e:
                self._send_error(500, str(e))
        else:
            self._send_error(404, "Not Found")

    def _send_error(self, code, message):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        error = json.dumps({"error": message}).encode('utf-8')
        self.wfile.write(error)

if __name__ == "__main__":
    PORT = 8000
    with socketserver.TCPServer(("", PORT), ChatHandler) as httpd:
        print(f"Server running at http://localhost:{PORT}")
        httpd.serve_forever()