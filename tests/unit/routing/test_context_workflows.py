import pytest

from routing.context import ConversationContext, InMemoryContextStore
from routing.models import Message
from routing.workflows import accept_workflow_input, start_workflow, transition_workflow


def test_context_store_isolates_user_and_conversation():
    store = InMemoryContextStore()
    context = ConversationContext(user_id="u1", conversation_id="c1", recent_messages=[Message(role="user", content="hi")])
    store.save(context)

    assert store.load("u1", "c1") == context
    assert store.load("u2", "c1") is None


def test_workflow_advances_and_collects_input():
    workflow = start_workflow("w1", "portfolio_builder")

    updated = accept_workflow_input(workflow, "risk_profile", "balanced")

    assert updated.current_step == "horizon"
    assert updated.collected_inputs == {"risk_profile": "balanced"}


def test_workflow_supports_suspend_and_resume():
    workflow = start_workflow("w1", "company_research")
    suspended = transition_workflow(workflow, "suspended")

    assert suspended.state == "suspended"
    assert transition_workflow(suspended, "active").state == "active"


def test_terminal_workflow_cannot_be_reactivated():
    workflow = transition_workflow(start_workflow("w1", "bond_evaluation"), "cancelled")

    with pytest.raises(ValueError, match="terminal"):
        transition_workflow(workflow, "active")
