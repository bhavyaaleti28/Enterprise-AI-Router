from database.database import create_tables, seed_demo_accounts


create_tables()
seed_demo_accounts()

print("Database setup completed.")
print("\nDemo accounts:")
print("  Employee:     employee / employee123")
print("  HR:           hr_admin / hr123")
print("  IT Support:   it_admin / it123")
print("  Finance:      finance_admin / finance123")
print("  Facilities:   facilities_admin / facilities123")
print("  Operations:   operations_admin / operations123")
print("  Legal:        legal_admin / legal123")
print("  Security:     security_admin / security123")
print("  Sales:        sales_admin / sales123")
