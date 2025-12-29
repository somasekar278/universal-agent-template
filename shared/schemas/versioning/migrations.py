"""
Schema migration utilities.

Handles transforming data from one schema version to another.
"""

from typing import Dict, Any, Optional, Callable, List
from abc import ABC, abstractmethod
from pydantic import BaseModel


class SchemaMigration(ABC):
    """
    Base class for schema migrations.
    
    Handles transforming data from one version to another.
    """
    
    def __init__(
        self,
        from_version: str,
        to_version: str,
        schema_name: str
    ):
        self.from_version = from_version
        self.to_version = to_version
        self.schema_name = schema_name
    
    @abstractmethod
    def migrate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate data from one version to another.
        
        Args:
            data: Data in from_version format
            
        Returns:
            Data in to_version format
        """
        pass
    
    def can_migrate(self, from_ver: str, to_ver: str) -> bool:
        """Check if this migration can handle given version pair."""
        return (from_ver == self.from_version and to_ver == self.to_version)


class FieldMigration(SchemaMigration):
    """
    Migration that applies field transformations.
    
    Example:
        # Rename field
        migration = FieldMigration(
            from_version="1.0.0",
            to_version="2.0.0",
            schema_name="Transaction",
            field_mappings={
                "old_field": "new_field"
            }
        )
    """
    
    def __init__(
        self,
        from_version: str,
        to_version: str,
        schema_name: str,
        field_mappings: Optional[Dict[str, str]] = None,
        field_transforms: Optional[Dict[str, Callable]] = None,
        default_values: Optional[Dict[str, Any]] = None,
        removed_fields: Optional[List[str]] = None,
    ):
        super().__init__(from_version, to_version, schema_name)
        
        self.field_mappings = field_mappings or {}
        self.field_transforms = field_transforms or {}
        self.default_values = default_values or {}
        self.removed_fields = removed_fields or []
    
    def migrate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply field migrations."""
        migrated = data.copy()
        
        # Remove deprecated fields
        for field in self.removed_fields:
            migrated.pop(field, None)
        
        # Rename fields
        for old_field, new_field in self.field_mappings.items():
            if old_field in migrated:
                migrated[new_field] = migrated.pop(old_field)
        
        # Transform field values
        for field, transform_fn in self.field_transforms.items():
            if field in migrated:
                migrated[field] = transform_fn(migrated[field])
        
        # Add default values for new fields
        for field, default_value in self.default_values.items():
            if field not in migrated:
                migrated[field] = default_value
        
        return migrated


class MigrationChain:
    """
    Chain of migrations to go from one version to another.
    
    Automatically finds path through intermediate versions.
    """
    
    def __init__(self):
        # (schema_name, from_ver, to_ver) -> SchemaMigration
        self._migrations: Dict[tuple, SchemaMigration] = {}
    
    def register(self, migration: SchemaMigration) -> None:
        """Register a migration."""
        key = (
            migration.schema_name,
            migration.from_version,
            migration.to_version
        )
        self._migrations[key] = migration
    
    def migrate(
        self,
        schema_name: str,
        data: Dict[str, Any],
        from_version: str,
        to_version: str
    ) -> Dict[str, Any]:
        """
        Migrate data from one version to another.
        
        Automatically chains migrations if needed.
        
        Args:
            schema_name: Schema name
            data: Data in from_version format
            from_version: Source version
            to_version: Target version
            
        Returns:
            Data in to_version format
            
        Raises:
            ValueError: If no migration path found
        """
        if from_version == to_version:
            return data
        
        # Find migration path
        path = self._find_migration_path(schema_name, from_version, to_version)
        
        if not path:
            raise ValueError(
                f"No migration path found from {from_version} to {to_version} "
                f"for schema {schema_name}"
            )
        
        # Apply migrations in sequence
        current_data = data
        for migration in path:
            current_data = migration.migrate(current_data)
        
        return current_data
    
    def _find_migration_path(
        self,
        schema_name: str,
        from_version: str,
        to_version: str
    ) -> Optional[List[SchemaMigration]]:
        """
        Find path of migrations from one version to another.
        
        Uses BFS to find shortest path.
        """
        from collections import deque
        
        # Direct migration exists?
        direct_key = (schema_name, from_version, to_version)
        if direct_key in self._migrations:
            return [self._migrations[direct_key]]
        
        # BFS to find path
        queue = deque([(from_version, [])])
        visited = {from_version}
        
        while queue:
            current_ver, path = queue.popleft()
            
            # Check all migrations from current version
            for (s_name, from_ver, to_ver), migration in self._migrations.items():
                if s_name != schema_name:
                    continue
                
                if from_ver != current_ver:
                    continue
                
                if to_ver in visited:
                    continue
                
                new_path = path + [migration]
                
                if to_ver == to_version:
                    return new_path
                
                queue.append((to_ver, new_path))
                visited.add(to_ver)
        
        return None


class AutoMigrator:
    """
    Automatically migrates data to latest schema version.
    
    Integrates with SchemaRegistry and MigrationChain.
    """
    
    def __init__(self, migration_chain: MigrationChain):
        self.migration_chain = migration_chain
    
    def migrate_to_latest(
        self,
        schema_name: str,
        data: Dict[str, Any],
        current_version: str,
        target_version: Optional[str] = None
    ) -> tuple[Dict[str, Any], str]:
        """
        Migrate data to latest (or target) version.
        
        Args:
            schema_name: Schema name
            data: Data in current_version format
            current_version: Current version of data
            target_version: Target version (None = latest)
            
        Returns:
            Tuple of (migrated_data, version)
        """
        from .base import schema_registry
        
        # Determine target version
        if target_version is None:
            latest_schema = schema_registry.get_latest(schema_name)
            if not latest_schema:
                raise ValueError(f"No schema registered for {schema_name}")
            target_version = latest_schema.version
        
        # No migration needed?
        if current_version == target_version:
            return data, current_version
        
        # Migrate
        migrated_data = self.migration_chain.migrate(
            schema_name=schema_name,
            data=data,
            from_version=current_version,
            to_version=target_version
        )
        
        return migrated_data, target_version
    
    def auto_upgrade(
        self,
        schema_name: str,
        data: Dict[str, Any],
        data_version: Optional[str] = None
    ) -> tuple[BaseModel, str]:
        """
        Automatically upgrade data to latest schema.
        
        Args:
            schema_name: Schema name
            data: Raw data dict
            data_version: Version of data (if known)
            
        Returns:
            Tuple of (parsed_model, version)
        """
        from .base import schema_registry
        
        # If version not specified, try to infer or use latest
        if data_version is None:
            # Could add version detection logic here
            latest_schema = schema_registry.get_latest(schema_name)
            if not latest_schema:
                raise ValueError(f"No schema registered for {schema_name}")
            return latest_schema.parse(data), latest_schema.version
        
        # Migrate to latest
        migrated_data, target_version = self.migrate_to_latest(
            schema_name=schema_name,
            data=data,
            current_version=data_version
        )
        
        # Parse with target version schema
        target_schema = schema_registry.get(schema_name, target_version)
        if not target_schema:
            raise ValueError(
                f"Schema {schema_name} version {target_version} not found"
            )
        
        return target_schema.parse(migrated_data), target_version


# Global migration chain
migration_chain = MigrationChain()

# Global auto migrator
auto_migrator = AutoMigrator(migration_chain)

