#!/bin/sh
addgroup -S appgroup && adduser -S app -G appgroup -s /bin/bash
chown -R app:appgroup /workspace
