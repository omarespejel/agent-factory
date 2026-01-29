/// Event Validator
/// 
/// Integrates quorum verification with key image tracking.

/// Interface for event validation
#[starknet::interface]
pub trait IEventValidator<TContractState> {
    /// Validates an attested event and records relevant state
    fn validate_event(ref self: TContractState, event_hash: felt252) -> bool;
}

/// TODO: Agent will implement validation flow.
