import psycopg
from psycopg_pool import AsyncConnectionPool, PoolTimeout
import asyncio
import random

class DatabaseManager:
    def __init__(self, dsn, min_size=1, max_size=5, max_lifetime=300, max_idle=60):
        self.dsn = dsn
        self.pool = AsyncConnectionPool(
            dsn,
            min_size=min_size,
            max_size=max_size,
            max_lifetime=max_lifetime,
            max_idle=max_idle,
            open=False
        )
    
    async def open(self):
        await self.pool.open()

    async def execute_with_retries(self, query, params=None, fetchall=False, retries=3, initial_delay=1, max_delay=30):
        attempts = 0
        delay = initial_delay
        
        while attempts < retries:
            try:
                async with self.pool.connection() as conn:
                    async with conn.cursor() as cursor:
                        await cursor.execute(query, params)
                        if query.strip().lower().startswith('select'):
                            if fetchall:
                                return await cursor.fetchall()
                            else:
                                return await cursor.fetchone()
                        else:
                            return None
            except (psycopg.OperationalError, psycopg.InterfaceError, PoolTimeout) as e:
                print(f'Database connection error: {e}. Retrying in {delay} seconds...')
                attempts += 1
                await asyncio.sleep(delay)
                
                # Exponential backoff with jitter
                delay = min(max_delay, delay * 2 + random.uniform(0, 1))
        
        raise Exception('Failed to execute query after multiple attempts.')

    async def commit(self):
        async with self.pool.connection() as conn:
            await conn.commit()

    async def close(self):
        await self.pool.close()

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


