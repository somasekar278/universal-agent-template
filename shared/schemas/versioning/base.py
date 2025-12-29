"""
Base classes for schema versioning.

Provides core infrastructure for managing multiple versions of Pydantic schemas.
"""

from typing import Type, Dict, Optional, Any, TypeVar, Generic
from datetime import datetime
from packaging import version as pkg_version
from pydantic import BaseModel, Field


T = TypeVar('T', bound=BaseModel)


class SchemaVersion(BaseModel):
    """
    Metadata about a schema version.
    """
    
    version: str = Field(..., description="Semantic version (e.g., 1.0.0, 2.1.3)")
    schema_name: str = Field(..., description="Schema name (e.g., Transaction, AgentOutput)")
    deprecated: bool = Field(default=False, description="Whether this version is deprecated")
    deprecated_date: Optional[datetime] = Field(default=None)
    sunset_date: Optional[datetime] = Field(
        default=None,
        description="When this version will be removed"
    )
    breaking_changes: list[str] = Field(
        default_factory=list,
        description="List of breaking changes from previous version"
    )
    migration_guide_url: Optional[str] = Field(default=None)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    def is_compatible_with(self, other_version: str) -> bool:
        """
        Check if this version is backward compatible with another version.
        
        Uses semantic versioning rules:
        - Major version change = breaking changes
        - Minor version change = backward compatible additions
        - Patch version change = backward compatible fixes
        """
        self_ver = pkg_version.parse(self.version)
        other_ver = pkg_version.parse(other_version)
        
        # Same major version = backward compatible
        return self_ver.major == other_ver.major
    
    def is_newer_than(self, other_version: str) -> bool:
        """Check if this version is newer than another."""
        return pkg_version.parse(self.version) > pkg_version.parse(other_version)


class VersionedSchema(Generic[T]):
    """
    Container for a versioned Pydantic schema.
    
    Wraps a Pydantic model with version metadata.
    """
    
    def __init__(
        self,
        schema_class: Type[T],
        version_info: SchemaVersion,
    ):
        self.schema_class = schema_class
        self.version_info = version_info
    
    @property
    def version(self) -> str:
        """Get version string."""
        return self.version_info.version
    
    @property
    def schema_name(self) -> str:
        """Get schema name."""
        return self.version_info.schema_name
    
    def parse(self, data: Dict[str, Any]) -> T:
        """Parse data into schema model."""
        return self.schema_class.model_validate(data)
    
    def is_deprecated(self) -> bool:
        """Check if this version is deprecated."""
        return self.version_info.deprecated
    
    def is_sunset(self) -> bool:
        """Check if this version has passed its sunset date."""
        if not self.version_info.sunset_date:
            return False
        return datetime.utcnow() > self.version_info.sunset_date


class SchemaRegistry:
    """
    Registry for managing multiple versions of schemas.
    
    Allows:
    - Registering schema versions
    - Looking up specific versions
    - Getting latest version
    - Version negotiation
    """
    
    def __init__(self):
        # schema_name -> version -> VersionedSchema
        self._schemas: Dict[str, Dict[str, VersionedSchema]] = {}
        
        # schema_name -> latest_version
        self._latest: Dict[str, str] = {}
    
    def register(
        self,
        schema_name: str,
        version: str,
        schema_class: Type[BaseModel],
        **version_metadata
    ) -> None:
        """
        Register a schema version.
        
        Args:
            schema_name: Name of the schema (e.g., "Transaction")
            version: Semantic version (e.g., "1.0.0")
            schema_class: Pydantic model class
            **version_metadata: Additional version metadata
        """
        if schema_name not in self._schemas:
            self._schemas[schema_name] = {}
        
        version_info = SchemaVersion(
            version=version,
            schema_name=schema_name,
            **version_metadata
        )
        
        versioned_schema = VersionedSchema(
            schema_class=schema_class,
            version_info=version_info
        )
        
        self._schemas[schema_name][version] = versioned_schema
        
        # Update latest version
        self._update_latest(schema_name, version)
    
    def get(
        self,
        schema_name: str,
        version: Optional[str] = None
    ) -> Optional[VersionedSchema]:
        """
        Get a specific schema version.
        
        Args:
            schema_name: Name of schema
            version: Version string (None = latest)
            
        Returns:
            VersionedSchema or None if not found
        """
        if schema_name not in self._schemas:
            return None
        
        if version is None:
            version = self._latest.get(schema_name)
            if version is None:
                return None
        
        return self._schemas[schema_name].get(version)
    
    def get_latest(self, schema_name: str) -> Optional[VersionedSchema]:
        """Get the latest version of a schema."""
        return self.get(schema_name, version=None)
    
    def list_versions(self, schema_name: str) -> list[str]:
        """List all versions of a schema, sorted newest to oldest."""
        if schema_name not in self._schemas:
            return []
        
        versions = list(self._schemas[schema_name].keys())
        versions.sort(key=pkg_version.parse, reverse=True)
        return versions
    
    def list_schemas(self) -> list[str]:
        """List all registered schema names."""
        return list(self._schemas.keys())
    
    def negotiate_version(
        self,
        schema_name: str,
        requested_version: str,
        accept_newer: bool = True
    ) -> Optional[VersionedSchema]:
        """
        Negotiate a schema version based on client request.
        
        Args:
            schema_name: Schema name
            requested_version: Client's requested version
            accept_newer: If True, return newer compatible version if available
            
        Returns:
            Best matching schema version
        """
        if schema_name not in self._schemas:
            return None
        
        # Exact match
        if requested_version in self._schemas[schema_name]:
            schema = self._schemas[schema_name][requested_version]
            if not schema.is_sunset():
                return schema
        
        if not accept_newer:
            return None
        
        # Find newest compatible version
        versions = self.list_versions(schema_name)
        requested_ver = pkg_version.parse(requested_version)
        
        for ver_str in versions:
            ver = pkg_version.parse(ver_str)
            schema = self._schemas[schema_name][ver_str]
            
            # Same major version = compatible
            if ver.major == requested_ver.major and not schema.is_sunset():
                return schema
        
        return None
    
    def _update_latest(self, schema_name: str, new_version: str) -> None:
        """Update the latest version for a schema."""
        current_latest = self._latest.get(schema_name)
        
        if current_latest is None:
            self._latest[schema_name] = new_version
            return
        
        # Compare versions
        if pkg_version.parse(new_version) > pkg_version.parse(current_latest):
            self._latest[schema_name] = new_version
    
    def deprecate_version(
        self,
        schema_name: str,
        version: str,
        sunset_date: Optional[datetime] = None
    ) -> None:
        """
        Mark a schema version as deprecated.
        
        Args:
            schema_name: Schema name
            version: Version to deprecate
            sunset_date: When version will be removed
        """
        schema = self.get(schema_name, version)
        if schema:
            schema.version_info.deprecated = True
            schema.version_info.deprecated_date = datetime.utcnow()
            if sunset_date:
                schema.version_info.sunset_date = sunset_date


# Global registry instance
schema_registry = SchemaRegistry()

