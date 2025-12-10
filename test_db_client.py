import asyncio
from app.services.db_service import db_service

async def test():
    await db_service.initialize()
    clients = await db_service.get_clients_data()
    print(f"Found {len(clients)} clients")
    if clients:
        print(f"\nFirst client:")
        for key, value in clients[0].items():
            print(f"  {key}: {value}")

if __name__ == "__main__":
    asyncio.run(test())
