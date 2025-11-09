"""
End-to-end workflow tests for the travel approval system.

These tests verify complete user workflows from start to finish,
ensuring that all components work together correctly.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.project import Project
from app.models.taccount import TAccount
from app.models.travel_request import TravelRequest
from app.models.user import User


class TestOperationsRequestWorkflow:
    """Test the complete workflow for operations travel requests."""

    def test_complete_operations_workflow_approval(
        self, client: TestClient, db_session: Session, sample_users: dict[str, User]
    ):
        """
        Test complete workflow: employee submits operations request ->
        manager approves -> notifications sent -> status updated.
        """
        employee = sample_users["employee"]
        manager = sample_users["manager"]
        taccount = db_session.query(TAccount).first()

        # Step 1: Employee logs in
        login_response = client.post(
            "/login",
            data={"email": employee.email, "password": "testpass123"},
            follow_redirects=False,
        )
        assert login_response.status_code == 303
        employee_cookies = {"travel_approval_session": login_response.cookies["travel_approval_session"]}

        # Step 2: Employee submits operations travel request
        tomorrow = date.today() + timedelta(days=1)
        week_later = tomorrow + timedelta(days=7)

        create_response = client.post(
            "/requests/new",
            data={
                "request_type": "operations",
                "destination": "Copenhagen",
                "start_date": tomorrow.isoformat(),
                "end_date": week_later.isoformat(),
                "purpose": "Client meeting and team collaboration",
                "estimated_cost": "15000.00",
                "taccount_id": taccount.id,
            },
            cookies=employee_cookies,
            follow_redirects=False,
        )
        assert create_response.status_code == 303
        assert create_response.headers["location"] == "/dashboard"

        # Step 3: Verify request was created and routed to manager
        travel_request = (
            db_session.query(TravelRequest)
            .filter(TravelRequest.requester_id == employee.id)
            .first()
        )
        assert travel_request is not None
        assert travel_request.approver_id == manager.id
        assert travel_request.status == "pending"
        assert travel_request.destination == "Copenhagen"

        # Step 4: Verify manager received notification
        manager_notifications = (
            db_session.query(Notification)
            .filter(Notification.user_id == manager.id, Notification.is_read == False)
            .all()
        )
        assert len(manager_notifications) >= 1
        notification = manager_notifications[0]
        assert "New travel request" in notification.message
        assert str(travel_request.id) in notification.message

        # Step 5: Manager logs in
        login_response = client.post(
            "/login",
            data={"email": manager.email, "password": "testpass123"},
            follow_redirects=False,
        )
        manager_cookies = {"travel_approval_session": login_response.cookies["travel_approval_session"]}

        # Step 6: Manager views approvals page
        approvals_response = client.get("/approvals", cookies=manager_cookies)
        assert approvals_response.status_code == 200
        assert b"Copenhagen" in approvals_response.content

        # Step 7: Manager approves the request
        approve_response = client.post(
            f"/requests/{travel_request.id}/approve",
            data={"comments": "Approved for client meeting"},
            cookies=manager_cookies,
            follow_redirects=False,
        )
        assert approve_response.status_code == 303

        # Step 8: Verify request status updated
        db_session.refresh(travel_request)
        assert travel_request.status == "approved"
        assert travel_request.approval_comments == "Approved for client meeting"
        assert travel_request.approval_date is not None

        # Step 9: Verify employee received approval notification
        employee_notifications = (
            db_session.query(Notification)
            .filter(
                Notification.user_id == employee.id,
                Notification.message.contains("approved"),
            )
            .all()
        )
        assert len(employee_notifications) >= 1

        # Step 10: Verify accounting received notification
        accounting_user = db_session.query(User).filter(User.role == "accounting").first()
        if accounting_user:
            accounting_notifications = (
                db_session.query(Notification)
                .filter(
                    Notification.user_id == accounting_user.id,
                    Notification.message.contains("approved"),
                )
                .all()
            )
            assert len(accounting_notifications) >= 1

        # Step 11: Employee can see approved request in dashboard
        dashboard_response = client.get("/dashboard", cookies=employee_cookies)
        assert dashboard_response.status_code == 200
        assert b"Approved" in dashboard_response.content
        assert b"Copenhagen" in dashboard_response.content

    def test_complete_operations_workflow_rejection(
        self, client: TestClient, db_session: Session, sample_users: dict[str, User]
    ):
        """
        Test complete workflow: employee submits operations request ->
        manager rejects -> employee sees rejection.
        """
        employee = sample_users["employee"]
        manager = sample_users["manager"]
        taccount = db_session.query(TAccount).first()

        # Step 1: Employee logs in and submits request
        login_response = client.post(
            "/login",
            data={"email": employee.email, "password": "testpass123"},
            follow_redirects=False,
        )
        employee_cookies = {"travel_approval_session": login_response.cookies["travel_approval_session"]}

        tomorrow = date.today() + timedelta(days=1)
        week_later = tomorrow + timedelta(days=7)

        client.post(
            "/requests/new",
            data={
                "request_type": "operations",
                "destination": "Berlin",
                "start_date": tomorrow.isoformat(),
                "end_date": week_later.isoformat(),
                "purpose": "Conference attendance",
                "estimated_cost": "8000.00",
                "taccount_id": taccount.id,
            },
            cookies=employee_cookies,
            follow_redirects=False,
        )

        travel_request = (
            db_session.query(TravelRequest)
            .filter(
                TravelRequest.requester_id == employee.id,
                TravelRequest.destination == "Berlin",
            )
            .first()
        )

        # Step 2: Manager logs in and rejects
        login_response = client.post(
            "/login",
            data={"email": manager.email, "password": "testpass123"},
            follow_redirects=False,
        )
        manager_cookies = {"travel_approval_session": login_response.cookies["travel_approval_session"]}

        reject_response = client.post(
            f"/requests/{travel_request.id}/reject",
            data={"reason": "Budget constraints for this quarter"},
            cookies=manager_cookies,
            follow_redirects=False,
        )
        assert reject_response.status_code == 303

        # Step 3: Verify rejection
        db_session.refresh(travel_request)
        assert travel_request.status == "rejected"
        assert travel_request.rejection_reason == "Budget constraints for this quarter"

        # Step 4: Verify employee received rejection notification
        employee_notifications = (
            db_session.query(Notification)
            .filter(
                Notification.user_id == employee.id,
                Notification.message.contains("rejected"),
            )
            .all()
        )
        assert len(employee_notifications) >= 1

        # Step 5: Employee can see rejection in dashboard
        dashboard_response = client.get("/dashboard", cookies=employee_cookies)
        assert dashboard_response.status_code == 200
        assert b"Rejected" in dashboard_response.content
        assert b"Berlin" in dashboard_response.content


class TestProjectRequestWorkflow:
    """Test the complete workflow for project travel requests."""

    def test_complete_project_workflow_approval(
        self, client: TestClient, db_session: Session, sample_users: dict[str, User]
    ):
        """
        Test complete workflow: employee submits project request ->
        team lead approves -> notifications sent.
        """
        employee = sample_users["employee"]
        team_lead = sample_users["team_lead"]
        project = db_session.query(Project).filter(Project.is_active == True).first()
        taccount = db_session.query(TAccount).first()

        # Step 1: Employee logs in and submits project request
        login_response = client.post(
            "/login",
            data={"email": employee.email, "password": "testpass123"},
            follow_redirects=False,
        )
        employee_cookies = {"travel_approval_session": login_response.cookies["travel_approval_session"]}

        tomorrow = date.today() + timedelta(days=1)
        week_later = tomorrow + timedelta(days=7)

        create_response = client.post(
            "/requests/new",
            data={
                "request_type": "project",
                "project_id": project.id,
                "destination": "Stockholm",
                "start_date": tomorrow.isoformat(),
                "end_date": week_later.isoformat(),
                "purpose": "Project kickoff meeting",
                "estimated_cost": "12000.00",
                "taccount_id": taccount.id,
            },
            cookies=employee_cookies,
            follow_redirects=False,
        )
        assert create_response.status_code == 303

        # Step 2: Verify request routed to team lead
        travel_request = (
            db_session.query(TravelRequest)
            .filter(
                TravelRequest.requester_id == employee.id,
                TravelRequest.request_type == "project",
            )
            .first()
        )
        assert travel_request.approver_id == team_lead.id
        assert travel_request.project_id == project.id

        # Step 3: Team lead approves
        login_response = client.post(
            "/login",
            data={"email": team_lead.email, "password": "testpass123"},
            follow_redirects=False,
        )
        team_lead_cookies = {"travel_approval_session": login_response.cookies["travel_approval_session"]}

        approve_response = client.post(
            f"/requests/{travel_request.id}/approve",
            data={"comments": "Approved for project work"},
            cookies=team_lead_cookies,
            follow_redirects=False,
        )
        assert approve_response.status_code == 303

        # Step 4: Verify approval
        db_session.refresh(travel_request)
        assert travel_request.status == "approved"

    def test_complete_project_workflow_rejection(
        self, client: TestClient, db_session: Session, sample_users: dict[str, User]
    ):
        """
        Test complete workflow: employee submits project request ->
        team lead rejects -> employee sees rejection.
        """
        employee = sample_users["employee"]
        team_lead = sample_users["team_lead"]
        project = db_session.query(Project).filter(Project.is_active == True).first()
        taccount = db_session.query(TAccount).first()

        # Step 1: Employee submits project request
        login_response = client.post(
            "/login",
            data={"email": employee.email, "password": "testpass123"},
            follow_redirects=False,
        )
        employee_cookies = {"travel_approval_session": login_response.cookies["travel_approval_session"]}

        tomorrow = date.today() + timedelta(days=1)
        week_later = tomorrow + timedelta(days=7)

        client.post(
            "/requests/new",
            data={
                "request_type": "project",
                "project_id": project.id,
                "destination": "Oslo",
                "start_date": tomorrow.isoformat(),
                "end_date": week_later.isoformat(),
                "purpose": "Site visit",
                "estimated_cost": "9000.00",
                "taccount_id": taccount.id,
            },
            cookies=employee_cookies,
            follow_redirects=False,
        )

        travel_request = (
            db_session.query(TravelRequest)
            .filter(
                TravelRequest.requester_id == employee.id,
                TravelRequest.destination == "Oslo",
            )
            .first()
        )

        # Step 2: Team lead rejects with reason
        login_response = client.post(
            "/login",
            data={"email": team_lead.email, "password": "testpass123"},
            follow_redirects=False,
        )
        team_lead_cookies = {"travel_approval_session": login_response.cookies["travel_approval_session"]}

        reject_response = client.post(
            f"/requests/{travel_request.id}/reject",
            data={"reason": "Site visit can be done remotely via video call"},
            cookies=team_lead_cookies,
            follow_redirects=False,
        )
        assert reject_response.status_code == 303

        # Step 3: Verify rejection
        db_session.refresh(travel_request)
        assert travel_request.status == "rejected"
        assert "remotely" in travel_request.rejection_reason

        # Step 4: Employee sees rejection notification
        employee_notifications = (
            db_session.query(Notification)
            .filter(
                Notification.user_id == employee.id,
                Notification.message.contains("rejected"),
            )
            .all()
        )
        assert len(employee_notifications) >= 1

        # Step 5: Employee can view rejection details
        detail_response = client.get(
            f"/requests/{travel_request.id}",
            cookies=employee_cookies,
        )
        assert detail_response.status_code == 200
        assert b"Oslo" in detail_response.content
        assert b"remotely" in detail_response.content


class TestAccountingReportWorkflow:
    """Test the complete workflow for accounting reports."""

    def test_accounting_can_view_approved_requests(
        self, client: TestClient, db_session: Session, sample_users: dict[str, User]
    ):
        """
        Test that accounting staff can view and filter approved travel requests.
        """
        # First create and approve a request
        employee = sample_users["employee"]
        manager = sample_users["manager"]
        taccount = db_session.query(TAccount).first()

        # Create approved request
        tomorrow = date.today() + timedelta(days=1)
        week_later = tomorrow + timedelta(days=7)

        travel_request = TravelRequest(
            requester_id=employee.id,
            approver_id=manager.id,
            request_type="operations",
            destination="Test City",
            start_date=tomorrow,
            end_date=week_later,
            purpose="Test purpose",
            estimated_cost=Decimal("10000.00"),
            taccount_id=taccount.id,
            status="approved",
        )
        db_session.add(travel_request)
        db_session.commit()

        # Create accounting user if not exists
        accounting_user = db_session.query(User).filter(User.role == "accounting").first()
        if not accounting_user:
            from app.auth.password import hash_password

            accounting_user = User(
                email="accounting@test.com",
                full_name="Test Accounting",
                password_hash=hash_password("testpass123"),
                role="accounting",
                is_active=True,
            )
            db_session.add(accounting_user)
            db_session.commit()

        # Login as accounting
        login_response = client.post(
            "/login",
            data={"email": accounting_user.email, "password": "testpass123"},
            follow_redirects=False,
        )
        accounting_cookies = {"travel_approval_session": login_response.cookies["travel_approval_session"]}

        # Access reports page
        reports_response = client.get("/reports", cookies=accounting_cookies)
        assert reports_response.status_code == 200
        assert b"Test City" in reports_response.content


class TestAdminProjectManagement:
    """Test the complete workflow for admin project management."""

    def test_admin_can_create_and_manage_project(
        self, client: TestClient, db_session: Session, sample_users: dict[str, User]
    ):
        """
        Test that admin can create projects and assign team leads.
        """
        admin = sample_users["admin"]
        team_lead = sample_users["team_lead"]

        # Login as admin
        login_response = client.post(
            "/login",
            data={"email": admin.email, "password": "testpass123"},
            follow_redirects=False,
        )
        admin_cookies = {"travel_approval_session": login_response.cookies["travel_approval_session"]}

        # Create new project
        create_response = client.post(
            "/admin/projects",
            data={
                "name": "E2E Test Project",
                "description": "Project created in E2E test",
                "team_lead_id": team_lead.id,
            },
            cookies=admin_cookies,
            follow_redirects=False,
        )
        assert create_response.status_code == 303

        # Verify project was created
        project = db_session.query(Project).filter(Project.name == "E2E Test Project").first()
        assert project is not None
        assert project.team_lead_id == team_lead.id
        assert project.is_active is True


@pytest.fixture
def sample_users(db_session: Session) -> dict[str, User]:
    """Create sample users for E2E tests."""
    from app.auth.password import hash_password

    users = {}

    # Create admin
    admin = User(
        email="admin_e2e@test.com",
        full_name="Admin User E2E",
        password_hash=hash_password("testpass123"),
        role="admin",
        is_active=True,
    )
    db_session.add(admin)
    users["admin"] = admin

    # Create manager
    manager = User(
        email="manager_e2e@test.com",
        full_name="Manager User E2E",
        password_hash=hash_password("testpass123"),
        role="manager",
        is_active=True,
    )
    db_session.add(manager)
    users["manager"] = manager

    # Create team lead
    team_lead = User(
        email="teamlead_e2e@test.com",
        full_name="Team Lead User E2E",
        password_hash=hash_password("testpass123"),
        role="team_lead",
        is_active=True,
    )
    db_session.add(team_lead)
    users["team_lead"] = team_lead

    # Create employee
    employee = User(
        email="employee_e2e@test.com",
        full_name="Employee User E2E",
        password_hash=hash_password("testpass123"),
        role="employee",
        manager_id=None,  # Will be set after manager is committed
        is_active=True,
    )
    db_session.add(employee)
    db_session.commit()

    # Set manager relationship
    employee.manager_id = manager.id
    db_session.commit()
    users["employee"] = employee

    # Create project with team lead
    project = Project(
        name="E2E Test Project Alpha",
        description="Test project for E2E tests",
        team_lead_id=team_lead.id,
        is_active=True,
    )
    db_session.add(project)

    # Create T-account
    taccount = TAccount(
        account_code="T-E2E-001",
        account_name="E2E Test Account",
        description="Test T-account for E2E tests",
        is_active=True,
    )
    db_session.add(taccount)

    db_session.commit()

    return users
