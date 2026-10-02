"""Unit tests for the Pulumi GCP Infrastructure demonstrating Advantage 5 (pytest + mocks)."""

import asyncio
import pytest # type: ignore
import pulumi # type: ignore

# Ensure event loop exists on main thread before setting Pulumi runtime mocks
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

# =============================================================================
# ADVANTAGE 5: In-Memory Unit Testing & Mocking (pytest)
# =============================================================================
class GcpMocks(pulumi.runtime.Mocks):
    def new_resource(self, args: pulumi.runtime.MockResourceArgs):
        # Return mock resource ID and inputs
        return [args.name + "_id", args.inputs]
        
    def call(self, args: pulumi.runtime.MockCallArgs):
        return {}

# Register mocks before importing infrastructure module
pulumi.runtime.set_mocks(GcpMocks())


@pytest.mark.asyncio
async def test_vm_instances_count_and_machine_type():
    """Verify 3 VM instances were created in loop with correct dev machine type."""
    import main # type: ignore
    
    # Assert exactly 3 VM instances were created
    assert len(main.instances) == 3

    # Assert machine_type set by if/else control flow for non-prod stack
    def check_machine_type(args):
        machine_type = args[0]
        assert machine_type == "e2-micro", f"Expected e2-micro for dev stack, got {machine_type}"

    return pulumi.Output.all(main.instances[0].machine_type).apply(check_machine_type)


@pytest.mark.asyncio
async def test_network_component_creation():
    """Verify ComponentResource exported network and subnet correctly."""
    import main # type: ignore
    
    assert main.network_sandbox.network is not None
    assert main.network_sandbox.subnet is not None
