# Bot2

A discord bot made with [interactions.py](https://github.com/interactions-py/interactions.py).
Visit [the official website](https://interactions-py.github.io/interactions.py/) to get started.

## Development installation

<details>
<summary>Click to expand</summary>

### Mongodb

You can either use a local mongodb instance or use mongodb atlas.

#### Local

1. Install mongodb on your machine ([Windows](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-windows/),
   [Mac](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-os-x/),
   [Linux](https://docs.mongodb.com/manual/administration/install-on-linux/))
2. Create a database called `bot2`

### Python

1. Create a virtual environment

2. Install packages using either poetry or pip `poetry install` or `pip install -r requirements.txt`

3. Change the name of `src/example_config.py` to `src/config.py` and fill in the required fields (Mandatory fields
   below)
    - DEV_GUILD_ID
    - DEV_CHANNEL_ID
    - DEV_ROLE_ID

4. [Optional] Change the name of `.env.example` to `.env` and fill in the required fields (Mandatory fields below)
    - PROJECT_NAME
    - DISCORD_TOKEN
    - MONGO_LOCAL_URI (Add db name at the end example: `mongodb://localhost:27017/DATABASE_NAME`)

5. [Optional] Incase you want to use mongodb atlas, fill in the required fields in `.env` and `src/config.py`
    - `.env`
        - MONGO_URI (Add db name at the end
          example: `mongodb+srv://<cluster-url>/DATABASE_NAME?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority`)
        - MONGO_CERT_PATH
    - `src/config.py`
        - MONGO_MODE = "atlas" (from localhost to atlas)

```bash
python src/main.py
```

</details>

# Additional Information

Additionally, this comes with a pre-made [pre-commit](https://pre-commit.com) config to keep your code clean.

It is recommended that you set this up by running:

```bash
pip install pre-commit
```

```bash
pre-commit install
```

---

# Todo

- [ ] Birthday Event extension
- [x] Add Mongo DB for persistence
- [ ] Meeting Scheduler
- [ ] create event while creating the object
