/// Relayer Registry
/// 
/// Manages authorized relayer public keys and governance.

/// Interface for relayer registry
#[starknet::interface]
pub trait IRelayerRegistry<TContractState> {
    /// Adds a relayer public key
    fn add_relayer(ref self: TContractState, relayer_key: felt252);

    /// Removes a relayer public key
    fn remove_relayer(ref self: TContractState, relayer_key: felt252);

    /// Checks if a relayer is authorized
    fn is_relayer(self: @TContractState, relayer_key: felt252) -> bool;
}

/// TODO: Agent will implement relayer governance with OZ Ownable.
