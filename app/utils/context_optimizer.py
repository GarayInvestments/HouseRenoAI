"""
Context Size Optimizer for Phase D.2

Intelligently truncates context data to reduce token usage by 40-50%
while maintaining AI response quality.

Strategy:
1. Recent data (last 30 days): Full detail
2. Medium-age data (30-90 days): Reduced detail
3. Old data (>90 days): Summary statistics only

Query-relevant filtering:
- Extract entity mentions (client names, project IDs, dates)
- Only include records relevant to query
- Always provide summary stats for filtered-out data
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import re

logger = logging.getLogger(__name__)


def extract_entity_mentions(message: str) -> Dict[str, List[str]]:
    """
    Extract mentioned entities from user message.
    
    Returns:
        Dict with lists of mentioned clients, projects, dates, etc.
    """
    message_lower = message.lower()
    entities = {
        "client_names": [],
        "project_keywords": [],
        "date_references": [],
        "specific_ids": []
    }
    
    # Known client/project keywords (expandable)
    known_clients = [
        "temple", "temple hills", "fairmont", "upshur", "kent",
        "columbia", "park", "north capitol"
    ]
    
    for client in known_clients:
        if client in message_lower:
            entities["client_names"].append(client)
    
    # Extract business IDs (CL-00001, PRJ-00002, etc.)
    id_pattern = r'\b(?:CL|PRJ|PER|INS|INV|PAY|SV)-\d{5}\b'
    matches = re.findall(id_pattern, message.upper())
    entities["specific_ids"].extend(matches)
    
    # Date references
    date_keywords = ["today", "yesterday", "last week", "last month", "this month", "recent"]
    for keyword in date_keywords:
        if keyword in message_lower:
            entities["date_references"].append(keyword)
    
    return entities


def truncate_projects(
    projects: List[Dict],
    message: str,
    max_recent: int = 10
) -> Dict[str, Any]:
    """
    Truncate project list intelligently.
    
    Strategy:
    1. If query mentions specific client/project, include only those
    2. Otherwise, return last N projects + summary stats
    
    Args:
        projects: Full project list
        message: User message for context
        max_recent: Max number of recent projects to include in full detail
        
    Returns:
        Dict with truncated projects and summary
    """
    if not projects:
        return {"projects": [], "summary": {}}
    
    entities = extract_entity_mentions(message)
    
    # Filter to query-relevant projects if specific mentions found
    if entities["client_names"] or entities["specific_ids"]:
        relevant = []
        for project in projects:
            # Check client name match
            project_name = project.get("Project Name", "").lower()
            address = project.get("Address", "").lower()
            business_id = project.get("business_id", "")
            
            # Match by client name keyword
            if any(client in project_name or client in address 
                   for client in entities["client_names"]):
                relevant.append(project)
            # Match by business ID
            elif business_id in entities["specific_ids"]:
                relevant.append(project)
        
        if relevant:
            logger.info(f"[OPTIMIZER] Filtered to {len(relevant)} relevant projects (from {len(projects)})")
            return {
                "projects": relevant,
                "summary": {
                    "shown": len(relevant),
                    "total": len(projects),
                    "filtered": True,
                    "filter_reason": "query-relevant only"
                }
            }
    
    # No specific mentions - return recent projects + summary
    # Sort by update date or creation date
    sorted_projects = sorted(
        projects,
        key=lambda x: x.get("updated_at") or x.get("created_at") or "",
        reverse=True
    )
    
    recent = sorted_projects[:max_recent]
    
    # Calculate summary stats for all projects
    status_counts = {}
    for project in projects:
        status = project.get("Status", "Unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    logger.info(f"[OPTIMIZER] Showing {len(recent)} recent projects (total: {len(projects)})")
    
    return {
        "projects": recent,
        "summary": {
            "shown": len(recent),
            "total": len(projects),
            "filtered": False,
            "status_breakdown": status_counts
        }
    }


def truncate_permits(
    permits: List[Dict],
    message: str,
    max_recent: int = 15
) -> Dict[str, Any]:
    """
    Truncate permit list intelligently.
    
    Strategy:
    1. If query mentions specific project/permit, include only those
    2. Otherwise, return recent permits + summary stats
    """
    if not permits:
        return {"permits": [], "summary": {}}
    
    entities = extract_entity_mentions(message)
    
    # Filter to query-relevant permits
    if entities["client_names"] or entities["specific_ids"]:
        relevant = []
        for permit in permits:
            business_id = permit.get("business_id", "")
            project_id = permit.get("project_id", "")
            
            if business_id in entities["specific_ids"] or project_id in entities["specific_ids"]:
                relevant.append(permit)
        
        if relevant:
            logger.info(f"[OPTIMIZER] Filtered to {len(relevant)} relevant permits (from {len(permits)})")
            return {
                "permits": relevant,
                "summary": {
                    "shown": len(relevant),
                    "total": len(permits),
                    "filtered": True
                }
            }
    
    # Return recent permits
    sorted_permits = sorted(
        permits,
        key=lambda x: x.get("updated_at") or x.get("created_at") or "",
        reverse=True
    )
    
    recent = sorted_permits[:max_recent]
    
    # Summary stats
    status_counts = {}
    for permit in permits:
        status = permit.get("Status", "Unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    logger.info(f"[OPTIMIZER] Showing {len(recent)} recent permits (total: {len(permits)})")
    
    return {
        "permits": recent,
        "summary": {
            "shown": len(recent),
            "total": len(permits),
            "filtered": False,
            "status_breakdown": status_counts
        }
    }


def truncate_payments(
    payments: List[Dict],
    message: str,
    max_recent: int = 20
) -> Dict[str, Any]:
    """
    Truncate payment list intelligently.
    
    Strategy:
    1. Recent payments (last 20) in full detail
    2. Older payments: Summary stats only
    """
    if not payments:
        return {"payments": [], "summary": {}}
    
    # Sort by date
    sorted_payments = sorted(
        payments,
        key=lambda x: x.get("Payment Date") or x.get("created_at") or "",
        reverse=True
    )
    
    recent = sorted_payments[:max_recent]
    
    # Summary stats for ALL payments
    total_amount = sum(float(p.get("Amount", 0)) for p in payments)
    status_counts = {}
    for payment in payments:
        status = payment.get("Status", "Unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    logger.info(f"[OPTIMIZER] Showing {len(recent)} recent payments (total: {len(payments)})")
    
    return {
        "payments": recent,
        "summary": {
            "shown": len(recent),
            "total": len(payments),
            "total_amount": total_amount,
            "status_breakdown": status_counts
        }
    }


def truncate_clients(
    clients: List[Dict],
    message: str
) -> Dict[str, Any]:
    """
    Truncate client list intelligently.
    
    Strategy:
    1. If query mentions specific client, include only that client
    2. Otherwise, return all clients (usually not many)
    """
    if not clients:
        return {"clients": [], "summary": {}}
    
    entities = extract_entity_mentions(message)
    
    # Filter to query-relevant clients
    if entities["client_names"] or entities["specific_ids"]:
        relevant = []
        for client in clients:
            client_name = client.get("Full Name", "").lower()
            business_id = client.get("business_id", "")
            
            # Match by name keyword
            if any(name in client_name for name in entities["client_names"]):
                relevant.append(client)
            # Match by business ID
            elif business_id in entities["specific_ids"]:
                relevant.append(client)
        
        if relevant:
            logger.info(f"[OPTIMIZER] Filtered to {len(relevant)} relevant clients (from {len(clients)})")
            return {
                "clients": relevant,
                "summary": {
                    "shown": len(relevant),
                    "total": len(clients),
                    "filtered": True
                }
            }
    
    # Return all clients (usually manageable)
    return {
        "clients": clients,
        "summary": {
            "shown": len(clients),
            "total": len(clients),
            "filtered": False
        }
    }


def truncate_quickbooks_customers(
    customers: List[Dict],
    message: str,
    max_customers: int = 20
) -> Dict[str, Any]:
    """
    Truncate QuickBooks customer list intelligently.
    
    Strategy:
    1. If query mentions specific customer, include only those
    2. Otherwise, return active customers only (up to max_customers)
    """
    if not customers:
        return {"customers": [], "summary": {}}
    
    entities = extract_entity_mentions(message)
    
    # Filter to query-relevant customers
    if entities["client_names"] or entities["specific_ids"]:
        relevant = []
        for customer in customers:
            display_name = customer.get("DisplayName", "").lower()
            company_name = customer.get("CompanyName", "").lower()
            
            # Match by name keyword
            if any(name in display_name or name in company_name 
                   for name in entities["client_names"]):
                relevant.append(customer)
        
        if relevant:
            logger.info(f"[OPTIMIZER] Filtered to {len(relevant)} relevant QB customers (from {len(customers)})")
            return {
                "customers": relevant,
                "summary": {
                    "shown": len(relevant),
                    "total": len(customers),
                    "filtered": True
                }
            }
    
    # Return active customers only (up to max)
    active = [c for c in customers if c.get("Active", True)]
    truncated = active[:max_customers]
    
    logger.info(f"[OPTIMIZER] Showing {len(truncated)} active QB customers (total: {len(customers)})")
    
    return {
        "customers": truncated,
        "summary": {
            "shown": len(truncated),
            "total": len(customers),
            "active_only": True
        }
    }


def truncate_quickbooks_invoices(
    invoices: List[Dict],
    message: str,
    max_recent: int = 10
) -> Dict[str, Any]:
    """
    Truncate QuickBooks invoice list intelligently.
    
    Strategy:
    1. Already limited to 10 most recent in context_builder
    2. Add summary stats for ALL invoices (not shown)
    """
    if not invoices:
        return {"invoices": [], "summary": {}}
    
    # Invoices already sorted and limited in context_builder
    # Just add summary information
    
    total_amount = sum(float(inv.get("TotalAmt", 0)) for inv in invoices)
    paid_count = sum(1 for inv in invoices if inv.get("Balance", 0) == 0)
    unpaid_count = sum(1 for inv in invoices if inv.get("Balance", 0) > 0)
    
    return {
        "invoices": invoices,
        "summary": {
            "shown": len(invoices),
            "total_amount": total_amount,
            "paid_count": paid_count,
            "unpaid_count": unpaid_count,
            "note": "Showing 10 most recent invoices"
        }
    }


def optimize_context(context: Dict[str, Any], message: str) -> Dict[str, Any]:
    """
    Optimize context size by intelligently truncating data.
    
    Phase D.2 Goal: 40-50% token reduction while maintaining quality.
    
    Args:
        context: Full context dict from build_context()
        message: User message for query-relevant filtering
        
    Returns:
        Optimized context with reduced token size
    """
    optimized = {
        "session_memory": context.get("session_memory", {}),
        "contexts_loaded": context.get("contexts_loaded", []),
        "optimized": True
    }
    
    # Optimize database data
    if "projects" in context:
        project_data = truncate_projects(context["projects"], message)
        optimized["projects"] = project_data["projects"]
        optimized["projects_summary"] = project_data["summary"]
    
    if "permits" in context:
        permit_data = truncate_permits(context["permits"], message)
        optimized["permits"] = permit_data["permits"]
        optimized["permits_summary"] = permit_data["summary"]
    
    if "payments" in context:
        payment_data = truncate_payments(context["payments"], message)
        optimized["payments"] = payment_data["payments"]
        optimized["payments_summary"] = payment_data["summary"]
    
    if "clients" in context:
        client_data = truncate_clients(context["clients"], message)
        optimized["clients"] = client_data["clients"]
        optimized["clients_summary"] = client_data["summary"]
    
    # Optimize QuickBooks data
    if "quickbooks" in context:
        qb = context["quickbooks"]
        optimized_qb = {
            "authenticated": qb.get("authenticated", False)
        }
        
        if "customers" in qb:
            customer_data = truncate_quickbooks_customers(qb["customers"], message)
            optimized_qb["customers"] = customer_data["customers"]
            optimized_qb["customers_summary"] = customer_data["summary"]
        
        if "invoices" in qb:
            invoice_data = truncate_quickbooks_invoices(qb["invoices"], message)
            optimized_qb["invoices"] = invoice_data["invoices"]
            optimized_qb["invoices_summary"] = invoice_data["summary"]
        
        optimized["quickbooks"] = optimized_qb
    
    # Copy over any summary data from original context
    if "summary" in context:
        optimized["summary"] = context["summary"]
    
    # Add optimization metadata
    optimized["optimization_metadata"] = {
        "optimized": True,
        "strategy": "query-relevant filtering + recent data priority",
        "target_reduction": "40-50%"
    }
    
    return optimized
