from database.database import (
    create_tables,
    add_user
)


create_tables()

# Demo users
add_user(
    "employee",
    "employee123",
    "EMPLOYEE",
    "EMPLOYEE"
)

add_user(
    "hr_admin",
    "hr123",
    "HR",
    "DOMAIN_ADMIN"
)

add_user(
    "it_admin",
    "it123",
    "IT_SUPPORT",
    "DOMAIN_ADMIN"
)

print("Database setup completed.")