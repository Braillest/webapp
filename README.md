# First time setup
./scripts/copy-env.bash
docker compose up -d
docker exec -it braillest_core_backend bash
composer install
symfony server:start --listen-ip=0.0.0.0
