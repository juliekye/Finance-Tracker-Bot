#!/bin/sh
chown -R app:appgroup /workspace
exec "$@"
