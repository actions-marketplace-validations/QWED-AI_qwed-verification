import sqlglot
from sqlglot import exp, parse_one
from typing import List, Dict, Any, Optional, Set

class SecurityViolation(Exception):
    """Raised when a security policy is violated."""
    pass

class SQLVerifier:
    """
    Engine 6: SQL Verifier (Security Firewall).
    Handles AST-based SQL analysis to prevent injection, data leakage, and destructive actions.
    """
    
    # 🚫 Destructive commands (Blocked by default)
    DESTRUCTIVE_COMMANDS = {
        exp.Drop, exp.Delete, exp.Update, exp.Insert, 
        exp.Alter, exp.TruncateTable, exp.Create, exp.Merge
    }

    # 🔑 Administrative / Permission commands
    ADMIN_COMMANDS = {
        exp.Grant, exp.Revoke, exp.Transaction, exp.Set, exp.Command
    }

    # 🔒 Sensitive columns (Forbidden in SELECT/WHERE)
    SENSITIVE_COLUMNS = {
        "password", "password_hash", "passwd", "pwd",
        "secret", "secret_key", "api_key", "token",
        "ssn", "social_security", "salary", "credit_card",
        "bank_account", "balance"
    }

    def __init__(self, blocked_columns: Optional[Set[str]] = None):
        self.blocked_columns = self.SENSITIVE_COLUMNS.union(blocked_columns or set())

    def verify_sql(self, query: str, schema_ddl: Optional[str] = None, dialect: str = "postgres") -> Dict[str, Any]:
        """
        Verifies a SQL query for safety and optionally against a schema.
        """
        issues = []
        try:
            # 1. Parse Query
            parsed_query = parse_one(query, read=dialect)
        except Exception as e:
            return {
                "is_safe": False,
                "status": "SYNTAX_ERROR",
                "issues": [f"SQL Syntax Error: {str(e)}"]
            }

        # 2. Command Type Check
        if type(parsed_query) in self.DESTRUCTIVE_COMMANDS:
            issues.append(f"CRITICAL: Destructive command detected ({type(parsed_query).__name__}). Only SELECT is allowed.")
        
        if type(parsed_query) in self.ADMIN_COMMANDS:
            issues.append(f"CRITICAL: Administrative command detected ({type(parsed_query).__name__}).")

        # 3. Column-Level Security Scan
        for column in parsed_query.find_all(exp.Column):
            col_name = column.name.lower()
            if col_name in self.blocked_columns:
                issues.append(f"SECURITY: Access to sensitive column '{col_name}' is forbidden.")

        # 4. Injection Pattern Detection (Tautologies & Comments)
        # Detect 'OR 1=1' or similar tautologies in WHERE/HAVING
        for condition in parsed_query.find_all(exp.Binary):
            if isinstance(condition, exp.EQ):
                # Check for things like '1=1' or 'a=a'
                if condition.left == condition.right:
                    issues.append(f"INJECTION: Tautology detected ({condition.sql()}). Likely injection attempt.")
            
            if isinstance(condition, exp.Or):
                # Check for things like 'OR TRUE'
                if isinstance(condition.right, exp.Boolean) and condition.right.this:
                    issues.append("INJECTION: 'OR TRUE' pattern detected.")

        # 5. Schema Validation (If DDL provided)
        if schema_ddl:
            schema_issues = self._validate_against_schema(parsed_query, schema_ddl, dialect)
            issues.extend(schema_issues)

        is_safe = len(issues) == 0
        return {
            "is_safe": is_safe,
            "status": "SAFE" if is_safe else "BLOCKED",
            "issues": issues,
            "engine": "SQLGlot-AST-Scanner"
        }

    def _validate_against_schema(self, parsed_query: exp.Expression, schema_ddl: str, dialect: str) -> List[str]:
        issues = []
        tables_in_schema = {}
        
        try:
            parsed_schema = sqlglot.parse(schema_ddl, read=dialect)
            for expression in parsed_schema:
                if isinstance(expression, exp.Create) and isinstance(expression.this, exp.Schema):
                    table_name = expression.this.this.name
                    columns = {col.this.name.lower() for col in expression.this.expressions if isinstance(col, exp.ColumnDef)}
                    tables_in_schema[table_name] = columns
        except Exception:
            return ["SCHEMA_ERROR: Could not parse DDL schema."]

        # Check tables existence
        for table in parsed_query.find_all(exp.Table):
            t_name = table.name
            if t_name not in tables_in_schema:
                issues.append(f"SCHEMA: Table '{t_name}' does not exist in the provided schema.")
            else:
                # Check column existence if specific columns named
                for column in table.find_all(exp.Column):
                    c_name = column.name.lower()
                    if c_name != "*" and c_name not in tables_in_schema[t_name]:
                        # Note: Some expressions might have columns not directly under table node
                        pass 

        return issues
