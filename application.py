import uvicorn
import argparse
from app import app

#Avvia il server su una specifica porta per poter utilizzare le API
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='paramaters')
    parser.add_argument(
        '-port',
        dest='port',
        default=5002,
        type=int,
        action='store',
        help='API service port number')
    parser.add_argument(
        '-host',
        dest='host',
        default='127.0.0.1',
        type=str,
        action='store',
        help='API host address')
    args = parser.parse_args()

    uvicorn.run(app, port=args.port, host=args.host)