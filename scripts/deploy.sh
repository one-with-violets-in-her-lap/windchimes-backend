export $(xargs < ./scripts/.env.scripts)

read -p "branch to deploy (main by default): " branch

# set branch to `main` on empty input
branch=${branch:-main}

sshpass -p $SSH_PASSWORD ssh -l root $SSH_ADDRESS -p $SSH_PORT "cd ~/projects/windchimes-backend && git remote set-url origin $GIT_ORIGIN && git fetch && git switch $branch && git pull origin $branch && docker compose down --rmi all && docker container prune --force && docker compose up -d"
