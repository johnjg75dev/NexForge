"""Start the local NeuralForge service: python -m neuralforge."""
import argparse
from neuralforge.http.server import create_server


def main():
    parser = argparse.ArgumentParser(description="Run the local NeuralForge workspace")
    parser.add_argument("--host", default="127.0.0.1", help="Bind address (loopback is the safe default)")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--data-dir", default=None, help="Storage directory; defaults to ~/.neuralforge")
    args = parser.parse_args()
    server = create_server(args.host, args.port, args.data_dir)
    print(f"NeuralForge listening at http://{args.host}:{args.port}")
    print(f"Data directory: {server.datasets.storage_root}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down…")
    finally:
        server.server_close()

if __name__ == "__main__": main()
