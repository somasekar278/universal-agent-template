"""
Schema compatibility checking.

Detects breaking changes between schema versions.
"""

from enum import Enum
from typing import Type, List, Optional, Set
from pydantic import BaseModel
from pydantic.fields import FieldInfo


class ChangeType(str, Enum):
    """Types of schema changes."""
    
    # Non-breaking changes
    FIELD_ADDED_OPTIONAL = "field_added_optional"
    FIELD_DESCRIPTION_CHANGED = "field_description_changed"
    DEFAULT_VALUE_ADDED = "default_value_added"
    
    # Breaking changes
    FIELD_REMOVED = "field_removed"
    FIELD_RENAMED = "field_renamed"
    FIELD_TYPE_CHANGED = "field_type_changed"
    FIELD_MADE_REQUIRED = "field_made_required"
    FIELD_MADE_OPTIONAL = "field_made_optional"
    DEFAULT_VALUE_REMOVED = "default_value_removed"
    DEFAULT_VALUE_CHANGED = "default_value_changed"
    VALIDATION_STRICTER = "validation_stricter"


class BreakingChange(BaseModel):
    """Represents a breaking change between schema versions."""
    
    change_type: ChangeType
    field_name: str
    description: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    
    def is_breaking(self) -> bool:
        """Check if this is a breaking change."""
        breaking_types = {
            ChangeType.FIELD_REMOVED,
            ChangeType.FIELD_RENAMED,
            ChangeType.FIELD_TYPE_CHANGED,
            ChangeType.FIELD_MADE_REQUIRED,
            ChangeType.DEFAULT_VALUE_REMOVED,
            ChangeType.VALIDATION_STRICTER,
        }
        return self.change_type in breaking_types


class CompatibilityChecker:
    """
    Checks compatibility between two schema versions.
    
    Detects breaking and non-breaking changes.
    """
    
    @staticmethod
    def compare_schemas(
        old_schema: Type[BaseModel],
        new_schema: Type[BaseModel]
    ) -> List[BreakingChange]:
        """
        Compare two schema versions and identify changes.
        
        Args:
            old_schema: Old schema version
            new_schema: New schema version
            
        Returns:
            List of detected changes
        """
        changes = []
        
        old_fields = old_schema.model_fields
        new_fields = new_schema.model_fields
        
        old_field_names = set(old_fields.keys())
        new_field_names = set(new_fields.keys())
        
        # Removed fields
        removed = old_field_names - new_field_names
        for field_name in removed:
            changes.append(BreakingChange(
                change_type=ChangeType.FIELD_REMOVED,
                field_name=field_name,
                description=f"Field '{field_name}' was removed"
            ))
        
        # Added fields
        added = new_field_names - old_field_names
        for field_name in added:
            field_info = new_fields[field_name]
            is_required = field_info.is_required()
            
            if is_required:
                changes.append(BreakingChange(
                    change_type=ChangeType.FIELD_MADE_REQUIRED,
                    field_name=field_name,
                    description=f"Required field '{field_name}' was added"
                ))
            else:
                changes.append(BreakingChange(
                    change_type=ChangeType.FIELD_ADDED_OPTIONAL,
                    field_name=field_name,
                    description=f"Optional field '{field_name}' was added"
                ))
        
        # Changed fields
        common = old_field_names & new_field_names
        for field_name in common:
            old_field = old_fields[field_name]
            new_field = new_fields[field_name]
            
            field_changes = CompatibilityChecker._compare_field(
                field_name, old_field, new_field
            )
            changes.extend(field_changes)
        
        return changes
    
    @staticmethod
    def _compare_field(
        field_name: str,
        old_field: FieldInfo,
        new_field: FieldInfo
    ) -> List[BreakingChange]:
        """Compare a single field between versions."""
        changes = []
        
        # Type changed
        if old_field.annotation != new_field.annotation:
            changes.append(BreakingChange(
                change_type=ChangeType.FIELD_TYPE_CHANGED,
                field_name=field_name,
                description=f"Field '{field_name}' type changed",
                old_value=str(old_field.annotation),
                new_value=str(new_field.annotation)
            ))
        
        # Required/optional changed
        old_required = old_field.is_required()
        new_required = new_field.is_required()
        
        if old_required and not new_required:
            changes.append(BreakingChange(
                change_type=ChangeType.FIELD_MADE_OPTIONAL,
                field_name=field_name,
                description=f"Field '{field_name}' changed from required to optional"
            ))
        elif not old_required and new_required:
            changes.append(BreakingChange(
                change_type=ChangeType.FIELD_MADE_REQUIRED,
                field_name=field_name,
                description=f"Field '{field_name}' changed from optional to required"
            ))
        
        # Default value changed
        old_default = old_field.default
        new_default = new_field.default
        
        if old_default != new_default:
            if old_default is not None and new_default is None:
                changes.append(BreakingChange(
                    change_type=ChangeType.DEFAULT_VALUE_REMOVED,
                    field_name=field_name,
                    description=f"Default value for '{field_name}' was removed",
                    old_value=str(old_default)
                ))
            elif old_default is None and new_default is not None:
                changes.append(BreakingChange(
                    change_type=ChangeType.DEFAULT_VALUE_ADDED,
                    field_name=field_name,
                    description=f"Default value for '{field_name}' was added",
                    new_value=str(new_default)
                ))
            else:
                changes.append(BreakingChange(
                    change_type=ChangeType.DEFAULT_VALUE_CHANGED,
                    field_name=field_name,
                    description=f"Default value for '{field_name}' changed",
                    old_value=str(old_default),
                    new_value=str(new_default)
                ))
        
        return changes
    
    @staticmethod
    def is_backward_compatible(
        old_schema: Type[BaseModel],
        new_schema: Type[BaseModel]
    ) -> tuple[bool, List[BreakingChange]]:
        """
        Check if new schema is backward compatible with old schema.
        
        Returns:
            Tuple of (is_compatible, list_of_breaking_changes)
        """
        changes = CompatibilityChecker.compare_schemas(old_schema, new_schema)
        breaking_changes = [c for c in changes if c.is_breaking()]
        
        is_compatible = len(breaking_changes) == 0
        
        return is_compatible, breaking_changes
    
    @staticmethod
    def suggest_version_bump(
        old_schema: Type[BaseModel],
        new_schema: Type[BaseModel],
        current_version: str
    ) -> str:
        """
        Suggest next version number based on changes.
        
        Uses semantic versioning:
        - Major bump for breaking changes
        - Minor bump for new features
        - Patch bump for fixes/docs
        
        Args:
            old_schema: Old schema version
            new_schema: New schema version
            current_version: Current version string
            
        Returns:
            Suggested new version
        """
        from packaging import version as pkg_version
        
        changes = CompatibilityChecker.compare_schemas(old_schema, new_schema)
        
        if not changes:
            # No changes - patch bump
            ver = pkg_version.parse(current_version)
            return f"{ver.major}.{ver.minor}.{ver.micro + 1}"
        
        has_breaking = any(c.is_breaking() for c in changes)
        
        if has_breaking:
            # Breaking changes - major bump
            ver = pkg_version.parse(current_version)
            return f"{ver.major + 1}.0.0"
        else:
            # Non-breaking additions - minor bump
            ver = pkg_version.parse(current_version)
            return f"{ver.major}.{ver.minor + 1}.0"

