import asyncio
from app.services.quickbooks_service import quickbooks_service

async def get_customer_type_id():
    query = 'SELECT * FROM CustomerType'
    response = await quickbooks_service._make_request('GET', 'query', params={'query': query})
    types = response.get('QueryResponse', {}).get('CustomerType', [])
    
    print(f'\nFound {len(types)} CustomerType entries:')
    for t in types:
        print(f"  - {t.get('Name')}: ID = {t.get('Id')}")
        if t.get('Name') == 'GC Compliance':
            print(f'\n✅ GC Compliance ID: {t.get(\"Id\")}')
            return t.get('Id')
    
    return None

if __name__ == '__main__':
    gc_id = asyncio.run(get_customer_type_id())
    if not gc_id:
        print('\n❌ GC Compliance CustomerType not found!')
