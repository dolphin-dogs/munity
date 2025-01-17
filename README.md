# munity
![logo-munity](./docs/logo.png)

Munity is an open source framework/boilerplate, easily and highly customizable.

## Start munity, the easy way
```
cp ./env.sample ./.env
./scripts/start.sh
```

## Start munity step by step

### Start Munity services
```
docker-compose up -d
```

### Create your database and migrate
```
docker-compose exec db psql -U munityapps -c "create database munity"
docker-compose exec api python manage.py migrate
```

### Database is now available, restart API
```
dokcer-compose restart api
```

### Create your first user
```
docker-compose exec api python manage.py createsuperuser
```

### Start frontend
```
cd app ; yarn install ; yarn start
```
