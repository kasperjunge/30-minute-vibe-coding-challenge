"""Seed initial data for development and testing."""

from sqlalchemy.orm import Session

from app.auth.password import hash_password
from app.database import SessionLocal
from app.models import User, Project, TAccount


def seed_database():
    """Seed the database with initial test data."""
    db = SessionLocal()

    try:
        # Check if data already exists
        existing_users = db.query(User).count()
        if existing_users > 0:
            print("Database already contains data. Skipping seed.")
            return

        print("Seeding database...")

        # Create users
        admin = User(
            email="admin@xyz.dk",
            password_hash=hash_password("admin123"),
            full_name="Admin User",
            role="admin",
            is_active=True
        )
        db.add(admin)

        manager = User(
            email="manager@xyz.dk",
            password_hash=hash_password("manager123"),
            full_name="Manager Name",
            role="manager",
            is_active=True
        )
        db.add(manager)

        team_lead = User(
            email="teamlead@xyz.dk",
            password_hash=hash_password("teamlead123"),
            full_name="Team Lead Name",
            role="team_lead",
            is_active=True
        )
        db.add(team_lead)

        accounting = User(
            email="accounting@xyz.dk",
            password_hash=hash_password("accounting123"),
            full_name="Accounting Staff",
            role="accounting",
            is_active=True
        )
        db.add(accounting)

        # Flush to get IDs for relationships
        db.flush()

        # Create employees with manager
        employee1 = User(
            email="employee1@xyz.dk",
            password_hash=hash_password("employee123"),
            full_name="Employee One",
            role="employee",
            manager_id=manager.id,
            is_active=True
        )
        db.add(employee1)

        employee2 = User(
            email="employee2@xyz.dk",
            password_hash=hash_password("employee123"),
            full_name="Employee Two",
            role="employee",
            manager_id=manager.id,
            is_active=True
        )
        db.add(employee2)

        print("✓ Created 6 users")

        # Create T-Accounts
        taccounts = [
            TAccount(
                account_code="T-1001",
                account_name="Sales Travel",
                description="Travel expenses for sales activities",
                is_active=True
            ),
            TAccount(
                account_code="T-1002",
                account_name="Project Travel",
                description="Travel expenses for project-related work",
                is_active=True
            ),
            TAccount(
                account_code="T-1003",
                account_name="Operations Travel",
                description="General operational travel expenses",
                is_active=True
            ),
            TAccount(
                account_code="T-1004",
                account_name="Training Travel",
                description="Travel for training and conferences",
                is_active=True
            ),
            TAccount(
                account_code="T-1005",
                account_name="Client Relations",
                description="Travel for client meetings and relations",
                is_active=True
            ),
        ]

        for taccount in taccounts:
            db.add(taccount)

        print("✓ Created 5 T-accounts")

        # Flush to get team_lead ID
        db.flush()

        # Create projects
        projects = [
            Project(
                name="Project Alpha",
                description="New client engagement in Sweden",
                team_lead_id=team_lead.id,
                is_active=True
            ),
            Project(
                name="Project Beta",
                description="Internal system upgrade",
                team_lead_id=manager.id,
                is_active=True
            ),
            Project(
                name="Project Gamma",
                description="Market expansion to Norway",
                team_lead_id=team_lead.id,
                is_active=True
            ),
        ]

        for project in projects:
            db.add(project)

        print("✓ Created 3 projects")

        # Commit all changes
        db.commit()
        print("\n✅ Database seeded successfully!")

        # Print summary
        print("\n📝 Test Accounts:")
        print("  Admin:      admin@xyz.dk / admin123")
        print("  Manager:    manager@xyz.dk / manager123")
        print("  Team Lead:  teamlead@xyz.dk / teamlead123")
        print("  Employee 1: employee1@xyz.dk / employee123")
        print("  Employee 2: employee2@xyz.dk / employee123")
        print("  Accounting: accounting@xyz.dk / accounting123")

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
