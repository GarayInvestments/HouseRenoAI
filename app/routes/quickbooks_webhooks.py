"""
QuickBooks Webhook Routes

Handles incoming webhook events from QuickBooks Online for real-time data sync.
"""

import hashlib
import hmac
import json
import logging
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Request, HTTPException, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.config import settings
from app.services.db_service import db_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/quickbooks", tags=["QuickBooks Webhooks"])


def verify_webhook_signature(payload: str, signature: str, webhook_token: str) -> bool:
    """
    Verify QuickBooks webhook signature using HMAC-SHA256.
    
    Args:
        payload: Raw request body as string
        signature: Signature from Intuit-Signature header
        webhook_token: Webhook verifier token from QuickBooks app settings
        
    Returns:
        True if signature is valid, False otherwise
    """
    if not webhook_token:
        logger.error("QUICKBOOKS_WEBHOOK_TOKEN not configured")
        return False
    
    # Compute HMAC-SHA256
    expected_signature = hmac.new(
        webhook_token.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).digest().hex()
    
    # Compare signatures (constant-time comparison to prevent timing attacks)
    return hmac.compare_digest(expected_signature, signature)


@router.post("/webhook")
async def receive_webhook(
    request: Request,
    intuit_signature: str = Header(None, alias="Intuit-Signature"),
    db: AsyncSession = Depends(get_db)
):
    """
    Receive and process QuickBooks webhook events.
    
    QuickBooks sends webhook events when entities are created, updated, or deleted.
    This endpoint verifies the signature, stores the event, and triggers sync.
    
    Event types:
    - Customer.Create, Customer.Update, Customer.Delete
    - Invoice.Create, Invoice.Update, Invoice.Delete
    - Payment.Create, Payment.Update, Payment.Delete
    
    Webhook documentation:
    https://developer.intuit.com/app/developer/qbo/docs/develop/webhooks
    """
    try:
        # Get raw request body for signature verification
        body_bytes = await request.body()
        body_str = body_bytes.decode('utf-8')
        
        # Verify webhook signature
        webhook_token = settings.QUICKBOOKS_WEBHOOK_TOKEN
        if not webhook_token:
            logger.warning("QuickBooks webhook received but QUICKBOOKS_WEBHOOK_TOKEN not configured - accepting anyway for testing")
        elif not intuit_signature:
            logger.error("Webhook received without Intuit-Signature header")
            raise HTTPException(status_code=401, detail="Missing webhook signature")
        elif not verify_webhook_signature(body_str, intuit_signature, webhook_token):
            logger.error("Invalid webhook signature")
            raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        # Parse webhook payload
        try:
            payload = json.loads(body_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse webhook payload: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        # QuickBooks webhook structure:
        # {
        #   "eventNotifications": [
        #     {
        #       "realmId": "123456789",
        #       "dataChangeEvent": {
        #         "entities": [
        #           {
        #             "name": "Customer",
        #             "id": "123",
        #             "operation": "Update",
        #             "lastUpdated": "2025-12-14T10:30:00-08:00"
        #           }
        #         ]
        #       }
        #     }
        #   ]
        # }
        
        event_notifications = payload.get("eventNotifications", [])
        if not event_notifications:
            logger.warning("Webhook received with no event notifications")
            return {"status": "ok", "message": "No events to process"}
        
        events_processed = 0
        events_stored = 0
        
        for notification in event_notifications:
            realm_id = notification.get("realmId")
            data_change_event = notification.get("dataChangeEvent", {})
            entities = data_change_event.get("entities", [])
            
            for entity in entities:
                entity_name = entity.get("name")  # Customer, Invoice, Payment
                entity_id = entity.get("id")
                operation = entity.get("operation")  # Create, Update, Delete
                last_updated = entity.get("lastUpdated")
                
                # Create event record
                event_data = {
                    "event_id": f"{realm_id}_{entity_name}_{entity_id}_{operation}_{datetime.utcnow().timestamp()}",
                    "realm_id": realm_id,
                    "event_type": f"{entity_name}.{operation}",
                    "entity_type": entity_name.lower(),
                    "entity_ids": [entity_id],
                    "payload": notification,
                    "processed": False,
                    "created_at": datetime.utcnow()
                }
                
                # Store webhook event in database
                try:
                    result = await db.execute(
                        """
                        INSERT INTO webhook_events 
                        (event_id, realm_id, event_type, entity_type, entity_ids, payload, processed, created_at)
                        VALUES (:event_id, :realm_id, :event_type, :entity_type, :entity_ids, :payload, :processed, :created_at)
                        ON CONFLICT (event_id) DO NOTHING
                        RETURNING id
                        """,
                        event_data
                    )
                    await db.commit()
                    
                    if result.rowcount > 0:
                        events_stored += 1
                        logger.info(f"[WEBHOOK] Stored event: {entity_name}.{operation} (ID: {entity_id})")
                    
                    events_processed += 1
                    
                except Exception as e:
                    logger.error(f"Failed to store webhook event: {e}", exc_info=True)
                    await db.rollback()
        
        logger.info(f"[WEBHOOK] Processed {events_processed} events, stored {events_stored} new events")
        
        # TODO: Trigger immediate sync for affected entity types (will implement in sync service)
        # For now, just log and let scheduled sync handle it
        
        return {
            "status": "ok",
            "events_processed": events_processed,
            "events_stored": events_stored,
            "message": "Webhook events received and queued for processing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook processing error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error processing webhook")


@router.get("/webhook/events")
async def list_webhook_events(
    limit: int = 50,
    processed: bool = None,
    entity_type: str = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List recent webhook events for debugging and monitoring.
    
    Query parameters:
    - limit: Max events to return (default: 50)
    - processed: Filter by processed status
    - entity_type: Filter by entity type (customer, invoice, payment)
    """
    try:
        # Build query
        query = "SELECT * FROM webhook_events WHERE 1=1"
        params = {"limit": limit}
        
        if processed is not None:
            query += " AND processed = :processed"
            params["processed"] = processed
        
        if entity_type:
            query += " AND entity_type = :entity_type"
            params["entity_type"] = entity_type.lower()
        
        query += " ORDER BY created_at DESC LIMIT :limit"
        
        result = await db.execute(query, params)
        events = result.fetchall()
        
        return {
            "events": [
                {
                    "id": event.id,
                    "event_id": event.event_id,
                    "realm_id": event.realm_id,
                    "event_type": event.event_type,
                    "entity_type": event.entity_type,
                    "entity_ids": event.entity_ids,
                    "processed": event.processed,
                    "processed_at": event.processed_at.isoformat() if event.processed_at else None,
                    "processing_error": event.processing_error,
                    "created_at": event.created_at.isoformat()
                }
                for event in events
            ],
            "count": len(events)
        }
        
    except Exception as e:
        logger.error(f"Failed to list webhook events: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve webhook events")


@router.post("/webhook/events/{event_id}/reprocess")
async def reprocess_webhook_event(
    event_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Manually reprocess a failed webhook event.
    
    Useful for debugging or retrying events that failed due to temporary errors.
    """
    try:
        # Mark event as unprocessed
        result = await db.execute(
            """
            UPDATE webhook_events
            SET processed = false,
                processed_at = NULL,
                processing_error = NULL
            WHERE id = :event_id
            RETURNING event_id, event_type
            """,
            {"event_id": event_id}
        )
        await db.commit()
        
        event = result.fetchone()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        logger.info(f"[WEBHOOK] Marked event {event.event_id} for reprocessing")
        
        # TODO: Trigger immediate sync (will implement in sync service)
        
        return {
            "status": "ok",
            "message": f"Event {event.event_id} queued for reprocessing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reprocess event: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to reprocess event")
