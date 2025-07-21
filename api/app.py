import os
import sys
import argparse


def is_db_command():
    if len(sys.argv) > 1 and sys.argv[0].endswith("flask") and sys.argv[1] == "db":
        return True
    return False


# create app
if is_db_command():
    from app_factory import create_migrations_app

    app = create_migrations_app()
else:
    # It seems that JetBrains Python debugger does not work well with gevent,
    # so we need to disable gevent in debug mode.
    # If you are using debugpy and set GEVENT_SUPPORT=True, you can debug with gevent.
    if (flask_debug := os.environ.get("FLASK_DEBUG", "0")) and flask_debug.lower() in {"false", "0", "no"}:
        from gevent import monkey

        # gevent
        monkey.patch_all()

        from grpc.experimental import gevent as grpc_gevent  # type: ignore

        # grpc gevent
        grpc_gevent.init_gevent()

        import psycogreen.gevent  # type: ignore

        psycogreen.gevent.patch_psycopg()

    from app_factory import create_app

    app = create_app()
    celery = app.extensions["celery"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Dify API Server')
    parser.add_argument('--port', type=int, default=5001, help='Port to run the server on (default: 5001)')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to run the server on (default: 0.0.0.0)')
    args = parser.parse_args()

    app.run(host=args.host, port=args.port)
