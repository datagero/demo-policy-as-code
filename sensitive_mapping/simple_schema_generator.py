#!/usr/bin/env python3
"""
Simple Schema Generator for OPA Validation
Converts dbt schema to a simple format for OPA policy validation.
"""

import yaml
import json
import os
from datetime import datetime


def load_dbt_schema(schema_file: str) -> dict:
    """Load dbt schema file."""
    with open(schema_file, 'r') as file:
        return yaml.safe_load(file)


def load_mapping(mapping_file: str) -> dict:
    """Load sensitive fields mapping."""
    with open(mapping_file, 'r') as file:
        return yaml.safe_load(file)


def generate_simple_schema(dbt_schema: dict, mapping: dict = None) -> dict:
    """Generate simple schema structure for OPA validation."""
    
    schema_data = {
        "schema": {
            "models": []
        }
    }
    
    for model in dbt_schema.get("models", []):
        model_info = {
            "name": model.get("name", ""),
            "description": model.get("description", ""),
            "columns": []
        }
        
        for column in model.get("columns", []):
            column_info = {
                "name": column.get("name", ""),
                "description": column.get("description", ""),
                "security_role": column.get("meta", {}).get("column_security_role"),
                "is_sensitive": bool(column.get("meta", {}).get("column_security_role"))
            }
            
            # Add mapping info if available
            if mapping:
                mapping_info = mapping.get("fields", {}).get(column.get("name", ""), {})
                if mapping_info:
                    column_info["mapping"] = mapping_info
            
            model_info["columns"].append(column_info)
        
        schema_data["schema"]["models"].append(model_info)
    
    # Wrap in input key for OPA
    return {"input": schema_data}


def save_schema(schema: dict, output_file: str):
    """Save schema to file."""
    with open(output_file, 'w') as file:
        json.dump(schema, file, indent=2)
    print(f"Schema saved to: {output_file}")


def main():
    """Main function."""
    # Load files
    dbt_schema = load_dbt_schema("dbt_model/anonymization.yml")
    mapping = load_mapping("sensitive_fields_mapping.yml")
    
    # Generate simple schema
    simple_schema = generate_simple_schema(dbt_schema, mapping)
    
    # Save to file
    save_schema(simple_schema, "schema_for_opa.json")
    
    print("Simple schema generated successfully!")
    print("You can now use this with OPA for validation.")


if __name__ == "__main__":
    main() 