import asyncpg, asyncio, pytz
from typing import List
from datetime import datetime, timedelta
from asyncpg import Pool, Record
from loguru import logger


class DictRecord(Record):
	def __getitem__(self, key):
		value = super().__getitem__(key)
		if isinstance(value, Record):
			return DictRecord(value)
		return value

	def to_dict(self):
		return self._convert_records_to_dicts(dict(super().items()))

	def _convert_records_to_dicts(self, obj):
		if isinstance(obj, dict):
			return {k: self._convert_records_to_dicts(v) for k, v in obj.items()}
		elif isinstance(obj, list):
			return [self._convert_records_to_dicts(item) for item in obj]
		elif isinstance(obj, Record):
			return dict(obj)
		else:
			return obj

	def __repr__(self):
		return str(self.to_dict())


class DB:
	db: Pool

	def __init__(self, host: str, port: int, user: str, password: str, db_name: str) -> None:
		self._host = host
		self._port = port
		self._user = user
		self._password = password
		self._db_name = db_name

	async def close(self) -> None:
		await self.db.close()
		logger.warning("Соединение с базой данных завершено!")

	async def setup(self) -> None:
		self.db = await asyncpg.create_pool(
			host=self._host, port=self._port, user=self._user,
			password=self._password, database=self._db_name,
			record_class=DictRecord, init=self._init_database
		)
		logger.success("Соединение с базой данных успешно установлено!")

	@staticmethod
	async def _init_database(db: asyncpg.Connection) -> None:
		await db.execute("""
			CREATE TABLE IF NOT EXISTS \"users\"(
				_id BIGINT NOT NULL PRIMARY KEY,
				username TEXT,
				full_name TEXT,
				role TEXT DEFAULT 'user',
				phone_number TEXT DEFAULT NULL,
				created_at TIMESTAMP DEFAULT now(),
				updated_at TIMESTAMP DEFAULT now()
		)""")

		await db.execute("""
			CREATE TABLE IF NOT EXISTS \"accounts\"(
				_id SERIAL PRIMARY KEY,
				phone_number TEXT NOT NULL,
				phone_code_hash TEXT NOT NULL,
				user_session_id BIGINT DEFAULT NULL,
				name_session TEXT DEFAULT NULL,
				username_session TEXT DEFAULT NULL,
				proxy TEXT DEFAULT NULL,
				type_proxy TEXT DEFAULT NULL,
				valid BOOLEAN DEFAULT True,
				cleint_session BYTEA DEFAULT NULL,
				created_at TIMESTAMP DEFAULT now(),
				updated_at TIMESTAMP DEFAULT now()
		)""")

		await db.execute("""
			CREATE TABLE IF NOT EXISTS \"settings\"(
				_id BIGINT PRIMARY KEY,
				api_id INTEGER DEFAULT NULL,
				api_hash TEXT DEFAULT NULL,
				device_model TEXT DEFAULT NULL
		)""")

		await db.execute("SET TIME ZONE 'Europe/Moscow'")


	async def update_hash_code(self, phone_number: str, hash_code: str):
		try:
			await self.db.execute("UPDATE accounts SET phone_code_hash = $1 WHERE phone_number = $2", hash_code, phone_number)
			return True
		except Exception as e:
			logger.exception(e)
			return False


	async def update_account_info_by_phone_number(self, phone_number: str, user_session_id: int, name_session: str, username_session: str,
											proxy_type: str = None, proxy: str = None):
		try:
			await self.db.execute("""
				UPDATE accounts SET user_session_id = $1, name_session = $2, username_session = $3, proxy = $4, proxy_type = $5, updated_at = now()
				WHERE phone_number = $4
			""", user_session_id, name_session, username_session, phone_number, proxy, proxy_type)
			return True

		except Exception as e:
			logger.exception(e)
			return False





	async def get_acount_bey_id(self, _id: int):
		response = await self.db.fetchrow("SELECT * FROM accounts WHERE _id = $1", _id)
		return response


	async def get_all_accounts(self):
		response = await self.db.fetch("SELECT * FROM accounts")
		return response


	async def delete_account_phone_number(self, phone_number: str):
		try:
			await self.db.execute("DELETE FROM accounts WHERE phone_number = $1", phone_number)
			return True

		except Exception as e:
			logger.error(e)
			return False

	async def check_double_account(self, phone_number: str):
		response = await self.db.fetchrow("SELECT * FROM accounts WHERE phone_number = $1", phone_number)
		return response


	async def add_account(self, phone_number: str, phone_code_hash: str):
		await self.db.execute("INSERT INTO accounts (phone_number, phone_code_hash) VALUES ($1, $2)", phone_number, phone_code_hash)


	async def get_account_by_phone_number(self, phone_number: str) -> dict:
		response = await self.db.fetchrow("SELECT * FROM accounts WHERE phone_number = $1", phone_number)
		return response

	async def update_client_session_by_phone_number(self, phone_number: str, clinet_session: bytes):
		await self.db.execute("UPDATE accounts SET cleint_session = $1 WHERE phone_number = $2", clinet_session, phone_number)


	async def update_api_config(self, api_id: int, api_hash: str):
		await self.db.execute("UPDATE settings SET api_id = $1, api_hash = $2 WHERE _id = 1", api_id, api_hash)

   
	async def get_settings(self) -> dict:
		response = await self.db.fetchrow("SELECT * FROM settings WHERE _id = 1")
		return response.to_dict()


	async def add_settings(self):
		try:
			await self.db.execute("INSERT INTO settings (_id) VALUES ($1)", 1)
			return True
		except Exception as e:
			logger.error(e)
			return False


	async def get_admins_role(self) -> List[dict]:
		response = await self.db.fetch("SELECT * FROM users WHERE role = 'admin'")
		return response.to_dict()


	async def get_user_info(self, user_id: int) -> dict:
		response = await self.db.fetchrow("SELECT * FROM users WHERE _id = $1", user_id)
		return response.to_dict()

	async def get_user_info_dict(self, user_id: int) -> dict:
		response = await self.db.fetchrow("SELECT * FROM users WHERE _id = $1", user_id)
		return response


	async def add_user(self, user_id: int, username: str, full_name: str) -> dict:
		if not await self.user_existence(user_id):
			response = (
				await self.db.fetchrow(
					"INSERT INTO users(_id, username, full_name) VALUES($1, $2, $3) RETURNING *",
					user_id, username, full_name
				)
			).to_dict()

		else:
			await self.update_user_activity(user_id)
			response = await self.get_user_info(user_id)

		return response


	async def update_user_role(self, user_id: int, role: str) -> dict:
		await self.db.execute("UPDATE users SET role=$1 WHERE _id=$2", role, user_id)
		response = await self.get_user_info(user_id)

		return response


	async def update_user_activity(self, user_id: int):
		if await self.user_existence(user_id):
			await self.db.execute("UPDATE users SET updated_at=$1", datetime.now())

	async def user_existence(self, user_id: int) -> bool:
		response = await self.db.fetchval("SELECT EXISTS(SELECT 1 FROM users WHERE _id=$1)", int(user_id))
		return response

	async def get_all_users(self) -> List[dict]:
		response = await self.db.fetch("SELECT * FROM users")
		return response
