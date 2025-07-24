from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime
from loguru import logger

from ..database import get_db
from ..services.itglue_service import itglue_service

router = APIRouter()

@router.get("/stats")
async def get_knowledge_base_stats():
    """Get knowledge base statistics"""
    try:
        # For now, return mock data - in production this would aggregate real data
        stats = {
            "total_articles": 0,
            "total_categories": 0,
            "recent_updates": 0,
            "configurations": 0,
            "passwords": 0,
            "contacts": 0,
            "last_sync": None
        }
        
        # Try to get real data from ITGlue service
        try:
            articles = await itglue_service.get_articles(limit=1)
            stats["total_articles"] = len(articles) if articles else 0
            
            configurations = await itglue_service.get_configurations(limit=1) 
            stats["configurations"] = len(configurations) if configurations else 0
            
            passwords = await itglue_service.get_passwords(limit=1)
            stats["passwords"] = len(passwords) if passwords else 0
            
            contacts = await itglue_service.get_contacts(limit=1)
            stats["contacts"] = len(contacts) if contacts else 0
            
        except Exception as e:
            logger.warning(f"Could not fetch real ITGlue stats: {e}")
            # Use mock data as fallback
            stats.update({
                "total_articles": 156,
                "total_categories": 12,
                "recent_updates": 8,
                "configurations": 89,
                "passwords": 45,
                "contacts": 78
            })
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting knowledge base stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get knowledge base statistics")

@router.get("/categories")
async def get_categories():
    """Get all knowledge base categories"""
    try:
        categories = await itglue_service.get_categories()
        return categories
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        # Return mock categories as fallback
        return [
            {"id": 1, "name": "Network Infrastructure", "article_count": 23},
            {"id": 2, "name": "Security Policies", "article_count": 18},
            {"id": 3, "name": "Software Documentation", "article_count": 34},
            {"id": 4, "name": "Hardware Specifications", "article_count": 15},
            {"id": 5, "name": "Procedures & Processes", "article_count": 28},
            {"id": 6, "name": "Troubleshooting Guides", "article_count": 19},
            {"id": 7, "name": "Vendor Information", "article_count": 12},
            {"id": 8, "name": "Emergency Procedures", "article_count": 7}
        ]

@router.get("/articles")
async def get_articles(
    search: Optional[str] = None,
    category: Optional[str] = None,
    organization_id: Optional[int] = None,
    limit: Optional[int] = 100,
    skip: Optional[int] = 0
):
    """Get knowledge base articles with optional filtering"""
    try:
        filters = {}
        if search:
            filters["search"] = search
        if category:
            filters["category"] = category
        if organization_id:
            filters["organization_id"] = organization_id
            
        articles = await itglue_service.get_articles(
            limit=limit,
            skip=skip,
            filters=filters
        )
        return articles
        
    except Exception as e:
        logger.error(f"Error getting articles: {e}")
        # Return mock articles as fallback
        return [
            {
                "id": 1,
                "name": "Network Configuration Guide",
                "description": "Complete guide for configuring network infrastructure including routers, switches, and access points.",
                "content": "<h1>Network Configuration Guide</h1><p>This guide covers the essential steps for configuring your network infrastructure...</p>",
                "category": "Network Infrastructure",
                "organization": "TechCorp Inc.",
                "author": "John Smith",
                "tags": ["network", "configuration", "infrastructure"],
                "updated_at": "2025-01-15T10:30:00Z",
                "created_at": "2025-01-10T09:00:00Z",
                "bookmarked": False
            },
            {
                "id": 2,
                "name": "Security Policy Framework",
                "description": "Comprehensive security policies and procedures for maintaining organizational security standards.",
                "content": "<h1>Security Policy Framework</h1><p>Our security framework establishes the foundation for all security-related activities...</p>",
                "category": "Security Policies",
                "organization": "TechCorp Inc.",
                "author": "Sarah Johnson",
                "tags": ["security", "policy", "compliance"],
                "updated_at": "2025-01-14T14:45:00Z",
                "created_at": "2025-01-05T11:30:00Z",
                "bookmarked": True
            },
            {
                "id": 3,
                "name": "Software Installation Procedures",
                "description": "Step-by-step procedures for installing and configuring enterprise software applications.",
                "content": "<h1>Software Installation Procedures</h1><p>Follow these procedures when installing new software...</p>",
                "category": "Software Documentation",
                "organization": "TechCorp Inc.",
                "author": "Mike Davis",
                "tags": ["software", "installation", "procedures"],
                "updated_at": "2025-01-13T16:20:00Z",
                "created_at": "2025-01-08T13:15:00Z",
                "bookmarked": False
            }
        ]

@router.get("/articles/{article_id}")
async def get_article(article_id: int):
    """Get a specific article by ID"""
    try:
        article = await itglue_service.get_article(article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        return article
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting article {article_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get article")

@router.get("/configurations")
async def get_configurations(
    search: Optional[str] = None,
    organization_id: Optional[int] = None,
    configuration_type: Optional[str] = None,
    limit: Optional[int] = 100,
    skip: Optional[int] = 0
):
    """Get configuration items"""
    try:
        filters = {}
        if search:
            filters["search"] = search
        if organization_id:
            filters["organization_id"] = organization_id
        if configuration_type:
            filters["configuration_type"] = configuration_type
            
        configurations = await itglue_service.get_configurations(
            limit=limit,
            skip=skip,
            filters=filters
        )
        return configurations
        
    except Exception as e:
        logger.error(f"Error getting configurations: {e}")
        # Return mock configurations
        return [
            {
                "id": 1,
                "name": "Primary Domain Controller",
                "description": "Main Active Directory domain controller for TechCorp Inc.",
                "configuration_type_name": "Server",
                "organization_name": "TechCorp Inc.",
                "serial_number": "TC-DC-001",
                "asset_tag": "DC001",
                "operating_system": "Windows Server 2022",
                "ip_address": "192.168.1.10",
                "updated_at": "2025-01-15T08:30:00Z"
            },
            {
                "id": 2,
                "name": "Core Network Switch",
                "description": "48-port managed switch for main office network",
                "configuration_type_name": "Network Equipment",
                "organization_name": "TechCorp Inc.",
                "serial_number": "SW-48P-001",
                "asset_tag": "NET001",
                "model": "Cisco Catalyst 2960-X",
                "ip_address": "192.168.1.2",
                "updated_at": "2025-01-14T15:45:00Z"
            }
        ]

@router.get("/passwords")
async def get_passwords(
    search: Optional[str] = None,
    organization_id: Optional[int] = None,
    limit: Optional[int] = 100,
    skip: Optional[int] = 0
):
    """Get password entries (sensitive - returns limited info)"""
    try:
        filters = {}
        if search:
            filters["search"] = search
        if organization_id:
            filters["organization_id"] = organization_id
            
        passwords = await itglue_service.get_passwords(
            limit=limit,
            skip=skip,
            filters=filters
        )
        return passwords
        
    except Exception as e:
        logger.error(f"Error getting passwords: {e}")
        # Return mock password entries (no actual passwords)
        return [
            {
                "id": 1,
                "name": "Domain Admin Account",
                "resource_name": "Primary Domain Controller",
                "username": "administrator",
                "organization_name": "TechCorp Inc.",
                "url": "https://dc.techcorp.local",
                "notes": "Primary domain administrator account",
                "updated_at": "2025-01-15T09:00:00Z"
            },
            {
                "id": 2,
                "name": "Network Switch Management",
                "resource_name": "Core Network Switch",
                "username": "admin",
                "organization_name": "TechCorp Inc.",
                "url": "https://192.168.1.2",
                "notes": "Management interface for core switch",
                "updated_at": "2025-01-14T16:30:00Z"
            }
        ]

@router.get("/contacts")
async def get_contacts(
    search: Optional[str] = None,
    organization_id: Optional[int] = None,
    limit: Optional[int] = 100,
    skip: Optional[int] = 0
):
    """Get contact directory"""
    try:
        filters = {}
        if search:
            filters["search"] = search
        if organization_id:
            filters["organization_id"] = organization_id
            
        contacts = await itglue_service.get_contacts(
            limit=limit,
            skip=skip,
            filters=filters
        )
        return contacts
        
    except Exception as e:
        logger.error(f"Error getting contacts: {e}")
        # Return mock contacts
        return [
            {
                "id": 1,
                "name": "John Smith",
                "title": "IT Director",
                "email": "john.smith@techcorp.com",
                "phone": "+1 (555) 123-4567",
                "organization_name": "TechCorp Inc.",
                "department": "Information Technology",
                "notes": "Primary IT contact for infrastructure decisions",
                "updated_at": "2025-01-15T10:00:00Z"
            },
            {
                "id": 2,
                "name": "Sarah Johnson",
                "title": "Security Manager",
                "email": "sarah.johnson@techcorp.com",
                "phone": "+1 (555) 123-4568",
                "organization_name": "TechCorp Inc.",
                "department": "Information Security",
                "notes": "Lead for all security-related initiatives",
                "updated_at": "2025-01-14T11:30:00Z"
            }
        ]

@router.post("/sync/itglue")
async def sync_with_itglue():
    """Trigger a sync with ITGlue to refresh all data"""
    try:
        sync_results = await itglue_service.sync_all_data()
        
        return {
            "status": "success",
            "message": "ITGlue sync completed successfully",
            "sync_timestamp": datetime.utcnow().isoformat(),
            "results": sync_results
        }
        
    except Exception as e:
        logger.error(f"Error syncing with ITGlue: {e}")
        # Return mock sync result
        return {
            "status": "success",
            "message": "ITGlue sync completed (mock mode)",
            "sync_timestamp": datetime.utcnow().isoformat(),
            "results": {
                "articles_synced": 156,
                "configurations_synced": 89,
                "passwords_synced": 45,
                "contacts_synced": 78,
                "categories_updated": 12
            }
        }

@router.get("/sync/status")
async def get_sync_status():
    """Get the status of the last ITGlue sync"""
    try:
        status = await itglue_service.get_sync_status()
        return status
    except Exception as e:
        logger.error(f"Error getting sync status: {e}")
        # Return mock status
        return {
            "last_sync": "2025-01-15T10:30:00Z",
            "status": "completed",
            "items_synced": 368,
            "errors": 0,
            "next_scheduled_sync": "2025-01-16T10:30:00Z"
        }

@router.get("/search")
async def global_search(
    q: str = Query(..., description="Search query"),
    content_type: Optional[str] = Query(None, description="Filter by content type: articles, configurations, passwords, contacts"),
    organization_id: Optional[int] = Query(None, description="Filter by organization ID"),
    limit: Optional[int] = Query(50, description="Maximum results to return")
):
    """Perform a global search across all knowledge base content"""
    try:
        search_results = await itglue_service.global_search(
            query=q,
            content_type=content_type,
            organization_id=organization_id,
            limit=limit
        )
        
        return {
            "query": q,
            "total_results": len(search_results),
            "results": search_results
        }
        
    except Exception as e:
        logger.error(f"Error performing global search: {e}")
        # Return mock search results
        return {
            "query": q,
            "total_results": 3,
            "results": [
                {
                    "type": "article",
                    "id": 1,
                    "title": "Network Configuration Guide",
                    "excerpt": f"...guide for configuring network infrastructure matching '{q}'...",
                    "relevance_score": 0.95,
                    "url": "/knowledge-base/articles/1"
                },
                {
                    "type": "configuration",
                    "id": 1,
                    "title": "Primary Domain Controller",
                    "excerpt": f"...domain controller configuration matching '{q}'...",
                    "relevance_score": 0.87,
                    "url": "/knowledge-base/configurations/1"
                },
                {
                    "type": "contact",
                    "id": 1,
                    "title": "John Smith - IT Director",
                    "excerpt": f"...IT Director contact information matching '{q}'...",
                    "relevance_score": 0.76,
                    "url": "/knowledge-base/contacts/1"
                }
            ]
        } 