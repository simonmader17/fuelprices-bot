# Fuelprices Telegram Bot

This is the Telegram Bot in [my Fuelprices application stack](https://github.com/simonmader17/fuelprices-svelte?tab=readme-ov-file#description).

## Docker

### `docker-compose.yml`

```yaml
name: fuelprices-bot
services:
  fuelprices-bot:
    image: simonmader17/fuelprices-bot:latest
    container_name: fuelprices-bot
    restart: always
    environment:
      - TOKEN="<telegram-bot-token>"
```

### Fuelprices Application Stack

This is my complete Fuelprices application stack, consisting of [Web UI](https://github.com/simonmader17/fuelprices-svelte) + [API](https://github.com/simonmader17/fuelprices-api) + [Telegram Bot](https://github.com/simonmader17/fuelprices-bot):

```yaml
name: fuelprices
services:
  fuelprices-svelte:
    image: simonmader17/fuelprices-svelte:latest
    container_name: fuelprices-svelte
    restart: always
    ports:
      - 30012:30012
  fuelprices-api:
    image: simonmader17/fuelprices-api:latest
    container_name: fuelprices-api
    restart: always
    environment:
      - DATABASE_URL="<postgres-db-address:port>"
      - DATABASE_USERNAME="<postgres-username>"
      - DATABASE_PASSWORD="<postgres-password>"
    ports:
      - 30011:30011
  fuelprices-bot:
    image: simonmader17/fuelprices-bot:latest
    container_name: fuelprices-bot
    restart: always
    environment:
      - TOKEN="<telegram-bot-token>"
```
