#!/bin/bash

cp -u docker/cache/.env.dist docker/cache/.env
cp -u docker/core-backend/.env.dist docker/core-backend/.env
cp -u docker/database/.env.dist docker/database/.env
cp -u docker/database-viewer/.env.dist docker/database-viewer/.env
cp -u docker/notification-backend/.env.dist docker/notification-backend/.env
