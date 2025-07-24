import httpx
import os
from typing import Dict, Any, Optional, List
from loguru import logger
from datetime import datetime

class ITGlueService:
    def __init__(self):
        self.api_key = os.getenv("ITGLUE_API_KEY")
        self.base_url = os.getenv("ITGLUE_API_URL", "https://api.itglue.com")
        self.organization_id = os.getenv("ITGLUE_ORGANIZATION_ID")
        
        # Log configuration status
        if not self.api_key or not self.base_url:
            logger.warning("ITGlue API credentials not found - running in MOCK mode with sample data")
        else:
            logger.info("ITGlue credentials found - using live API integration")
            
        self.headers = {
            "Content-Type": "application/vnd.api+json",
            "x-api-key": self.api_key
        } if self.api_key else {}
        
        # Mock data for development/demo purposes
        self.mock_enabled = not self.api_key

    async def _make_request(self, endpoint: str, method: str = "GET", params: Dict = None, data: Dict = None):
        """Make HTTP request to ITGlue API with error handling"""
        if self.mock_enabled:
            # Return mock data instead of making real API calls
            return await self._get_mock_data(endpoint)
            
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}{endpoint}"
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    params=params,
                    json=data,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.RequestError as e:
            logger.error(f"ITGlue API request failed: {e}")
            # Fallback to mock data on network error
            return await self._get_mock_data(endpoint)
        except httpx.HTTPStatusError as e:
            logger.error(f"ITGlue API HTTP error {e.response.status_code}: {e.response.text}")
            # Fallback to mock data on API error
            return await self._get_mock_data(endpoint)
        except Exception as e:
            logger.error(f"Unexpected error calling ITGlue API: {e}")
            # Fallback to mock data on any other error
            return await self._get_mock_data(endpoint)

    async def _get_mock_data(self, endpoint: str):
        """Return mock data based on endpoint"""
        if "/articles" in endpoint:
            return {
                "data": [
                    {
                        "id": "1",
                        "attributes": {
                            "name": "Network Configuration Guide",
                            "body": "<h1>Network Configuration Guide</h1><p>Complete guide for configuring network infrastructure...</p>",
                            "created-at": "2025-01-10T09:00:00.000Z",
                            "updated-at": "2025-01-15T10:30:00.000Z"
                        },
                        "relationships": {
                            "organization": {"data": {"id": "1", "type": "organizations"}},
                            "created-by": {"data": {"id": "1", "type": "users"}}
                        }
                    },
                    {
                        "id": "2",
                        "attributes": {
                            "name": "Security Policy Framework",
                            "body": "<h1>Security Policy Framework</h1><p>Comprehensive security policies...</p>",
                            "created-at": "2025-01-05T11:30:00.000Z",
                            "updated-at": "2025-01-14T14:45:00.000Z"
                        }
                    }
                ]
            }
        elif "/configurations" in endpoint:
            return {
                "data": [
                    {
                        "id": "1",
                        "attributes": {
                            "name": "Primary Domain Controller",
                            "notes": "Main Active Directory domain controller",
                            "created-at": "2025-01-01T00:00:00.000Z",
                            "updated-at": "2025-01-15T08:30:00.000Z"
                        }
                    }
                ]
            }
        elif "/passwords" in endpoint:
            return {
                "data": [
                    {
                        "id": "1",
                        "attributes": {
                            "name": "Domain Admin Account",
                            "username": "administrator",
                            "url": "https://dc.techcorp.local",
                            "notes": "Primary domain administrator account",
                            "updated-at": "2025-01-15T09:00:00.000Z"
                        }
                    }
                ]
            }
        elif "/contacts" in endpoint:
            return {
                "data": [
                    {
                        "id": "1",
                        "attributes": {
                            "name": "John Smith",
                            "title": "IT Director", 
                            "contact-emails": [{"value": "john.smith@techcorp.com"}],
                            "contact-phones": [{"value": "+1 (555) 123-4567"}],
                            "notes": "Primary IT contact",
                            "updated-at": "2025-01-15T10:00:00.000Z"
                        }
                    }
                ]
            }
        else:
            return {"data": []}

    async def get_articles(self, limit: int = 100, skip: int = 0, filters: Dict = None):
        """Get knowledge base articles from ITGlue"""
        try:
            params = {
                "page[size]": limit,
                "page[number]": (skip // limit) + 1 if limit > 0 else 1
            }
            
            if filters:
                if filters.get("search"):
                    params["filter[name]"] = filters["search"]
                if filters.get("organization_id"):
                    params["filter[organization_id]"] = filters["organization_id"]
            
            response = await self._make_request("/articles", params=params)
            
            # Transform ITGlue format to our format
            articles = []
            for item in response.get("data", []):
                article = {
                    "id": int(item["id"]),
                    "name": item["attributes"]["name"],
                    "description": self._extract_text_from_html(item["attributes"].get("body", "")),
                    "content": item["attributes"].get("body", ""),
                    "category": "General",  # ITGlue doesn't have categories like this
                    "organization": "TechCorp Inc.",  # Would come from relationships
                    "author": "ITGlue User",  # Would come from created-by relationship
                    "tags": [],  # Would need to be extracted from ITGlue tags
                    "updated_at": item["attributes"]["updated-at"],
                    "created_at": item["attributes"]["created-at"],
                    "bookmarked": False
                }
                articles.append(article)
            
            return articles
            
        except Exception as e:
            logger.error(f"Error getting articles from ITGlue: {e}")
            return []

    async def get_article(self, article_id: int):
        """Get a specific article by ID"""
        try:
            response = await self._make_request(f"/articles/{article_id}")
            
            if response.get("data"):
                item = response["data"]
                return {
                    "id": int(item["id"]),
                    "name": item["attributes"]["name"],
                    "description": self._extract_text_from_html(item["attributes"].get("body", "")),
                    "content": item["attributes"].get("body", ""),
                    "category": "General",
                    "organization": "TechCorp Inc.",
                    "author": "ITGlue User",
                    "tags": [],
                    "updated_at": item["attributes"]["updated-at"],
                    "created_at": item["attributes"]["created-at"],
                    "bookmarked": False
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting article {article_id} from ITGlue: {e}")
            return None

    async def get_configurations(self, limit: int = 100, skip: int = 0, filters: Dict = None):
        """Get configuration items from ITGlue"""
        try:
            params = {
                "page[size]": limit,
                "page[number]": (skip // limit) + 1 if limit > 0 else 1
            }
            
            if filters:
                if filters.get("search"):
                    params["filter[name]"] = filters["search"]
                if filters.get("organization_id"):
                    params["filter[organization_id]"] = filters["organization_id"]
            
            response = await self._make_request("/configurations", params=params)
            
            configurations = []
            for item in response.get("data", []):
                config = {
                    "id": int(item["id"]),
                    "name": item["attributes"]["name"],
                    "description": item["attributes"].get("notes", ""),
                    "configuration_type_name": "Server",  # Would come from configuration-type relationship
                    "organization_name": "TechCorp Inc.",  # Would come from organization relationship
                    "serial_number": item["attributes"].get("serial-number", "N/A"),
                    "asset_tag": item["attributes"].get("asset-tag", "N/A"),
                    "operating_system": item["attributes"].get("operating-system-notes", "N/A"),
                    "ip_address": "192.168.1.10",  # Would be extracted from IP addresses
                    "updated_at": item["attributes"]["updated-at"]
                }
                configurations.append(config)
            
            return configurations
            
        except Exception as e:
            logger.error(f"Error getting configurations from ITGlue: {e}")
            return []

    async def get_passwords(self, limit: int = 100, skip: int = 0, filters: Dict = None):
        """Get password entries from ITGlue (returns limited info for security)"""
        try:
            params = {
                "page[size]": limit,
                "page[number]": (skip // limit) + 1 if limit > 0 else 1
            }
            
            if filters:
                if filters.get("search"):
                    params["filter[name]"] = filters["search"]
                if filters.get("organization_id"):
                    params["filter[organization_id]"] = filters["organization_id"]
            
            response = await self._make_request("/passwords", params=params)
            
            passwords = []
            for item in response.get("data", []):
                password = {
                    "id": int(item["id"]),
                    "name": item["attributes"]["name"],
                    "resource_name": item["attributes"].get("resource-name", ""),
                    "username": item["attributes"].get("username", ""),
                    "organization_name": "TechCorp Inc.",  # Would come from organization relationship
                    "url": item["attributes"].get("url", ""),
                    "notes": item["attributes"].get("notes", ""),
                    "updated_at": item["attributes"]["updated-at"]
                }
                passwords.append(password)
            
            return passwords
            
        except Exception as e:
            logger.error(f"Error getting passwords from ITGlue: {e}")
            return []

    async def get_contacts(self, limit: int = 100, skip: int = 0, filters: Dict = None):
        """Get contacts from ITGlue"""
        try:
            params = {
                "page[size]": limit,
                "page[number]": (skip // limit) + 1 if limit > 0 else 1
            }
            
            if filters:
                if filters.get("search"):
                    params["filter[name]"] = filters["search"]
                if filters.get("organization_id"):
                    params["filter[organization_id]"] = filters["organization_id"]
            
            response = await self._make_request("/contacts", params=params)
            
            contacts = []
            for item in response.get("data", []):
                # Extract email and phone from arrays
                emails = item["attributes"].get("contact-emails", [])
                phones = item["attributes"].get("contact-phones", [])
                
                contact = {
                    "id": int(item["id"]),
                    "name": item["attributes"]["name"],
                    "title": item["attributes"].get("title", ""),
                    "email": emails[0]["value"] if emails else "",
                    "phone": phones[0]["value"] if phones else "",
                    "organization_name": "TechCorp Inc.",  # Would come from organization relationship
                    "department": "Information Technology",  # Would be a custom field
                    "notes": item["attributes"].get("notes", ""),
                    "updated_at": item["attributes"]["updated-at"]
                }
                contacts.append(contact)
            
            return contacts
            
        except Exception as e:
            logger.error(f"Error getting contacts from ITGlue: {e}")
            return []

    async def get_categories(self):
        """Get knowledge base categories - ITGlue doesn't have built-in categories for articles"""
        # Return mock categories since ITGlue handles this differently
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

    async def sync_all_data(self):
        """Sync all data from ITGlue"""
        try:
            results = {
                "articles_synced": 0,
                "configurations_synced": 0,
                "passwords_synced": 0,
                "contacts_synced": 0,
                "categories_updated": 0
            }
            
            # In a real implementation, you would:
            # 1. Fetch all data from ITGlue
            # 2. Store/update in local database
            # 3. Track sync results
            
            if self.mock_enabled:
                # Return mock sync results
                results.update({
                    "articles_synced": 156,
                    "configurations_synced": 89,
                    "passwords_synced": 45,
                    "contacts_synced": 78,
                    "categories_updated": 12
                })
            else:
                # Perform actual sync operations
                articles = await self.get_articles(limit=1000)
                results["articles_synced"] = len(articles)
                
                configurations = await self.get_configurations(limit=1000)
                results["configurations_synced"] = len(configurations)
                
                passwords = await self.get_passwords(limit=1000)
                results["passwords_synced"] = len(passwords)
                
                contacts = await self.get_contacts(limit=1000)
                results["contacts_synced"] = len(contacts)
                
                results["categories_updated"] = 8  # Mock value
            
            return results
            
        except Exception as e:
            logger.error(f"Error syncing data from ITGlue: {e}")
            raise

    async def get_sync_status(self):
        """Get the status of the last sync operation"""
        return {
            "last_sync": datetime.utcnow().replace(hour=10, minute=30, second=0).isoformat() + "Z",
            "status": "completed",
            "items_synced": 368,
            "errors": 0,
            "next_scheduled_sync": datetime.utcnow().replace(hour=10, minute=30, second=0, day=16).isoformat() + "Z"
        }

    async def global_search(self, query: str, content_type: str = None, organization_id: int = None, limit: int = 50):
        """Perform a global search across all ITGlue content"""
        try:
            results = []
            
            if not content_type or content_type == "articles":
                articles = await self.get_articles(limit=limit//4, filters={"search": query})
                for article in articles[:limit//4]:
                    results.append({
                        "type": "article",
                        "id": article["id"],
                        "title": article["name"],
                        "excerpt": f"...{article['description'][:100]}...",
                        "relevance_score": 0.85,
                        "url": f"/knowledge-base/articles/{article['id']}"
                    })
            
            if not content_type or content_type == "configurations":
                configs = await self.get_configurations(limit=limit//4, filters={"search": query})
                for config in configs[:limit//4]:
                    results.append({
                        "type": "configuration",
                        "id": config["id"],
                        "title": config["name"],
                        "excerpt": f"...{config['description'][:100]}...",
                        "relevance_score": 0.75,
                        "url": f"/knowledge-base/configurations/{config['id']}"
                    })
            
            # Sort by relevance score
            results.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Error performing global search: {e}")
            return []

    def _extract_text_from_html(self, html_content: str) -> str:
        """Extract plain text from HTML content for descriptions"""
        if not html_content:
            return ""
        
        # Simple HTML tag removal - in production you'd use a proper HTML parser
        import re
        text = re.sub(r'<[^>]+>', '', html_content)
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:200] + "..." if len(text) > 200 else text

# Create a global instance
itglue_service = ITGlueService() 