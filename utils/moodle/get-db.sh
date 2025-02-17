curl --header "PRIVATE-TOKEN: XXXXXXXXXXXXXXXX" "https://gitlab.com/api/YYYYYYYYYYYYYYYYYYY" > ci.env
# Step 2: Extract variables from the single line
# Use jq to extract values for each key
export PRODUCTION_USER=$(jq -r '.[] | select(.key=="PRODUCTION_USER") | .value' ci.env)
export PRODUCTION_IP=$(jq -r '.[] | select(.key=="PRODUCTION_IP") | .value' ci.env)
export PRODUCTION_KEY=$(jq -r '.[] | select(.key=="PRODUCTION_KEY") | .value' ci.env)



echo "$PRODUCTION_KEY" | sed 's/\\n/\n/g' > ./prod.key
# Ensure correct ownership and permissions
chmod 400 ./prod.key


ssh -o StrictHostKeyChecking=no -i ./prod.key $PRODUCTION_USER@$PRODUCTION_IP "cd /srv/moodle-plugin && docker compose exec moodle_db mariadb-dump -u moodle -pmoodle moodle" > ./moodle.sql
rm -rf ./prod.key
rm -rf ./ci.env
