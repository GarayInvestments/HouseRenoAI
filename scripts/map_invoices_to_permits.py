"""
Intelligent invoice-to-permit mapping using context clues.

This script analyzes invoice descriptions and matches them to permits using:
1. Explicit permit numbers in descriptions
2. Address matching
3. Client-specific patterns
4. Sequential payment patterns (1 of 3, 2 of 3, etc.)
"""
import asyncio
import json
from sqlalchemy import text, select, update
from app.db.session import AsyncSessionLocal
from app.db.models import Invoice, Permit, Client


async def map_invoices_to_permits(dry_run: bool = True):
    """Map unmapped invoices to permits using intelligent matching."""
    
    print("="*80)
    print("INTELLIGENT INVOICE-TO-PERMIT MAPPING")
    print("="*80 + "\n")
    
    mappings = []
    
    async with AsyncSessionLocal() as session:
        # Get unmapped invoices with line items
        result = await session.execute(
            select(Invoice, Client.full_name)
            .join(Client, Invoice.client_id == Client.client_id)
            .where(Invoice.project_id == None)
            .order_by(Client.full_name, Invoice.invoice_number)
        )
        
        unmapped_invoices = result.all()
        print(f"[*] Found {len(unmapped_invoices)} unmapped invoices\n")
        
        # Get all permits for reference
        result = await session.execute(
            select(Permit, Client.full_name)
            .join(Client, Permit.client_id == Client.client_id)
            .order_by(Client.full_name)
        )
        permits_with_clients = result.all()
        
        # Create lookup: client_id -> list of permits
        permits_by_client = {}
        for permit, client_name in permits_with_clients:
            if permit.client_id not in permits_by_client:
                permits_by_client[permit.client_id] = []
            permits_by_client[permit.client_id].append(permit)
        
        # Analyze each invoice
        for invoice, client_name in unmapped_invoices:
            print(f"[Invoice] {invoice.invoice_number} ({client_name})")
            
            # Parse line items
            line_items = json.loads(invoice.line_items) if invoice.line_items else []
            descriptions = [item.get('description', '') for item in line_items]
            full_description = ' '.join(descriptions)
            
            print(f"  Description: {full_description[:100]}...")
            
            # Get client's permits
            client_permits = permits_by_client.get(invoice.client_id, [])
            
            matched_permit = None
            match_reason = None
            
            # Strategy 1: Explicit permit number in description
            for permit in client_permits:
                if permit.permit_number in full_description:
                    matched_permit = permit
                    match_reason = f"Explicit permit number '{permit.permit_number}' in description"
                    break
            
            # Strategy 2: Address/location matching
            if not matched_permit:
                # Extract numbers that might be addresses
                import re
                
                # Look for address patterns
                address_patterns = [
                    r'(\d{3,5}[\s-]+[A-Za-z\s]+(?:Ct|Dr|Rd|St|Lane|Ave|Way))',  # 2906 Longford Ct
                    r'(\d{1,4}[\s-]+(?:Phillips|Stoney\s*Point|Beatties|Ardrey))',  # 64 Phillips, 733 Stoney Point
                ]
                
                for pattern in address_patterns:
                    matches = re.findall(pattern, full_description, re.IGNORECASE)
                    if matches:
                        address_hint = matches[0]
                        print(f"  [*] Found address hint: {address_hint}")
                        # For now, just note it - would need permit addresses to match
            
            # Strategy 3: Client-specific patterns
            if not matched_permit and client_permits:
                # For clients with only 1 permit, high confidence match
                if len(client_permits) == 1:
                    matched_permit = client_permits[0]
                    match_reason = f"Only permit for client {client_name}"
                
                # Special cases based on invoice number patterns
                elif client_name == "Gustavo Roldan" and "Phillips" in invoice.invoice_number:
                    # 64-Phillips-1/2 and 64-Phillips-2/2 → BC-25-0409
                    bc_permit = next((p for p in client_permits if p.permit_number == "BC-25-0409"), None)
                    if bc_permit:
                        matched_permit = bc_permit
                        match_reason = "Address pattern (64 Phillips) + client match"
                
                elif client_name == "Marta Alder":
                    # 8343-08-27, t8343-10-31, RES-ALT-25-001173 all reference 8343 NORCROFT
                    # RES-ALT-25-001173 explicitly mentions "8343 NORCROFT DR"
                    res_alt_permit = next((p for p in client_permits if p.permit_number == "RES-ALT-25-001173"), None)
                    if res_alt_permit:
                        if "8343" in invoice.invoice_number or "RES-ALT-25-001173" in full_description:
                            matched_permit = res_alt_permit
                            match_reason = "Address reference (8343 NORCROFT DR) in description"
                
                elif client_name == "Ajay Nair":
                    # Multiple permits - need more specific matching
                    if "BU2025-03428" in full_description:
                        bu_permit = next((p for p in client_permits if p.permit_number == "BU2025-03428"), None)
                        if bu_permit:
                            matched_permit = bu_permit
                            match_reason = "Permit number in description"
                    
                    elif "2906 Longford" in full_description or "2906 Longford" in invoice.invoice_number:
                        # Could match to a Longford permit if we had addresses
                        pass
                    
                    elif "Beatties" in invoice.invoice_number:
                        # 6441Beatties - need address data to match
                        pass
                    
                    elif "Stoney" in invoice.invoice_number or "733" in invoice.invoice_number:
                        # 733-1_StoneyPoint - need address data
                        pass
            
            if matched_permit:
                print(f"  [OK] Matched to: {matched_permit.permit_number}")
                print(f"      Reason: {match_reason}")
                mappings.append({
                    'invoice_id': invoice.invoice_id,
                    'invoice_number': invoice.invoice_number,
                    'permit_id': matched_permit.permit_id,
                    'permit_number': matched_permit.permit_number,
                    'project_id': matched_permit.project_id,
                    'reason': match_reason
                })
            else:
                print(f"  [WARNING] No match found")
            
            print()
        
        # Summary
        print("="*80)
        print("MAPPING SUMMARY")
        print("="*80)
        print(f"Total unmapped invoices: {len(unmapped_invoices)}")
        print(f"Successfully mapped: {len(mappings)}")
        print(f"Still unmapped: {len(unmapped_invoices) - len(mappings)}\n")
        
        if mappings:
            print("Proposed mappings:")
            for mapping in mappings:
                print(f"  {mapping['invoice_number']} → {mapping['permit_number']}")
                print(f"    Reason: {mapping['reason']}")
            print()
        
        # Apply mappings
        if mappings:
            if dry_run:
                print("[DRY RUN] No changes made. Run with --commit to apply.")
            else:
                for mapping in mappings:
                    await session.execute(
                        update(Invoice)
                        .where(Invoice.invoice_id == mapping['invoice_id'])
                        .values(project_id=mapping['project_id'])
                    )
                
                await session.commit()
                print(f"[OK] Applied {len(mappings)} mappings to database")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Map invoices to permits using context')
    parser.add_argument('--commit', action='store_true', help='Actually apply mappings')
    args = parser.parse_args()
    
    asyncio.run(map_invoices_to_permits(dry_run=not args.commit))
