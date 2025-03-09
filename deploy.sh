#!/bin/bash

# Hata alındığında işlemi durdur
set -e

# Sunucuya SSH ile bağlanıp güncellemeleri uygula
ssh -i ~/.ssh/id_rsa user@your-server-ip <<EOF
    cd /path/to/project
    git pull origin dev
    docker stack deploy -c docker-stack.yml fastapi_stack
    docker system prune -f
EOF

echo "🚀 Deployment tamamlandı!"
